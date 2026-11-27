import { useEffect, useLayoutEffect, useMemo, useRef, useState, type RefObject } from 'react';
import { Map as MapLibreMap, NavigationControl, type ExpressionSpecification } from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import geography from '../../../src/chefbot/maps/globe.json';
import type { CuisineTree } from '../api';
import { cuisineLabel } from '../cooking';
import { regionColors } from '../CuisineMap';
import anchorData from './anchors.json';
import { layoutCallouts, followAnchors, type Callout } from './callouts';
import land from './land.geojson?url';
import regionsUrl from './regions.geojson?url';
import viewData from './views.json';
import './globe.css';

type LngLat = [number, number];
export type GlobeCamera = { center: LngLat; zoom: number; bearing: number; pitch: number };
type Feature = {
  type: 'Feature';
  properties: { level: string; cuisine: string; label: string; color: string };
  geometry: { type: 'MultiPolygon'; coordinates: LngLat[][][] };
};

const views = viewData.views as unknown as Record<string, GlobeCamera>;
const anchors = anchorData as unknown as Record<string, Record<string, LngLat>>;
const continents = geography.regions.map((region) => ({
  type: 'Feature' as const,
  properties: { continent: region.id, label: region.label, color: regionColors[region.color] },
  geometry: { type: 'MultiPolygon' as const, coordinates: region.polygons.map((ring) => [ring]) },
}));
const colorMatch = [
  'match',
  ['get', 'color'],
  ...Object.entries(regionColors).flat(),
  '#ff9a70',
] as unknown as ExpressionSpecification;
const fillLayer = 'cuisine-fill';
const outlineLayer = 'cuisine-outlines';
const coarse = () => window.matchMedia('(any-pointer: coarse)').matches;

let measure: CanvasRenderingContext2D | null = null;
function chipWidth(text: string) {
  measure ??= document.createElement('canvas').getContext('2d');
  if (!measure) return text.length * 7.4 + 26;
  measure.font = "600 13px 'DM Sans', system-ui, sans-serif";
  return Math.ceil(measure.measureText(text).width) + 26;
}

/** The fixed camera for a level, scaled so the same area shows on a phone and a desktop. */
function fixedView(level: string, element: HTMLElement): GlobeCamera {
  const view = views[level] ?? views.world;
  // The frame's area sets the scale, so a tall phone frame and a wide desktop one show about the same region.
  const short = Math.min(element.clientWidth, element.clientHeight);
  const size = Math.max(200, Math.min(Math.sqrt(element.clientWidth * element.clientHeight), short * 1.25));
  return { ...view, zoom: view.zoom + Math.log2(size / viewData.reference_size) };
}

function cameraOf(map: MapLibreMap): GlobeCamera {
  return {
    center: map.getCenter().toArray() as LngLat,
    zoom: map.getZoom(),
    bearing: map.getBearing(),
    pitch: map.getPitch(),
  };
}

const rad = Math.PI / 180;
const toVector = ([lon, lat]: LngLat) => [
  Math.cos(lat * rad) * Math.cos(lon * rad),
  Math.cos(lat * rad) * Math.sin(lon * rad),
  Math.sin(lat * rad),
];

/** The point `angle` degrees from `from` on the way to `to`, along the shortest path over the sphere. */
function toward(from: LngLat, to: LngLat, angle: number): LngLat {
  const total = arc(from, to) * rad;
  const a = toVector(from);
  const b = toVector(to);
  const sin = Math.sin(total) || 1;
  const t = angle * rad;
  const [x, y, z] = a.map((value, i) => (Math.sin(total - t) * value + Math.sin(t) * b[i]) / sin);
  return [Math.atan2(y, x) / rad, Math.asin(Math.max(-1, Math.min(1, z))) / rad];
}

/** Angle in degrees between two points on the sphere. */
function arc([lon1, lat1]: LngLat, [lon2, lat2]: LngLat) {
  const cos =
    Math.sin(lat1 * rad) * Math.sin(lat2 * rad) +
    Math.cos(lat1 * rad) * Math.cos(lat2 * rad) * Math.cos((lon1 - lon2) * rad);
  return Math.acos(Math.max(-1, Math.min(1, cos))) / rad;
}

