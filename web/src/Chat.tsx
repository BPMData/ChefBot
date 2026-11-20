import { ArrowUp, Copy, Download, Image, Mail, RotateCcw, Share2, Star } from "lucide-react";
import { useState, type FormEvent } from "react";
import { dishPicture, recipePdf } from "./api";
import { download, exportHtml, fileName, mailto, recipeHtml } from "./exports";
import { backup, type Conversation, type Message } from "./storage";
import { Waiting } from "./Waiting";

type Progress = { stage: string; ingredients: string[]; steps: number };
type ReplyArgs = { conversation: Conversation; text: string; history: Message[] };

function Reply({ message, title, photo, savePhoto, report }: {
  message: Message; title: string; photo?: string; savePhoto: (photo: string) => Promise<void>; report: (message: string) => void;
}) {
  const [action, setAction] = useState("");
  const name = message.title || title;

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
    {photo && <img className="dish" src={photo} alt={name} />}
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
      <a href={mailto(name, message.content)}><Mail size={15} /> Email</a>
      <button type="button" disabled={!!action} onClick={() => void run("Share", async () => {
        if (navigator.share) await navigator.share({ title: name, text: message.content });
        else {
          await navigator.clipboard.writeText(message.content);
          report("Recipe copied to share.");
        }
      })}><Share2 size={15} /> Share</button>
      {message.jobId && message.title && !photo && <button type="button" disabled={!!action}
        onClick={() => void run("Picture", async () => savePhoto(await dishPicture(message.jobId!)))}>
        <Image size={15} /> {action === "Picture" ? "Making picture…" : "Picture"}
      </button>}
    </div>
  </article>;
}

export function Chat({ conversation, send, mutate, favorite, progress, provisional, busy, reconnect, canReconnect, report, followUpLimit, messageLimit }: {
  conversation: Conversation;
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
  const [undo, setUndo] = useState<Conversation | null>(null);
  const messages = conversation.messages;
  const pending = conversation.pending;
  const lastUserIndex = messages.length - 2;
  const blocked = busy || !!pending;
  const history = editing ? messages.slice(0, lastUserIndex) : messages;
  const canFollowUp = history.length / 2 <= followUpLimit;

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!text.trim() || blocked || !canFollowUp) return;
    if (await send({ conversation, text: text.trim(), history })) {
      setText("");
      setEditing(false);
      setUndo(null);
    }
  }

  async function removeLast() {
    const kept = messages.slice(0, lastUserIndex);
    try {
      await mutate((recipe) => ({ ...recipe, messages: kept,
        photos: Object.fromEntries(Object.entries(recipe.photos).filter(([index]) => Number(index) < lastUserIndex)),
        title: [...kept].reverse().find((message) => message.title)?.title || recipe.title, updated: Date.now() }));
      setUndo(conversation);
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
    <div className="messages">
      {messages.map((message, index) => message.role === "user"
        ? <div className="user-message" key={index}>
          <p>{message.content}</p>
          {index === lastUserIndex && index > 0 && !blocked && <div>
            <button className="text-button" type="button" onClick={() => { setEditing(true); setText(message.content); }}>Edit</button>
            <button className="text-button" type="button" onClick={() => void removeLast()}>Delete</button>
          </div>}
        </div>
        : <Reply key={message.jobId || index} message={message} title={conversation.title}
          photo={conversation.photos[index]} report={report}
          savePhoto={(photo) => mutate((recipe) => {
            if (recipe.messages[index]?.jobId !== message.jobId) throw new Error("This reply has changed.");
            return { ...recipe, photos: { ...recipe.photos, [index]: photo }, updated: Date.now() };
          })} />)}
      {pending && <>
        <div className="user-message"><p>{pending.ingredients}</p></div>
        {provisional && <article className="card reply" aria-label="Draft recipe">
          <h2>Draft recipe</h2>
          <div className="recipe-markdown" dangerouslySetInnerHTML={{ __html: recipeHtml(provisional) }} />
        </article>}
        {canReconnect ? <button className="secondary" type="button" onClick={reconnect}>Reconnect to recipe</button> :
          <Waiting stage={progress.stage} ingredients={progress.ingredients} steps={progress.steps} />}
      </>}
    </div>
    {undo && !blocked && <button type="button" className="secondary" onClick={() => {
      void mutate((recipe) => ({ ...undo, favorite: recipe.favorite, updated: Date.now() }))
        .then(() => setUndo(null)).catch(() => report("Couldn’t restore this follow-up."));
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
    {!blocked && <form className="card follow-up" onSubmit={submit}>
      <label htmlFor="follow-up">{editing ? "Edit your follow-up" : messages.length ? "Ask a follow-up" : "Try your request again"}</label>
      <div className="follow-up-input">
        <textarea id="follow-up" rows={2} value={text} maxLength={messageLimit}
          disabled={!canFollowUp} placeholder={canFollowUp ? "Make it spicier, or ask a question…" : "This recipe has reached its follow-up limit."}
          onChange={(event) => setText(event.target.value)} />
        <button type="submit" className="primary icon-button" aria-label="Send reply" disabled={!text.trim() || !canFollowUp}>
          <ArrowUp size={21} />
        </button>
      </div>
      {editing && <button type="button" className="text-button" onClick={() => { setEditing(false); setText(""); }}>Cancel edit</button>}
    </form>}
  </>;
}
