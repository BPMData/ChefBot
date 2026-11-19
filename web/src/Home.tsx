import { Camera, ChevronDown, ChevronLeft, ChevronRight, Globe2, Leaf, Search, Star, X } from "lucide-react";
import { useState, type Dispatch, type FormEvent, type SetStateAction } from "react";
import { dietLimit, readPhoto, resizePhoto, type CuisineTree, type Options } from "./api";
import type { Conversation } from "./storage";

export type Draft = { ingredients: string; settings: Options };
const shortAudience = [
  "Weeknight dinner", "Something impressive", "Busy family", "Easy prep",
  "Meal prep", "Cooking for one", "Health-conscious", "Microwave only",
];

function CuisinePicker({ tree, options, change }: {
  tree: CuisineTree; options: Options; change: (settings: Options) => void;
}) {
  const [expanded, setExpanded] = useState(false);
  const [branch, setBranch] = useState<string[]>([]);
  const parent = branch.at(-1);
  const ids = parent ? tree.nodes[parent].children ?? [] : tree.roots;
  const selected = tree.nodes[options.cuisine];
  const select = (id: string) => {
    change({ ...options, cuisine: id, pantry: id === tree.no_cuisine ? false : options.pantry });
    setExpanded(false);
    setBranch([]);
  };

  return <div className="form-field">
    <label htmlFor="cuisine-picker">Cuisine</label>
    <button type="button" className="field-button" id="cuisine-picker" aria-expanded={expanded}
      onClick={() => setExpanded(!expanded)}>
      <span>{selected?.label ?? tree.no_cuisine}</span><ChevronDown size={17} />
    </button>
    {expanded && <div className="cuisine-list">
      {parent && <button type="button" className="text-button" onClick={() => setBranch(branch.slice(0, -1))}>
        <ChevronLeft size={16} /> {branch.length > 1 ? tree.nodes[branch[branch.length - 2]].label : "All regions"}
      </button>}
      {!parent && <button type="button" onClick={() => select(tree.no_cuisine)}>{tree.no_cuisine}</button>}
      {ids.map((id) => {
        const node = tree.nodes[id];
        return <button key={id} type="button" onClick={() => node.children?.length ? setBranch([...branch, id]) : select(id)}>
          <span>{node.label}</span>{!!node.children?.length && <ChevronRight size={16} />}
        </button>;
      })}
    </div>}
    {selected?.subtitle && <small>{selected.subtitle}</small>}
    {!!selected?.pantry?.length && options.pantry && <small>Pantry staples include {selected.pantry.join(", ")}.</small>}
  </div>;
}

