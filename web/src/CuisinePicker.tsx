import { ArrowLeft, ChevronRight, Compass, Globe2, Info, Search, Shuffle, X } from "lucide-react";
import { useLayoutEffect, useRef, useState, type ReactNode } from "react";
import type { Cuisine, CuisineTree } from "./api";
import { cuisineLabel, cuisinePath, recentCuisines } from "./cooking";
import { CuisineMap, RegionIcon, useMapLevel } from "./CuisineMap";

function CuisineDialog({ title, close, children, className = "" }: {
  title: string; close: () => void; children: ReactNode; className?: string;
}) {
  const ref = useRef<HTMLDialogElement>(null);
  useLayoutEffect(() => {
    const element = ref.current!;
    element.showModal();
    return () => element.close();
  }, []);
  return <dialog className={"cuisine-dialog " + className} ref={ref} aria-label={title}
    onCancel={(event) => { event.preventDefault(); close(); }}>
    <div className="dialog-header">
      <h2>{title}</h2>
      <button type="button" className="icon-button" aria-label="Close" onClick={close}><X size={20} /></button>
    </div>
    {children}
  </dialog>;
}

export function CuisineBrowser({ tree, close, preview, reset }: {
  tree: CuisineTree; close: () => void; preview: (id: string) => void; reset: () => void;
}) {
  const [branch, setBranch] = useState<string[]>([]);
  const [query, setQuery] = useState("");
  const grid = useRef<HTMLDivElement>(null);
  const parent = branch.at(-1);
  const level = useMapLevel(parent ?? "world");
  const terms = query.trim().toLowerCase().split(/\s+/).filter(Boolean);
  const matches = terms.length ? Object.values(tree.nodes).filter((node) => {
    if (node.children?.length) return false;
    const names = [...cuisinePath(node.id, tree).map((region) => region.label), node.prompt_name].join(" ").toLowerCase();
    return terms.every((word) => names.includes(word));
  }) : (parent ? tree.nodes[parent].children ?? [] : tree.roots).map((id) => tree.nodes[id]);

  function openBranch(path: string[]) {
    setBranch(path);
    grid.current?.scrollTo(0, 0);
  }
  return <CuisineDialog title="Browse cuisines" close={close}>
    <div className="catalog-controls">
      <label className="search"><Search size={17} />
        <input type="search" aria-label="Find a cuisine" placeholder="Find a cuisine" value={query}
          onChange={(event) => { setQuery(event.target.value); grid.current?.scrollTo(0, 0); }} />
      </label>
      {!terms.length && parent && <nav className="catalog-path" aria-label="Cuisine regions">
        <button type="button" aria-label="All regions" onClick={() => openBranch([])}><Compass size={16}/></button>
        {branch.map((id, i) => <span key={id}><ChevronRight size={14} />
          <button type="button" aria-current={i === branch.length - 1 ? "location" : undefined}
            onClick={() => openBranch(branch.slice(0, i + 1))}>{tree.nodes[id].label}</button></span>)}
      </nav>}
    </div>
    <div className="catalog-scroll" ref={grid}>
      <div className={"catalog-grid " + (!parent && !terms.length ? "continents" : "")}>
        {matches.map((node) => <button key={node.id} className="catalog-tile" type="button" aria-label={cuisineLabel(node.id, tree)}
          onClick={() => node.children?.length ? openBranch([...branch, node.id]) : preview(node.id)}>
          {!terms.length && !parent && <RegionIcon level={level} id={node.id} />}
          <span>{node.id === "americas" ? "Americas" : cuisineLabel(node.id, tree)}</span>
          {node.children?.length && <ChevronRight className="tile-arrow" size={15} />}
        </button>)}
      </div>
      {matches.length === 0 && <p className="empty">No matching cuisines.</p>}
    </div>
    <div className="dialog-footer">
      {!parent || terms.length ? <button type="button" className="text-button" onClick={reset}>Use any cuisine</button> :
        <button type="button" className="text-button" onClick={() => openBranch(branch.slice(0, -1))}><ArrowLeft size={17} /> Back a region</button>}
    </div>
  </CuisineDialog>;
}

export function CuisineInfo({ tree, id, close, choose }: {
  tree: CuisineTree; id: string; close: () => void; choose: () => void;
}) {
  const path = cuisinePath(id, tree);
  const node: Cuisine = tree.nodes[id];
  const region = node.kind === "any" ? path.length - 2 : path.length - 1;
  const name = cuisineLabel(id, tree);
  return <CuisineDialog title={name} close={close} className="cuisine-info">
    <div className="info-scroll">
      <div className="info-geography">
        <p>{path.slice(0, -1).map((region) => region.label).join(" / ")}</p>
        <CuisineMap levelId={path[region - 1]?.id ?? "world"} regionId={path[region].id} label={name} />
      </div>
      {node.subtitle && <p className="cuisine-subtitle">{node.subtitle}</p>}
      {node.about && <p>{node.about}</p>}
      {([
        ["Classic flavors", node.flavors], ["For desserts", node.sweet_only],
        ["Signature ingredients (if you have them)", node.signature_ingredients],
        ["If you’re missing one", node.substitutes], ["Pantry staples", node.pantry],
      ] as const).map(([heading, items]) => items?.length ? <section key={heading}>
        <h3>{heading}</h3><p>{items.join(", ")}</p>
      </section> : null)}
    </div>
    <div className="dialog-footer"><button type="button" className="primary" onClick={choose}>Use {name}</button></div>
  </CuisineDialog>;
}

export function CuisinePicker({ tree, cuisine, browse, preview, openGlobe }: {
  tree: CuisineTree; cuisine: string; browse: () => void; preview: (id: string) => void; openGlobe: () => void;
}) {
  const recents = recentCuisines().filter((id) => tree.nodes[id] && id !== cuisine);
  return <div className="form-field cuisine-field">
    <div className="cuisine-heading">
      <h2>Cuisine</h2>
      <button className="current-cuisine" type="button" onClick={() => tree.nodes[cuisine] ? preview(cuisine) : browse()}>
        {cuisineLabel(cuisine, tree)}{tree.nodes[cuisine] && <Info size={15} />}</button>
    </div>
    <div className="cuisine-tools">
      <button type="button" className="secondary" onClick={browse}><Compass size={18} /> Browse cuisines</button>
      <button type="button" className="secondary" onClick={openGlobe}><Globe2 size={18} /> Cuisine globe</button>
      <button type="button" className="text-button" onClick={() => {
        const choices = Object.values(tree.nodes).filter((node) => node.kind === "cuisine" || node.kind === "any");
        preview(choices[Math.floor(Math.random() * choices.length)].id);
      }}><Shuffle size={17} /> Surprise me</button>
    </div>
    {recents.length > 0 && <div className="recent-cuisines" aria-label="Recent cuisines">
      {recents.map((id) => <button type="button" className="chip" onClick={() => preview(id)} key={id}>{cuisineLabel(id, tree)}</button>)}
    </div>}
  </div>;
}
