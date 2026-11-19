import { createStore, get, update } from "idb-keyval";
import type { Fix, Options, Result, Turn } from "./api";

export type Message = Turn & { title?: string | null; fixes?: Fix[]; jobId?: string };
export type Pending = { id: string; ingredients: string; history: Message[] };
export type Conversation = {
  id: string;
  title: string;
  settings: Options;
  messages: Message[];
  photos: Record<string, string>;
  favorite: boolean;
  access_count: number;
  last_accessed: number;
  updated: number;
  pending?: Pending;
};

const db = createStore("chefbot", "recipes");
const key = "conversations";
const format = "chefbot-recipes";
const photoUrl = /^data:image\/(?:jpeg|png|webp);base64,[A-Za-z0-9+/]+={0,2}$/;

export function readConversations() {
  return get<Conversation[]>(key, db).then((value) => value ?? []);
}

export async function changeConversations(change: (current: Conversation[]) => Conversation[]) {
  let result: Conversation[] = [];
  await update<Conversation[]>(key, (current) => {
    result = change(current ?? []);
    return result;
  }, db);
  return result;
}

export async function requestPersistence() {
  try {
    if (!localStorage.getItem("chefbot.persistence-requested")) {
      localStorage.setItem("chefbot.persistence-requested", "yes");
      await navigator.storage?.persist?.();
    }
  } catch {
    // The browser can still store recipes when persistent storage isn't available.
  }
}

export function completeConversation(conversation: Conversation, pending: Pending, result: Result): Conversation {
  const photos = Object.fromEntries(
    Object.entries(conversation.photos).filter(([index]) => Number(index) < pending.history.length),
  );
  return {
    ...conversation, title: result.title || conversation.title, updated: Date.now(), pending: undefined, photos,
    messages: [...pending.history, { role: "user", content: pending.ingredients },
      { role: "assistant", content: result.markdown, title: result.title, fixes: result.fixes, jobId: pending.id }],
  };
}

export function backup(conversations: Conversation[]) {
  const recipes = conversations.filter((recipe) => recipe.messages.length > 0)
    .map(({ pending, ...recipe }) => recipe);
  return JSON.stringify({ format, version: 1, conversations: recipes }, null, 2);
}

function validConversation(value: unknown): value is Conversation {
  if (typeof value !== "object" || value === null) return false;
  const recipe = value as Conversation;
  const settings = recipe.settings;
  return typeof recipe.id === "string" && recipe.id.length > 0 && typeof recipe.title === "string"
    && typeof recipe.favorite === "boolean" && typeof recipe.updated === "number"
    && typeof recipe.access_count === "number" && typeof recipe.last_accessed === "number"
    && Array.isArray(recipe.messages) && recipe.messages.length >= 2 && recipe.messages.length % 2 === 0
    && recipe.messages.every((turn, index) => turn && turn.role === (index % 2 ? "assistant" : "user")
      && typeof turn.content === "string" && (turn.title == null || typeof turn.title === "string")
      && (turn.fixes === undefined || (Array.isArray(turn.fixes) && turn.fixes.every((entry) => entry
        && typeof entry.issue === "string" && typeof entry.location === "string" && typeof entry.fix === "string"))))
    && !!settings && typeof settings.must_not === "string" && typeof settings.audience === "string"
    && typeof settings.cuisine === "string" && typeof settings.dessert === "boolean" && typeof settings.pantry === "boolean"
    && Array.isArray(settings.restrictions) && settings.restrictions.every((item) => typeof item === "string")
    && !!recipe.photos && typeof recipe.photos === "object" && Object.entries(recipe.photos).every(([index, photo]) =>
      /^\d+$/.test(index) && recipe.messages[Number(index)]?.role === "assistant" && typeof photo === "string" && photoUrl.test(photo));
}

export async function restoreBackup(file: File) {
  const data = JSON.parse(await file.text());
  if (data?.format !== format || data?.version !== 1 || !Array.isArray(data.conversations)
      || !data.conversations.every(validConversation)) {
    throw new Error("Choose a valid ChefBot recipes backup.");
  }
  const imported = new Map<string, Conversation>();
  for (const recipe of data.conversations as Conversation[]) {
    const previous = imported.get(recipe.id);
    if (!previous || previous.updated < recipe.updated) imported.set(recipe.id, { ...recipe, pending: undefined });
  }
  let added = 0;
  let changed = 0;
  const conversations = await changeConversations((current) => {
    const merged = new Map(current.map((recipe) => [recipe.id, recipe]));
    for (const recipe of imported.values()) {
      const previous = merged.get(recipe.id);
      if (previous && (previous.pending || previous.updated >= recipe.updated)) continue;
      if (previous) changed += 1;
      else added += 1;
      merged.set(recipe.id, recipe);
    }
    return [...merged.values()];
  });
  void requestPersistence();
  return { conversations, added, changed };
}
