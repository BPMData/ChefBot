import DOMPurify from "dompurify";
import { marked } from "marked";

export function recipeText(markdown: string) {
  return markdown.replace(/^[#*_ \t]*Recipe Title:.*\n?/gim, "").trim();
}

export function recipeHtml(markdown: string) {
  return DOMPurify.sanitize(marked.parse(recipeText(markdown), { async: false }), {
    FORBID_TAGS: ["img", "form", "input", "style", "svg", "math", "audio", "video"],
    FORBID_ATTR: ["style"],
  });
}

export function download(data: BlobPart, name: string, mime: string) {
  const url = URL.createObjectURL(data instanceof Blob ? data : new Blob([data], { type: mime }));
  const link = document.createElement("a");
  link.href = url;
  link.download = name;
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 30_000);
}

export function fileName(title: string) {
  return title.replace(/[^\p{L}\p{N} -]/gu, "").trim().replace(/ +/g, "-").slice(0, 80) || "recipe";
}

export function exportHtml(title: string, markdown: string, photo?: string) {
  const heading = document.createElement("h1");
  heading.textContent = title;
  const picture = document.createElement("img");
  if (photo && /^data:image\/(jpeg|png|webp);base64,/.test(photo)) {
    picture.src = photo;
    picture.alt = title;
  }
  const safeTitle = heading.innerHTML;
  const body = `<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${safeTitle}</title><style>body{max-width:45rem;margin:3rem auto;padding:0 1rem;color:#30201a;background:#fffaf5;font:1.1rem/1.65 system-ui}h1,h2,h3{font-family:Georgia,serif;line-height:1.2}img{max-width:100%;border-radius:1rem}a{color:#9b3929}</style>
  <main>${heading.outerHTML}${picture.src ? picture.outerHTML : ""}${recipeHtml(markdown)}</main></html>`;
  download(body, fileName(title) + ".html", "text/html");
}

export function mailto(title: string, markdown: string) {
  const body = recipeText(markdown).replace(/\*\*|__|^`|`$/gm, "");
  let end = Math.min(body.length, 6500);
  const encode = (value: string) => encodeURIComponent(value.replace(/[\uD800-\uDBFF](?![\uDC00-\uDFFF])|(?<![\uD800-\uDBFF])[\uDC00-\uDFFF]/g, "�"));
  const prefix = "mailto:?subject=" + encode(title.slice(0, 250)) + "&body=";
  while (end > 0 && prefix.length + encode(body.slice(0, end)).length > 6_900) end = Math.max(0, end - 128);
  return prefix + encode(body.slice(0, end) + (end < body.length ? "\n\n[Recipe shortened for email.]" : ""));
}
