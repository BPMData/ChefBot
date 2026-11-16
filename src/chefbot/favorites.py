"""Pure sorting, grouping, and search helpers for Recents and hierarchical Favorites."""

from chefbot import cuisines, prompts
from chefbot.history import Conversation

ANY_BUCKET = "__any__"
FAVORITES_PAGE_SIZE = 15


def conv_cuisine_label(conv: Conversation) -> str:
    """Return the concise cuisine chip label for a conversation, or '' if unresolved/Anything."""
    raw_cid = conv.settings.get("cuisine_id") or conv.settings.get("cuisine", "")
    resolved = cuisines.resolve(raw_cid) if raw_cid and raw_cid != prompts.NO_CUISINE else None
    return cuisines.chip_label(resolved["id"]) if resolved else ""


def conv_search_text(conv: Conversation) -> str:
    """Return lowercase searchable text covering title, cuisine labels, and non-system messages."""
    parts: list[str] = [conv.title or ""]
    raw_cid = conv.settings.get("cuisine_id") or conv.settings.get("cuisine", "")
    if raw_cid and raw_cid != prompts.NO_CUISINE:
        parts.append(str(raw_cid))
        resolved = cuisines.resolve(raw_cid)
        if resolved:
            parts.append(cuisines.chip_label(resolved["id"]))
            parts.append(resolved["label"])
            parts.extend(cuisines.path(resolved["id"]))
    ingredients = conv.settings.get("ingredients")
    if ingredients:
        parts.append(str(ingredients))
    for msg in conv.messages:
        if msg.get("role") == "system":
            continue
        text = msg.get("display") or msg.get("content") or ""
        if text:
            parts.append(str(text))
    return "\n".join(parts).lower()


def filter_conversations(convs: list[Conversation], query: str) -> list[Conversation]:
    """Filter conversations while preserving their existing order (case-insensitive all-token match)."""
    tokens = query.strip().lower().split()
    if not tokens:
        return list(convs)
    out: list[Conversation] = []
    for conv in convs:
        hay = conv_search_text(conv)
        if all(tok in hay for tok in tokens):
            out.append(conv)
    return out


def resolve_favorite_lineage(conv: Conversation) -> tuple[str | None, str | None, str | None]:
    """Map a conversation onto (continent_id, top_node_id, subcat_id), or (None, None, None) for Any cuisine."""
    raw_cid = conv.settings.get("cuisine_id") or conv.settings.get("cuisine", "")
    if not raw_cid or raw_cid == prompts.NO_CUISINE:
        return (None, None, None)
    node = cuisines.resolve(raw_cid)
    if not node:
        return (None, None, None)
    chain: list[str] = []
    cur: str | None = node["id"]
    while cur and cuisines.get(cur):
        chain.append(cur)
        cur = cuisines._PARENT_OF.get(cur)
    chain.reverse()
    if len(chain) == 2:
        return (chain[0], chain[1], None)
    if len(chain) >= 3:
        return (chain[0], chain[1], chain[2])
    return (None, None, None)


def sort_by_recent_access(convs: list[Conversation]) -> list[Conversation]:
    """Sort conversations by last_accessed descending (falling back to updated/created)."""
    return sorted(convs, key=lambda c: (c.last_accessed, c.updated, c.created), reverse=True)


def bucket_sort_key(convs: list[Conversation]) -> tuple[int, float, float]:
    """Sort key for Favorites folders: total access_count desc, then max last_accessed desc."""
    return (
        sum(c.access_count for c in convs),
        max((c.last_accessed for c in convs), default=0.0),
        max((c.updated for c in convs), default=0.0),
    )


def _folder_entry(folder_id: str, label: str, items: list[Conversation], **extra) -> dict:
    total_access, max_la, _ = bucket_sort_key(items)
    entry = {
        "id": folder_id,
        "label": label,
        "count": len(items),
        "access_count": total_access,
        "last_accessed": max_la,
    }
    entry.update(extra)
    return entry


def favorite_conversations(convs: list[Conversation]) -> list[Conversation]:
    """Return only conversations marked favorite."""
    return [c for c in convs if c.favorite]


def build_favorites_root(favs: list[Conversation]) -> dict:
    """Build Root of Favorites: top 5 recently accessed, sorted continents (all 6), and Any cuisine."""
    by_continent: dict[str, list[Conversation]] = {}
    any_items: list[Conversation] = []
    for conv in favs:
        cont_id = resolve_favorite_lineage(conv)[0]
        if cont_id is None:
            any_items.append(conv)
        else:
            by_continent.setdefault(cont_id, []).append(conv)

    continent_rows: list[tuple[tuple[int, float, float], dict]] = []
    for cont in cuisines.continents():
        items = by_continent.get(cont["id"])
        if items:
            continent_rows.append((
                bucket_sort_key(items),
                _folder_entry(cont["id"], cont["label"], items),
            ))
    continent_rows.sort(key=lambda pair: pair[0], reverse=True)

    return {
        "top_recent": sort_by_recent_access(favs)[:5],
        "continents": [row for _, row in continent_rows],
        "any_items": sort_by_recent_access(any_items),
    }


def build_continent_view(favs: list[Conversation], cont_id: str) -> dict:
    """Build Continent drill-down: countries and top-level cuisines sorted by access_count desc."""
    by_top: dict[str, list[Conversation]] = {}
    for conv in favs:
        c_cont, top_id, _ = resolve_favorite_lineage(conv)
        if c_cont == cont_id and top_id:
            by_top.setdefault(top_id, []).append(conv)

    rows: list[tuple[tuple[int, float, float], dict]] = []
    for top_id, items in by_top.items():
        node = cuisines.get(top_id)
        if not node:
            continue
        rows.append((
            bucket_sort_key(items),
            _folder_entry(top_id, node["label"], items, has_children=(node.get("kind") == "country")),
        ))
    rows.sort(key=lambda pair: pair[0], reverse=True)
    return {"items": [row for _, row in rows]}


def build_country_view(favs: list[Conversation], cont_id: str, country_id: str) -> dict:
    """Build Country drill-down: top 3 recently accessed + subcategories sorted by access_count desc."""
    country_favs: list[Conversation] = []
    by_sub: dict[str, list[Conversation]] = {}
    for conv in favs:
        c_cont, c_top, sub_id = resolve_favorite_lineage(conv)
        if c_cont == cont_id and c_top == country_id:
            country_favs.append(conv)
            if sub_id:
                by_sub.setdefault(sub_id, []).append(conv)

    rows: list[tuple[tuple[int, float, float], dict]] = []
    for sub_id, items in by_sub.items():
        node = cuisines.get(sub_id)
        if not node:
            continue
        rows.append((
            bucket_sort_key(items),
            _folder_entry(sub_id, node["label"], items),
        ))
    rows.sort(key=lambda pair: pair[0], reverse=True)
    return {
        "top_recent": sort_by_recent_access(country_favs)[:3],
        "subcategories": [row for _, row in rows],
    }


def build_leaf_list(favs: list[Conversation], path_ids: tuple[str, ...]) -> list[Conversation]:
    """Return all favorites matching a leaf cuisine, subcategory, or ANY_BUCKET, sorted by last_accessed desc."""
    if path_ids == (ANY_BUCKET,):
        matched = [c for c in favs if resolve_favorite_lineage(c)[0] is None]
    elif len(path_ids) == 2:
        matched = [c for c in favs if resolve_favorite_lineage(c)[:2] == path_ids]
    elif len(path_ids) == 3:
        matched = [c for c in favs if resolve_favorite_lineage(c) == path_ids]
    else:
        matched = []
    return sort_by_recent_access(matched)
