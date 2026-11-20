import { ArrowDown, ArrowUp, Copy, Download, Image, RotateCcw, Star, X } from "lucide-react";
import { useEffect, useRef, useState, type FormEvent } from "react";
import { dishPicture, recipePdf, type CuisineTree } from "./api";
import { download, exportHtml, fileName, recipeHtml } from "./exports";
import { backup, type Conversation, type Message } from "./storage";
import { historicalRequest, requestTags, tweaks } from "./cooking";
import { ShareReply } from "./ShareReply";
import { Waiting } from "./Waiting";

type Progress = { stage: string; ingredients: string[]; steps: number };
type ReplyArgs = { conversation: Conversation; text: string; history: Message[] };

function Reply({ message, title, photo, savePhoto, report }: {
  message: Message; title: string; photo?: string; savePhoto: (photo: string) => Promise<void>; report: (message: string) => void;
}) {
  const [action, setAction] = useState("");
  const name = message.title || title;
  const viewer = useRef<HTMLDialogElement>(null);

  async function run(label: string, execute: () => Promise<void>) {
    setAction(label);
    try { await execute(); }
    catch (error) {
      if (error instanceof DOMException && error.name === "AbortError") return;
      report(error instanceof Error ? error.message : "ChefBot couldn’t complete this action.");
    } finally { setAction(""); }
  }

  return <article className="card reply">
    {message.title && <h2>{message.title}</h2>}
    {photo && <>
      <button type="button" className="dish-preview" aria-label={"View picture of " + name}
        onClick={() => viewer.current?.showModal()}><img className="dish" src={photo} alt={name} /></button>
      <dialog className="picture-viewer" ref={viewer} aria-label={"Picture of " + name}>
        <div className="viewer-toolbar">
          <a className="secondary" href={photo} download={fileName(name) + "." + photo.slice(11, photo.indexOf(";")).replace("jpeg", "jpg")}>
            <Download size={17} /> Save picture
          </a>
          <button className="secondary" type="button" onClick={() => viewer.current?.close()}><X size={17} /> Close</button>
        </div>
        <img src={photo} alt={name} />
      </dialog>
    </>}
    <div className="recipe-markdown" dangerouslySetInnerHTML={{ __html: recipeHtml(message.content) }} />
    {!!message.fixes?.length && <details className="fixes">
      <summary>Fixed {message.fixes.length} {message.fixes.length === 1 ? "thing" : "things"}</summary>
      <ul>{message.fixes.map((item, index) => <li key={index}><strong>{item.location}</strong><p>{item.issue}</p><p>{item.fix}</p></li>)}</ul>
    </details>}
    <div className="reply-actions">
      <button type="button" disabled={!!action} onClick={() => void run("Copy", async () => {
        await navigator.clipboard.writeText(message.content);
        report("Recipe copied.");
      })}><Copy size={15} /> Copy</button>
      <button type="button" disabled={!!action} onClick={() => void run("PDF", async () => {
        download(await recipePdf(name.slice(0, 250), message.content, photo), fileName(name) + ".pdf", "application/pdf");
      })}><Download size={15} /> {action === "PDF" ? "Preparing PDF…" : "PDF"}</button>
      <button type="button" disabled={!!action} onClick={() => exportHtml(name, message.content, photo)}>HTML</button>
      <ShareReply title={name} markdown={message.content} photo={photo} report={report} />
      {message.jobId && message.title && <button type="button" disabled={!!action}
        onClick={() => void run("Picture", async () => savePhoto(await dishPicture(message.jobId!)))}>
        <Image size={15} /> {action === "Picture" ? "Making picture…" : photo ? "New picture" : "Picture"}
      </button>}
    </div>
  </article>;
}