export function Home({ tree, draft, setDraft, create, busy, recipes, open, toggleFavorite, openGlobe }: {
  tree: CuisineTree | null; draft: Draft; setDraft: Dispatch<SetStateAction<Draft>>;
  create: () => void; busy: boolean; recipes: Conversation[];
  openGlobe: () => void;
  open: (id: string) => void; toggleFavorite: (id: string) => void;
}) {
  const [reading, setReading] = useState(false);
  const [photoStatus, setPhotoStatus] = useState("");
  const [favorites, setFavorites] = useState(false);
  const [query, setQuery] = useState("");
  const { ingredients, settings } = draft;
  const change = (settings: Options) => setDraft({ ...draft, settings });
  const messages = tree?.limits.message_characters ?? 4000;

  async function handlePhoto(file: File) {
    setPhotoStatus("");
    setReading(true);
    try {
      const found = await readPhoto(await resizePhoto(file));
      if (found) setDraft((current) => ({ ...current, ingredients: [current.ingredients.trim(), found].filter(Boolean).join(", ").slice(0, messages) }));
      else setPhotoStatus("ChefBot couldn’t see any ingredients in that photo.");
    } catch (error) {
      setPhotoStatus(error instanceof Error ? error.message : "ChefBot couldn’t read that photo.");
    } finally {
      setReading(false);
    }
  }

  const visible = recipes.filter((recipe) => (!favorites || recipe.favorite)
    && recipe.title.toLowerCase().includes(query.trim().toLowerCase())).sort((a, b) =>
      favorites ? b.last_accessed - a.last_accessed || b.updated - a.updated : b.updated - a.updated);
  const submit = (event: FormEvent) => {
    event.preventDefault();
    if (ingredients.trim() && !busy && !reading) create();
  };

  return <>
    <div className="intro">
      <h1>What’s in your kitchen?</h1>
      <p>Start with what you have and make the recipe your own.</p>
    </div>
    <form className="card home-form" onSubmit={submit} aria-label="New recipe">
      <div className="form-field">
        <label htmlFor="ingredients">Ingredients</label>
        <div className="ingredients-box">
          <textarea id="ingredients" placeholder="Chicken thighs, tomatoes, feta…" maxLength={messages}
            value={ingredients} onChange={(event) => setDraft({ ...draft, ingredients: event.target.value })} rows={3} required disabled={reading || busy} />
          <div className="input-tools">
            <label className="photo-control">
              <Camera size={17} /> {reading ? "Reading photo…" : "Add a photo"}
              <input type="file" accept="image/*" capture="environment" aria-label="Add an ingredient photo"
                disabled={reading || busy} onChange={(event) => {
                  const file = event.currentTarget.files?.[0];
                  event.currentTarget.value = "";
                  if (file) void handlePhoto(file);
                }} />
            </label>
            {ingredients && <button type="button" className="icon-button" aria-label="Clear ingredients"
              onClick={() => setDraft({ ...draft, ingredients: "" })}><X size={17} /></button>}
          </div>
        </div>
        {photoStatus && <small role="status">{photoStatus}</small>}
      </div>
      <div className="form-field">
        <label htmlFor="must-not">Never use</label>
        <input id="must-not" placeholder="Ingredients to leave out" value={settings.must_not} maxLength={messages}
          onChange={(event) => change({ ...settings, must_not: event.target.value })} />
      </div>
      <div className="form-columns">
        {tree && <CuisinePicker tree={tree} options={settings} change={change} />}
        <div className="form-field">
          <label htmlFor="audience">Who’s eating?</label>
          <select id="audience" value={settings.audience}
            onChange={(event) => change({ ...settings, audience: event.target.value })}>
            {(tree?.audiences ?? [settings.audience]).map((audience, index) =>
              <option key={audience} value={audience}>{shortAudience[index] ?? audience}</option>)}
          </select>
        </div>
      </div>
      {tree && <button type="button" className="text-button globe-button" onClick={openGlobe}>
        <Globe2 size={17} /> Preview cuisine globe
      </button>}
      <fieldset>
        <legend>Dietary requirements</legend>
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
        <label className={settings.cuisine === tree?.no_cuisine || !tree ? "disabled" : ""}>
          <input type="checkbox" disabled={!tree || settings.cuisine === tree.no_cuisine} checked={settings.pantry}
            onChange={(event) => change({ ...settings, pantry: event.target.checked })} /> Pantry defaults
        </label>
      </div>
      <button type="submit" className="primary" disabled={busy || reading || !ingredients.trim()}>
        <Leaf size={18} /> {busy ? "Starting…" : "Make a recipe"}
      </button>
    </form>
    <section className="saved" aria-label="Saved recipes">
      <div className="saved-header">
        <div className="segmented">
          <button type="button" aria-pressed={!favorites} onClick={() => setFavorites(false)}>Recents</button>
          <button type="button" aria-pressed={favorites} onClick={() => setFavorites(true)}>Favorites</button>
        </div>
        {!!recipes.length && <label className="search"><Search size={16} /><input placeholder="Search recipes" aria-label="Search recipes" value={query}
          onChange={(event) => setQuery(event.target.value)} /></label>}
      </div>
      {visible.length ? <ul className="recipe-list">
        {visible.map((recipe) => <li key={recipe.id}>
          <button type="button" className="recipe-row" onClick={() => open(recipe.id)}>
            <span>{recipe.title}</span><small>{recipe.pending ? "In progress" : new Date(recipe.updated).toLocaleDateString(undefined, { month: "short", day: "numeric" })}</small>
          </button>
          {!!recipe.messages.length && <button type="button" className="icon-button star" aria-label={recipe.favorite ? "Remove from favorites" : "Add to favorites"}
            aria-pressed={recipe.favorite} onClick={() => toggleFavorite(recipe.id)}><Star size={18} fill={recipe.favorite ? "currentColor" : "none"} /></button>}
        </li>)}
      </ul> : <p className="empty">{query ? "No matching recipes." : favorites ? "Star a recipe to keep it here." : "Recipes you make appear here."}</p>}
    </section>
  </>;
}
