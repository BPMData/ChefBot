import io

import pytest

from chefbot import export

RECIPE = """Hello foodies! Tonight: **Galbijjim (갈비찜)**, with oregano (ρίγανη) and a little 🔥.

Recipe Title: Galbijjim (갈비찜) — Braised Short Ribs

**The sauce:**
- 2 tbsp soy sauce (ganjang, 간장)
- 1 tbsp *honey*

## Method
1. Soak the ribs.
2. Braise until tender.
"""
TITLE = "Galbijjim (갈비찜) — Braised Short Ribs"
PNG = (b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde"
       b"\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x03\x01\x01\x00\xc9\xfe\x92\xef\x00\x00\x00\x00IEND\xaeB`\x82")


def test_lists_right_under_a_label_still_become_lists():
    html = export.markdown_to_html(RECIPE)
    assert "<ul>" in html and "<li>2 tbsp soy sauce" in html and "<ol>" in html


def test_html_page_is_standalone():
    page = export.recipe_html(TITLE, RECIPE, PNG)
    assert page.startswith("<!doctype html>") and "<title>Galbijjim (갈비찜)" in page
    assert "data:image/png;base64," in page and "<strong>Galbijjim (갈비찜)</strong>" in page
    assert "Recipe Title:" not in page          # the title is the heading instead


def test_file_stem():
    assert export.file_stem("Galbijjim (갈비찜) — Braised Short Ribs!") == "Galbijjim-갈비찜-Braised-Short-Ribs"
    assert export.file_stem("???") == "recipe"


def test_strip_cjk_tidies_brackets():
    assert export.strip_cjk("Galbijjim (갈비찜) and sesame oil (chamgireum, 참기름)") == \
        "Galbijjim and sesame oil (chamgireum)"


def test_assign_fonts_marks_runs():
    base = {ord(c) for c in "abc ()"}
    out = export.assign_fonts("<p>abc (갈비) ρ 🔥</p>", base, [("Greek", {ord("ρ")}), ("KR", {ord("갈"), ord("비")})])
    # spaces stay inside a run (so "갈비 찜" stays in one font); the emoji, which no font has, is dropped
    assert out == '<p>abc (<font face="KR">갈비</font>) <font face="Greek">ρ </font></p>'


def test_pdf_without_cjk_fonts_drops_only_cjk():
    pypdf = pytest.importorskip("pypdf")
    pdf = export.recipe_pdf(TITLE, RECIPE, PNG)
    assert pdf[:5] == b"%PDF-"
    text = "".join(p.extract_text() for p in pypdf.PdfReader(io.BytesIO(pdf)).pages)
    assert "Galbijjim" in text and "Braise until tender" in text and "ρίγανη"[:1] in text
    assert "갈비찜" not in text and "Recipe Title" not in text


def test_email_has_html_photo_and_pdf():
    msg = export.build_email("me@example.com", "you@example.com", TITLE, RECIPE, PNG, b"%PDF-1.4 fake")
    types = [p.get_content_type() for p in msg.walk()]
    assert types == ["multipart/mixed", "multipart/alternative", "text/plain", "multipart/related", "text/html",
                     "image/png", "application/pdf"]
    html = msg.get_payload()[0].get_payload()[1].get_payload()[0].get_content()
    assert "cid:" in html and "<li>2 tbsp soy sauce" in html
    assert msg["Subject"] == f"Recipe: {TITLE}"


def test_relay_payload_and_errors(monkeypatch):
    import httpx
    sent = {}

    def fake_post(url, json, timeout, follow_redirects):
        sent.update(json, url=url, follow=follow_redirects)
        return httpx.Response(200, json={"ok": True})

    monkeypatch.setattr(httpx, "post", fake_post)
    export.send_via_relay("https://script.google.com/x/exec", "s3cret", "you@example.com", TITLE, RECIPE, PNG, b"%PDF")
    assert sent["secret"] == "s3cret" and sent["to"] == "you@example.com" and sent["follow"] is True
    assert 'src="cid:dish"' in sent["html"] and sent["photoType"] == "image/png" and sent["pdfName"].endswith(".pdf")

    monkeypatch.setattr(httpx, "post", lambda *a, **k: httpx.Response(200, json={"ok": False, "error": "Wrong relay secret."}))
    with pytest.raises(export.EmailError, match="Wrong relay secret"):
        export.send_via_relay("https://x/exec", "bad", "you@example.com", TITLE, RECIPE)


