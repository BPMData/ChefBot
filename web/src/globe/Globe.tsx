import { useEffect, useRef, useState } from "react";
import { Map as MapLibreMap, NavigationControl, type MapGeoJSONFeature } from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import geography from "../../../src/chefbot/maps/globe.json";
import { regionColors } from "../CuisineMap";
import land from "./land.geojson?url";
import regions from "./regions.geojson?url";
import "./globe.css";

const cuisines = [
  { id: "greek", name: "Greek", center: [23.73, 37.98], zoom: 4.5, color: "#f4a46f" },
  { id: "central_west_india", name: "Central & West Indian", center: [75.7, 22.7], zoom: 4.6, color: "#d9a6f0" },
  { id: "us_italian_american", name: "Italian-American", center: [-73.985, 40.748], zoom: 9.2, color: "#8ed9bc" },
] satisfies { id: string; name: string; center: [number, number]; zoom: number; color: string }[];

const continents = geography.regions.map((region) => ({
  type: "Feature" as const,
  properties: { continent: region.id, label: region.label, color: regionColors[region.color] },
  geometry: { type: "MultiPolygon" as const, coordinates: region.polygons.map((ring) => [ring]) },
}));
const fillLayer = "cuisine-fill";
const outlineLayer = "cuisine-outlines";
const nameFrom = (feature?: MapGeoJSONFeature) => feature?.properties.name as string | undefined;
const cuisineFrom = (feature?: MapGeoJSONFeature) => cuisines.find((region) => feature?.properties.cuisine === region.id);

export default function Globe({ preview, openRegion }: { preview: (id: string) => void; openRegion: (id: string) => void }) {
  const host = useRef<HTMLDivElement>(null);
  const actions = useRef({ preview, openRegion });
  actions.current = { preview, openRegion };
  const map = useRef<MapLibreMap | null>(null);
  const [selected, setSelected] = useState<(typeof cuisines)[number] | null>(null);
  const [place, setPlace] = useState("");
  const [hovered, setHovered] = useState("");
  const [ready, setReady] = useState(false);
  const [failed, setFailed] = useState(false);

  function focus(region: (typeof cuisines)[number], name = "") {
    setSelected(region);
    setPlace(name);
    actions.current.preview(region.id);
    if (map.current?.getLayer(fillLayer)) {
      map.current.setPaintProperty(fillLayer, "fill-opacity", ["case", ["==", ["get", "cuisine"], region.id], 0.87, 0.57]);
      map.current.flyTo({ center: region.center, zoom: region.zoom, duration: 1_500 });
    }
  }

  useEffect(() => {
    if (!host.current) return;
    let globe: MapLibreMap;
    try {
      globe = new MapLibreMap({
        container: host.current, center: [-20, 23], zoom: 0.55, minZoom: 0.2, maxZoom: 12,
        dragRotate: false, pitchWithRotate: false,
        cooperativeGestures: !window.matchMedia("(any-pointer: coarse)").matches,
        style: {
          version: 8,
          projection: { type: "globe" },
          sources: {
            continents: { type: "geojson", data: { type: "FeatureCollection", features: continents }, maxzoom: 4 },
            land: { type: "geojson", data: land, attribution: "Made with Natural Earth", maxzoom: 8 },
            regions: { type: "geojson", data: regions, attribution: "U.S. Census Bureau", maxzoom: 10 },
          },
          layers: [
            { id: "ocean", type: "background", paint: { "background-color": "#202a30" } },
            { id: "land", type: "fill", source: "land", paint: { "fill-color": "#5a5146" } },
            { id: "continents", type: "fill", source: "continents", paint: {
              "fill-color": ["get", "color"], "fill-opacity": ["interpolate", ["linear"], ["zoom"], 1, 0.72, 5, 0.15],
            } },
            { id: "country-borders", type: "line", source: "land", paint: { "line-color": "#292d2b", "line-width": 0.65 } },
            { id: fillLayer, type: "fill", source: "regions", paint: {
              "fill-color": ["match", ["get", "cuisine"], cuisines[0].id, cuisines[0].color,
                cuisines[1].id, cuisines[1].color, cuisines[2].id, cuisines[2].color, "#ff9a70"],
              "fill-opacity": 0.72,
            } },
            { id: outlineLayer, type: "line", source: "regions", paint: {
              "line-color": "#eadbd0",
              "line-width": ["interpolate", ["linear"], ["zoom"], 1, 0.65, 9, 1.15],
              "line-opacity": 0.75,
            } },
          ],
        },
      });
    } catch {
      setFailed(true);
      return;
    }
    map.current = globe;
    globe.touchZoomRotate.disableRotation();
    globe.addControl(new NavigationControl({ showCompass: false }), "top-right");
    globe.once("idle", () => {
      setReady(globe.isSourceLoaded("land") && globe.isSourceLoaded("regions"));
    });
    globe.on("error", () => setFailed(true));
    function pickAt(point: { x: number; y: number }) {
      if (!globe.getLayer(fillLayer)) return;
      return globe.queryRenderedFeatures([point.x, point.y], { layers: [fillLayer, "continents"] })[0];
    }
    globe.on("mousemove", (event) => {
      const feature = pickAt(event.point);
      globe.getCanvas().style.cursor = feature ? "pointer" : "";
      setHovered(nameFrom(feature) ?? feature?.properties.label ?? "");
    });
    globe.on("mouseout", () => setHovered(""));
    globe.on("click", (event) => {
      const feature = pickAt(event.point);
      const region = cuisineFrom(feature);
      if (region) focus(region, nameFrom(feature));
      else if (feature?.properties.continent) actions.current.openRegion(feature.properties.continent);
    });
    if (import.meta.env.DEV) {
      globe.on("render", () => {
        if (globe.isMoving()) performance.mark("chefbot-globe-frame");
      });
      globe.on("moveend", () => {
        if (host.current) host.current.dataset.zoom = globe.getZoom().toFixed(2);
      });
    }
    return () => {
      globe.remove();
      map.current = null;
    };
  }, []);

  return <>
    <div className="intro">
      <h1>Cuisine globe</h1>
      <p>Spin the globe and tap a region to explore its cuisines.</p>
    </div>
    <section className="card globe-panel" aria-label="Cuisine globe">
      <div className="globe-frame">
        <div className="globe-host" ref={host} data-ready={ready} aria-label="Interactive cuisine map" />
        {(selected || hovered) && <output className="globe-location">{hovered || place || selected?.name}</output>}
        {failed && <p className="globe-message" role="status">The map couldn’t load. You can still select a cuisine below.</p>}
        {!ready && !failed && <p className="globe-message" role="status">Loading the globe…</p>}
      </div>
      <div className="globe-cuisines" aria-label="Regions">
        {geography.regions.map((region) => <button className="secondary" type="button" key={region.id}
          onClick={() => openRegion(region.id)}><span className="region-swatch" style={{ backgroundColor: regionColors[region.color] }} />
          {region.label}</button>)}
      </div>
      <details className="globe-closeups"><summary>Regional close-ups</summary>
      <div className="globe-cuisines">
        {cuisines.map((region) => <button type="button" className="secondary" key={region.id}
          aria-pressed={selected?.id === region.id} onClick={() => focus(region)}>
          <span className="region-swatch" style={{ backgroundColor: region.color }} /> {region.name}
        </button>)}
      </div>
      </details>
    </section>
  </>;
}
