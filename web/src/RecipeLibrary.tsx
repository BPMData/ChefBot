import { ChevronRight, Folder, Search, Star, Trash2, X } from "lucide-react";
import type { CuisineTree } from "./api";
import { cuisinePath, requestTags } from "./cooking";
import type { Conversation } from "./storage";

const anyCuisine = "__any__";
export const favoritePageSize = 15;

type RecipeActions = {
  open: (id: string) => void;
  toggleFavorite: (id: string) => void;
  removeRecipe?: (id: string) => Promise<void>;
};

function lineage(recipe: Conversation, tree: CuisineTree | null) {
  if (!tree) return [];
  const value = recipe.settings.cuisine;
  const id = Object.hasOwn(tree.legacy_ids ?? {}, value) ? tree.legacy_ids![value] : value;
  const node = tree.nodes[id];
  return node && (node.kind === "any" || node.kind === "cuisine") ? cuisinePath(id, tree) : [];
}

function matching(recipes: Conversation[], query: string, tree: CuisineTree | null) {
  const tokens = query.toLowerCase().trim().split(/\s+/).filter(Boolean);
  if (!tokens.length) return recipes;
  return recipes.filter((recipe) => {
    const searchable = [
      recipe.title, ...lineage(recipe, tree).map((node) => node.label), ...requestTags(recipe.settings, tree),
      recipe.pending?.ingredients, ...recipe.messages.map((message) => message.content),
    ].join("\n").toLowerCase();
    return tokens.every((word) => searchable.includes(word));
  });
}

function RecipeList({ recipes, open, toggleFavorite, removeRecipe }: RecipeActions & { recipes: Conversation[] }) {
  return <ul className="recipe-list">
    {recipes.map((recipe) => <li key={recipe.id}>
      <button type="button" className="recipe-row" onClick={() => open(recipe.id)}>
        <span>{recipe.title}</span><small>{recipe.pending ? "In progress" : new Date(recipe.updated).toLocaleDateString(undefined, { month: "short", day: "numeric" })}</small>
      </button>
      {!!recipe.messages.length && <button type="button" className="icon-button star" aria-label={recipe.favorite ? "Remove from favorites" : "Add to favorites"}
        aria-pressed={recipe.favorite} onClick={() => toggleFavorite(recipe.id)}><Star size={18} fill={recipe.favorite ? "currentColor" : "none"} /></button>}
      {removeRecipe && !recipe.pending && <button type="button" className="icon-button" aria-label={"Delete " + recipe.title}
        onClick={() => {
          if (window.confirm('Delete “' + recipe.title + '” and its pictures from this browser?')) void removeRecipe(recipe.id);
        }}><Trash2 size={17} /></button>}
    </li>)}
  </ul>;
}

function RecipeSearch({ label, query, setQuery }: { label: string; query: string; setQuery: (value: string) => void }) {
  return <div className="search library-search">
    <Search size={16} aria-hidden="true" />
    <input placeholder={label} aria-label={label} value={query} onChange={(event) => setQuery(event.target.value)} />
    {query && <button className="icon-button" type="button" aria-label="Clear search"
      onClick={() => setQuery("")}><X size={16} /></button>}
  </div>;
}

export function Recents({ recipes, tree, query, setQuery, openFavorites, ...actions }: RecipeActions & {
  recipes: Conversation[]; tree: CuisineTree | null; query: string; setQuery: (query: string) => void; openFavorites: () => void;
}) {
  const visible = [...matching(recipes, query, tree)].sort((a, b) => b.updated - a.updated);
  return <section id="saved-recipes" className="saved" aria-label="Saved recipes">
    <h2>Your recipes</h2>
    <div className="saved-header">
      <h3>Recents</h3>
      <button className="secondary" type="button" onClick={openFavorites}><Star size={16} /> Favorites</button>
    </div>
    {!!recipes.length && <RecipeSearch label="Search recipes" query={query} setQuery={setQuery} />}
    {visible.length ? <RecipeList recipes={visible} {...actions} /> :
      <p className="empty">{query.trim() ? "No matching recipes." : "Recipes you make appear here."}</p>}
  </section>;
}

