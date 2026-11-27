import type { CuisineTree } from '../api';
import { cuisineLabel } from '../cooking';

/** "Sichuan (Chinese)" becomes "Sichuan food", for the question at the bottom of the infobox. */
export function foodName(id: string, tree: CuisineTree) {
  const node = tree.nodes[id];
  const name = (node?.prompt_name ?? cuisineLabel(id, tree)).replace(/\s*\([^)]*\)\s*$/, '');
  return /\bfood$/i.test(name) ? name : name + ' food';
}