export function Chat({ conversation, tree, send, mutate, favorite, progress, provisional, busy, reconnect, canReconnect, report, followUpLimit, messageLimit }: {
  conversation: Conversation;
  tree: CuisineTree | null;
  send: (args: ReplyArgs) => Promise<boolean>;
  mutate: (change: (recipe: Conversation) => Conversation) => Promise<void>;
  favorite: () => void;
  progress: Progress;
  provisional: string;
  busy: boolean;
  reconnect: () => void;
  canReconnect: boolean;
  report: (message: string) => void;
  followUpLimit: number;
  messageLimit: number;
}) {
  const [text, setText] = useState("");
  const [editing, setEditing] = useState(false);
  const [undo, setUndo] = useState<{ before: Conversation; revision: number } | null>(null);
  const composer = useRef<HTMLTextAreaElement>(null);
  const thread = useRef<HTMLDivElement>(null);
  const warning = useRef<HTMLDialogElement>(null);
  const [awayFromEnd, setAwayFromEnd] = useState(false);
  const tags = requestTags(conversation.settings, tree);
  const messages = conversation.messages;
  const pending = conversation.pending;
  const lastUserIndex = messages.length - 2;
  const blocked = busy || !!pending;
  const history = editing ? messages.slice(0, lastUserIndex) : messages;
  const canFollowUp = history.length / 2 <= followUpLimit;

  const failed = conversation.failedRequest;
  useEffect(() => {
    if (failed) {
      setText(failed.text);
      setEditing(failed.historyLength < messages.length);
    }
  }, [failed?.text, failed?.historyLength, messages.length]);

  const latest = messages.at(-1)?.jobId;
  useEffect(() => {
    const list = thread.current;
    if (!list) return;
    if (pending) list.scrollTop = list.scrollHeight;
    else if (messages.length > 2) list.querySelector(".reply:last-of-type")?.scrollIntoView({ block: "start" });
    else list.scrollTop = 0;
  }, [pending?.id, latest, messages.length]);

  useEffect(() => {
    const list = thread.current;
    if (!list) return;
    const check = () => setAwayFromEnd(list.scrollHeight - list.clientHeight - list.scrollTop > list.clientHeight * 0.8);
    const observer = new ResizeObserver(check);
    observer.observe(list);
    observer.observe(list.firstElementChild!);
    list.addEventListener("scroll", check, { passive: true });
    return () => { observer.disconnect(); list.removeEventListener("scroll", check); };
  }, []);

  async function sendText(value: string) {
    if (!value.trim() || blocked || !canFollowUp) return;
    if (await send({ conversation, text: value.trim(), history })) {
      setText("");
      setEditing(false);
      setUndo(null);
    }
  }

  function submit(event: FormEvent) {
    event.preventDefault();
    void sendText(text);
  }

  async function removeLast() {
    const kept = messages.slice(0, lastUserIndex);
    try {
      const revision = Date.now();
      await mutate((recipe) => {
        if (recipe.pending || recipe.updated !== conversation.updated) throw new Error("This reply changed.");
        return { ...recipe, failedRequest: undefined, messages: kept,
          photos: Object.fromEntries(Object.entries(recipe.photos).filter(([index]) => Number(index) < lastUserIndex)),
          title: [...kept].reverse().find((message) => message.title)?.title || "New recipe", updated: revision };
      });
      setUndo({ before: conversation, revision });
      setText("");
      setEditing(false);
    } catch { report("Couldn’t delete this follow-up."); }
  }

  return <>
    <div className="chat-heading">
      <h1>{conversation.title}</h1>
      {!!messages.length && <button type="button" className="icon-button star" aria-label={conversation.favorite ? "Remove from favorites" : "Add to favorites"}
        aria-pressed={conversation.favorite} onClick={favorite}><Star size={22} fill={conversation.favorite ? "currentColor" : "none"} /></button>}
    </div>
    <div className="thread-frame">
      <div ref={thread} className="thread" role="region" aria-label="Recipe conversation" tabIndex={0}>
        <div className="messages">
          {(pending?.history ?? messages).map((message, index) => message.role === "user"
            ? <div className="user-message" key={index}>
              <p>{message.content}</p>
              {index === 0 && <div className="request-tags">{tags.map((tag, i) => <span key={i}>{tag}</span>)}</div>}
              <div className="user-actions">
                <button className="text-button" type="button" aria-label="Copy your message" onClick={async () => {
                  try {
                    await navigator.clipboard.writeText(index === 0 ? message.content + "\n\n" + tags.join(" · ") : message.content);
                    report("Message copied.");
                  } catch { report("Couldn’t copy this message."); }
                }}><Copy size={15} /> Copy</button>
                {index === lastUserIndex && index > 0 && !blocked && <>
                  <button className="text-button" type="button" onClick={() => {
                    setEditing(true); setText(message.content); composer.current?.focus();
                  }}>Edit</button>
                  <button className="text-button" type="button" onClick={() => void removeLast()}>Delete</button>
                </>}
              </div>
            </div>
            : <Reply key={message.jobId || index} message={message} title={conversation.title}
              photo={conversation.photos[index]} report={report}
              savePhoto={(photo) => mutate((recipe) => {
                if (recipe.messages[index]?.jobId !== message.jobId) throw new Error("This reply has changed.");
                return { ...recipe, photos: { ...recipe.photos, [index]: photo }, updated: Date.now() };
              })} />)}
          {pending && <>
            <div className="user-message"><p>{pending.ingredients}</p>
              {!pending.history.length && <div className="request-tags">{tags.map((tag, i) => <span key={i}>{tag}</span>)}</div>}
            </div>
            {provisional && <article className="card reply" aria-label="Draft recipe">
              <h2>Draft recipe</h2>
              <div className="recipe-markdown" dangerouslySetInnerHTML={{ __html: recipeHtml(provisional) }} />
            </article>}
            {canReconnect ? <button className="secondary" type="button" onClick={reconnect}>Reconnect to recipe</button> :
              <Waiting stage={progress.stage} ingredients={progress.ingredients} steps={progress.steps} />}
          </>}
        </div>
        {undo && undo.revision === conversation.updated && !blocked && <button type="button" className="secondary" onClick={() => {
          void mutate((recipe) => {
            if (recipe.pending || recipe.updated !== undo.revision) throw new Error("This reply changed.");
            return { ...recipe, title: undo.before.title, messages: undo.before.messages, photos: undo.before.photos, updated: Date.now() };
          }).then(() => setUndo(null)).catch(() => report("Couldn’t restore this follow-up."));
        }}>Undo delete</button>}
        {!!messages.length && !blocked && <div className="chat-actions">
          <button className="secondary" type="button" onClick={() => void send({
            conversation, text: messages[lastUserIndex].content, history: messages.slice(0, lastUserIndex),
          })}><RotateCcw size={16} /> Try again</button>
          <button className="secondary" type="button" onClick={() =>
            download(backup([conversation]), fileName(conversation.title) + ".chefbot.json", "application/json")}>
            <Download size={16} /> Export recipe
          </button>
        </div>}
      </div>
    {awayFromEnd && <button type="button" className="jump secondary" aria-label="Jump to the bottom"
      onClick={() => thread.current?.scrollTo({ top: thread.current.scrollHeight })}><ArrowDown size={18} /></button>}
    </div>
    {!blocked && <form className="card follow-up" onSubmit={submit}>
      {!!messages.length && canFollowUp && !editing && <div className="quick-tweaks" role="group" aria-label="Quick changes">
        {tweaks.map(([label, prompt]) => <button className="chip" type="button" key={label}
          onClick={() => void sendText(prompt)}>{label}</button>)}
        <button className="chip" type="button" onClick={() => warning.current?.showModal()}>The 1817 version (beta)</button>
      </div>}
      <label htmlFor="follow-up">{editing ? "Edit your follow-up" : messages.length ? "Ask a follow-up" : "Try your request again"}</label>
      <div className="follow-up-input">
        <textarea ref={composer} id="follow-up" rows={1} value={text} maxLength={messageLimit}
          disabled={!canFollowUp} placeholder={canFollowUp ? "Ask for a change…" : "This recipe has reached its follow-up limit."}
          onChange={(event) => setText(event.target.value)} />
        <button type="submit" className="primary icon-button" aria-label="Send reply" disabled={!text.trim() || !canFollowUp}>
          <ArrowUp size={21} />
        </button>
      </div>
      {editing && <button type="button" className="text-button" onClick={() => { setEditing(false); setText(""); }}>Cancel edit</button>}
    </form>}
    <dialog ref={warning} className="card historical-warning" aria-labelledby="historical-title">
      <h2 id="historical-title">Historical recipes (beta)</h2>
      <p>ChefBot will imagine how the dish might have been cooked in 1817. AI can invent convincing techniques,
        cookbooks and quotations. Treat this as inspiration and check historical claims against a period source.</p>
      <div className="action-row">
        <button type="button" className="secondary" onClick={() => warning.current?.close()}>Cancel</button>
        <button type="button" className="primary" onClick={() => {
          warning.current?.close(); void sendText(historicalRequest);
        }}>I understand, rewrite it</button>
      </div>
    </dialog>
  </>;
}
