"""Turning a ChefBot reply into things you can keep: Markdown, a standalone HTML page, a PDF, an e-mail."""
import base64
import html
import io
import re
import smtplib
import ssl
from email.message import EmailMessage
from email.utils import make_msgid
from pathlib import Path

import markdown as markdown_lib

ASSET_FONTS = Path(__file__).resolve().parents[1] / "assets" / "fonts"
CJK_FONT_URLS = {   # downloaded the first time a PDF needs them (10-18 MB each), then cached
    "kr": "https://raw.githubusercontent.com/google/fonts/main/ofl/notosanskr/NotoSansKR%5Bwght%5D.ttf",
    "jp": "https://raw.githubusercontent.com/google/fonts/main/ofl/notosansjp/NotoSansJP%5Bwght%5D.ttf",
    "sc": "https://raw.githubusercontent.com/google/fonts/main/ofl/notosanssc/NotoSansSC%5Bwght%5D.ttf",
}
_HANGUL = re.compile(r"[ᄀ-ᇿ㄰-㆏가-힯]")
_KANA = re.compile(r"[぀-ヿㇰ-ㇿ]")
_HAN = re.compile(r"[㐀-䶿一-鿿豈-﫿]")
STATIC_FONTS = ASSET_FONTS / "static"
_EMOJI = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u200D]")
_CJK_ANY = re.compile(r"[ᄀ-ᇿ　-〿぀-ヿ㄰-㆏ㇰ-ㇿ㐀-䶿"
                      r"一-鿿가-힯豈-﫿＀-￯]")


# ---------------------------------------------------------------- names and markdown

def file_stem(title: str) -> str:
    stem = re.sub(r"[^\w\s-]", "", title, flags=re.UNICODE).strip()
    stem = re.sub(r"[\s_]+", "-", stem)[:80].strip("-")
    return stem or "recipe"


_LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")


def normalize_markdown(text: str) -> str:
    """Models often start a list right under a line of text ('**Sauce:**' then '- item'). Strict Markdown needs a
    blank line there, or the list collapses into one paragraph."""
    out: list[str] = []
    for line in text.splitlines():
        if _LIST_ITEM.match(line) and out and out[-1].strip() and not _LIST_ITEM.match(out[-1]) \
                and not out[-1].startswith(("    ", "\t")):
            out.append("")
        out.append(line)
    return "\n".join(out)


def without_title_line(text: str) -> str:
    """Exports show the title as a heading, so drop the model's 'Recipe Title: ...' line from the body."""
    return re.sub(r"(?m)^[#*_\s]*Recipe Title:.*\n?", "", text)


def markdown_to_html(text: str) -> str:
    return markdown_lib.markdown(normalize_markdown(text), extensions=["extra", "sane_lists"],
                                 output_format="html")


