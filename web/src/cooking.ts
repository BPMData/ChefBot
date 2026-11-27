import type { CuisineTree, Options } from './api';

const audienceLabels: Record<string, string> = {
  'A working professional.': 'Busy weeknight',
  'An important person you want to impress!': 'Impress someone',
  'A busy family with children.': 'Family with kids',
  'The elderly or mobility impaired.': 'Easy on the body',
  'A meal prepper who makes food for the entire week in one go.': 'Meal prep',
  "A solo diner who doesn't want to deal with leftovers.": 'Just me',
  "A health conscious individual who prefers food that's nutritious, high in protein and low in empty calories.":
    'Healthy',
  'A college student with only a microwave.': 'Microwave only',
};

export const audienceLabel = (audience: string) => audienceLabels[audience] ?? audience;

export function cuisineLabel(id: string, tree: CuisineTree | null) {
  if (id === 'Nothing in particular') return 'Anything';
  const node = tree?.nodes[id];
  if (node?.kind === 'any' && node.prompt_name) return node.prompt_name;
  return node?.label ?? id.replaceAll('_', ' ');
}

export function requestTags(settings: Options, tree: CuisineTree | null) {
  return [
    cuisineLabel(settings.cuisine, tree),
    audienceLabel(settings.audience),
    ...(settings.dessert ? ['Dessert'] : []),
    ...(settings.pantry ? ['Pantry defaults'] : []),
    ...settings.restrictions,
    ...(settings.must_not ? ['Never: ' + settings.must_not] : []),
  ];
}

export function recentCuisines(): string[] {
  try {
    const ids = JSON.parse(localStorage.getItem('chefbot.recent-cuisines') ?? '[]');
    return Array.isArray(ids) ? ids.filter((id) => typeof id === 'string').slice(0, 5) : [];
  } catch {
    return [];
  }
}

export function rememberCuisine(id: string) {
  const ids = [id, ...recentCuisines().filter((other) => other !== id)].slice(0, 5);
  localStorage.setItem('chefbot.recent-cuisines', JSON.stringify(ids));
}

export const tweaks = [
  ['Spicier', 'Make it spicier.'],
  ['Serves 6', 'Scale it to serve 6.'],
  ['Vegetarian', 'Make it vegetarian.'],
  ['Faster', 'Make it faster, under 30 minutes, without losing what makes it good.'],
  ['Shopping list', "Give me a shopping list for this, grouped by store section. Don't rewrite the recipe."],
  ['Pairing', "What should I drink with this? Don't rewrite the recipe."],
] as const;

export const historicalRequest =
  "How would this dish have been made in 1817? Rewrite it as a faithful period recipe, with the historical techniques, and note any modern substitutions. Be honest about uncertainty: don't invent people, book titles, dates or quotations, and if you aren't sure something is historically accurate, say so plainly. Start with one line reminding me this is an AI reconstruction, not a verified historical source.";

export function cuisinePath(id: string, tree: CuisineTree) {
  const path = [tree.nodes[id]];
  const nodes = Object.values(tree.nodes);
  let parent = nodes.find((node) => node.children?.includes(id));
  while (parent) {
    path.unshift(parent);
    const child = parent.id;
    parent = nodes.find((node) => node.children?.includes(child));
  }
  return path;
}
