// Places one label chip per region so chips never overlap and stay inside the map, like the
// call-out chips on the Android map. A chip sits on its region when there is room, and otherwise
// moves out along a leader line to the nearest free spot.

export type CalloutInput = {
  id: string;
  /** Screen position of the region's anchor point. */
  anchor: { x: number; y: number };
  /** The region is on the far side of the globe; the anchor is the globe's edge in its direction. */
  behind?: boolean;
  /** Screen size of the region's outline, used to decide whether a chip fits on top of it. */
  size: { width: number; height: number };
  width: number;
  height: number;
};

export type Callout = {
  id: string; x: number; y: number; width: number; height: number;
  /** Where the leader line starts (the anchor, pulled inside the frame), when the chip moved away. */
  lead: { x: number; y: number } | null;
  offscreen: boolean;
  behind: boolean;
};

type Rect = { left: number; top: number; right: number; bottom: number };

const margin = 6;
const gap = 4;
const dotClearance = 7;
const distances = [0, 14, 24, 36, 50, 66, 84, 106, 132, 162, 196];
const directions = Array.from({ length: 16 }, (_, i) => {
  const angle = -Math.PI / 2 + (i * Math.PI) / 8;
  return { dx: Math.cos(angle), dy: Math.sin(angle) };
});

function overlaps(a: Rect, b: Rect, pad = gap) {
  return a.left < b.right + pad && b.left < a.right + pad && a.top < b.bottom + pad && b.top < a.bottom + pad;
}

function overlapArea(a: Rect, b: Rect) {
  const width = Math.min(a.right, b.right) - Math.max(a.left, b.left) + gap;
  const height = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top) + gap;
  return width > 0 && height > 0 ? width * height : 0;
}

function rectAt(x: number, y: number, width: number, height: number): Rect {
  return { left: x - width / 2, top: y - height / 2, right: x + width / 2, bottom: y + height / 2 };
}

type Segment = { x1: number; y1: number; x2: number; y2: number };

function crosses(a: Segment, b: Segment) {
  const side = (x: number, y: number, s: Segment) => Math.sign((s.x2 - s.x1) * (y - s.y1) - (s.y2 - s.y1) * (x - s.x1));
  return side(a.x1, a.y1, b) !== side(a.x2, a.y2, b) && side(b.x1, b.y1, a) !== side(b.x2, b.y2, a);
}

function lineHitsRect(line: Segment, rect: Rect) {
  // Samples the line; chips are much larger than the step, so this never misses one.
  const steps = Math.ceil(Math.hypot(line.x2 - line.x1, line.y2 - line.y1) / 6);
  for (let i = 1; i < steps; i++) {
    const x = line.x1 + (line.x2 - line.x1) * i / steps;
    const y = line.y1 + (line.y2 - line.y1) * i / steps;
    if (x > rect.left && x < rect.right && y > rect.top && y < rect.bottom) return true;
  }
  return false;
}

