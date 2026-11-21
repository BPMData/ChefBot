import { useEffect, useState } from "react";
import type { CuisineTree } from "./api";
import { cuisineLabel } from "./cooking";

type Point = [number, number];
type Bounds = [number, number, number, number];
type Region = {
  id: string; label: string; color: string; bbox: Bounds; center: Point; polygons: Point[][];
  label_pos: Point; callout?: { pos: Point; anchor: Point; label: string };
};
type Level = { id: string; any_id?: string; regions: Region[]; background: Point[][]; inset_boxes?: Bounds[] };

const levels = import.meta.glob<Level>(["../../src/chefbot/maps/*.json", "!../../src/chefbot/maps/globe.json"], { import: "default" });

export const regionColors: Record<string, string> = {
  coral: "#ea946d", amber: "#e9bf64", teal: "#70b9ae", blue: "#86acdd", purple: "#b99acb",
  green: "#94bd83", pink: "#da98b2", cyan: "#83c4da", orange: "#e6a965", indigo: "#a4a8da", lime: "#b2c785",
};

export function useMapLevel(id: string) {
  const [loaded, setLoaded] = useState<{ id: string; data: Level | null }>();
  useEffect(() => {
    let active = true;
    const load = levels["../../src/chefbot/maps/" + id + ".json"];
    async function read() {
      try {
        const data = await load();
        if (active) setLoaded({ id, data });
      } catch {
        if (active) setLoaded({ id, data: null });
      }
    }
    void read();
    return () => { active = false; };
  }, [id]);
  return loaded?.id === id ? loaded.data : undefined;
}

function outline(polygons: Point[][]) {
  return polygons.map((ring) => "M" + ring.map((point) => point.join(",")).join("L") + "Z").join("");
}

function viewBox([x0, y0, x1, y1]: Bounds, pad: number) {
  return [x0 - pad, y0 - pad, x1 - x0 + 2 * pad, y1 - y0 + 2 * pad].join(" ");
}

export function RegionIcon({ level, id }: { level?: Level | null; id: string }) {
  const region = level?.regions.find((item) => item.id === id);
  if (!region) return null;
  return <svg className="region-icon" viewBox={viewBox(region.bbox, 1)} aria-hidden="true">
    <path d={outline(region.polygons)} fill={regionColors[region.color]} />
  </svg>;
}

export function CuisineMap({ levelId, regionId, label }: { levelId: string; regionId: string; label: string }) {
  const level = useMapLevel(levelId);
  const selected = level?.regions.find((region) => region.id === regionId);
  if (!level || !selected) return null;
  const bounds: Bounds = [Infinity, Infinity, -Infinity, -Infinity];
  for (const ring of [...level.background, ...level.regions.flatMap((region) => region.polygons)]) {
    for (const [x, y] of ring) {
      bounds[0] = Math.min(bounds[0], x); bounds[1] = Math.min(bounds[1], y);
      bounds[2] = Math.max(bounds[2], x); bounds[3] = Math.max(bounds[3], y);
    }
  }
  const tiny = selected.bbox[2] - selected.bbox[0] < 15 || selected.bbox[3] - selected.bbox[1] < 15;
  return <svg className="cuisine-map" viewBox={viewBox(bounds, 9)} role="img" aria-label={label + " region highlighted"}>
    {level.inset_boxes?.map(([x, y, x1, y1]) => <rect key={x + "," + y} x={x} y={y} width={x1-x} height={y1-y}
      fill="none" stroke="var(--border)" rx="2" />)}
    <path className="map-land" d={outline(level.background)} />
    {level.regions.map((region) => <path className="map-land" key={region.id} d={outline(region.polygons)} />)}
    <path className="map-pick" d={outline(selected.polygons)} />
    {tiny && <circle cx={selected.center[0]} cy={selected.center[1]} r="4" className="map-pick" />}
  </svg>;
}

function mapViewBox(level: Level) {
  const ys = level.background.flatMap((ring) => ring.map((point) => point[1]));
  for (const region of level.regions) {
    const labelY = region.callout?.pos[1] ?? region.label_pos[1];
    ys.push(region.bbox[1], region.bbox[3], labelY - 13, labelY + 13);
  }
  for (const box of level.inset_boxes ?? []) ys.push(box[1], box[3]);
  const top = Math.min(...ys) - 8;
  return [0, top, 360, Math.max(...ys) - top + 8].join(" ");
}

export function RegionalMap({ id, tree, choose }: { id: string; tree: CuisineTree; choose: (id: string) => void }) {
  const { label, children = [] } = tree.nodes[id];
  const level = useMapLevel(id);
  if (level === undefined) return <p role="status">Loading the regional map…</p>;
  return <section className="regional-map">
    <div className="regional-heading"><h1>{label}</h1>
      {level?.any_id && <button type="button" className="secondary" onClick={() => choose(level.any_id!)}>
        Any region</button>}
    </div>
    {level ? <svg viewBox={mapViewBox(level)} role="group" aria-label={label + " cuisine map"}>
      <path className="map-land" d={outline(level.background)} />
      {level.inset_boxes?.map(([x, y, x1, y1]) => <rect key={x + "," + y} x={x} y={y} width={x1-x} height={y1-y}
        fill="none" stroke="var(--border)" rx="2" />)}
      {level.regions.map((region) => <path key={region.id} d={outline(region.polygons)} fill={regionColors[region.color]}
        className="map-area" onClick={() => choose(region.id)}><title>{region.label}</title></path>)}
      {level.regions.map(({ id, callout, color }) => callout && <line key={id} pointerEvents="none"
        x1={callout.anchor[0]} y1={callout.anchor[1]} x2={callout.pos[0]} y2={callout.pos[1]} stroke={regionColors[color]} />)}
      {level.regions.map((region) => {
        const [centerX, y] = region.callout?.pos ?? region.label_pos;
        const labelWidth = Math.max(56, region.label.length * 6.5 + 16);
        const x = Math.max(4 + labelWidth / 2, Math.min(centerX, 356 - labelWidth / 2));
        return <g key={region.id} role="button" tabIndex={0} aria-label={region.label} className="map-label"
          onClick={() => choose(region.id)} onKeyDown={(event) => {
            if (event.key === "Enter" || event.key === " ") { event.preventDefault(); choose(region.id); }
          }}>
          {region.callout && <rect x={x - labelWidth / 2} y={y - 13} width={labelWidth} height="26" rx="7"
            stroke={regionColors[region.color]} />}
          <text x={x} y={y} textAnchor="middle" dominantBaseline="central">{region.label}</text>
        </g>;
      })}
    </svg> : <p role="status">Couldn’t load the map. Choose a region by name.</p>}
    <details className="region-names" open={level ? undefined : true}>
      <summary>Choose by name</summary>
      <div className="catalog-grid">{children.map((child) => <button type="button" className="catalog-tile"
        onClick={() => choose(child)} key={child}>{cuisineLabel(child, tree)}</button>)}</div>
    </details>
  </section>;
}
