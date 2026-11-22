import { BookOpen, Camera, ImagePlus, Leaf, X } from "lucide-react";
import { useState, type Dispatch, type FormEvent, type ReactNode, type SetStateAction } from "react";
import { dietLimit, readPhoto, resizePhoto, type CuisineTree, type Options } from "./api";
import { audienceLabel } from "./cooking";
import { Recents } from "./RecipeLibrary";
import { CuisinePicker } from "./CuisinePicker";
import type { Conversation } from "./storage";

export type Draft = { ingredients: string; settings: Options };
/** Whether the home page's cuisine section starts with the spinning globe or the list. */
export type PickerStart = "globe" | "list";

export function Home({ tree, draft, setDraft, create, busy, recipes, open, toggleFavorite, openGlobe, browse, preview, removeRecipe, query, setQuery, openFavorites, globe, picker, setPicker }: {
  tree: CuisineTree | null; draft: Draft; setDraft: Dispatch<SetStateAction<Draft>>;
  create: () => void; busy: boolean; recipes: Conversation[];
  openGlobe: () => void; browse: () => void; preview: (id: string) => void; removeRecipe: (id: string) => Promise<void>;
  query: string; setQuery: (query: string) => void; openFavorites: () => void;
  open: (id: string) => void; toggleFavorite: (id: string) => void;
  /** The spinning globe, when it is the chosen way to pick a cuisine. */
  globe?: ReactNode; picker: PickerStart; setPicker?: (picker: PickerStart) => void;
}) {
  const [reading, setReading] = useState(false);
  const [photoStatus, setPhotoStatus] = useState("");
  const { ingredients, settings } = draft;
  const change = (settings: Options) => setDraft({ ...draft, settings });
  const messages = tree?.limits.message_characters ?? 4000;

  async function handlePhoto(file: File) {
    setPhotoStatus("");
    setReading(true);
    try {
      const found = await readPhoto(await resizePhoto(file));
      if (found) {
        setPhotoStatus("Check the ingredients and correct anything ChefBot missed.");
        setDraft((current) => ({ ...current, ingredients: [current.ingredients.trim(), found].filter(Boolean).join(", ").slice(0, messages) }));
      } else setPhotoStatus("ChefBot couldn’t see any ingredients in that photo.");
    } catch (error) {
      setPhotoStatus(error instanceof Error ? error.message : "ChefBot couldn’t read that photo.");
    } finally {
      setReading(false);
    }
  }

  const submit = (event: FormEvent) => {
    event.preventDefault();
    if (ingredients.trim() && !busy && !reading) create();
  };

  const cuisineCard = <>
      {tree && <section className={"card form-card" + (globe ? " cuisine-card globe-first" : "")} aria-label="Cuisine">
        {globe}
        <CuisinePicker tree={tree} cuisine={settings.cuisine} browse={browse} preview={preview}
          openGlobe={globe ? undefined : openGlobe} />
        {setPicker && <button type="button" className="text-button picker-switch"
          onClick={() => setPicker(picker === "globe" ? "list" : "globe")}>
          {picker === "globe" ? "Start with the cuisine list instead" : "Start with the spinning globe instead"}</button>}
        {settings.cuisine !== tree.no_cuisine && <div className="preferences">
          <label><input type="checkbox" checked={settings.pantry} onChange={(event) => {
            localStorage.setItem("chefbot.pantry", String(event.target.checked));
            change({ ...settings, pantry: event.target.checked });
          }} /> Pantry defaults</label>
          <small>Assume the staples in this cuisine’s infobox. ChefBot marks them in the recipe.</small>
        </div>}
      </section>}
  </>;

  return <>
    <div className="intro home-intro">
      <h1>What’s in your kitchen?</h1>
      {!!recipes.length && <button className="text-button saved-shortcut" type="button"
        onClick={() => document.getElementById("saved-recipes")?.scrollIntoView()}><BookOpen size={17} /> Your recipes</button>}
    </div>
    <form className="home-form" onSubmit={submit} aria-label="New recipe">
      {globe && cuisineCard}
      <section className="card form-card" aria-label="Recipe ingredients">
        <div className="form-field">
          <label htmlFor="ingredients">Ingredients</label>
          <div className="ingredients-box">
            <textarea id="ingredients" placeholder="Chicken thighs, tomatoes, feta…" maxLength={messages}
              value={ingredients} onChange={(event) => setDraft({ ...draft, ingredients: event.target.value })} rows={3} required disabled={reading || busy} />
            <div className="input-tools">
              <div className="photo-tools">
                {(["gallery", "camera"] as const).map((source) => <label key={source} className={"photo-control " + source}>
                  {source === "camera" ? <Camera size={17} /> : <ImagePlus size={17} />}
                  {source === "camera" ? "Camera" : "Add a photo"}
                  <input type="file" accept="image/*" capture={source === "camera" ? "environment" : undefined}
                    aria-label={source === "camera" ? "Photograph ingredients" : "Add an ingredient photo"}
                    disabled={reading || busy} onChange={(event) => {
                      const file = event.currentTarget.files?.[0];
                      event.currentTarget.value = "";
                      if (file) void handlePhoto(file);
                    }} />
                </label>)}
              </div>
              {ingredients && <button type="button" className="icon-button" aria-label="Clear ingredients"
                onClick={() => setDraft({ ...draft, ingredients: "" })}><X size={17} /></button>}
            </div>
          </div>
          {(reading || photoStatus) && <small role="status">{reading ? "Reading photo…" : photoStatus}</small>}
        </div>
        <div className="form-field">
          <label htmlFor="must-not">Never use</label>
          <input id="must-not" placeholder="Ingredients to leave out" value={settings.must_not} maxLength={messages}
            onChange={(event) => {
              localStorage.setItem("chefbot.must-not", event.target.value);
              change({ ...settings, must_not: event.target.value });
            }} />
        </div>
        <button type="submit" className="primary" disabled={busy || reading || !ingredients.trim()}>
          <Leaf size={18} /> {busy ? "Starting…" : "Make a recipe"}
        </button>
      </section>
      {!globe && cuisineCard}
      <section className="card form-card">
        <div className="form-field">
          <label htmlFor="audience">Who’s eating?</label>
          <select id="audience" value={settings.audience}
            onChange={(event) => change({ ...settings, audience: event.target.value })}>
            {(tree?.audiences ?? [settings.audience]).map((audience) =>
              <option key={audience} value={audience}>{audienceLabel(audience)}</option>)}
          </select>
        </div>
        <fieldset>
          <legend>Dietary requirements <small>(up to {dietLimit})</small></legend>
          <div className="chips">{tree?.restrictions.map((restriction) => {
            const checked = settings.restrictions.includes(restriction);
            return <label className="check-chip" key={restriction}>
              <input type="checkbox" checked={checked} disabled={!checked && settings.restrictions.length >= dietLimit}
                onChange={() => change({ ...settings, restrictions: checked ? settings.restrictions.filter((r) => r !== restriction) : [...settings.restrictions, restriction] })} />
              <span>{restriction}</span>
            </label>;
          })}</div>
        </fieldset>
        <div className="preferences">
          <label><input type="checkbox" checked={settings.dessert}
            onChange={(event) => change({ ...settings, dessert: event.target.checked })} /> Dessert</label>
        </div>
      </section>
    </form>
    <Recents recipes={recipes} tree={tree} query={query} setQuery={setQuery} openFavorites={openFavorites}
      open={open} toggleFavorite={toggleFavorite} removeRecipe={removeRecipe} />
  </>;
}