def test_smtp_hangup_during_sign_in_is_explained(monkeypatch):
    import smtplib

    class FakeSMTP:
        def __init__(self, *a, **k): pass
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def login(self, u, p): raise smtplib.SMTPServerDisconnected("Connection unexpectedly closed")

    monkeypatch.setattr(smtplib, "SMTP_SSL", FakeSMTP)
    msg = export.build_email("me@example.com", "you@example.com", TITLE, RECIPE)
    with pytest.raises(export.EmailError, match="hung up while signing in"):
        export.send_email(msg, "smtp.gmail.com", 465, "me@example.com", "x" * 16)


def test_email_note_mentions_photo_only_when_there_is_one():
    assert export.attachments_phrase(True) == "the dish photo and a PDF"
    assert export.attachments_phrase(False) == "a PDF"


def _image_count(pdf: bytes) -> int:
    pypdf = pytest.importorskip("pypdf")
    return sum(len(p.images) for p in pypdf.PdfReader(io.BytesIO(pdf)).pages)


def test_pdf_has_the_photo():
    assert _image_count(export.recipe_pdf(TITLE, RECIPE, PNG)) == 1


@pytest.mark.parametrize("case", ["no pillow", "damaged photo"])
def test_pdf_leaves_out_a_photo_it_cannot_add(monkeypatch, case):
    """On a phone without Pillow (or with a broken picture) the PDF still gets made, just without the photo,
    so Save PDF, Email and Share keep working."""
    photo = PNG
    if case == "no pillow":
        import sys
        monkeypatch.setitem(sys.modules, "PIL", None)        # makes `from PIL import ...` fail
    else:
        photo = PNG[:20]
    with pytest.warns(UserWarning, match="Left the dish photo out"):
        pdf = export.recipe_pdf(TITLE, RECIPE, photo)
    monkeypatch.undo()          # count images with Pillow back, so a 0 can't come from the counting itself
    assert pdf.startswith(b"%PDF") and _image_count(pdf) == 0


def test_plain_text_drops_markdown_markers_but_keeps_lists():
    md = "## Ingredients\n**Sauce:**\n* 2 tbsp *gochujang*\n- 1 tsp sugar\n\nStir __well__."
    out = export.plain_text(md)
    assert "##" not in out and "**" not in out and "__" not in out
    assert "Sauce:" in out and "gochujang" in out and "*gochujang*" not in out
    assert "* 2 tbsp" in out and "- 1 tsp sugar" in out      # list bullets survive


def test_email_text_is_plain_and_complete():
    long = "Recipe Title: Stew\n" + "\n".join(f"**Step {i}:** stir" for i in range(2000))
    out = export.email_text("Stew", long)
    assert out.startswith("Stew\n\n") and "Recipe Title" not in out and "**" not in out
    assert "Step 1999: stir" in out                            # nothing cut off


def test_mailto_link_keeps_everything_unless_limited():
    from urllib.parse import unquote
    text = "Recipe Title: Galbijjim (갈비찜)\n" + "braise " * 3000
    full = unquote(export.mailto_link("a@b.c", "Galbijjim (갈비찜)", text))
    assert full.startswith("mailto:a@b.c?subject=Recipe: Galbijjim (갈비찜)&body=")
    assert full.count("braise") == 3000 and "Shortened" not in full
    short = unquote(export.mailto_link("a@b.c", "Galbijjim", text, limit=100))
    assert "Shortened here" in short and short.count("braise") < 20


def test_free_path_never_overwrites(tmp_path):
    first = export.free_path(tmp_path, "Galbijjim.png")
    assert first == tmp_path / "Galbijjim.png"
    first.write_bytes(b"x")
    second = export.free_path(tmp_path, "Galbijjim.png")
    assert second.name == "Galbijjim (2).png"
    second.write_bytes(b"y")
    assert export.free_path(tmp_path, "Galbijjim.png").name == "Galbijjim (3).png"
