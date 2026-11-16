"""Tests for History favorites/access tracking, hierarchical Favorites, search, and Try again."""
import asyncio
import json
from types import SimpleNamespace

import flet as ft
import pytest

import main
from chefbot import api, favorites, prompts
from chefbot.history import Conversation, History
from chefbot.keepalive import KeepAlive


def _make_conv(
    cid: str,
    title: str,
    cuisine_id: str,
    *,
    created: float = 100.0,
    updated: float = 100.0,
    favorite: bool = False,
    access_count: int = 0,
    last_accessed: float = 0.0,
    ingredients: str = "chicken, garlic",
    reply_text: str = "# Recipe\n\nCook it cleanly.",
) -> Conversation:
    return Conversation(
        id=cid,
        created=created,
        updated=updated,
        title=title,
        settings={"cuisine_id": cuisine_id, "cuisine": cuisine_id, "ingredients": ingredients},
        messages=[
            {"role": "system", "content": "Never invent salmon or papaya unless listed."},
            {"role": "user", "content": f"Ingredients: {ingredients}", "display": ingredients},
            {"role": "assistant", "content": reply_text},
        ],
        favorite=favorite,
        access_count=access_count,
        last_accessed=last_accessed,
    )


# ---------------------------------------------------------------- History compatibility & counters

def test_history_loads_legacy_conversations_without_favorite_fields(tmp_path):
    legacy_path = tmp_path / "conversations.json"
    legacy_path.write_text(json.dumps([{
        "id": "old1",
        "created": 50.0,
        "updated": 80.0,
        "title": "Old Stew",
        "settings": {"cuisine": "french"},
        "messages": [],
        "photos": {},
    }]), encoding="utf-8")
    hist = History(tmp_path)
    loaded = hist.load()
    assert len(loaded) == 1
    assert loaded[0].favorite is False
    assert loaded[0].access_count == 0
    assert loaded[0].last_accessed == 0.0


def test_history_save_toggle_and_record_access_preserve_recents_order(tmp_path):
    hist = History(tmp_path)
    c1 = _make_conv("c1", "First Recipe", "french", created=100.0, updated=100.0)
    c2 = _make_conv("c2", "Second Recipe", "korean", created=200.0, updated=200.0)
    hist.save(c1)
    hist.save(c2)

    loaded_after_init = {c.id: c for c in hist.load()}
    assert loaded_after_init["c1"].access_count == 1
    assert loaded_after_init["c1"].last_accessed == 100.0

    # Mutate updated cleanly on disk to verify toggle_favorite / record_access keep Recents intact
    c1_saved = loaded_after_init["c1"]
    c2_saved = loaded_after_init["c2"]
    c1_saved.updated = 100.0
    c2_saved.updated = 200.0
    hist._write([c2_saved, c1_saved])

    assert hist.toggle_favorite("c1") is True
    rec = hist.record_access("c1")
    assert rec is not None
    assert rec.access_count == 2
    assert rec.last_accessed > 100.0

    reloaded = hist.load()
    # Recents stays ordered by `updated` desc: c2 (200.0) still comes before c1 (100.0)
    assert [c.id for c in reloaded] == ["c2", "c1"]
    assert reloaded[1].updated == 100.0
    assert reloaded[1].favorite is True
    assert reloaded[1].access_count == 2

    # Subsequent save of c1 preserves favorite and access_count
    reloaded[1].title = "Updated Title"
    hist.save(reloaded[1])
    final_c1 = next(c for c in hist.load() if c.id == "c1")
    assert final_c1.favorite is True
    assert final_c1.access_count == 2


# ---------------------------------------------------------------- Search filtering