/** Lays out chips for a frame of `width` by `height` pixels. */
export function layoutCallouts(items: CalloutInput[], width: number, height: number): Callout[] {
  const anchors = items.map((item) => {
    const { x, y } = item.anchor;
    const inside = x >= margin && x <= width - margin && y >= margin && y <= height - margin;
    return { item, inside, x: Math.min(width - margin, Math.max(margin, x)), y: Math.min(height - margin, Math.max(margin, y)) };
  });
  type Anchor = (typeof anchors)[number];
  type Spot = { x: number; y: number; rect: Rect; line: Segment | null; cost: number };
  const centroid = anchors.reduce((sum, a) => ({ x: sum.x + a.x / anchors.length, y: sum.y + a.y / anchors.length }), { x: 0, y: 0 });
  const crowd = (a: Anchor) => anchors.filter((b) => b !== a && Math.hypot(a.x - b.x, a.y - b.y) < 90).length;
  const fits = (a: Anchor) => a.inside && !a.item.behind
    && a.item.size.width >= a.item.width * 0.8 && a.item.size.height >= a.item.height * 1.2;
  // Chips that fit on their own region go first; then crowded and off-screen regions, so they get the
  // free spots closest to their anchors.
  const order = [...anchors].sort((a, b) => Number(fits(b)) - Number(fits(a)) || Number(a.inside) - Number(b.inside)
    || crowd(b) - crowd(a) || a.y - b.y);
  const dots = anchors.filter((anchor) => anchor.inside && !anchor.item.behind);
  const chosen = new Map<Anchor, Spot>();

  function candidates(anchor: Anchor) {
    const { item } = anchor;
    const fitsOnRegion = fits(anchor);
    // Chips prefer to move away from the middle of the crowd, so leader lines fan out instead of crossing.
    const out = { x: anchor.x - centroid.x, y: anchor.y - centroid.y };
    const outLength = Math.hypot(out.x, out.y) || 1;
    const spots: { x: number; y: number; base: number }[] = [];
    for (const distance of distances) {
      if (distance === 0) {
        if (fitsOnRegion) spots.push({ x: anchor.x, y: anchor.y, base: 0 });
        continue;
      }
      for (const { dx, dy } of directions) {
        // Measured from the chip's edge, not its centre.
        const x = anchor.x + dx * (distance + item.width / 2 - 6);
        const y = anchor.y + dy * (distance + item.height / 2);
        const away = (dx * out.x + dy * out.y) / outLength;
        spots.push({ x, y, base: distance * 1.4 + (1 - away) * 10 });
      }
    }
    return spots;
  }

  function score(anchor: Anchor, spot: { x: number; y: number; base: number }): Spot | null {
    const { item } = anchor;
    const rect = rectAt(spot.x, spot.y, item.width, item.height);
    if (rect.left < margin || rect.top < margin || rect.right > width - margin || rect.bottom > height - margin) return null;
    const moved = !anchor.inside || !!item.behind || spot.base > 0;
    const line = moved ? { x1: anchor.x, y1: anchor.y, x2: spot.x, y2: spot.y } : null;
    let cost = spot.base;
    for (const [other, placed] of chosen) {
      if (other === anchor) continue;
      cost += overlapArea(rect, placed.rect) * 50;
      if (line && placed.line && crosses(line, placed.line)) cost += 120;
      if (placed.line && lineHitsRect(placed.line, rect)) cost += 60;
      if (line && lineHitsRect(line, placed.rect)) cost += 60;
    }
    // A chip nearer another region's point than its own reads as that region's label.
    const own = Math.hypot(spot.x - anchor.x, spot.y - anchor.y);
    for (const other of dots) {
      if (other !== anchor && Math.hypot(spot.x - other.x, spot.y - other.y) < own - 4) cost += 70;
    }
    for (const dot of dots) {
      if (dot === anchor) continue;
      if (dot.x > rect.left - dotClearance && dot.x < rect.right + dotClearance
        && dot.y > rect.top - dotClearance && dot.y < rect.bottom + dotClearance) cost += 400;
    }
    return { x: spot.x, y: spot.y, rect, line, cost };
  }

  function place(anchor: Anchor) {
    let best: Spot | null = null;
    for (const spot of candidates(anchor)) {
      const scored = score(anchor, spot);
      if (scored && (!best || scored.cost < best.cost)) best = scored;
    }
    if (!best) {
      const { item } = anchor;
      const x = Math.min(width - margin - item.width / 2, Math.max(margin + item.width / 2, anchor.x));
      const y = Math.min(height - margin - item.height / 2, Math.max(margin + item.height / 2, anchor.y));
      best = { x, y, rect: rectAt(x, y, item.width, item.height), line: { x1: anchor.x, y1: anchor.y, x2: x, y2: y }, cost: 0 };
    }
    chosen.set(anchor, best);
  }

  for (const anchor of order) place(anchor);
  // A few passes where each chip moves to its best spot given where all the others ended up.
  for (let pass = 0; pass < 4; pass++) for (const anchor of order) place(anchor);

  return anchors.map((anchor) => {
    const spot = chosen.get(anchor)!;
    const { item } = anchor;
    return {
      id: item.id, x: spot.x, y: spot.y, width: item.width, height: item.height,
      lead: spot.line && { x: anchor.x, y: anchor.y }, offscreen: !anchor.inside, behind: !!item.behind,
    };
  });
}

/** Moves chips with their anchors while the globe is being dragged, without re-running the layout. */
export function followAnchors(callouts: Callout[], previous: Map<string, { x: number; y: number }>,
  next: Map<string, { x: number; y: number }>) {
  return callouts.flatMap((callout) => {
    const before = previous.get(callout.id);
    const after = next.get(callout.id);
    if (!before || !after) return [];
    const dx = after.x - before.x;
    const dy = after.y - before.y;
    return [{ ...callout, x: callout.x + dx, y: callout.y + dy,
      lead: callout.lead && { x: callout.lead.x + dx, y: callout.lead.y + dy } }];
  });
}
