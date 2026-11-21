import { Mail, Share2 } from "lucide-react";
import { useRef, useState } from "react";
import { recipePdf } from "./api";
import { fileName, mailto, plainRecipe } from "./exports";

export function ShareReply({ title, markdown, photo, report }: {
  title: string; markdown: string; photo?: string; report: (message: string) => void;
}) {
  const dialog = useRef<HTMLDialogElement>(null);
  const [mode, setMode] = useState<"email" | "share">("share");
  const [files, setFiles] = useState<File[]>([]);
  const [preparing, setPreparing] = useState(false);
  const [error, setError] = useState("");
  const generation = useRef(0);
  const text = plainRecipe(title, markdown);
  const email = mailto(title, markdown, localStorage.getItem("chefbot.email-to") ?? "");
  const supportsFiles = typeof navigator.share === "function" &&
    navigator.canShare?.({ files: [new File([], "recipe.pdf", { type: "application/pdf" })] });
  const emailWithFiles = supportsFiles && window.matchMedia("(any-pointer: coarse)").matches;

  async function shareText() {
    if (navigator.share) await navigator.share({ title, text });
    else {
      await navigator.clipboard.writeText(text);
      report("Recipe copied to share.");
    }
  }

  async function prepare(next: "email" | "share") {
    const request = ++generation.current;
    setMode(next);
    setFiles([]);
    setError("");
    setPreparing(true);
    dialog.current?.showModal();
    try {
      const stem = fileName(title);
      const pdf = await recipePdf(title.slice(0, 250), markdown, photo);
      const attachments = [new File([pdf], stem + ".pdf", { type: "application/pdf" })];
      if (photo) {
        const blob = await (await fetch(photo)).blob();
        attachments.push(new File([blob], stem + "." + blob.type.split("/")[1].replace("jpeg", "jpg"), { type: blob.type }));
      }
      if (generation.current !== request) return;
      if (navigator.canShare({ files: attachments })) setFiles(attachments);
      else setError("This browser can share the recipe as text.");
    } catch {
      if (generation.current === request) setError("Couldn’t prepare the attachments. You can still share the recipe text.");
    } finally {
      if (generation.current === request) setPreparing(false);
    }
  }

  async function share(attachments: File[] = []) {
    try {
      if (attachments.length) await navigator.share({ title, text, files: attachments });
      else await shareText();
      dialog.current?.close();
    } catch (error) {
      if (error instanceof Error && error.name === "AbortError") return;
      if (dialog.current?.open) {
        setFiles([]);
        setError("Couldn’t share the attachments. You can still share the recipe text.");
      } else report("Couldn’t share this recipe.");
    }
  }

  return <>
    {emailWithFiles ? <button type="button" onClick={() => void prepare("email")}><Mail size={15} /> Email</button>
      : <a href={email}><Mail size={15} /> Email</a>}
    <button type="button" onClick={() => supportsFiles ? void prepare("share") : void share()}><Share2 size={15} /> Share</button>
    <dialog ref={dialog} className="card share-dialog" onClose={() => generation.current++} aria-label="Share this reply">
      <h2>{title}</h2>
      <p role="status">{preparing ? "Preparing attachments…" : error || files.map((file) => file.name).join(" · ")}</p>
      <div className="action-row">
        <button type="button" onClick={() => dialog.current?.close()}>Cancel</button>
        {files.length > 0 && <button type="button" onClick={() => void share(files)}>
          {mode === "email" ? "Choose mail app" : "Share files"}</button>}
        {!preparing && !files.length && (mode === "email" ? <a href={email}>Open mail app</a> :
          <button type="button" onClick={() => void share()}>Share text</button>)}
      </div>
    </dialog>
  </>;
}