def test_search_matches_title_cuisine_and_ingredients_without_system_noise():
    c1 = _make_conv("c1", "Herb Roast Chicken", "french", updated=300.0, ingredients="chicken, thyme, garlic")
    c2 = _make_conv("c2", "Bibimbap Bowl", "korean", updated=200.0, ingredients="rice, spinach, gochujang")
    c3 = _make_conv("c3", "Pan-Seared Barramundi", "australian", updated=100.0, ingredients="barramundi, lemon myrtle")
    convs = [c1, c2, c3]

    # Chronological order preserved
    assert [c.id for c in favorites.filter_conversations(convs, "")] == ["c1", "c2", "c3"]
    # Title + cuisine multi-word match
    assert [c.id for c in favorites.filter_conversations(convs, "french chicken")] == ["c1"]
    # Ancestor continent match ("oceania")
    assert [c.id for c in favorites.filter_conversations(convs, "oceania")] == ["c3"]
    # Key ingredient match
    assert [c.id for c in favorites.filter_conversations(convs, "gochujang")] == ["c2"]
    # System prompt words ("papaya") must not match
    assert favorites.filter_conversations(convs, "papaya") == []


# ---------------------------------------------------------------- Hierarchical Favorites & sorting

def test_favorites_hierarchy_six_continents_sorting_and_legacy_fallback():
    favs = [
        _make_conv("f_au", "Damper", "australian", favorite=True, access_count=8, last_accessed=900.0),
        _make_conv("f_jp_k", "Tempura", "kanto", favorite=True, access_count=3, last_accessed=800.0),
        _make_conv("f_cn_leg", "Wok Greens", "Chinese (Hong Kong)", favorite=True, access_count=10, last_accessed=700.0),
        _make_conv("f_cn_sc", "Mapo Tofu", "sichuan", favorite=True, access_count=2, last_accessed=650.0),
        _make_conv("f_fr", "Ratatouille", "french", favorite=True, access_count=4, last_accessed=600.0),
        _make_conv("f_us_na", "Three Sisters Stew", "us_native_american", favorite=True, access_count=2, last_accessed=550.0),
        _make_conv("f_us_cj", "Gumbo", "us_cajun", favorite=True, access_count=1, last_accessed=500.0),
        _make_conv("f_us_gl", "Walleye Fry", "us_great_lakes", favorite=True, access_count=1, last_accessed=450.0),
        _make_conv("f_us_ap", "Soup Beans", "us_appalachian", favorite=True, access_count=1, last_accessed=400.0),
        _make_conv("f_ye", "Saltah", "yemeni", favorite=True, access_count=2, last_accessed=350.0),
        _make_conv("f_gh", "Jollof", "ghanaian", favorite=True, access_count=1, last_accessed=300.0),
        _make_conv("f_any", "Midnight Eggs", prompts.NO_CUISINE, favorite=True, access_count=5, last_accessed=850.0),
        _make_conv("f_unk", "Mystery Dish", "no_such_cuisine", favorite=True, access_count=1, last_accessed=200.0),
    ]

    # Root: top 5 recently accessed (desc last_accessed), all 6 continents sorted by access_count desc + Any cuisine
    root = favorites.build_favorites_root(favs)
    assert [c.id for c in root["top_recent"]] == ["f_au", "f_any", "f_jp_k", "f_cn_leg", "f_cn_sc"]
    assert [c["id"] for c in root["continents"]] == [
        "asia",      # 3 + 10 + 2 = 15
        "oceania",   # 8
        "americas",  # 2 + 1 + 1 + 1 = 5
        "europe",    # 4
        "near_east", # 2
        "africa",    # 1
    ]
    assert [c.id for c in root["any_items"]] == ["f_any", "f_unk"]

    # Continent -> countries / top-level leaves sorted by access_count desc (China 12 > Japan 3)
    asia = favorites.build_continent_view(favs, "asia")
    assert [(item["id"], item["has_children"], item["count"]) for item in asia["items"]] == [
        ("china", True, 2),
        ("japan", True, 1),
    ]

    # Country with subcategories -> top 3 across country + subcategories sorted by access_count desc
    us = favorites.build_country_view(favs, "americas", "united_states")
    assert [c.id for c in us["top_recent"]] == ["f_us_na", "f_us_cj", "f_us_gl"]
    assert [s["id"] for s in us["subcategories"]][0] == "us_native_american"

    # Legacy "Chinese (Hong Kong)" resolved into ("asia", "china", "cantonese")
    china = favorites.build_country_view(favs, "asia", "china")
    assert [s["id"] for s in china["subcategories"]] == ["cantonese", "sichuan"]
    assert [c.id for c in favorites.build_leaf_list(favs, ("asia", "china", "cantonese"))] == ["f_cn_leg"]

    # Country/cuisine with NO subcategories -> leaf list directly
    assert [c.id for c in favorites.build_leaf_list(favs, ("europe", "french"))] == ["f_fr"]
    assert [c.id for c in favorites.build_leaf_list(favs, (favorites.ANY_BUCKET,))] == ["f_any", "f_unk"]


