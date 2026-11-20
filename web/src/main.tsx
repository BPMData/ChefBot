import { ArrowLeft, Download, ExternalLink, Settings as SettingsIcon, Upload } from "lucide-react";
import { MotionConfig } from "motion/react";
import { lazy, Suspense, useCallback, useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import logo from "../../src/assets/logo_white.svg";
import { Chat } from "./Chat";
import { Home, type Draft } from "./Home";
import {
  loadCuisines, RequestError, startJob, warmUp, watchJob, type CuisineTree, type JobEvent,
} from "./api";
import { RegionalMap } from "./CuisineMap";
import { CuisineBrowser, CuisineInfo } from "./CuisinePicker";
import { rememberCuisine } from "./cooking";
import { useNavigation } from "./navigation";
import { download } from "./exports";
import {
  backup, changeConversations, completeConversation, readConversations, requestPersistence, restoreBackup,
  type Conversation, type Message,
} from "./storage";
import "./style.css";

const Globe = lazy(() => import("./globe/Globe"));

const storageNotice = "Recipes are saved in this browser only. Clearing site data deletes them. Export them to keep a backup.";
const emptyDraft: Draft = {
  ingredients: "",
  settings: {
    must_not: "", cuisine: "Nothing in particular", audience: "A working professional.",
    dessert: false, pantry: false, restrictions: [],
  },
};
const initialProgress = { stage: "drafting", ingredients: [] as string[], steps: 0 };

function applyTheme(theme: string) {
  document.documentElement.dataset.theme = theme;
  document.documentElement.style.colorScheme = theme === "system" ? "light dark" : theme;
}

function Settings({ recipes, refresh, report }: {
  recipes: Conversation[]; refresh: (recipes: Conversation[]) => void; report: (status: string) => void;
}) {
  const [theme, setTheme] = useState(document.documentElement.dataset.theme ?? "dark");
  const [recipient, setRecipient] = useState(() => localStorage.getItem("chefbot.email-to") ?? "");
  const [importing, setImporting] = useState(false);
  return <>
    <div className="intro"><h1>Settings</h1></div>
    <section className="card settings-card form-card">
      <div className="form-field">
        <label htmlFor="theme">Appearance</label>
        <select id="theme" value={theme} onChange={(event) => {
          const choice = event.target.value;
          applyTheme(choice);
          setTheme(choice);
          localStorage.setItem("chefbot.theme", choice);
        }}>
          <option value="dark">Dark</option><option value="light">Light</option><option value="system">System</option>
        </select>
      </div>
      <div className="form-field">
        <label htmlFor="email-to">Send recipes to</label>
        <input id="email-to" type="email" autoComplete="email" placeholder="Optional email address" value={recipient}
          onChange={(event) => setRecipient(event.target.value)} onBlur={(event) => {
            if (event.currentTarget.reportValidity()) localStorage.setItem("chefbot.email-to", recipient.trim());
          }} />
        <small>Fills in the recipient when ChefBot opens an email link.</small>
      </div>
    </section>
    <section className="card settings-card">
      <h2>Recipe backups</h2>
      <p>{storageNotice}</p>
      <div className="action-row">
        <button className="secondary" type="button" disabled={!recipes.some((recipe) => recipe.messages.length)}
          onClick={() => {
            download(backup(recipes), "chefbot-recipes.json", "application/json");
            localStorage.setItem("chefbot.has-backup", "yes");
          }}><Download size={17} /> Export all recipes</button>
        <label className="secondary photo-control">
          <Upload size={17} /> {importing ? "Importing…" : "Import recipes"}
          <input type="file" accept=".json,application/json" aria-label="Import recipes" disabled={importing}
            onChange={async (event) => {
              const file = event.currentTarget.files?.[0];
              event.currentTarget.value = "";
              if (!file) return;
              setImporting(true);
              try {
                const result = await restoreBackup(file);
                refresh(result.conversations);
                localStorage.setItem("chefbot.has-backup", "yes");
                report(`Added ${result.added}, updated ${result.changed}.`);
              } catch {
                report("Couldn’t import this file. Choose a valid ChefBot recipes backup.");
              } finally { setImporting(false); }
            }} />
        </label>
      </div>
    </section>
    <section className="card settings-card">
      <h2>About ChefBot</h2>
      <p>ChefBot’s source code is available under the GNU Affero General Public License.</p>
      <a className="secondary" href="https://github.com/BPMData/ChefBot" target="_blank"
        rel="noreferrer">Source code <ExternalLink size={15} /></a>
    </section>
  </>;
}

function App() {
  const [draft, setDraft] = useState<Draft>(() => ({
    ...emptyDraft, settings: { ...emptyDraft.settings, must_not: localStorage.getItem("chefbot.must-not") ?? "",
      pantry: localStorage.getItem("chefbot.pantry") === "true" },
  }));
  const [tree, setTree] = useState<CuisineTree | null>(null);
  const [recipes, setRecipes] = useState<Conversation[]>([]);
  const { route, navigate, back, openCuisine, dismissCuisine, finishCuisine } = useNavigation();
  const chatId = route.id;
  const settings = route.screen === "settings";
  const globe = route.screen === "globe";
  const mapPath = route.mapPath ?? [];
  const level = mapPath.at(-1);
  const parentLevel = mapPath.at(-2);
  const backLabel = level ? (parentLevel ? "Back to " + (tree?.nodes[parentLevel]?.label ?? "region") : "Back to globe")
    : route.previous === "globe" ? "Back to globe" : settings && chatId ? "Back to recipe" : "Back to recipes";
  const [ready, setReady] = useState(false);
  const [status, report] = useState("");
  const [busy, setBusy] = useState(false);
  const [provisional, setProvisional] = useState("");
  const [progress, setProgress] = useState(initialProgress);
  const [reconnect, setReconnect] = useState(0);
  const [canReconnect, setCanReconnect] = useState(false);
  const starting = useRef(false);
  const chat = recipes.find((recipe) => recipe.id === chatId);
  const jobId = chat?.pending?.id;

  const change = useCallback(async (transaction: (recipes: Conversation[]) => Conversation[]) => {
    const result = await changeConversations(transaction);
    setRecipes(result);
    return result;
  }, []);

  useEffect(() => {
    void warmUp().catch(() => {});
    const load = () => void loadCuisines().then(setTree).catch(() => {});
    const refresh = () => void readConversations().then(setRecipes)
      .catch(() => report("This browser couldn’t open saved recipes."))
      .finally(() => setReady(true));
    load();
    refresh();
    window.addEventListener("focus", refresh);
    window.addEventListener("online", load);
    return () => {
      window.removeEventListener("focus", refresh);
      window.removeEventListener("online", load);
    };
  }, []);

  useEffect(() => {
    if (ready && chatId && !chat) {
      navigate("home", null, true);
    }
  }, [ready, chatId, chat, navigate]);

  useEffect(() => report(""), [route]);

  useEffect(() => {
    if (!jobId || !chatId || settings) return;
    const controller = new AbortController();
    const { signal } = controller;
    setProgress(initialProgress);
    setCanReconnect(false);
    let terminal: Extract<JobEvent, { kind: "result" | "error" }> | undefined;
    const event = (message: JobEvent) => {
      if (message.kind === "stage") setProgress((old) => ({ ...old, stage: message.stage }));
      if (message.kind === "progress") setProgress((old) => ({ ...old, ingredients: message.ingredients, steps: message.step_count }));
      if (message.kind === "draft") setProvisional((current) => current + message.delta);
      if (message.kind === "result" || message.kind === "error") terminal = message;
    };

    async function watch() {
      let failure: unknown;
      for (let attempt = 0; attempt < 3 && !signal.aborted; attempt += 1) {
        try {
          setProvisional("");
          await watchJob(jobId!, event, signal);
          break;
        } catch (error) {
          if (signal.aborted) return;
          failure = error;
          if (error instanceof RequestError && error.status === 404) break;
          if (attempt < 2) await new Promise((resolve) => setTimeout(resolve, (attempt + 1) * 800));
        }
      }
      if (signal.aborted) return;
      if (!terminal && !(failure instanceof RequestError && failure.status === 404)) {
        setCanReconnect(true);
        report("The connection paused. Reconnect to check your recipe.");
        return;
      }
      try {
        const completed = await change((current) => current.map((recipe) => {
          if (recipe.id !== chatId || !recipe.pending || recipe.pending.id !== jobId) return recipe;
          return terminal?.kind === "result"
            ? completeConversation(recipe, recipe.pending, terminal) : { ...recipe, pending: undefined,
              failedRequest: { text: recipe.pending.ingredients, historyLength: recipe.pending.history.length } };
        }));
        if (signal.aborted) return;
        if (terminal?.kind === "error") report(terminal.message);
        else if (!terminal) report("This recipe job expired. Send the request again.");
        else if (completed.filter((recipe) => recipe.messages.length).length >= 3
          && !localStorage.getItem("chefbot.has-backup") && !localStorage.getItem("chefbot.backup-notice")) {
          localStorage.setItem("chefbot.backup-notice", "yes");
          report(storageNotice);
        }
      } catch {
        if (signal.aborted) return;
        setCanReconnect(true);
        report("The recipe couldn’t be saved. Reconnect to try saving it again.");
      }
    }
    void watch();
    return () => controller.abort();
  }, [change, chatId, jobId, reconnect, settings]);

  function pickCuisine(id: string) {
    if (id !== tree?.no_cuisine) rememberCuisine(id);
    setDraft((current) => ({ ...current, settings: { ...current.settings, cuisine: id } }));
  }

  async function removeRecipe(id: string) {
    try {
      await change((current) => {
        if (current.find((recipe) => recipe.id === id)?.pending) throw new Error();
        return current.filter((recipe) => recipe.id !== id);
      });
    } catch { report("Couldn’t delete this recipe. Check whether a reply is still in progress."); }
  }

  async function mutate(id: string, transform: (recipe: Conversation) => Conversation) {
    await change((current) => current.map((recipe) => recipe.id === id ? transform(recipe) : recipe));
  }

  function toggleFavorite(id: string) {
    void mutate(id, (recipe) => ({ ...recipe, favorite: !recipe.favorite }))
      .catch(() => report("Couldn’t update favorites."));
  }

  async function send({ conversation, text, history }: { conversation: Conversation; text: string; history: Message[] }) {
    if (starting.current || conversation.pending) return false;
    starting.current = true;
    setBusy(true);
    report("");
    try {
      const id = await startJob(conversation.settings, text, history.map(({ role, content }) => ({ role, content })));
      const pending = { id, ingredients: text, history };
      await change((current) => {
        const stored = current.find((recipe) => recipe.id === conversation.id);
        if (!stored && !conversation.messages.length && !chatId) return [...current, { ...conversation, pending }];
        if (!stored || stored.pending || stored.updated !== conversation.updated) {
          throw new RequestError("This recipe changed in another tab. Reopen it before sending another request.", 409);
        }
        return current.map((recipe) => recipe.id === conversation.id ? { ...recipe, failedRequest: undefined, pending } : recipe);
      });
      void requestPersistence();
      if (chatId !== conversation.id || settings) navigate("recipe", conversation.id);
      return true;
    } catch (error) {
      report(error instanceof RequestError ? error.message : "ChefBot couldn’t save this request in your browser.");
      return false;
    } finally {
      starting.current = false;
      setBusy(false);
    }
  }

  async function create() {
    const now = Date.now();
    const recipe: Conversation = {
      id: crypto.randomUUID(), title: "New recipe", settings: { ...draft.settings, pantry: draft.settings.pantry && draft.settings.cuisine !== emptyDraft.settings.cuisine },
      messages: [], photos: {}, favorite: false, access_count: 0, last_accessed: now, updated: now,
    };
    if (await send({ conversation: recipe, text: draft.ingredients.trim(), history: [] })) {
      setDraft((current) => ({ ...current, ingredients: "" }));
    }
  }

  return <MotionConfig reducedMotion="user">
    <header className="site-header">
      <div className="header-inner">
        <button type="button" className="wordmark" onClick={() => navigate("home")} aria-label="ChefBot home">
          <span className="brand-icon"><img src={logo} alt="" /></span> ChefBot
        </button>
        <button type="button" className="icon-button settings-button" aria-label="Settings" onClick={() => navigate("settings", chatId)}><SettingsIcon size={21} /></button>
      </div>
    </header>
    <main>
      {(settings || chat || globe) && <button type="button" className="text-button back" onClick={back}>
        <ArrowLeft size={17} /> {backLabel}
      </button>}
      {status && <div className="notice" role="status">{status}</div>}
      {settings ? <Settings recipes={recipes} refresh={setRecipes} report={report} /> :
        globe && level && tree ? <RegionalMap id={level} tree={tree} choose={(id) =>
          tree.nodes[id]?.children?.length ? openCuisine({ mapPath: [...mapPath, id] }) : openCuisine({ preview: id })} /> :
        globe ? <Suspense fallback={<p role="status">Loading the globe…</p>}>
          <Globe openRegion={(id) => openCuisine({ mapPath: [id] })} preview={(id) => openCuisine({ preview: id })} />
        </Suspense> :
        chat ? <Chat key={chat.id} conversation={chat} tree={tree} send={send} mutate={(transform) => mutate(chat.id, transform)}
          favorite={() => toggleFavorite(chat.id)} progress={progress} provisional={provisional} busy={busy} canReconnect={canReconnect}
          reconnect={() => { report(""); setReconnect((attempt) => attempt + 1); }}
          report={report} followUpLimit={tree?.limits.follow_ups ?? 5} messageLimit={tree?.limits.message_characters ?? 4000} /> :
        ready ? <Home tree={tree} draft={draft} setDraft={setDraft} create={() => void create()} busy={busy}
          recipes={recipes} browse={() => openCuisine({ picker: true })} preview={(id) => openCuisine({ preview: id })} removeRecipe={removeRecipe} openGlobe={() => navigate("globe")} open={(id) => {
            navigate("recipe", id);
            void mutate(id, (recipe) => ({ ...recipe, access_count: recipe.access_count + 1, last_accessed: Date.now() }))
              .catch(() => report("Couldn’t update recipe history."));
          }} toggleFavorite={toggleFavorite} /> : <p role="status">Opening your recipe book…</p>}
      {tree && route.picker && <CuisineBrowser tree={tree} close={dismissCuisine}
        preview={(id) => openCuisine({ preview: id })} reset={() => { pickCuisine(tree.no_cuisine); finishCuisine(); }} />}
      {tree && route.preview && tree.nodes[route.preview] && <CuisineInfo tree={tree} id={route.preview} close={dismissCuisine}
        choose={() => { pickCuisine(route.preview!); finishCuisine(); }} />}
    </main>
  </MotionConfig>;
}

const savedTheme = localStorage.getItem("chefbot.theme");
applyTheme(savedTheme === "light" || savedTheme === "system" ? savedTheme : "dark");
createRoot(document.getElementById("root")!).render(<App />);