/** Set once the person touches a spinning globe, so it stays still for the rest of the visit. */
let spinStopped = false;
const spinDegreesPerSecond = 4;

/**
 * The cuisine globe. On its own screen it drills down through `path`; `compact` is the smaller globe at the
 * top of the home page, which only shows continents and can spin slowly until the first touch.
 */
export default function Globe({
  tree,
  path,
  choose,
  cameras,
  compact = false,
  spin = false,
  onFail,
}: {
  tree: CuisineTree;
  path: string[];
  choose: (id: string) => void;
  cameras: RefObject<Record<string, GlobeCamera>>;
  compact?: boolean;
  spin?: boolean;
  onFail?: () => void;
}) {
  const host = useRef<HTMLDivElement>(null);
  const map = useRef<MapLibreMap | null>(null);
  const actions = useRef({ choose });
  actions.current = { choose };
  const level = path.at(-1) ?? 'world';
  const key = path.join('/') || 'world';
  const shown = useRef({ level, key });
  const [features, setFeatures] = useState<Feature[] | null>(compact ? [] : null);
  const [ready, setReady] = useState(false);
  const [failed, setFailed] = useState(false);
  const [hovered, setHovered] = useState('');
  const [callouts, setCallouts] = useState<Callout[]>([]);
  const [settled, setSettled] = useState(false);
  const lastAnchors = useRef(new Map<string, { x: number; y: number }>());

  const children = level === 'world' ? tree.roots : (tree.nodes[level]?.children ?? []);
  const anyId = children.find((id) => tree.nodes[id]?.kind === 'any');
  const choices = useMemo(
    () => children.filter((id) => tree.nodes[id] && tree.nodes[id].kind !== 'any' && anchors[level]?.[id]),
    [children, level, tree]
  );
  const label = (id: string) => (id === 'americas' ? 'The Americas' : cuisineLabel(id, tree));
  const regionBoxes = useMemo(() => {
    const boxes = new Map<string, [number, number, number, number]>();
    for (const feature of features ?? []) {
      if (feature.properties.level !== level) continue;
      let [x0, y0, x1, y1] = [Infinity, Infinity, -Infinity, -Infinity];
      for (const polygon of feature.geometry.coordinates)
        for (const [x, y] of polygon[0]) {
          x0 = Math.min(x0, x);
          y0 = Math.min(y0, y);
          x1 = Math.max(x1, x);
          y1 = Math.max(y1, y);
        }
      boxes.set(feature.properties.cuisine, [x0, y0, x1, y1]);
    }
    return boxes;
  }, [features, level]);
  const palette = useMemo(
    () =>
      new Map(
        (features ?? []).map(({ properties }) => [
          properties.level + '/' + properties.cuisine,
          regionColors[properties.color],
        ])
      ),
    [features]
  );
  const regionColor = (id: string) =>
    (level === 'world'
      ? regionColors[geography.regions.find((region) => region.id === id)?.color ?? '']
      : palette.get(level + '/' + id)) ?? '#ff9a70';
  const layoutInputs = useRef({ choices, regionBoxes, level, label });
  layoutInputs.current = { choices, regionBoxes, level, label };

  /**
   * Screen positions of the current level's anchors. One on the far side of the globe is drawn at the
   * globe's edge, in its direction, so a continent behind the globe still has a chip to tap.
   */
  function project(globe: MapLibreMap) {
    const { choices, level } = layoutInputs.current;
    const center = globe.getCenter().toArray() as LngLat;
    return new Map(
      choices.map((id) => {
        const anchor = anchors[level][id];
        const behind = arc(anchor, center) > 80;
        const point = globe.project(behind ? toward(center, anchor, 80) : anchor);
        return [id, { x: point.x, y: point.y, behind }];
      })
    );
  }

  function relayout() {
    const globe = map.current;
    const element = host.current;
    if (!globe || !element) return;
    const { choices, regionBoxes, label } = layoutInputs.current;
    const points = project(globe);
    const height = coarse() ? 32 : 28;
    const center = globe.getCenter().toArray() as LngLat;
    setCallouts(
      layoutCallouts(
        choices.map((id) => {
          const box = regionBoxes.get(id);
          let size = { width: 0, height: 0 };
          if (box && arc([(box[0] + box[2]) / 2, (box[1] + box[3]) / 2], center) < 70) {
            const a = globe.project([box[0], box[1]]);
            const b = globe.project([box[2], box[3]]);
            size = { width: Math.abs(b.x - a.x), height: Math.abs(b.y - a.y) };
          }
          const anchor = points.get(id)!;
          if (anchor.behind) size = { width: 0, height: 0 };
          return { id, anchor, size, width: chipWidth(label(id)), height, behind: anchor.behind };
        }),
        element.clientWidth,
        element.clientHeight
      )
    );
    lastAnchors.current = points;
  }

  useEffect(() => {
    if (failed) onFail?.();
  }, [failed, onFail]);

  useEffect(() => {
    if (compact) return;
    let active = true;
    fetch(regionsUrl)
      .then((response) => response.json())
      .then((data) => {
        if (active) setFeatures(data.features);
      })
      .catch(() => {
        if (active) setFailed(true);
      });
    return () => {
      active = false;
    };
  }, [compact]);

  useEffect(() => {
    if (!host.current || !features) return;
    let globe: MapLibreMap;
    const saved = cameras.current[shown.current.key];
    // Opening a continent from the home page's globe starts where that globe was and flies in.
    const flyIn = !saved && shown.current.level !== 'world' ? cameras.current.world : undefined;
    const start = saved ?? flyIn ?? fixedView(shown.current.level, host.current);
    try {
      globe = new MapLibreMap({
        container: host.current,
        ...start,
        minZoom: 0.2,
        maxZoom: 9,
        dragRotate: false,
        pitchWithRotate: false,
        cooperativeGestures: !coarse(),
        attributionControl: { compact: true },
        style: {
          version: 8,
          projection: { type: 'globe' },
          sources: {
            continents: { type: 'geojson', data: { type: 'FeatureCollection', features: continents }, maxzoom: 4 },
            land: { type: 'geojson', data: land, attribution: 'Made with Natural Earth', maxzoom: 8 },
            regions: {
              type: 'geojson',
              data: { type: 'FeatureCollection', features },
              attribution: 'U.S. Census Bureau',
              maxzoom: 9,
            },
          },
          layers: [
            { id: 'ocean', type: 'background', paint: { 'background-color': '#202a30' } },
            { id: 'land', type: 'fill', source: 'land', paint: { 'fill-color': '#4d463e' } },
            {
              id: 'continents',
              type: 'fill',
              source: 'continents',
              layout: { visibility: shown.current.level === 'world' ? 'visible' : 'none' },
              paint: { 'fill-color': ['get', 'color'], 'fill-opacity': 0.72 },
            },
            {
              id: 'country-borders',
              type: 'line',
              source: 'land',
              paint: { 'line-color': '#2a2c2a', 'line-width': 0.65 },
            },
            {
              id: fillLayer,
              type: 'fill',
              source: 'regions',
              filter: levelFilter(shown.current.level),
              paint: { 'fill-color': colorMatch, 'fill-opacity': 0.66 },
            },
            {
              id: outlineLayer,
              type: 'line',
              source: 'regions',
              filter: levelFilter(shown.current.level),
              paint: {
                'line-color': '#f1e4d8',
                'line-width': ['interpolate', ['linear'], ['zoom'], 1, 0.6, 6, 1.2],
                'line-opacity': 0.7,
              },
            },
          ],
        },
      });
    } catch {
      setFailed(true);
      return;
    }
    map.current = globe;
    globe.touchZoomRotate.disableRotation();
    globe.addControl(new NavigationControl({ showCompass: false }), 'top-right');
    // Starts the attribution folded into its info button so it doesn't cover the map on a phone.
    globe.once('load', () => {
      host.current?.querySelector('.maplibregl-compact-show')?.classList.remove('maplibregl-compact-show');
      if (flyIn && host.current) globe.flyTo({ ...fixedView(shown.current.level, host.current), duration: 1_400 });
    });
    globe.once('idle', () => {
      setReady(globe.isSourceLoaded('land') && globe.isSourceLoaded('regions'));
      relayout();
      setSettled(true);
    });
    globe.on('error', () => setFailed(true));
    function pickAt(point: { x: number; y: number }) {
      const layers = shown.current.level === 'world' ? ['continents'] : [fillLayer];
      const feature = globe.queryRenderedFeatures([point.x, point.y], { layers })[0];
      return (feature?.properties.continent ?? feature?.properties.cuisine) as string | undefined;
    }
    const hover = window.matchMedia('(hover: hover)').matches && !coarse();
    globe.on('mousemove', (event) => {
      if (!hover) return;
      const id = pickAt(event.point);
      globe.getCanvas().style.cursor = id ? 'pointer' : '';
      setHovered(id ?? '');
    });
    globe.on('mouseout', () => setHovered(''));
    globe.on('click', (event) => {
      const id = pickAt(event.point);
      if (id) actions.current.choose(id);
    });
    globe.on('move', () => {
      // A few chips are cheap to lay out every frame, which keeps them steady while the globe turns.
      if (layoutInputs.current.choices.length <= 8) return relayout();
      const next = project(globe);
      setCallouts((current) => followAnchors(current, lastAnchors.current, next));
      lastAnchors.current = next;
    });

    // The slow spin: short linear eases chained end to end, paused while hidden or scrolled away.
    let visible = true;
    let loaded = false;
    const spinning = () =>
      loaded &&
      spin &&
      !spinStopped &&
      visible &&
      document.visibilityState === 'visible' &&
      !window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    function turn() {
      if (!spinning() || globe.isMoving()) return;
      const [lng, lat] = globe.getCenter().toArray();
      globe.easeTo({
        center: [lng + spinDegreesPerSecond * 2, lat],
        duration: 2_000,
        easing: (t) => t,
        essential: true,
      });
    }
    function stopSpin() {
      if (!spin || spinStopped) return;
      spinStopped = true;
      globe.stop();
    }
    for (const type of ['mousedown', 'touchstart', 'wheel'] as const) globe.on(type, stopSpin);
    const watch = new IntersectionObserver(([entry]) => {
      visible = entry.isIntersecting;
      if (visible) turn();
      else if (spin && !spinStopped) globe.stop();
    });
    watch.observe(host.current);
    const resume = () => turn();
    document.addEventListener('visibilitychange', resume);
    globe.once('idle', () => {
      loaded = true;
      turn();
    });
    globe.on('moveend', () => turn());

    globe.on('moveend', () => {
      if (host.current) host.current.dataset.spinning = String(spinning());
      relayout();
      setSettled(true);
      cameras.current[shown.current.key] = cameraOf(globe);
      if (host.current) host.current.dataset.zoom = globe.getZoom().toFixed(2);
    });
    if (import.meta.env.DEV) {
      // Lets the browser tests find a place on the globe; not part of the built site.
      (window as unknown as { chefbotGlobe: MapLibreMap }).chefbotGlobe = globe;
      host.current.dataset.zoom = globe.getZoom().toFixed(2);
      globe.on('render', () => {
        if (globe.isMoving()) performance.mark('chefbot-globe-frame');
      });
    }
    const resize = new ResizeObserver(() => relayout());
    resize.observe(host.current);
    return () => {
      watch.disconnect();
      document.removeEventListener('visibilitychange', resume);
      resize.disconnect();
      cameras.current[shown.current.key] = cameraOf(globe);
      globe.remove();
      map.current = null;
    };
    // The map is created once; level changes fly the existing map.
  }, [features, cameras, spin]);

  // Flies to the level's fixed view going down, or back to where the person left it going up.
  useLayoutEffect(() => {
    const previous = shown.current;
    if (previous.key === key) return;
    const globe = map.current;
    shown.current = { level, key };
    setHovered('');
    if (!globe || !host.current) return;
    cameras.current[previous.key] = cameraOf(globe);
    const deeper = key.startsWith(previous.key + '/') || previous.key === 'world';
    if (deeper) delete cameras.current[key];
    const target = cameras.current[key] ?? fixedView(level, host.current);
    spinStopped = true;
    showLevel(globe, level);
    setCallouts([]);
    setSettled(false);
    globe.flyTo({ ...target, duration: 1_400 });
  }, [key, level, cameras]);

  useEffect(() => {
    if (map.current?.getLayer(fillLayer)) {
      map.current.setPaintProperty(fillLayer, 'fill-opacity', ['case', ['==', ['get', 'cuisine'], hovered], 0.9, 0.66]);
      map.current.setPaintProperty('continents', 'fill-opacity', [
        'case',
        ['==', ['get', 'continent'], hovered],
        0.9,
        0.72,
      ]);
    }
  }, [hovered]);

  const heading = level === 'world' ? 'Cuisine globe' : label(level);
  const hint =
    level === 'world'
      ? 'Spin the globe and tap a continent.'
      : choices.some((id) => tree.nodes[id]?.children?.length)
        ? 'Tap a highlighted region to see its cuisines.'
        : 'Tap a cuisine to read about it.';

  const frame = (
    <div className={'globe-frame' + (compact ? ' compact' : '')}>
      <div
        className="globe-host"
        ref={host}
        data-ready={ready}
        data-level={level}
        data-settled={settled && ready}
        aria-label="Interactive cuisine map"
      />
      {ready && !failed && (
        <div className="globe-callouts" role="group" aria-label={compact ? 'Continents' : heading + ' regions'}>
          <svg aria-hidden="true">
            {callouts.map((callout) => {
              const color = regionColor(callout.id);
              return (
                callout.lead && (
                  <g key={callout.id}>
                    <line
                      x1={callout.lead.x}
                      y1={callout.lead.y}
                      x2={callout.x}
                      y2={callout.y}
                      stroke={color}
                      strokeDasharray={callout.behind || callout.offscreen ? '3 3' : undefined}
                    />
                    {!callout.offscreen && !callout.behind && (
                      <circle cx={callout.lead.x} cy={callout.lead.y} r="3.2" fill={color} />
                    )}
                  </g>
                )
              );
            })}
          </svg>
          {callouts.map((callout) => (
            <button
              key={callout.id}
              type="button"
              className="globe-callout"
              data-hovered={hovered === callout.id || undefined}
              onClick={() => choose(callout.id)}
              onPointerEnter={(event) => {
                if (event.pointerType === 'mouse' && !coarse()) setHovered(callout.id);
              }}
              onPointerLeave={() => setHovered('')}
              style={{
                left: callout.x - callout.width / 2,
                top: callout.y - callout.height / 2,
                width: callout.width,
                height: callout.height,
                borderColor: regionColor(callout.id),
              }}
            >
              {label(callout.id)}
            </button>
          ))}
        </div>
      )}
      {hovered && <output className="globe-location">{label(hovered)}</output>}
      {failed && (
        <p className="globe-message" role="status">
          The map couldn’t load. Choose by name below.
        </p>
      )}
      {!ready && !failed && (
        <p className="globe-message" role="status">
          Loading the globe…
        </p>
      )}
    </div>
  );
  if (compact) return frame;

  return (
    <>
      <div className="intro globe-intro">
        <h1>{heading}</h1>
        <p>{hint}</p>
      </div>
      <section className="card globe-panel" aria-label="Cuisine globe">
        {frame}
        <div className="globe-actions">
          {anyId && (
            <button type="button" className="secondary" onClick={() => choose(anyId)}>
              Any region <span className="globe-any">{cuisineLabel(anyId, tree)}</span>
            </button>
          )}
          <details className="globe-names" open={failed || undefined}>
            <summary>Choose by name</summary>
            <div className="globe-cuisines">
              {choices.map((id) => (
                <button className="secondary" type="button" key={id} onClick={() => choose(id)}>
                  <span className="region-swatch" style={{ backgroundColor: regionColor(id) }} />
                  {label(id)}
                </button>
              ))}
            </div>
          </details>
        </div>
      </section>
    </>
  );
}

const levelFilter = (level: string) => ['==', ['get', 'level'], level] as ['==', ['get', string], string];

function showLevel(globe: MapLibreMap, level: string) {
  if (!globe.getLayer(fillLayer)) return;
  globe.setFilter(fillLayer, levelFilter(level));
  globe.setFilter(outlineLayer, levelFilter(level));
  globe.setLayoutProperty('continents', 'visibility', level === 'world' ? 'visible' : 'none');
}