def test_bucket_tiebreaker_prefers_most_recently_accessed():
    # Equal total access_count (3 == 3), Europe has newer last_accessed (950 vs 500)
    favs = [
        _make_conv("f1", "Pasta", "northern_italy", favorite=True, access_count=3, last_accessed=950.0),
        _make_conv("f2", "Tacos", "mx_any", favorite=True, access_count=3, last_accessed=500.0),
    ]
    root = favorites.build_favorites_root(favs)
    assert [c["id"] for c in root["continents"]] == ["europe", "americas"]


# ---------------------------------------------------------------- UI Favorites, Pagination & Try Again

def _ui_app(tmp_path):
    app = main.ChefBotApp.__new__(main.ChefBotApp)
    app.history = History(tmp_path)
    app.working = {}
    app.live_bubbles = {}
    app.kept_photos = set()
    app.cards = {}
    app.user_tools = {}
    app.on_map = False
    app.on_favorites = False
    app.fav_path = ()
    app.fav_query = ""
    app.fav_limit = favorites.FAVORITES_PAGE_SIZE
    app.recent_query = ""
    app.cuisine = prompts.NO_CUISINE
    app.audience = prompts.DEFAULT_AUDIENCE
    app._globe_motion_gen = 0
    app._globe_flying = False
    app.padded = []
    app.away = False
    app.times_away = 0
    app.back = asyncio.Event()
    app.back.set()
    app.RETRY_SETTLE = 0
    app.keepalive = KeepAlive(SimpleNamespace(can_notify=lambda: False, start=lambda *a: None,
                                              stop=lambda: None, notify=lambda *a: None))
    app.root = SimpleNamespace(content=None)
    app.page = SimpleNamespace(
        width=375,
        height=800,
        appbar=None,
        views=[SimpleNamespace(can_pop=True)],
        update=lambda: None,
    )
    app.chef = SimpleNamespace()
    app.recent = ft.Column()
    app.recent_rows_col = ft.Column()
    app.recent_search_clear = ft.IconButton(ft.Icons.CLOSE, visible=False)
    app.recent_search = ft.TextField(suffix_icon=app.recent_search_clear)
    app.star_btn = None
    return app


def test_ui_favorites_drilldown_pagination_and_record_access(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "snack", lambda page, text: None)
    app = _ui_app(tmp_path)
    for i in range(18):
        c = _make_conv(
            f"fr{i}", f"French Dish {i}", "french",
            created=100.0 + i, updated=100.0 + i, favorite=True,
            access_count=1, last_accessed=200.0 + i,
        )
        app.history._write([*app.history.load(), c])

    app.open_favorites(("europe", "french"))
    # Initial cutoff is 15 recipes + 1 "Show more (3 more)" button
    recipe_rows = [c for c in app.fav_body.controls if isinstance(c, ft.Container)]
    more_btns = [c for c in app.fav_body.controls if isinstance(c, ft.TextButton)]
    assert len(recipe_rows) == 15
    assert len(more_btns) == 1 and "3 more" in more_btns[0].content

    app._show_more_favs()
    recipe_rows = [c for c in app.fav_body.controls if isinstance(c, ft.Container)]
    assert len(recipe_rows) == 18

    # Back walks up French -> Europe -> Favorites root -> Home
    app._favorites_back()
    assert app.fav_path == ("europe",)
    app._favorites_back()
    assert app.fav_path == ()

    # Opening a saved chat updates access_count & last_accessed without changing updated
    opened_ids = []
    monkeypatch.setattr(app, "show_chat", lambda conv: opened_ids.append(conv.id))
    app.open_conversation("fr0")
    assert opened_ids == ["fr0"]
    fr0 = next(c for c in app.history.load() if c.id == "fr0")
    assert fr0.access_count == 2
    assert fr0.updated == 100.0


