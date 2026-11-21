import { ArrowLeft, Download, ExternalLink, Settings as SettingsIcon, Upload } from "lucide-react";
import { MotionConfig } from "motion/react";
import { lazy, Suspense, useCallback, useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import logo from "../../src/assets/logo_white.svg";
import { Chat } from "./Chat";
import { Home, type Draft } from "./Home";
import { Favorites, favoritePageSize } from "./RecipeLibrary";
import {
  loadCuisines, RequestError, startJob, stopJob, warmUp, type CuisineTree,
} from "./api";
import { RegionalMap } from "./CuisineMap";
import { CuisineBrowser, CuisineInfo } from "./CuisinePicker";
import { rememberCuisine } from "./cooking";
import { initialJobView, JobWatch, type JobView, type Terminal } from "./JobWatch";
import { useNavigation } from "./navigation";
import { download } from "./exports";
import type { GlobeCamera } from "./globe/Globe";
import {
  backup, changeConversations, completeConversation, readConversations, requestPersistence, restoreBackup,
  type Conversation, type Message, type Pending,
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
  const { route, navigate, back, openCuisine, dismissCuisine, finishCuisine, openFavoriteFolder, updateLibrary } = useNavigation();
  const chatId = route.id;
  const settings = route.screen === "settings";
  const globe = route.screen === "globe";
  const favorites = route.screen === "favorites";
  const favoritePath = route.favoritePath ?? [];
  const favoriteLimit = route.favoriteLimit ?? favoritePageSize;
  const mapPath = route.mapPath ?? [];
  const level = mapPath.at(-1);
  const parentLevel = mapPath.at(-2);
  const backLabel = level ? (parentLevel ? "Back to " + (tree?.nodes[parentLevel]?.label ?? "region") : "Back to globe")
    : route.previous === "globe" ? "Back to globe" : settings && chatId ? "Back to recipe" :
      (favorites && !!favoritePath.length) || route.previous === "favorites" ? "Back to Favorites" : "Back to recipes";
  const [ready, setReady] = useState(false);
  const [status, report] = useState("");
  const [startingJob, setStartingJob] = useState<string | null>(null);
  const [jobViews, setJobViews] = useState<Record<string, JobView>>({});
  const [retry, setRetry] = useState<{ id: string } | null>(null);
  const starting = useRef(false);
  const globeCamera = useRef<GlobeCamera | null>(null);
  const foregroundChat = useRef<string | null>(null);
  foregroundChat.current = route.screen === "recipe" ? chatId : null;
  const chat = recipes.find((recipe) => recipe.id === chatId);
  const jobId = chat?.pending?.id;
  const jobView = jobId ? jobViews[jobId] ?? initialJobView : initialJobView;
  const readyReply = recipes.filter((recipe) => recipe.unreadReply).sort((a, b) => b.updated - a.updated)[0];
  const busy = startingJob !== null;

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

  const updateJob = useCallback((id: string, view: JobView | null) => {
    setJobViews((current) => {
      if (view) return { ...current, [id]: view };
      const { [id]: removed, ...remaining } = current;
      return remaining;
    });
  }, []);

  const finishJob = useCallback(async (id: string, pending: Pending, terminal?: Terminal) => {
    let applied = false;
    const completed = await change((current) => current.map((recipe) => {
      if (recipe.id !== id || recipe.pending?.id !== pending.id) return recipe;
      applied = true;
      if (terminal?.kind === "result") {
        return { ...completeConversation(recipe, recipe.pending, terminal),
          unreadReply: foregroundChat.current !== id || document.visibilityState === "hidden" };
      }
      return { ...recipe, pending: undefined,
        failedRequest: { text: pending.ingredients, historyLength: pending.history.length } };
    }));
    if (!applied || foregroundChat.current !== id) return;
    if (terminal?.kind === "error") report(terminal.message);
    else if (terminal?.kind === "stopped") report("Stopped. You can edit your request and send it again.");
    else if (!terminal) report("This recipe job is no longer available. You can send the request again.");
    else if (completed.filter((recipe) => recipe.messages.length).length >= 3
      && !localStorage.getItem("chefbot.has-backup") && !localStorage.getItem("chefbot.backup-notice")) {
      localStorage.setItem("chefbot.backup-notice", "yes");
      report(storageNotice);
    }
  }, [change]);

  useEffect(() => {
    document.title = readyReply ? "Recipe ready · ChefBot" : "ChefBot";
  }, [readyReply?.id]);

  async function stop() {
    if (!jobId) return;
    try {
      await stopJob(jobId);
    } catch (error) {
      if (!(error instanceof RequestError && error.status === 404)) {
        report("Couldn’t stop the recipe. Check your connection and try again.");
        return;
      }
    }
    setRetry({ id: jobId });
  }

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
    const pending = { id: crypto.randomUUID(), ingredients: text, history, submittedAt: Date.now() };
    setStartingJob(pending.id);
    report("");
    const isNew = chatId !== conversation.id;
    try {
      // Store the ID first so even a lost POST response can be recovered by replaying it.
      await change((current) => {
        const stored = current.find((recipe) => recipe.id === conversation.id);
        if (!stored && isNew) return [...current, { ...conversation, pending }];
        if (!stored || stored.pending || stored.updated !== conversation.updated) {
          throw new RequestError("This recipe changed in another tab. Reopen it before sending another request.", 409);
        }
        return current.map((recipe) => recipe.id === conversation.id ? { ...recipe, pending, failedRequest: undefined } : recipe);
      });
      let acknowledged = false;
      try {
        await startJob(pending.id, conversation.settings, text, history.map(({ role, content }) => ({ role, content })));
        acknowledged = true;
      } catch (error) {
        // A lost connection or gateway error can happen after the server accepted the job.
        if (!(error instanceof RequestError) || (error.status >= 400 && error.status < 500)) {
          await change((current) => current.flatMap((recipe) => {
            if (recipe.id !== conversation.id || recipe.pending?.id !== pending.id) return [recipe];
            return isNew ? [] : [{ ...recipe, pending: undefined, failedRequest: conversation.failedRequest }];
          }));
          throw error;
        }
      }
      if (acknowledged) {
        // If this write fails, the persisted ID still works. Only the startup grace period remains.
        await mutate(conversation.id, (recipe) => recipe.pending?.id === pending.id
          ? { ...recipe, pending: { ...recipe.pending, submittedAt: undefined } } : recipe).catch(() => {});
      }
      void requestPersistence();
      if (isNew || settings) navigate("recipe", conversation.id);
      return true;
    } catch (error) {
      report(error instanceof RequestError ? error.message : "ChefBot couldn’t save this request in your browser.");
      return false;
    } finally {
      starting.current = false;
      setStartingJob(null);
    }
  }

  function openRecipe(id: string) {
    navigate("recipe", id);
    void mutate(id, (recipe) => ({
      ...recipe, unreadReply: undefined, access_count: (recipe.access_count ?? 0) + 1, last_accessed: Date.now(),
    })).catch(() => report("Couldn’t update recipe history."));
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
      {recipes.map(({ id, pending }) => pending && pending.id !== startingJob &&
        <JobWatch key={pending.id} id={id} pending={pending} retry={retry?.id === pending.id ? retry : null}
          update={updateJob} finish={finishJob} />)}
      {(settings || chat || globe || favorites) && <button type="button" className="text-button back" onClick={back}>
        <ArrowLeft size={17} /> {backLabel}
      </button>}
      {status && <div className="notice" role="status">{status}</div>}
      {readyReply && <div className="notice ready-reply">
        <span role="status">Ready: {readyReply.title}</span>
        {readyReply.id === foregroundChat.current
          ? <button className="text-button" type="button" onClick={() => {
            void mutate(readyReply.id, (recipe) => ({ ...recipe, unreadReply: undefined }))
              .catch(() => report("Couldn’t dismiss this notice."));
          }}>Dismiss</button>
          : <button className="text-button" type="button" onClick={() => openRecipe(readyReply.id)}>Open recipe</button>}
      </div>}
      {chat && jobView.paused && <div className="notice" role="status">{jobView.paused}</div>}
      {settings ? <Settings recipes={recipes} refresh={setRecipes} report={report} /> :
        favorites && ready ? <Favorites recipes={recipes} tree={tree} path={favoritePath} query={route.query ?? ""}
          setQuery={(query) => updateLibrary({ query, favoriteLimit: favoritePageSize })}
          limit={favoriteLimit} showMore={() => updateLibrary({ favoriteLimit: favoriteLimit + favoritePageSize })}
          openFolder={openFavoriteFolder} goToLevel={(depth) => history.go(depth - favoritePath.length)}
          open={openRecipe} toggleFavorite={toggleFavorite} /> :
        globe && level && tree ? <RegionalMap id={level} tree={tree} choose={(id) =>
          tree.nodes[id]?.children?.length ? openCuisine({ mapPath: [...mapPath, id] }) : openCuisine({ preview: id })} /> :
        globe ? <Suspense fallback={<p role="status">Loading the globe…</p>}>
          <Globe camera={globeCamera} openRegion={(id) => openCuisine({ mapPath: [id] })}
            preview={(id) => openCuisine({ preview: id })} />
        </Suspense> :
        chat ? <Chat key={chat.id} conversation={chat} tree={tree} send={send} mutate={(transform) => mutate(chat.id, transform)}
          favorite={() => toggleFavorite(chat.id)} progress={jobView} provisional={jobView.draft} busy={busy} canReconnect={!!jobView.paused} stop={stop}
          reconnect={() => { if (jobId) setRetry({ id: jobId }); }}
          report={report} followUpLimit={tree?.limits.follow_ups ?? 5} messageLimit={tree?.limits.message_characters ?? 4000} /> :
        ready ? <Home tree={tree} draft={draft} setDraft={setDraft} create={() => void create()} busy={busy}
          recipes={recipes} browse={() => openCuisine({ picker: true })} preview={(id) => openCuisine({ preview: id })}
          removeRecipe={removeRecipe} openGlobe={() => { globeCamera.current = null; navigate("globe"); }}
          open={openRecipe} toggleFavorite={toggleFavorite}
          query={route.query ?? ""} setQuery={(query) => updateLibrary({ query })}
          openFavorites={() => navigate("favorites")} /> : <p role="status">Opening your recipe book…</p>}
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
