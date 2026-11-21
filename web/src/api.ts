import { getVisitorId } from "./storage";

export type Turn = { role: "user" | "assistant"; content: string };
export type Options = {
  must_not: string;
  cuisine: string;
  audience: string;
  dessert: boolean;
  pantry: boolean;
  restrictions: string[];
};
export type Cuisine = {
  id: string;
  label: string;
  kind: string;
  children?: string[];
  subtitle?: string;
  about?: string;
  prompt_name?: string;
  flavors?: string[];
  sweet_only?: string[];
  signature_ingredients?: string[];
  substitutes?: string[];
  pantry?: string[];
};
export type CuisineTree = {
  roots: string[];
  nodes: Record<string, Cuisine>;
  legacy_ids?: Record<string, string>;
  audiences: string[];
  default_audience: string;
  restrictions: string[];
  no_cuisine: string;
  limits: { message_characters: number; follow_ups: number; photo_bytes: number };
};
export type Fix = { issue: string; location: string; fix: string };
export type Result = { title: string | null; markdown: string; fixes: Fix[] };
export type JobEvent =
  | { kind: "stage"; stage: "drafting" | "checking" | "fixing" | "done" }
  | { kind: "progress"; ingredients: string[]; step_count: number }
  | { kind: "draft"; delta: string }
  | ({ kind: "result" } & Result)
  | { kind: "stopped" }
  | { kind: "error"; message: string };

const base = (import.meta.env.VITE_API_URL ?? "http://localhost:8000").replace(/\/$/, "");
export const dietLimit = 3;

export class RequestError extends Error {
  constructor(message: string, readonly status: number) {
    super(message);
  }
}

async function request(path: string, init?: RequestInit) {
  const headers = new Headers(init?.headers);
  if (path !== "/healthz" && path !== "/api/cuisines") headers.set("X-Visitor-ID", await getVisitorId());
  let response: Response;
  try {
    response = await fetch(base + path, { ...init, headers });
  } catch (error) {
    if (init?.signal?.aborted) throw error;
    throw new RequestError("Couldn’t reach ChefBot. Check your connection and try again.", 0);
  }
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new RequestError(body?.detail ?? "ChefBot couldn’t complete this request.", response.status);
  }
  return response;
}

function jsonPost(data: unknown) {
  return { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) };
}

export const warmUp = () => request("/healthz");
export const loadCuisines = async (): Promise<CuisineTree> => (await request("/api/cuisines")).json();

export async function startJob(id: string, options: Options, ingredients: string, history: Turn[]) {
  await request("/api/jobs", jsonPost({ ...options, job_id: id, ingredients, history }));
}

export const stopJob = (id: string) => request(`/api/jobs/${encodeURIComponent(id)}/stop`, { method: "POST" });

export async function watchJob(id: string, onEvent: (event: JobEvent) => void, signal: AbortSignal) {
  const response = await request(`/api/jobs/${encodeURIComponent(id)}/events`, { signal });
  const reader = response.body?.pipeThrough(new TextDecoderStream()).getReader();
  if (!reader) throw new RequestError("This browser couldn’t read the reply stream.", 0);
  let buffer = "";
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += value.replace(/\r\n/g, "\n");
      let boundary = buffer.indexOf("\n\n");
      while (boundary !== -1) {
        const frame = buffer.slice(0, boundary);
        buffer = buffer.slice(boundary + 2);
        const kind = frame.match(/^event: (.+)$/m)?.[1];
        const data = frame.match(/^data: (.+)$/m)?.[1];
        if (kind && data) {
          onEvent({ ...JSON.parse(data), kind });
          if (kind === "result" || kind === "error" || kind === "stopped") return;
        }
        boundary = buffer.indexOf("\n\n");
      }
    }
    throw new RequestError("The reply stream paused. Reconnect to see the recipe.", 0);
  } finally {
    await reader.cancel().catch(() => {});
  }
}

export async function readPhoto(file: Blob): Promise<string> {
  const response = await request("/api/photo/ingredients", {
    method: "POST",
    headers: { "Content-Type": file.type },
    body: file,
  });
  return (await response.json()).ingredients;
}

export async function dishPicture(title: string) {
  const response = await request("/api/picture", jsonPost({ title: title.trim().slice(0, 250) }));
  return toDataUrl(await response.blob());
}

export async function recipePdf(title: string, markdown: string, photo?: string) {
  const response = await request("/api/pdf", jsonPost({ title, markdown, photo: photo?.split(",")[1] }));
  return response.blob();
}

function toDataUrl(blob: Blob): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result));
    reader.onerror = () => reject(new Error("Couldn’t save this picture."));
    reader.readAsDataURL(blob);
  });
}

export async function resizePhoto(file: File): Promise<Blob> {
  const photo = await createImageBitmap(file);
  try {
    const scale = Math.min(1, 1440 / Math.max(photo.width, photo.height));
    const canvas = document.createElement("canvas");
    canvas.width = Math.max(1, Math.round(photo.width * scale));
    canvas.height = Math.max(1, Math.round(photo.height * scale));
    const context = canvas.getContext("2d");
    if (!context) throw new Error("This browser couldn’t resize the photo.");
    context.fillStyle = "#fff";
    context.fillRect(0, 0, canvas.width, canvas.height);
    context.drawImage(photo, 0, 0, canvas.width, canvas.height);
    return await new Promise((resolve, reject) => {
      canvas.toBlob((blob) => blob ? resolve(blob) : reject(new Error("Couldn’t resize this photo.")), "image/jpeg", 0.86);
    });
  } finally {
    photo.close();
  }
}