def test_try_again_replaces_reply_guards_double_tap_and_rolls_back_on_error(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "snack", lambda page, text: None)
    app = _ui_app(tmp_path)
    conv = Conversation(
        id="conv1",
        title="Original Dish",
        messages=[
            {"role": "system", "content": "sys"},
            {"role": "user", "content": "eggs"},
            {"role": "assistant", "content": "**Recipe Title: Original Dish**\n\nBoil eggs."},
            {"role": "user", "content": "Make it spicy"},
            {"role": "assistant", "content": "**Recipe Title: Spicy Dish**\n\nAdd chili."},
        ],
        photos={"4": "spicy.jpg"},
    )
    app.history.save(conv)
    app.conv = conv
    app.star_btn = ft.IconButton(ft.Icons.STAR_BORDER)
    app.composer = SimpleNamespace(value="", disabled=False, update=lambda: None)
    app.send_btn = SimpleNamespace(disabled=False, update=lambda: None)
    app.tweaks = SimpleNamespace(disabled=False, update=lambda: None)
    app.title_text = SimpleNamespace(value=conv.title, update=lambda: None)
    app._refresh_user_tools = lambda: None
    app._refresh_assistant_actions = lambda: None
    app._set_status = lambda t: None
    app._assistant_card = lambda text: SimpleNamespace(
        data={"md": SimpleNamespace(value=text, update=lambda: None), "actions": ft.Row()},
        key=None,
        update=lambda: None,
    )
    old_card = SimpleNamespace(data={})
    app.cards = {4: old_card}
    app.thread = SimpleNamespace(controls=[old_card], update=lambda: None)
    app._add_to_thread = lambda c: app.thread.controls.append(c)
    app._scroll_to_end = lambda: asyncio.sleep(0)

    # Live star toggle updates open conv, AppBar icon, and disk without shifting updated
    orig_updated = conv.updated
    app.toggle_favorite(conv.id, refresh_view=False)
    assert conv.favorite is True
    assert app.star_btn.icon == ft.Icons.STAR
    assert next(c for c in app.history.load() if c.id == conv.id).updated == orig_updated

    async def run():
        # 1. Double-tap guard while conv.id in self.working
        app.working[conv.id] = conv
        await app.retry_reply(4)
        assert len(conv.messages) == 5
        app.working.pop(conv.id, None)

        # 2. Failed Try again on follow-up turn restores user message, old reply, photo, and title
        async def fail_stream(c, md):
            assert c.messages[-1] == {"role": "user", "content": "Make it spicy"}
            assert "spicy.jpg" in app.kept_photos
            return "", api.ApiError("down"), False

        app._stream_reply = fail_stream
        shown = []
        monkeypatch.setattr(app, "show_chat", lambda c: shown.append(len(c.messages)))
        await app.retry_reply(4)
        assert shown[-1] == 5
        assert len(conv.messages) == 5
        assert conv.messages[4]["content"] == "**Recipe Title: Spicy Dish**\n\nAdd chili."
        assert conv.photos == {"4": "spicy.jpg"}
        assert "spicy.jpg" not in app.kept_photos

        # 3. Successful Try again replaces reply and clears old photo reference
        async def ok_stream(c, md):
            return "**Recipe Title: Extra Spicy Dish**\n\nDouble chili.", None, False

        app._stream_reply = ok_stream
        app.cards = {4: SimpleNamespace(data={})}
        app.thread.controls = [app.cards[4]]
        await app.retry_reply(4)
        assert len(conv.messages) == 5
        assert conv.messages[4]["content"] == "**Recipe Title: Extra Spicy Dish**\n\nDouble chili."
        assert conv.title == "Extra Spicy Dish"
        assert "4" not in conv.photos
        assert "spicy.jpg" not in app.kept_photos

    asyncio.run(run())