def image_mime(data: bytes) -> str:
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if data[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    return "image/png"


# ---------------------------------------------------------------- standalone HTML page

PAGE_CSS = """
:root { --ink:#2a1d16; --muted:#7b6a60; --accent:#e8452c; --paper:#fffaf4; --card:#ffffff; --line:#eadfd5; }
@media (prefers-color-scheme: dark) {
  :root { --ink:#f3e9e1; --muted:#b4a399; --accent:#ff8a3d; --paper:#110e0c; --card:#1e1916; --line:#3a302a; }
}
* { box-sizing: border-box; }
body { margin:0; background:var(--paper); color:var(--ink);
       font:17px/1.6 "DM Sans", system-ui, -apple-system, "Segoe UI", sans-serif; }
main { max-width:760px; margin:0 auto; padding:32px 20px 64px; }
.card { background:var(--card); border:1px solid var(--line); border-radius:22px; padding:28px; }
.brand { font:700 14px "DM Sans", sans-serif; letter-spacing:.08em; text-transform:uppercase; color:var(--accent); }
h1, h2, h3, h4 { font-family:"Fraunces", Georgia, serif; line-height:1.2; }
h1.title { font-size:34px; margin:6px 0 20px; }
img.dish { width:100%; border-radius:18px; margin-bottom:20px; display:block; }
table { border-collapse:collapse; width:100%; } th, td { border:1px solid var(--line); padding:6px 10px; }
hr { border:0; border-top:1px solid var(--line); margin:24px 0; }
footer { color:var(--muted); font-size:13px; margin-top:24px; text-align:center; }
@media print { body { background:#fff; color:#000; } .card { border:0; padding:0; } }
"""


def recipe_html(title: str, text: str, photo: bytes | None = None) -> str:
    """A self-contained web page for the reply: styles inline, photo embedded."""
    img = ""
    if photo:
        img = (f'<img class="dish" alt="{html.escape(title)}" '
               f'src="data:{image_mime(photo)};base64,{base64.b64encode(photo).decode()}">')
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;600;700&family=Fraunces:wght@600;700&display=swap" rel="stylesheet">
<style>{PAGE_CSS}</style></head>
<body><main><div class="card">
{img}<div class="brand">ChefBot</div>
<h1 class="title">{html.escape(title)}</h1>
{markdown_to_html(without_title_line(text))}
</div>
<footer>Made with ChefBot. It's an AI: double-check recipes yourself, especially for allergies.</footer>
</main></body></html>
"""


# ---------------------------------------------------------------- PDF

def cjk_needed(text: str) -> list[str]:
    """Which CJK fonts this text needs, in fallback order."""
    need = []
    if _HANGUL.search(text):
        need.append("kr")
    if _KANA.search(text):
        need.append("jp")
    if _HAN.search(text) and "jp" not in need:
        need.append("sc")
    return need


def static_instance(variable_font: Path, weight: int, out: Path) -> Path:
    """Pin a variable font to one weight (other axes at their defaults) and save it. Cached by file name."""
    if out.exists():
        return out
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer

    font = TTFont(variable_font)
    axes = {a.axisTag: None for a in font["fvar"].axes}
    if "wght" in axes:
        axes["wght"] = weight
    static = instancer.instantiateVariableFont(font, axes)
    # Give the cut its own name. Otherwise every cut keeps the parent's default name (e.g. both regular and bold
    # say "DMSans9ptRegular") and fpdf2 mixes up their glyphs, garbling text.
    family = f"{out.stem.split('-')[0]} W{weight}"
    postscript = f"{out.stem.replace(' ', '')}-W{weight}"
    names = static["name"]
    for rec in list(names.names):
        if rec.nameID in (1, 2, 3, 4, 6, 16, 17, 21, 22, 25):
            names.removeNames(nameID=rec.nameID)
    for name_id, value in ((1, family), (2, "Regular"), (3, postscript), (4, f"{family} Regular"), (6, postscript)):
        names.setName(value, name_id, 3, 1, 0x409)
        names.setName(value, name_id, 1, 0, 0)
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(".part")
    static.save(tmp)
    tmp.replace(out)
    return out


def ensure_cjk_fonts(text: str, cache_dir: Path, timeout: float = 120) -> dict[str, tuple[Path, Path]]:
    """Download (once) the CJK fonts this text needs and cut regular + bold. Returns what's available; never
    raises."""
    import httpx

    found: dict[str, tuple[Path, Path]] = {}
    cache_dir.mkdir(parents=True, exist_ok=True)
    for key in cjk_needed(text):
        regular, bold = cache_dir / f"NotoSans{key.upper()}-Regular.ttf", cache_dir / f"NotoSans{key.upper()}-Bold.ttf"
        if not (regular.exists() and bold.exists()):
            raw = cache_dir / f"NotoSans{key.upper()}-variable.ttf"
            try:
                with httpx.Client(timeout=timeout, follow_redirects=True) as client:
                    r = client.get(CJK_FONT_URLS[key])
                    r.raise_for_status()
                raw.write_bytes(r.content)
                static_instance(raw, 400, regular)
                static_instance(raw, 700, bold)
            except Exception:
                continue
            finally:
                raw.unlink(missing_ok=True)
        found[key] = (regular, bold)
    return found


def strip_cjk(text: str) -> str:
    """Remove CJK characters a PDF can't draw, and tidy what's left: 'Galbijjim (갈비찜)' -> 'Galbijjim'."""
    return tidy_brackets(_CJK_ANY.sub("", text))


def tidy_brackets(text: str) -> str:
    out = re.sub(r"\(\s*[,;/·]*\s*\)", "", text)
    out = re.sub(r"\(\s*[,;/·]\s*", "(", out)
    out = re.sub(r"\s*[,;/·]\s*\)", ")", out)
    return re.sub(r"[ \t]{2,}", " ", out)


def _cmap(path: Path) -> set[int]:
    from fontTools.ttLib import TTFont
    return set(TTFont(path, lazy=True)["cmap"].getBestCmap())


def assign_fonts(html_text: str, base: set[int], extras: list[tuple[str, set[int]]]) -> str:
    """Wrap every run of characters the base font can't draw in <font face="..."> naming a font that can.
    Characters no font has (emoji, rare symbols) are dropped. fpdf2's automatic fallback garbles long mixed-script
    paragraphs, so the switching is made explicit."""
    out: list[str] = []
    for part in re.split(r"(<[^>]+>|&[#\w]+;)", html_text):
        if not part or part[0] in "<&":
            out.append(part)
            continue
        run_face, run = None, []

        def flush():
            if run:
                chunk = "".join(run)
                out.append(f'<font face="{run_face}">{chunk}</font>' if run_face else chunk)
                run.clear()

        for ch in part:
            cp = ord(ch)
            if cp in base or ch.isspace():
                face = None if not (run_face and ch.isspace()) else run_face
            else:
                face = next((name for name, cmap in extras if cp in cmap), "")
                if face == "":
                    continue
            if face != run_face:
                flush()
                run_face = face
            run.append(ch)
        flush()
    return "".join(out)


def recipe_pdf(title: str, text: str, photo: bytes | None = None,
               cjk_fonts: dict[str, tuple[Path, Path]] | None = None) -> bytes:
    """A printable PDF of the reply, with the dish photo on top."""
    from fpdf import FPDF, TextStyle

    cjk_fonts = cjk_fonts or {}
    title, text = _EMOJI.sub("", title), _EMOJI.sub("", text)
    if [k for k in cjk_needed(title + text) if k not in cjk_fonts]:
        title, text = strip_cjk(title), strip_cjk(text)

    pdf = FPDF(format="Letter")
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.set_margins(20, 18, 20)
    ink, accent, muted = (42, 29, 22), (232, 69, 44), (123, 106, 96)

    title_html = f"<h1>{html.escape(title)}</h1>"
    body_html = re.sub(r"</?(?:em|i)>", "", markdown_to_html(without_title_line(text)))   # no italic cuts bundled for PDFs
    if (STATIC_FONTS / "DMSans-Regular.ttf").exists():
        pdf.add_font("DMSans", "", STATIC_FONTS / "DMSans-Regular.ttf")
        pdf.add_font("DMSans", "B", STATIC_FONTS / "DMSans-Bold.ttf")
        pdf.add_font("Fraunces", "B", STATIC_FONTS / "Fraunces-Bold.ttf")
        pdf.add_font("NotoSans", "", STATIC_FONTS / "NotoSans-Regular.ttf")
        pdf.add_font("NotoSans", "B", STATIC_FONTS / "NotoSans-Bold.ttf")
        extras = [("NotoSans", _cmap(STATIC_FONTS / "NotoSans-Regular.ttf"))]
        for key, (regular, bold) in cjk_fonts.items():
            pdf.add_font(f"NotoSans{key.upper()}", "", regular)
            pdf.add_font(f"NotoSans{key.upper()}", "B", bold)
            extras.append((f"NotoSans{key.upper()}", _cmap(regular)))
        base = _cmap(STATIC_FONTS / "DMSans-Regular.ttf") & _cmap(STATIC_FONTS / "Fraunces-Bold.ttf")
        title_html, body_html = assign_fonts(title_html, base, extras), assign_fonts(body_html, base, extras)
        body, heading = "DMSans", "Fraunces"
    else:   # bare-bones fallback if the bundled fonts are missing
        body, heading = "helvetica", "helvetica"
        title_html = title_html.encode("latin-1", "replace").decode("latin-1")
        body_html = body_html.encode("latin-1", "replace").decode("latin-1")

    pdf.add_page()
    if photo:
        from PIL import Image as PILImage
        with PILImage.open(io.BytesIO(photo)) as im:
            w, h = im.size
        disp_w, disp_h = pdf.epw, pdf.epw * h / w
        if disp_h > 110:                      # keep tall photos from eating the first page
            disp_h, disp_w = 110, 110 * w / h
        pdf.image(io.BytesIO(photo), x=pdf.l_margin + (pdf.epw - disp_w) / 2, w=disp_w, h=disp_h)
        pdf.ln(6)
    pdf.set_text_color(*accent)
    pdf.set_font(body, "B", 9)
    pdf.cell(text="CHEFBOT", new_x="LMARGIN", new_y="NEXT")

    pdf.set_text_color(*ink)
    pdf.set_font(body, "", 11)
    heading_styles = {tag: TextStyle(font_family=heading, font_style="B", font_size_pt=size, color=ink,
                                     t_margin=5, b_margin=2)
                      for tag, size in (("h1", 18), ("h2", 16), ("h3", 14), ("h4", 12))}
    title_style = {"h1": TextStyle(font_family=heading, font_style="B", font_size_pt=22, color=ink,
                                   t_margin=0, b_margin=0)}
    pdf.write_html(title_html, font_family=body, tag_styles=title_style, warn_on_tags_not_matching=False)
    pdf.write_html(body_html, font_family=body, tag_styles=heading_styles, li_prefix_color=accent,
                   ul_bullet_char="\u2022", warn_on_tags_not_matching=False)

    pdf.ln(6)
    pdf.set_font(body, "", 8.5)
    pdf.set_text_color(*muted)
    pdf.multi_cell(0, 4.5, "Made with ChefBot. It's an AI: double-check recipes yourself, especially for allergies.")
    return bytes(pdf.output())


# ---------------------------------------------------------------- e-mail

class EmailError(Exception):
    """Sending failed. The message is safe to show the user."""


def attachments_phrase(has_photo: bool) -> str:
    """What an emailed recipe carries, for the Email dialog. The photo only if one was made."""
    return "the dish photo and a PDF" if has_photo else "a PDF"


def email_text(title: str, text: str) -> str:
    return f"{title}\n\n{without_title_line(text)}\n\n-- Made with ChefBot"


def email_html(title: str, text: str, photo_cid: str | None = None) -> str:
    """The email body. `photo_cid` names an inline image attached alongside it."""
    img = (f'<img src="cid:{photo_cid}" alt="" style="width:100%;max-width:640px;border-radius:16px;'
           f'margin-bottom:16px">') if photo_cid else ""
    return (f'<div style="font-family:Georgia,serif;max-width:680px;margin:0 auto;color:#2a1d16;line-height:1.55">'
            f'{img}<div style="color:#e8452c;font:700 12px sans-serif;letter-spacing:.08em">CHEFBOT</div>'
            f'<h1 style="margin:4px 0 16px">{html.escape(title)}</h1>'
            f'<div style="font-family:-apple-system,Segoe UI,Roboto,sans-serif;font-size:15px">'
            f'{markdown_to_html(without_title_line(text))}</div>'
            f'<p style="color:#7b6a60;font-size:12px;margin-top:24px">Made with ChefBot. It\'s an AI: double-check '
            f'recipes yourself, especially for allergies.</p></div>')


def build_email(sender: str, to: str, title: str, text: str, photo: bytes | None = None,
                pdf: bytes | None = None) -> EmailMessage:
    """A formatted e-mail: HTML body with the photo inline, plain-text fallback, PDF attached."""
    msg = EmailMessage()
    msg["Subject"] = f"Recipe: {title}"
    msg["From"] = sender
    msg["To"] = to
    msg.set_content(email_text(title, text))
    cid = make_msgid(domain="chefbot.local")
    msg.add_alternative(email_html(title, text, cid[1:-1] if photo else None), subtype="html")
    if photo:
        mime = image_mime(photo)
        msg.get_payload()[1].add_related(photo, maintype="image", subtype=mime.split("/")[1], cid=cid)
    if pdf:
        msg.add_attachment(pdf, maintype="application", subtype="pdf", filename=f"{file_stem(title)}.pdf")
    return msg


def send_email(msg: EmailMessage, host: str, port: int, username: str, password: str, timeout: float = 30) -> None:
    """Send through the user's own mail account. Port 465 = SSL, anything else = STARTTLS.
    Raises EmailError saying which step failed: connecting, signing in, or sending."""
    context = ssl.create_default_context()
    stage = "connecting to the mail server"
    try:
        server = (smtplib.SMTP_SSL(host, port, context=context, timeout=timeout) if port == 465
                  else smtplib.SMTP(host, port, timeout=timeout))
        with server:
            if port != 465:
                server.starttls(context=context)
            stage = "signing in"
            server.login(username, password)
            stage = "sending"
            server.send_message(msg)
    except smtplib.SMTPAuthenticationError as e:
        raise EmailError("The mail server didn't accept the address and app password. The app password has to "
                         "be made on the same account as 'Send from'.") from e
    except (smtplib.SMTPServerDisconnected, ConnectionError, OSError) as e:
        if stage == "signing in":
            raise EmailError("The mail server hung up while signing in. That usually means the app password "
                             "belongs to a different account than 'Send from', or Google blocked the sign-in. "
                             "The ChefBot mail relay avoids this (docs/EMAIL.md).") from e
        raise EmailError(f"Lost the connection while {stage} ({type(e).__name__}). Some networks block "
                         f"outgoing mail; the ChefBot mail relay works anywhere (docs/EMAIL.md).") from e
    except smtplib.SMTPException as e:
        raise EmailError(f"The mail server refused it while {stage}: {e}") from e


def send_via_relay(url: str, secret: str, to: str, title: str, text: str, photo: bytes | None = None,
                   pdf: bytes | None = None, timeout: float = 60) -> None:
    """Send through the ChefBot mail relay (tools/mail-relay.gs, an Apps Script web app)."""
    import httpx

    payload = {"secret": secret, "to": to, "subject": f"Recipe: {title}", "text": email_text(title, text),
               "html": email_html(title, text, "dish" if photo else None)}
    if photo:
        payload["photo"] = base64.b64encode(photo).decode()
        payload["photoType"] = image_mime(photo)
    if pdf:
        payload["pdf"] = base64.b64encode(pdf).decode()
        payload["pdfName"] = f"{file_stem(title)}.pdf"
    try:
        # Apps Script answers a POST with a redirect to the result; following it is how you read the reply.
        r = httpx.post(url, json=payload, timeout=timeout, follow_redirects=True)
    except httpx.HTTPError as e:
        raise EmailError(f"Couldn't reach the mail relay ({type(e).__name__}). Check the web address in Settings.") from e
    try:
        data = r.json()
    except ValueError:
        raise EmailError("The mail relay sent back something unexpected. Check that it's deployed as a web app "
                         "with access for 'Anyone' (docs/EMAIL.md).") from None
    if not data.get("ok"):
        raise EmailError(f"The mail relay said: {data.get('error', 'unknown error')}")
