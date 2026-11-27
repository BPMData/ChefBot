import { useEffect, useState } from 'react';

type Screen = 'home' | 'recipe' | 'globe' | 'settings' | 'favorites';
type Route = {
  screen: Screen;
  id: string | null;
  previous?: Screen;
  picker?: boolean;
  preview?: string;
  mapPath?: string[];
  favoritePath?: string[];
  query?: string;
  favoriteLimit?: number;
};
const home: Route = { screen: 'home', id: null };

function remember(route: Route) {
  if (route.id) sessionStorage.setItem('chefbot.open-chat', route.id);
  else sessionStorage.removeItem('chefbot.open-chat');
}

function currentRoute(): Route {
  if (history.state?.chefbot) return history.state.chefbot;
  const id = sessionStorage.getItem('chefbot.open-chat');
  return id ? { screen: 'recipe', id } : home;
}

export function useNavigation() {
  const [route, setRoute] = useState<Route>(currentRoute);
  useEffect(() => {
    history.replaceState({ ...history.state, chefbot: currentRoute() }, '');
    const pop = () => {
      const next: Route = history.state?.chefbot ?? home;
      remember(next);
      setRoute(next);
    };
    window.addEventListener('popstate', pop);
    return () => window.removeEventListener('popstate', pop);
  }, []);

  function navigate(screen: Screen, id: string | null = null, replace = false) {
    if (route.screen === screen && route.id === id) return;
    const next: Route = { screen, id, previous: replace ? route.previous : route.screen };
    if (replace) history.replaceState({ ...history.state, chefbot: next }, '');
    else history.pushState({ chefbot: next }, '');
    remember(next);
    setRoute(next);
    window.scrollTo(0, 0);
  }

  function back() {
    if (route.previous || route.mapPath?.length) history.back();
    else navigate('home', null, true);
  }

  function openFavoriteFolder(id: string) {
    const next = { ...route, query: '', favoriteLimit: undefined, favoritePath: [...(route.favoritePath ?? []), id] };
    history.pushState({ chefbot: next }, '');
    setRoute(next);
    window.scrollTo(0, 0);
  }

  function updateLibrary(fields: Pick<Route, 'query' | 'favoriteLimit'>) {
    const next = { ...route, ...fields };
    history.replaceState({ ...history.state, chefbot: next }, '');
    setRoute(next);
  }

  function openCuisine(next: Pick<Route, 'picker' | 'preview' | 'mapPath'>) {
    const entry = { ...route, ...next };
    history.pushState({ chefbot: entry }, '');
    setRoute(entry);
    if (next.mapPath) window.scrollTo(0, 0);
  }

  /** Opens the globe screen, optionally already inside `path` (one history entry per level, so Back climbs out). */
  function openGlobe(path: string[] = []) {
    let next: Route = { screen: 'globe', id: null, previous: route.screen };
    history.pushState({ chefbot: next }, '');
    for (let depth = 1; depth <= path.length; depth++) {
      next = { ...next, mapPath: path.slice(0, depth) };
      history.pushState({ chefbot: next }, '');
    }
    remember(next);
    setRoute(next);
    window.scrollTo(0, 0);
  }

  function dismissCuisine() {
    history.back();
  }

  function finishCuisine() {
    // A confirmed pick returns to the existing form, including the ingredients typed there.
    const entries =
      Number(!!route.preview) +
      Number(!!route.picker) +
      Number(route.screen === 'globe') +
      (route.mapPath?.length ?? 0);
    if (entries) history.go(-entries);
  }

  return {
    route,
    navigate,
    back,
    openCuisine,
    openGlobe,
    dismissCuisine,
    finishCuisine,
    openFavoriteFolder,
    updateLibrary,
  };
}