export function Favorites({ recipes, tree, path, query, limit, setQuery, showMore, openFolder, goToLevel, ...actions }: RecipeActions & {
  recipes: Conversation[]; tree: CuisineTree | null; path: string[]; query: string; limit: number;
  setQuery: (query: string) => void; showMore: () => void; openFolder: (id: string) => void; goToLevel: (depth: number) => void;
}) {
  const label = (id: string) => id === anyCuisine ? "Any cuisine" : tree?.nodes[id]?.label ?? id;
  const favorites = recipes.filter((recipe) => recipe.favorite).sort(
    (a, b) => (b.last_accessed || b.updated) - (a.last_accessed || a.updated) || b.updated - a.updated,
  );
  const rows = favorites.map((recipe) => {
    const ids = lineage(recipe, tree).map((node) => node.id);
    return { recipe, ids: ids.length ? ids : [anyCuisine] };
  }).filter(({ ids }) => path.every((id, index) => ids[index] === id));
  const country = path.length === 2 && tree?.nodes[path[1]]?.kind === "country";
  const branch = !!tree && (!path.length || (path.length === 1 && path[0] !== anyCuisine) || country);
  const folders = new Map<string, { count: number; access: number; recent: number; updated: number }>();
  if (branch) for (const { recipe, ids } of rows) {
    const id = ids[path.length];
    if (!id) continue;
    const folder = folders.get(id) ?? { count: 0, access: 0, recent: 0, updated: 0 };
    folder.count += 1;
    folder.access += recipe.access_count ?? 0;
    folder.recent = Math.max(folder.recent, recipe.last_accessed || recipe.updated);
    folder.updated = Math.max(folder.updated, recipe.updated);
    folders.set(id, folder);
  }
  const ranked = [...folders].sort(([aId, a], [bId, b]) =>
    Number(aId === anyCuisine) - Number(bId === anyCuisine) ||
    b.access - a.access || b.recent - a.recent || b.updated - a.updated);
  const searching = !!query.trim();
  const results = searching ? matching(favorites, query, tree) : rows.map(({ recipe }) => recipe);
  const recent = !searching && branch && (!path.length || country);
  const visible = recent ? results.slice(0, country ? 3 : 5) : results.slice(0, limit);
  const showResults = searching || !branch || recent;

  return <section className="favorites-library">
    <div className="intro"><h1>Favorites</h1></div>
    <RecipeSearch label="Search favorites" query={query} setQuery={setQuery} />
    {!!path.length && <nav className="favorite-crumbs" aria-label="Favorites folders">
      <button className="text-button" type="button" onClick={() => goToLevel(0)}>Favorites</button>
      {path.map((id, index) => <span key={id}>
        <ChevronRight size={15} aria-hidden="true" />
        {index === path.length - 1 ? <span aria-current="page">{label(id)}</span> :
          <button className="text-button" type="button" onClick={() => goToLevel(index + 1)}>{label(id)}</button>}
      </span>)}
    </nav>}
    {recent && !!visible.length && <h2>Recently accessed</h2>}
    {showResults && !!visible.length && <RecipeList recipes={visible} {...actions} />}
    {showResults && !recent && results.length > limit && <button type="button" className="secondary more-favorites"
      onClick={showMore}>Show more ({results.length - limit} more)</button>}
    {!searching && !!ranked.length && <>
      {!path.length && <h2>Browse by region</h2>}
      {country && <h2>Subcategories</h2>}
      <ul className="recipe-list favorite-folders" aria-label="Cuisine folders">
        {ranked.map(([id, { count }]) => <li key={id}>
          <button className="recipe-row" type="button" onClick={() => openFolder(id)}>
            <Folder size={18} aria-hidden="true" /><span>{label(id)}</span>
            <small>{count} {count === 1 ? "recipe" : "recipes"}</small><ChevronRight size={16} aria-hidden="true" />
          </button>
        </li>)}
      </ul>
    </>}
    {(!showResults && !ranked.length || showResults && !results.length) &&
      <p className="empty">{searching ? "No matching favorites." : path.length ? "No favorites in this folder." :
        "Star a recipe to keep it here."}</p>}
  </section>;
}
