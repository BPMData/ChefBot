"""ChefBot: tell it what's in your fridge, get a recipe, then keep refining it in conversation."""
import asyncio
import json
import logging
import math
import os
import random
import time
from datetime import datetime

import flet as ft
import flet.canvas as cv

from chefbot import android, api, cuisines, export, maps, prompts
from chefbot.history import Conversation, History
from chefbot.keepalive import PICTURE, WRITING, KeepAlive
from chefbot.recipe import extract_title

log = logging.getLogger("chefbot")

PREF_KEY = "chefbot.openrouter_key"
PREF_MODEL = "chefbot.model"
PREF_EFFORT = "chefbot.effort"
PREF_THEME = "chefbot.theme"
PREF_EMAIL_TO = "chefbot.email_to"          # default recipient
PREF_SMTP_USER = "chefbot.smtp_user"        # the account ChefBot sends from
PREF_SMTP_PASSWORD = "chefbot.smtp_password"
PREF_SMTP_SERVER = "chefbot.smtp_server"
PREF_RELAY_URL = "chefbot.relay_url"        # ChefBot mail relay (tools/mail-relay.gs), preferred over SMTP
PREF_RELAY_SECRET = "chefbot.relay_secret"
PREF_MUST_NOT = "chefbot.must_not"          # the "Never use..." box, remembered (allergies don't go away)
PREF_RECENT_CUISINES = "chefbot.recent_cuisines"  # JSON list of last 5 picked leaf cuisine ids
PREF_DEV_MODE = "chefbot.dev_mode"          # "on" shows the hidden email-sending settings (tap Settings 7 times)
DEV_MODE_TAPS = 7
PREFS_FAILED = ("ChefBot couldn't read its saved settings (your key is still safe). Close ChefBot and open it "
                "again.")
ALL_PREFS = (PREF_KEY, PREF_MODEL, PREF_EFFORT, PREF_THEME, PREF_EMAIL_TO, PREF_SMTP_USER, PREF_SMTP_PASSWORD,
             PREF_SMTP_SERVER, PREF_RELAY_URL, PREF_RELAY_SECRET, PREF_DEV_MODE,
             PREF_MUST_NOT, PREF_RECENT_CUISINES)
DEFAULT_SMTP = "smtp.gmail.com:465"
MAILTO_LIMIT_WINDOWS = 1500   # characters of recipe text in a mailto link on Windows

# ---------------------------------------------------------------- look and feel

FONTS = {   # open-licensed (OFL) Google Fonts, bundled in src/assets/fonts with their licenses
    "Fraunces": "fonts/Fraunces.ttf",
    "DM Sans": "fonts/DMSans.ttf",
}
HEADING_FONT, BODY_FONT = "Fraunces", "DM Sans"
SEED = "#E8590C"
GRADIENT = ["#FF8A3D", "#E8452C"]
BG_LIGHT, BG_DARK = "#FFF6EC", "#110E0C"
PHOTO_LABEL = "Photograph my ingredients instead"
MAX_WIDTH = 780          # content column width on wide screens
THEMES = {"dark": ft.ThemeMode.DARK, "light": ft.ThemeMode.LIGHT, "system": ft.ThemeMode.SYSTEM}

CONTINENT_ICONS = {
    "americas": ft.Icons.PUBLIC,
    "asia": ft.Icons.RAMEN_DINING,
    "europe": ft.Icons.RESTAURANT,
    "near_east": ft.Icons.LOCAL_CAFE,
    "africa": ft.Icons.WB_SUNNY_OUTLINED,
}
# Distinct color families from Flet's built-in palette (fill shade, border/outline shade)
MAP_PALETTE: dict[str, tuple[str, str]] = {
    "coral": (ft.Colors.DEEP_ORANGE_400, ft.Colors.DEEP_ORANGE_200),
    "amber": (ft.Colors.AMBER_500, ft.Colors.AMBER_200),
    "teal": (ft.Colors.TEAL_400, ft.Colors.TEAL_200),
    "blue": (ft.Colors.BLUE_400, ft.Colors.BLUE_200),
    "purple": (ft.Colors.PURPLE_300, ft.Colors.PURPLE_100),
    "green": (ft.Colors.GREEN_500, ft.Colors.GREEN_200),
    "pink": (ft.Colors.PINK_300, ft.Colors.PINK_100),
    "cyan": (ft.Colors.CYAN_500, ft.Colors.CYAN_200),
    "orange": (ft.Colors.ORANGE_500, ft.Colors.ORANGE_200),
    "indigo": (ft.Colors.INDIGO_300, ft.Colors.INDIGO_100),
    "lime": (ft.Colors.LIME_500, ft.Colors.LIME_200),
}
MAX_RECENT_CUISINES = 5
# Slow idle spin (degrees/sec) until the first touch on the globe; set to 0.0 to disable.
GLOBE_IDLE_SPIN_DPS = 6.0
GLOBE_MIN_ZOOM = 0.85
GLOBE_MAX_ZOOM = 2.6
GLOBE_MAX_LAT = 65.0
GLOBE_INITIAL_LON = 22.0
GLOBE_INITIAL_LAT = 20.0
GLOBE_FLY_SECONDS = 0.50
# Zoom between map levels: the old map scales up around the tapped region and fades while the new one
# grows out of that spot (reversed for Back). Flutter animates it on the device, so Python sends only
# the start and end states.
MAP_ZOOM_MS = 420
MAP_ZOOM_IN_SCALE = 2.6
MAP_ZOOM_OUT_SCALE = 0.32
AUDIENCE_CARDS = {
    "A working professional.": (ft.Icons.WORK_OUTLINE, "Busy weeknight"),
    "An important person you want to impress!": (ft.Icons.AUTO_AWESOME, "Impress someone"),
    "A busy family with children.": (ft.Icons.FAMILY_RESTROOM, "Family with kids"),
    "The elderly or mobility impaired.": (ft.Icons.ELDERLY, "Easy on the body"),
    "A meal prepper who makes food for the entire week in one go.": (ft.Icons.CALENDAR_VIEW_WEEK, "Meal prep"),
    "A solo diner who doesn't want to deal with leftovers.": (ft.Icons.PERSON_OUTLINE, "Just me"),
    "A health conscious individual who prefers food that's nutritious, high in protein and low in empty calories.":
        (ft.Icons.FITNESS_CENTER, "Healthy"),
    "A college student with only a microwave.": (ft.Icons.MICROWAVE, "Microwave only"),
}
QUICK_TWEAKS = [
    (ft.Icons.LOCAL_FIRE_DEPARTMENT, "Spicier", "Make it spicier."),
    (ft.Icons.GROUP, "Serves 6", "Scale it to serve 6."),
    (ft.Icons.HISTORY_EDU, "The 1817 version",
     "How would this dish have been made in 1817? Rewrite it as a faithful period recipe, with the historical "
     "techniques, and note any modern substitutions. Be honest about uncertainty: don't invent people, book "
     "titles, dates or quotations, and if you aren't sure something is historically accurate, say so plainly. "
     "Start with one line reminding me this is an AI reconstruction, not a verified historical source."),
    (ft.Icons.ECO, "Vegetarian", "Make it vegetarian."),
    (ft.Icons.TIMER, "Faster", "Make it faster, under 30 minutes, without losing what makes it good."),
    (ft.Icons.SHOPPING_CART, "Shopping list",
     "Give me a shopping list for this, grouped by store section. Don't rewrite the recipe."),
    (ft.Icons.WINE_BAR, "Pairing", "What should I drink with this? Don't rewrite the recipe."),
]
BETA_TWEAKS = {"The 1817 version"}
HISTORY_WARNING = (
    "This asks the AI to imagine how the dish was cooked in 1817. AI models regularly make up history that "
    "sounds convincing: people, cookbooks, dates, quotations and \"traditional\" techniques that never existed. "
    "Treat the result as inspiration, not as history, and check anything you rely on against a real period "
    "cookbook or a food historian.")
THINKING_LINES = ["Sharpening knives", "Smashing garlic", "Consulting old cookbooks", "Heating the pan",
                  "Tasting for salt", "Picking herbs", "Reading the ingredients twice"]
DISCLAIMER = ("ChefBot is an AI, not a dietitian. Double-check recipes yourself, and never rely on it "
              "for serious allergies.")
EFFORT_LABELS = {"low": "Low (fastest)", "medium": "Medium", "high": "High (most careful)"}


def heading(text: str, size: int = 20, color=None, weight=ft.FontWeight.W_700) -> ft.Text:
    return ft.Text(text, size=size, weight=weight, color=color, font_family=HEADING_FONT)


def section_title(icon: str, text: str) -> ft.Row:
    return ft.Row([ft.Icon(icon, color=ft.Colors.PRIMARY, size=22), heading(text)], spacing=10)


def card(*controls: ft.Control, padding: int = 18) -> ft.Container:
    return ft.Container(
        ft.Column(list(controls), spacing=14, tight=True, horizontal_alignment=ft.CrossAxisAlignment.STRETCH),
        padding=padding, border_radius=22, bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
        border=ft.Border.all(1, ft.Colors.with_opacity(0.06, ft.Colors.ON_SURFACE)),
        shadow=ft.BoxShadow(blur_radius=20, spread_radius=-8, color=ft.Colors.with_opacity(0.25, "#000000"),
                            offset=ft.Offset(0, 8)))


def gradient_button(label: str, icon: str, on_click) -> ft.Container:
    return ft.Container(
        ft.Row([ft.Icon(icon, color=ft.Colors.WHITE, size=24), heading(label, 19, ft.Colors.WHITE)],
               alignment=ft.MainAxisAlignment.CENTER, spacing=10),
        height=60, border_radius=30, ink=True, on_click=on_click,
        gradient=ft.LinearGradient(colors=GRADIENT, begin=ft.Alignment.CENTER_LEFT, end=ft.Alignment.CENTER_RIGHT),
        shadow=ft.BoxShadow(blur_radius=18, spread_radius=-4, color=ft.Colors.with_opacity(0.45, "#E8452C"),
                            offset=ft.Offset(0, 6)))


def small_gradient_button(label: str, icon: str, on_click) -> ft.Container:
    """A compact version of gradient_button, sized like a regular button (for shortcuts)."""
    return ft.Container(
        ft.Row([ft.Icon(icon, color=ft.Colors.WHITE, size=18),
                ft.Text(label, color=ft.Colors.WHITE, size=14, weight=ft.FontWeight.W_600)],
               spacing=8, tight=True),
        height=40, border_radius=20, ink=True, on_click=on_click, padding=ft.Padding(left=16, right=18, top=0, bottom=0),
        gradient=ft.LinearGradient(colors=GRADIENT, begin=ft.Alignment.CENTER_LEFT, end=ft.Alignment.CENTER_RIGHT))


def show_clear_button(field: ft.TextField, button: ft.IconButton | None = None):
    """A text field's x shows only when there's something to clear. The x is the field's suffix_icon unless
    it's placed separately (`button`)."""
    button = button or field.suffix_icon
    visible = bool((field.value or "").strip())
    if button.visible != visible:
        button.visible = visible
        try:
            (field if button is field.suffix_icon else button).update()
        except Exception:
            pass             # not on screen yet: it shows when drawn


def soft_border(radius: int) -> ft.OutlineInputBorder:
    """Rounded, borderless text field outline (the fill color does the work)."""
    return ft.OutlineInputBorder(border_radius=radius, side=ft.BorderSide(0, ft.Colors.TRANSPARENT))


def snack(page: ft.Page, message: str):
    page.show_dialog(ft.SnackBar(ft.Text(message)))


# Quotes and code blocks get theme colors: Flutter's defaults are a fixed light blue (quotes) and a light code
# background, which put the dark theme's light text on a light box. Models use them to show a corrected step.
QUOTE_BOX = ft.BoxDecoration(bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
                             border=ft.Border(left=ft.BorderSide(3, ft.Colors.PRIMARY)))
CODE_BOX = ft.BoxDecoration(bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH, border_radius=12)


def md_style() -> ft.MarkdownStyleSheet:
    h = lambda size: ft.TextStyle(font_family=HEADING_FONT, size=size, weight=ft.FontWeight.W_700)
    return ft.MarkdownStyleSheet(h1_text_style=h(24), h2_text_style=h(21), h3_text_style=h(18),
                                 h4_text_style=h(16), p_text_style=ft.TextStyle(size=15, height=1.5),
                                 blockquote_decoration=QUOTE_BOX, blockquote_padding=ft.Padding.symmetric(vertical=12, horizontal=14),
                                 block_spacing=10)


def md_code_style() -> ft.MarkdownStyleSheet:
    """Code blocks: in a recipe they hold prose (a corrected step), so normal text on a themed box."""
    return ft.MarkdownStyleSheet(code_text_style=ft.TextStyle(size=15, height=1.5, color=ft.Colors.ON_SURFACE),
                                 codeblock_decoration=CODE_BOX, codeblock_padding=ft.Padding.all(14))


# The code highlighter paints its own background unless `root` sets one; transparent lets CODE_BOX show.
MD_CODE_THEME = ft.MarkdownCustomCodeTheme(root=ft.TextStyle(color=ft.Colors.ON_SURFACE,
                                                             bgcolor=ft.Colors.TRANSPARENT))


class ChefBotApp:
    RETRY_SETTLE = 1.0     # seconds to let lifecycle events queued while frozen arrive (see reply())

    def __init__(self, page: ft.Page):
        self.page = page
        self.prefs = ft.SharedPreferences()
        self.clipboard = ft.Clipboard()
        self.share = ft.Share()
        self.picker = ft.FilePicker()
        self.history = History()
        self.key = ""
        self.model = api.DEFAULT_MODEL
        self.effort = api.DEFAULT_EFFORT
        self.theme = "dark"
        self.email_to = ""
        self.smtp_user = ""
        self.smtp_password = ""
        self.smtp_server = DEFAULT_SMTP
        self.relay_url = ""
        self.relay_secret = ""
        self.dev_mode = False
        self.saved_must_not = ""
        self.user_tools: dict[int, ft.Row] = {}     # edit/delete buttons under user messages
        self.editing_index: int | None = None
        self.urls = ft.UrlLauncher()
        self.prefs_loaded = False
        self.prefs_failed = False      # saved settings couldn't be read: never show or save a blank form over them
        self.cards: dict[int, ft.Container] = {}   # message index -> its card, on the conversation screen
        self.chef: api.ChefBotAPI | None = None
        self.conv: Conversation | None = None
        # Conversations with a reply or picture in progress, by id. A reply keeps going if you leave its chat.
        self.working: dict[str, Conversation] = {}
        self.live_bubbles: dict[str, ft.Container] = {}   # conv id -> the reply card still being written
        self.kept_photos: set[str] = set()     # photo files an in-flight edit may still need (see send_text)
        self.stop_requested = False
        # In another app (phones) or minimized (desktop). Replies keep going thanks to the keep-alive; if one dies
        # anyway while we're away, it starts again when we're back (see reply()).
        self.away = False
        self.times_away = 0
        self.back = asyncio.Event()
        self.back.set()
        android_app = page.platform == ft.PagePlatform.ANDROID and not page.web
        self.keepalive = KeepAlive.for_android() if android_app else KeepAlive()
        self.cuisine = prompts.NO_CUISINE
        self.recent_cuisines: list[str] = []
        self.audience = prompts.DEFAULT_AUDIENCE
        self.on_map = False
        self.map_stack: list[str] = ["world"]
        self.map_highlight_id: str | None = None
        self.map_scale = 1.0
        self._map_layer: ft.Container | None = None
        self._map_pending: tuple | None = None
        self.globe_lon = GLOBE_INITIAL_LON
        self.globe_lat = GLOBE_INITIAL_LAT
        self.globe_zoom = 1.0
        self.globe_touched = False
        self._globe_flying = False
        self._globe_pre_fly_zoom = 1.0
        self._globe_motion_gen = 0
        self._globe_pinch_base_zoom = 1.0
        self._globe_last_focal: tuple[float, float] | None = None
        self._globe_vel_lon = 0.0
        self._globe_vel_lat = 0.0
        self._globe_last_drag_t = 0.0
        self._globe_last_draw_t = 0.0
        self._globe_draw_cost = 0.0
        self._globe_view_size: tuple[float, float] = (360.0, 520.0)
        self._globe_canvas: cv.Canvas | None = None
        self._globe_stack: ft.Stack | None = None
        self._globe_labels: dict[str, ft.Container] = {}
        self.padded: list[ft.Control] = []     # containers whose side padding follows the window width
        self.root = ft.Container(expand=True)
        self._build_home_controls()

    # ------------------------------------------------------------ startup, layout, settings

    async def start(self):
        p = self.page
        p.title = "ChefBot"
        p.fonts = FONTS
        p.theme = ft.Theme(color_scheme_seed=SEED, font_family=BODY_FONT, scaffold_bgcolor=BG_LIGHT)
        p.dark_theme = ft.Theme(color_scheme_seed=SEED, font_family=BODY_FONT, scaffold_bgcolor=BG_DARK)
        p.padding = 0
        p.on_resize = self._on_resize
        p.theme_mode = THEMES[self.theme]
        p.add(ft.SafeArea(self.root, expand=True))
        p.views[0].on_confirm_pop = self._on_back
        p.on_app_lifecycle_state_change = self._on_lifecycle
        self.key = os.environ.get("OPENROUTER_API_KEY", "").strip()     # development shortcut
        self.chef = api.ChefBotAPI(self.key) if self.key else None
        self.show_home()      # draw first; saved settings arrive a moment later

        prefs = await self._load_prefs()
        if prefs is None:
            self.prefs_failed = True
            snack(self.page, PREFS_FAILED)
            return
        self.prefs_loaded = True
        self.key = (prefs.get(PREF_KEY) or os.environ.get("OPENROUTER_API_KEY", "")).strip()
        model, effort, theme = prefs.get(PREF_MODEL), prefs.get(PREF_EFFORT), prefs.get(PREF_THEME)
        self.model = model if model in api.MODELS else api.DEFAULT_MODEL
        self.effort = effort if effort in api.EFFORTS else api.DEFAULT_EFFORT
        self.theme = theme if theme in THEMES else "dark"
        self.email_to = prefs.get(PREF_EMAIL_TO) or ""
        self.smtp_user = prefs.get(PREF_SMTP_USER) or ""
        self.smtp_password = prefs.get(PREF_SMTP_PASSWORD) or ""
        self.smtp_server = prefs.get(PREF_SMTP_SERVER) or DEFAULT_SMTP
        self.relay_url = prefs.get(PREF_RELAY_URL) or ""
        self.relay_secret = prefs.get(PREF_RELAY_SECRET) or ""
        self.dev_mode = prefs.get(PREF_DEV_MODE) == "on"
        self.saved_must_not = prefs.get(PREF_MUST_NOT) or ""
        if not (self.must_not.value or "").strip():     # don't overwrite anything typed while settings loaded
            self.must_not.value = self.saved_must_not
            show_clear_button(self.must_not)
        raw_recent = prefs.get(PREF_RECENT_CUISINES) or ""
        if raw_recent:
            try:
                loaded_recent = json.loads(raw_recent)
                if isinstance(loaded_recent, list):
                    valid = [x for x in loaded_recent if isinstance(x, str) and cuisines.resolve(x)]
                    for cid in reversed(self.recent_cuisines):
                        valid = [cid] + [x for x in valid if x != cid]
                    self.recent_cuisines = valid[:MAX_RECENT_CUISINES]
                    self._rebuild_cuisine_chips()
            except Exception:
                pass
        p.theme_mode = THEMES[self.theme]
        self.chef = api.ChefBotAPI(self.key) if self.key else None
        p.update()
        if not self.key:
            self.open_settings(first_run=True)

    async def _load_prefs(self) -> dict | None:
        """Read saved settings, all at once. On a slow first load the storage service can take a few seconds to come
        up, so retry a little. None means they couldn't be read (not the same as "nothing saved")."""
        for attempt in range(4):
            try:
                values = await asyncio.gather(*(self.prefs.get(k) for k in ALL_PREFS))
                return dict(zip(ALL_PREFS, values))
            except RuntimeError:
                await asyncio.sleep(0.5 * (attempt + 1))
        return None

    def _side(self) -> float:
        return max(14.0, ((self.page.width or 0) - MAX_WIDTH) / 2)

    def _pad(self, control: ft.Control, top: float = 0, bottom: float = 0, extra: float = 0) -> ft.Control:
        """Give a container/list the centered-column side padding, and keep it right on resize."""
        control.data = (top, bottom, extra)
        self.padded.append(control)
        self._apply_pad(control)
        return control

    def _apply_pad(self, control: ft.Control):
        top, bottom, extra = control.data
        s = self._side() + extra
        control.padding = ft.Padding(left=s, right=s, top=top, bottom=bottom)

    def _on_resize(self, e):
        for c in self.padded:
            self._apply_pad(c)
        if self.on_map:
            self._render_map_level()
        self.page.update()

    def open_settings(self, e=None, first_run: bool = False):
        # Until the saved settings are read, the form would be blank, and saving it would wipe them.
        if self.prefs_failed:
            snack(self.page, PREFS_FAILED)
            return
        if not self.prefs_loaded:
            snack(self.page, "Still loading your settings. Try again in a second.")
            return
        key_field = ft.TextField(label="OpenRouter API key", value=self.key, password=True,
                                 can_reveal_password=True, hint_text="sk-or-v1-...")
        model_dd = ft.Dropdown(label="Recipe model", value=self.model, expand=True,
                               options=[ft.DropdownOption(key=k, text=m.label) for k, m in api.MODELS.items()])
        effort_dd = ft.Dropdown(label="Thinking", value=self.effort, expand=True,
                                options=[ft.DropdownOption(key=k, text=EFFORT_LABELS[k]) for k in api.EFFORTS])
        # Some models run at one thinking level only (Kimi K3.1 Pro: medium). Show that level, greyed out, but keep
        # the choice made for the other models, so switching back restores it.
        chosen_effort = {"value": self.effort}

        def show_effort_for_model():
            allowed = api.MODELS.get(model_dd.value or api.DEFAULT_MODEL, api.MODELS[api.DEFAULT_MODEL]).efforts
            locked = len(allowed) == 1
            effort_dd.disabled = locked
            effort_dd.value = allowed[0] if locked else api.effort_for(model_dd.value, chosen_effort["value"])
            effort_dd.helper_text = f"This model only runs at {EFFORT_LABELS[allowed[0]]}." if locked else None

        def on_model(_):
            show_effort_for_model()
            effort_dd.update()

        def on_effort(_):
            if not effort_dd.disabled and effort_dd.value:
                chosen_effort["value"] = effort_dd.value

        model_dd.on_select = on_model
        effort_dd.on_select = on_effort
        show_effort_for_model()
        # On a phone the dialog is too narrow for icon + label in three segments ("Dar k"), so labels
        # only, and the fill alone marks the selected one.
        theme_icons = (self.page.width or 0) >= 480
        theme_seg = ft.SegmentedButton(
            selected=[self.theme], allow_multiple_selection=False, show_selected_icon=theme_icons,
            segments=[ft.Segment(value=v, label=lab, icon=ic if theme_icons else None)
                      for v, lab, ic in (("dark", "Dark", ft.Icons.DARK_MODE_OUTLINED),
                                         ("light", "Light", ft.Icons.LIGHT_MODE_OUTLINED),
                                         ("system", "System", ft.Icons.BRIGHTNESS_AUTO_OUTLINED))])
        to_field = ft.TextField(label="Send recipes to", value=self.email_to, hint_text="you@example.com",
                                keyboard_type=ft.KeyboardType.EMAIL, prefix_icon=ft.Icons.EMAIL_OUTLINED)
        user_field = ft.TextField(label="Send from (your Gmail address)", value=self.smtp_user,
                                  keyboard_type=ft.KeyboardType.EMAIL)
        pass_field = ft.TextField(label="Gmail app password", value=self.smtp_password, password=True,
                                  can_reveal_password=True, hint_text="16 letters, from Google")
        server_field = ft.TextField(label="Mail server", value=self.smtp_server, dense=True,
                                    hint_text=DEFAULT_SMTP)
        relay_url_field = ft.TextField(label="Relay web address", value=self.relay_url,
                                       hint_text="https://script.google.com/macros/s/.../exec")
        relay_secret_field = ft.TextField(label="Relay secret", value=self.relay_secret, password=True,
                                          can_reveal_password=True, expand=True)

        async def generate_secret(_):
            import secrets
            relay_secret_field.value = secrets.token_urlsafe(24)
            relay_secret_field.update()
            await self.clipboard.set(relay_secret_field.value)
            snack(self.page, "New secret copied. Paste it into the relay's RELAY_SECRET script property.")

        # Developer mode: tapping the dialog's title 7 times shows (or hides again) the email-sending settings.
        # Everyday users email through their own mail app and never need them.
        dev_section = ft.Column(tight=True, spacing=16, visible=self.dev_mode)
        taps = [0]

        async def tap_title(_):
            taps[0] += 1
            if taps[0] < DEV_MODE_TAPS:
                return
            taps[0] = 0
            self.dev_mode = not self.dev_mode
            dev_section.visible = self.dev_mode
            dev_section.update()
            try:
                await self.prefs.set(PREF_DEV_MODE, "on" if self.dev_mode else "")
            except Exception:
                pass                 # it still applies until ChefBot closes
            snack(self.page, "Developer mode on: email-sending settings are below." if self.dev_mode else
                  "Developer mode off.")

        save_button = ft.FilledButton("Save")
        save_problem = ft.Text("", color=ft.Colors.ERROR, size=13, visible=False, selectable=True)

        async def save(_):
            values = {PREF_KEY: (key_field.value or "").strip(),
                      PREF_MODEL: model_dd.value or api.DEFAULT_MODEL, PREF_EFFORT: chosen_effort["value"] or api.DEFAULT_EFFORT,
                      PREF_THEME: (list(theme_seg.selected) or ["dark"])[0],
                      PREF_EMAIL_TO: (to_field.value or "").strip(), PREF_SMTP_USER: (user_field.value or "").strip(),
                      PREF_SMTP_PASSWORD: (pass_field.value or "").replace(" ", ""),
                      PREF_SMTP_SERVER: (server_field.value or "").strip() or DEFAULT_SMTP,
                      PREF_RELAY_URL: (relay_url_field.value or "").strip(),
                      PREF_RELAY_SECRET: (relay_secret_field.value or "").strip()}
            save_button.disabled, save_problem.visible = True, False
            save_button.update()
            save_problem.update()
            try:
                await asyncio.gather(*(self.prefs.set(k, v) for k, v in values.items()))
            except Exception as err:
                save_button.disabled = False
                save_problem.value = (f"Couldn't save ({type(err).__name__}). ChefBot lost touch with its settings "
                                      "storage. Close ChefBot and open it again, then try once more.")
                save_problem.visible = True
                save_button.update()
                save_problem.update()
                return
            self.key = values[PREF_KEY]
            self.model, self.effort, self.theme = values[PREF_MODEL], values[PREF_EFFORT], values[PREF_THEME]
            self.email_to, self.smtp_user = values[PREF_EMAIL_TO], values[PREF_SMTP_USER]
            self.smtp_password, self.smtp_server = values[PREF_SMTP_PASSWORD], values[PREF_SMTP_SERVER]
            self.relay_url, self.relay_secret = values[PREF_RELAY_URL], values[PREF_RELAY_SECRET]
            self.chef = api.ChefBotAPI(self.key) if self.key else None
            self.page.theme_mode = THEMES[self.theme]
            self.page.pop_dialog()
            self.page.update()
            snack(self.page, "Settings saved." if self.key else "No API key yet: ChefBot can't cook without one.")

        save_button.on_click = save
        intro = ("Paste an OpenRouter API key to get started (openrouter.ai/keys). It's stored only on this "
                 "device.") if first_run else "Your key is stored only on this device."
        dev_section.controls = [
            ft.Divider(),
            heading("Email sending (developer)", 18),
            ft.Text("Normally the Email button hands the recipe and its PDF to your own mail app. With a relay or "
                    "a Gmail app password set here, ChefBot sends the email itself instead. Everything here stays "
                    "on this device. Setup: docs/EMAIL.md.",
                    size=12.5, color=ft.Colors.ON_SURFACE_VARIANT),
            to_field,
            ft.Text("ChefBot mail relay", weight=ft.FontWeight.W_600),
            relay_url_field,
            ft.Row([relay_secret_field, ft.TextButton("Generate", icon=ft.Icons.AUTORENEW,
                                                      on_click=generate_secret)]),
            ft.Text("Or: a Gmail app password", weight=ft.FontWeight.W_600),
            ft.Text("Made at myaccount.google.com/apppasswords on the same account as 'Send from'. Some "
                    "networks block this kind of sending.", size=12, color=ft.Colors.ON_SURFACE_VARIANT),
            user_field, pass_field, server_field,
        ]
        self.page.show_dialog(ft.AlertDialog(
            modal=first_run, scrollable=True,
            title=ft.GestureDetector(content=heading("Settings", 22), on_tap=tap_title),
            content=ft.Column(tight=True, spacing=16, width=440, controls=[
                ft.Text(intro, size=13), key_field, ft.Row([model_dd]), ft.Row([effort_dd]),
                ft.Text("Appearance", size=13, color=ft.Colors.ON_SURFACE_VARIANT), theme_seg,
                ft.Text("Ingredient photos are read by GLM 5.3 Flash; dish pictures come from Gemini 3.1 Flash Lite "
                        "Image.", size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                dev_section, save_problem,
            ]),
            actions=[ft.TextButton("Cancel", on_click=lambda _: self.page.pop_dialog()), save_button],
        ))

    async def _on_lifecycle(self, e: ft.AppLifecycleStateChangeEvent):     # async: runs on the event loop
        if e.state in (ft.AppLifecycleState.HIDE, ft.AppLifecycleState.PAUSE):
            if not self.away:
                self.away = True
                self.times_away += 1
                self.back.clear()
        elif e.state in (ft.AppLifecycleState.SHOW, ft.AppLifecycleState.RESUME):
            if self.away:
                self.away = False
                self.back.set()
                self.keepalive.clear()

    def _run(self, fn, *args):
        """Start a background task; if it fails, say so instead of failing silently."""
        async def guarded():
            try:
                await fn(*args)
            except Exception as err:
                import traceback
                traceback.print_exc()
                snack(self.page, f"Something went wrong: {type(err).__name__}: {err}")
        self.page.run_task(guarded)

    def _need_key(self) -> bool:
        if self.chef:
            return False
        if self.prefs_failed:
            snack(self.page, PREFS_FAILED)
            return True
        if not self.prefs_loaded:
            snack(self.page, "Still starting up. Try again in a second.")
            return True
        self.open_settings(first_run=True)
        return True

    # ------------------------------------------------------------ home screen

    def _build_home_controls(self):
        self.ingredients_clear = ft.IconButton(ft.Icons.CLOSE, tooltip="Clear", icon_size=18, visible=False,
                                               on_click=self._clear_ingredients)
        # No `capitalization=` on text fields: Flet implements it by rewriting the text after each keystroke,
        # which resets the Android keyboard (voice typing stops, caps lock turns off). See test_text_fields.py.
        self.ingredients = ft.TextField(
            on_change=lambda e: show_clear_button(self.ingredients, self.ingredients_clear),
            hint_text="Potatoes, carrots, tomatoes...", multiline=True, min_lines=4, max_lines=8,
            content_padding=ft.Padding(left=16, right=44, top=16, bottom=16),     # room for the x
            filled=True, border=soft_border(16), text_size=16)
        # The x sits in the bottom-right corner of this tall box (a suffix icon would center it vertically).
        self.ingredients_box = ft.Stack([self.ingredients,
                                         ft.Container(self.ingredients_clear, right=2, bottom=2)])
        self.photo_btn = ft.FilledTonalButton(PHOTO_LABEL, icon=ft.Icons.PHOTO_CAMERA_OUTLINED,
                                              on_click=self.read_photo)
        self.cuisine_chips: dict[str, ft.Chip] = {}
        self.cuisine_chips_row = ft.Row(wrap=True, spacing=8, run_spacing=8)
        self._rebuild_cuisine_chips()
        self.audience_tiles: dict[str, ft.Container] = {}
        for label, (icon, short) in AUDIENCE_CARDS.items():
            self.audience_tiles[label] = ft.Container(
                ft.Column([ft.Icon(icon, size=28),
                           ft.Text(short, size=12.5, weight=ft.FontWeight.W_600, text_align=ft.TextAlign.CENTER)],
                          horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6, tight=True),
                width=108, height=96, border_radius=18, padding=8, ink=True,
                alignment=ft.Alignment.CENTER, on_click=lambda e, lab=label: self._pick_audience(lab))
        self._style_audience()
        self.dessert = ft.Chip(label="Dessert instead", leading=ft.Icon(ft.Icons.CAKE_OUTLINED, size=18),
                               show_checkmark=True, on_select=lambda e: None)   # a handler makes it tappable
        self.diet_chips = {r: ft.Chip(label=r, show_checkmark=True, on_select=self._on_diet_select)
                           for r in prompts.RESTRICTIONS}
        self.must_not_clear = ft.IconButton(ft.Icons.CLOSE, tooltip="Clear (and forget)", icon_size=18,
                                            visible=False, on_click=lambda e: self._run(self._clear_must_not))
        self.must_not = ft.TextField(hint_text="Never use... (e.g. peanuts, cilantro)", filled=True,
                                     border=soft_border(16), prefix_icon=ft.Icons.BLOCK,
                                     suffix_icon=self.must_not_clear,
                                     helper="Remembered for next time. Clear it to forget.",
                                     on_change=lambda e: show_clear_button(self.must_not),
                                     on_blur=lambda e: self._run(self._remember_must_not))
        self.recent = ft.Column(spacing=10, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)

    def _rebuild_cuisine_chips(self):
        chip_ids = [prompts.NO_CUISINE] + list(self.recent_cuisines[:MAX_RECENT_CUISINES])
        if self.cuisine != prompts.NO_CUISINE and self.cuisine not in chip_ids and cuisines.resolve(self.cuisine):
            chip_ids.insert(1, self.cuisine)
            chip_ids = chip_ids[: MAX_RECENT_CUISINES + 1]
        self.cuisine_chips = {}
        for cid in chip_ids:
            short = "Anything" if cid == prompts.NO_CUISINE else cuisines.chip_label(cid)
            chip = ft.Chip(
                label=short,
                selected=cid == self.cuisine,
                show_checkmark=False,
                on_select=lambda e, c=cid: self._pick_cuisine(c),
                delete_icon=ft.Icon(ft.Icons.INFO_OUTLINE, size=18),
                delete_icon_tooltip=f"About {short} cooking",
            )
            self._show_cuisine_info(chip, cid)
            self.cuisine_chips[cid] = chip
        self.cuisine_chips_row.controls = list(self.cuisine_chips.values())

    async def _remember_recent_cuisines(self):
        if not self.prefs_loaded:
            return
        try:
            await self.prefs.set(PREF_RECENT_CUISINES, json.dumps(self.recent_cuisines))
        except Exception:
            log.warning("Couldn't save recent cuisines", exc_info=True)

    def _pick_cuisine(self, node_id: str):
        resolved = None if node_id == prompts.NO_CUISINE else cuisines.resolve(node_id)
        if resolved:
            cid = resolved["id"]
            self.cuisine = cid
            self.recent_cuisines = [cid] + [x for x in self.recent_cuisines if x != cid]
            self.recent_cuisines = self.recent_cuisines[:MAX_RECENT_CUISINES]
            if self.prefs_loaded:
                self._run(self._remember_recent_cuisines)
        else:
            self.cuisine = prompts.NO_CUISINE
        self._rebuild_cuisine_chips()
        try:
            self.cuisine_chips_row.update()
        except Exception:
            pass

    def _show_cuisine_info(self, chip: ft.Chip, node_id: str):
        """Only the picked cuisine shows the info icon (Flutter shows a chip's trailing icon only with a handler)."""
        node = None if node_id == prompts.NO_CUISINE else cuisines.resolve(node_id)
        has_info = node_id == self.cuisine and node is not None and bool(node.get("about"))
        chip.on_delete = (lambda e, cid=node_id: self._cuisine_info(cid)) if has_info else None

    def _poly_paths(
        self,
        polygons: list[list[list[float]]],
        fill_color: str,
        stroke_color: str,
        stroke_width: float = 1.2,
        tx=lambda x: x,
        ty=lambda y: y,
    ) -> list[cv.Shape]:
        shapes: list[cv.Shape] = []
        fill_paint = ft.Paint(color=fill_color, style=ft.PaintingStyle.FILL)
        stroke_paint = ft.Paint(color=stroke_color, stroke_width=stroke_width, style=ft.PaintingStyle.STROKE)
        for poly in polygons:
            if len(poly) < 3:
                continue
            elems: list[cv.Path.PathElement] = [cv.Path.MoveTo(tx(poly[0][0]), ty(poly[0][1]))]
            for pt in poly[1:]:
                elems.append(cv.Path.LineTo(tx(pt[0]), ty(pt[1])))
            elems.append(cv.Path.Close())
            shapes.append(cv.Path(elements=elems, paint=fill_paint))
            shapes.append(cv.Path(elements=elems, paint=stroke_paint))
        return shapes

    def _cuisine_mini_map(self, node_id: str) -> ft.Control | None:
        """Small region map at the top of the cuisine info sheet with that cuisine's region highlighted."""
        found = maps.region_for_cuisine(node_id)
        if not found:
            return None
        lvl, highlight_ids = found
        highlight_set = set(highlight_ids)
        all_polys = list(lvl["background"]) + [p for r in lvl["regions"] for p in r["polygons"]]
        if not all_polys:
            return None
        xs = [pt[0] for poly in all_polys for pt in poly]
        ys = [pt[1] for poly in all_polys for pt in poly]
        x0, x1 = min(xs), max(xs)
        y0, y1 = min(ys), max(ys)
        span_w = max(1.0, x1 - x0)
        span_h = max(1.0, y1 - y0)

        mini_w, mini_h = 260.0, 156.0
        pad = 12.0
        scale = min((mini_w - 2 * pad) / span_w, (mini_h - 2 * pad) / span_h)
        off_x = (mini_w - span_w * scale) * 0.5
        off_y = (mini_h - span_h * scale) * 0.5
        tx = lambda x: off_x + (x - x0) * scale
        ty = lambda y: off_y + (y - y0) * scale

        shapes: list[cv.Shape] = []
        shapes.extend(self._poly_paths(
            lvl["background"],
            fill_color=ft.Colors.with_opacity(0.45, ft.Colors.SURFACE_CONTAINER_HIGH),
            stroke_color=ft.Colors.with_opacity(0.45, ft.Colors.OUTLINE_VARIANT),
            stroke_width=0.8,
            tx=tx,
            ty=ty,
        ))
        for bx0, by0, bx1, by1 in lvl.get("inset_boxes", []):
            rx, ry = tx(bx0), ty(by0)
            rw, rh = (bx1 - bx0) * scale, (by1 - by0) * scale
            shapes.append(cv.Rect(
                rx, ry, width=rw, height=rh, border_radius=6,
                paint=ft.Paint(
                    color=ft.Colors.with_opacity(0.45, ft.Colors.OUTLINE_VARIANT),
                    stroke_width=0.9,
                    style=ft.PaintingStyle.STROKE,
                ),
            ))
        for reg in lvl["regions"]:
            if reg["id"] in highlight_set:
                continue
            shapes.extend(self._poly_paths(
                reg["polygons"],
                fill_color=ft.Colors.SURFACE_CONTAINER_HIGH,
                stroke_color=ft.Colors.OUTLINE_VARIANT,
                stroke_width=0.9,
                tx=tx,
                ty=ty,
            ))
        for reg in lvl["regions"]:
            if reg["id"] not in highlight_set:
                continue
            c_fill, c_stroke = MAP_PALETTE.get(reg.get("color", "coral"), (ft.Colors.PRIMARY, ft.Colors.ON_PRIMARY_CONTAINER))
            shapes.extend(self._poly_paths(
                reg["polygons"],
                fill_color=c_fill,
                stroke_color=c_stroke,
                stroke_width=1.6,
                tx=tx,
                ty=ty,
            ))
            bx0, by0, bx1, by1 = reg["bbox"]
            if (bx1 - bx0) * scale < 14.0 or (by1 - by0) * scale < 14.0:
                cx, cy = tx(reg["center"][0]), ty(reg["center"][1])
                shapes.append(cv.Circle(
                    cx, cy, radius=5.0,
                    paint=ft.Paint(color=c_fill, style=ft.PaintingStyle.FILL),
                ))
                shapes.append(cv.Circle(
                    cx, cy, radius=5.0,
                    paint=ft.Paint(color=c_stroke, stroke_width=1.5, style=ft.PaintingStyle.STROKE),
                ))

        return ft.Container(
            cv.Canvas(shapes=shapes, width=mini_w, height=mini_h),
            width=mini_w,
            height=mini_h,
            bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
            border_radius=16,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.2, ft.Colors.OUTLINE)),
            alignment=ft.Alignment.CENTER,
        )

    def _cuisine_info_lines(self, node: dict) -> list[ft.Control]:
        """Build the info controls for a cuisine node, starting with the small region map."""
        lines: list[ft.Control] = []
        mini_map = self._cuisine_mini_map(node["id"])
        if mini_map is not None:
            lines.append(ft.Row([mini_map], alignment=ft.MainAxisAlignment.CENTER))
        if node.get("subtitle"):
            lines.append(ft.Text(node["subtitle"], size=13.5, italic=True, color=ft.Colors.ON_SURFACE_VARIANT))
        if node.get("about"):
            lines.append(ft.Text(node["about"], size=15))

        def section(title: str, items: list[str], sep: str = ", "):
            if not items:
                return
            text = sep.join(items)
            lines.append(ft.Text(title, size=13, weight=ft.FontWeight.W_700, color=ft.Colors.PRIMARY))
            lines.append(ft.Text(text[0].upper() + text[1:] + ("" if text.endswith(".") else "."),
                                 size=14, color=ft.Colors.ON_SURFACE_VARIANT))

        section("Classic flavors", node.get("flavors", []))
        section("For desserts", node.get("sweet_only", []))
        section("Signature ingredients (used if you have them)", node.get("signature_ingredients", []), sep="; ")
        section("If you're missing one", node.get("substitutes", []), sep="; ")
        return lines

    def _cuisine_info(self, node_id: str):
        """A sheet about the cuisine: where it's from, its style, and the flavors ChefBot draws on."""
        node = cuisines.resolve(node_id) or cuisines.get(node_id)
        if not node:
            return
        lines = self._cuisine_info_lines(node)
        self.page.show_dialog(ft.BottomSheet(
            show_drag_handle=True, scrollable=True,
            content=ft.SafeArea(
                ft.Container(
                    ft.Column([heading(cuisines.chip_label(node["id"]), 22), *lines],
                              spacing=10, tight=True, scroll=ft.ScrollMode.AUTO),
                    padding=ft.Padding(left=24, right=24, top=8, bottom=80), width=MAX_WIDTH,
                ),
            ),
        ))

    def open_cuisine_picker(self, e=None):
        """Full-height bottom sheet that drills down Continent -> Country / Cuisine -> Regional Cuisine."""
        body = ft.Column(spacing=10, tight=True, scroll=ft.ScrollMode.AUTO,
                         horizontal_alignment=ft.CrossAxisAlignment.STRETCH)

        def pick_leaf(leaf_id: str):
            self._pick_cuisine(leaf_id)
            self.page.pop_dialog()

        def render_info(node_id: str, return_branch_id: str | None):
            node = cuisines.resolve(node_id) or cuisines.get(node_id)
            if not node:
                return
            leaf_id = node["id"]
            label = cuisines.chip_label(leaf_id)
            body.controls = [
                ft.Row([
                    ft.IconButton(ft.Icons.ARROW_BACK, tooltip="Back",
                                  on_click=lambda _, bid=return_branch_id: switch_to(bid)),
                    heading(label, 21),
                ], spacing=4, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                *self._cuisine_info_lines(node),
                ft.Container(
                    gradient_button(f"Pick {label}", ft.Icons.RESTAURANT_MENU,
                                    lambda _, lid=leaf_id: pick_leaf(lid)),
                    padding=ft.Padding(left=0, right=0, top=8, bottom=0),
                ),
            ]
            try:
                body.update()
            except Exception:
                pass

        def render_level(branch_id: str | None = None):
            controls: list[ft.Control] = []
            if branch_id is None:
                controls.append(heading("Browse cuisines", 22))
                controls.append(ft.Text("Pick a region of the world to explore.", size=13.5,
                                        color=ft.Colors.ON_SURFACE_VARIANT))
                for cont in cuisines.continents():
                    icon = CONTINENT_ICONS.get(cont["id"], ft.Icons.PUBLIC)
                    controls.append(ft.Container(
                        ft.Row([
                            ft.Icon(icon, size=28, color=ft.Colors.PRIMARY),
                            ft.Column([
                                ft.Text(cont["label"], size=16, weight=ft.FontWeight.W_700, font_family=HEADING_FONT),
                                ft.Text(cont["subtitle"], size=13, color=ft.Colors.ON_SURFACE_VARIANT),
                            ], spacing=2, expand=True, tight=True),
                            ft.Icon(ft.Icons.CHEVRON_RIGHT, color=ft.Colors.ON_SURFACE_VARIANT),
                        ], spacing=14),
                        padding=ft.Padding(left=16, right=12, top=14, bottom=14),
                        border_radius=18, ink=True, bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
                        on_click=lambda _, cid=cont["id"]: switch_to(cid),
                    ))
            else:
                crumbs = cuisines.path(branch_id)
                parent_id = None
                if len(crumbs) > 1:
                    for cont in cuisines.continents():
                        if any(c["id"] == branch_id for c in cuisines.children(cont["id"])):
                            parent_id = cont["id"]
                            break
                controls.append(ft.Row([
                    ft.IconButton(ft.Icons.ARROW_BACK, tooltip="Back",
                                  on_click=lambda _, pid=parent_id: switch_to(pid)),
                    heading(" > ".join(crumbs), 19),
                ], spacing=4, vertical_alignment=ft.CrossAxisAlignment.CENTER))
                for child in cuisines.children(branch_id):
                    is_country = child["kind"] == "country"
                    info_node = cuisines.resolve(child["id"])
                    has_info = info_node is not None and bool(info_node.get("about"))
                    trailing: list[ft.Control] = []
                    if has_info:
                        trailing.append(ft.IconButton(
                            ft.Icons.INFO_OUTLINE,
                            icon_size=20,
                            icon_color=ft.Colors.PRIMARY,
                            tooltip=f"About {child['label']}",
                            on_click=lambda _, cid=child["id"], bid=branch_id: render_info(cid, bid),
                        ))
                    if is_country:
                        trailing.append(ft.Icon(ft.Icons.CHEVRON_RIGHT, color=ft.Colors.ON_SURFACE_VARIANT))
                    controls.append(ft.Container(
                        ft.Row([
                            ft.Column([
                                ft.Text(child["label"], size=15.5, weight=ft.FontWeight.W_600,
                                        font_family=HEADING_FONT),
                                ft.Text(child["subtitle"], size=12.5, color=ft.Colors.ON_SURFACE_VARIANT),
                            ], spacing=2, expand=True, tight=True),
                            *trailing,
                        ], spacing=6),
                        padding=ft.Padding(left=16, right=8, top=10, bottom=10),
                        border_radius=16, ink=True, bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
                        on_click=(
                            (lambda _, cid=child["id"]: switch_to(cid))
                            if is_country
                            else (lambda _, cid=child["id"]: pick_leaf(cid))
                        ),
                    ))
            body.controls = controls

        def switch_to(branch_id: str | None):
            render_level(branch_id)
            try:
                body.update()
            except Exception:
                pass

        render_level(None)
        self.page.show_dialog(ft.BottomSheet(
            show_drag_handle=True, scrollable=True,
            content=ft.SafeArea(
                ft.Container(body, padding=ft.Padding(left=20, right=20, top=8, bottom=80), width=MAX_WIDTH),
            ),
        ))

    def open_map_browser(self, e=None):
        """Full-screen interactive map browser replacing the screen until Back is pressed."""
        self.on_map = True
        self.map_stack = ["world"]
        self.map_highlight_id = None
        self.globe_lon = GLOBE_INITIAL_LON
        self.globe_lat = GLOBE_INITIAL_LAT
        self.globe_zoom = 1.0
        self.globe_touched = False
        self._globe_flying = False
        self._globe_pre_fly_zoom = 1.0
        self._globe_motion_gen += 1
        self.page.views[0].can_pop = False
        self.page.appbar = None
        self._map_layer = None
        self._render_map_level()
        self.page.update()
        if GLOBE_IDLE_SPIN_DPS > 0.0 and isinstance(self.page, ft.Page):
            self._run(self._globe_idle_loop)

    def _map_back(self, e=None):
        self._globe_motion_gen += 1
        self._globe_flying = False
        self.map_highlight_id = None
        if len(self.map_stack) > 1:
            child = self.map_stack.pop()
            if self.map_stack[-1] == "world":
                self.globe_zoom = self._globe_pre_fly_zoom
                self.globe_touched = True
            self._render_map_level(transition=("out", self._map_focus_alignment(self.map_stack[-1], child)))
            self.page.update()
            if self._map_pending and isinstance(self.page, ft.Page):
                self._run(self._play_map_transition)
        else:
            self.on_map = False
            self.show_home()

    def _on_map_canvas_tap(self, e: ft.TapEvent):
        if not self.on_map or not e.local_position:
            return
        level_id = self.map_stack[-1]
        s = self.map_scale or 1.0
        x = e.local_position.x / s
        y = e.local_position.y / s
        hit = maps.hit_test(level_id, x, y, tolerance=6.0)
        if hit:
            self._run(self._trigger_map_region, hit)

    def _globe_geometry(self) -> tuple[float, float, float]:
        view_w, view_h = self._globe_view_size
        cx = view_w * 0.5
        cy = view_h * 0.5
        base_r = min(view_w, view_h) * 0.43
        return cx, cy, base_r * self.globe_zoom

    def _combined_poly_paths(
        self,
        polygons: list[list[tuple[float, float]]],
        fill_color: str,
        stroke_color: str,
        stroke_width: float = 1.2,
        outline: bool = True,
        step: int = 1,
    ) -> list[cv.Shape]:
        # Every path point is a Flet control that gets diffed and sent to the screen each frame, which is
        # what makes the spinning globe slow on a phone. While it moves, callers pass step=2 (every other
        # point) and outline=False (the outline path would send every point a second time).
        elems: list[cv.Path.PathElement] = []
        for poly in polygons:
            if len(poly) < 3:
                continue
            if step > 1 and len(poly) > 8 * step:
                poly = poly[::step]
            elems.append(cv.Path.MoveTo(round(poly[0][0], 1), round(poly[0][1], 1)))
            for pt in poly[1:]:
                elems.append(cv.Path.LineTo(round(pt[0], 1), round(pt[1], 1)))
            elems.append(cv.Path.Close())
        if not elems:
            return []
        shapes: list[cv.Shape] = [
            cv.Path(elements=elems, paint=ft.Paint(color=fill_color, style=ft.PaintingStyle.FILL)),
        ]
        if outline:
            shapes.append(cv.Path(
                elements=elems,
                paint=ft.Paint(color=stroke_color, stroke_width=stroke_width, style=ft.PaintingStyle.STROKE),
            ))
        return shapes

    def _build_globe_shapes(self, fast: bool = False) -> list[cv.Shape]:
        cx, cy, radius = self._globe_geometry()
        shapes: list[cv.Shape] = [
            # Subtle atmospheric halo around the sphere
            cv.Circle(
                cx, cy, radius + 3.0,
                paint=ft.Paint(color=ft.Colors.with_opacity(0.10, ft.Colors.BLUE_200), style=ft.PaintingStyle.FILL),
            ),
            # Shaded dark ocean disc
            cv.Circle(
                cx, cy, radius,
                paint=ft.Paint(
                    style=ft.PaintingStyle.FILL,
                    gradient=ft.PaintRadialGradient(
                        center=(cx - radius * 0.28, cy - radius * 0.28),
                        radius=radius * 1.18,
                        colors=[ft.Colors.BLUE_GREY_800, ft.Colors.BLUE_GREY_900, ft.Colors.BLACK],
                        color_stops=[0.0, 0.65, 1.0],
                    ),
                ),
            ),
        ]

        # Faint spherical lat/lon graticule
        grat_elems: list[cv.Path.PathElement] = []
        for seg in [] if fast else maps.project_globe_graticule(self.globe_lon, self.globe_lat, cx, cy, radius):
            grat_elems.append(cv.Path.MoveTo(seg[0][0], seg[0][1]))
            for pt in seg[1:]:
                grat_elems.append(cv.Path.LineTo(pt[0], pt[1]))
        if grat_elems:
            shapes.append(cv.Path(
                elements=grat_elems,
                paint=ft.Paint(color=ft.Colors.with_opacity(0.10, ft.Colors.WHITE), stroke_width=0.9, style=ft.PaintingStyle.STROKE),
            ))

        bg_polys, reg_polys = maps.project_globe_polygons(
            self.globe_lon, self.globe_lat, cx, cy, radius, fast=fast,
        )
        shapes.extend(self._combined_poly_paths(
            bg_polys,
            fill_color=ft.Colors.with_opacity(0.38, ft.Colors.BLUE_GREY_500),
            stroke_color=ft.Colors.with_opacity(0.42, ft.Colors.BLUE_GREY_300),
            stroke_width=0.9,
            outline=not fast,
            step=2 if fast else 1,
        ))

        for reg in maps.get_globe()["regions"]:
            rid = reg["id"]
            polys = reg_polys.get(rid)
            if not polys:
                continue
            is_hi = rid == self.map_highlight_id
            c_fill, c_stroke = MAP_PALETTE.get(reg.get("color", "teal"), (ft.Colors.PRIMARY_CONTAINER, ft.Colors.PRIMARY))
            shapes.extend(self._combined_poly_paths(
                polys,
                fill_color=ft.Colors.PRIMARY if is_hi else ft.Colors.with_opacity(0.76, c_fill),
                stroke_color=ft.Colors.ON_PRIMARY if is_hi else c_stroke,
                stroke_width=2.2 if is_hi else 1.3,
                outline=is_hi or not fast,
                step=2 if fast else 1,
            ))

        # 3D limb darkening / specular shading + crisp sphere rim
        shapes.append(cv.Circle(
            cx, cy, radius,
            paint=ft.Paint(
                style=ft.PaintingStyle.FILL,
                gradient=ft.PaintRadialGradient(
                    center=(cx - radius * 0.25, cy - radius * 0.25),
                    radius=radius * 1.05,
                    colors=[
                        ft.Colors.with_opacity(0.06, ft.Colors.WHITE),
                        ft.Colors.TRANSPARENT,
                        ft.Colors.with_opacity(0.36, ft.Colors.BLACK),
                    ],
                    color_stops=[0.0, 0.58, 1.0],
                ),
            ),
        ))
        shapes.append(cv.Circle(
            cx, cy, radius,
            paint=ft.Paint(
                color=ft.Colors.with_opacity(0.35, ft.Colors.BLUE_200),
                stroke_width=1.4,
                style=ft.PaintingStyle.STROKE,
            ),
        ))
        return shapes

    def _update_globe_labels(self):
        view_w, view_h = self._globe_view_size
        cx, cy, radius = self._globe_geometry()
        for reg in maps.get_globe()["regions"]:
            rid = reg["id"]
            pill = self._globe_labels.get(rid)
            if pill is None:
                continue
            lon, lat = reg["center"]
            x3, y3, z3 = maps.project_globe_vector(lon, lat, self.globe_lon, self.globe_lat)
            sx = cx + radius * x3
            sy = cy - radius * y3
            if z3 <= 0.28 or sx < -20.0 or sx > view_w + 20.0 or sy < -20.0 or sy > view_h + 20.0:
                pill.visible = False
                continue
            lbl_w = pill.width or 72.0
            lbl_h = pill.height or 24.0
            pill.left = round(max(4.0, min(view_w - lbl_w - 4.0, sx - lbl_w * 0.5)), 1)
            pill.top = round(max(4.0, min(view_h - lbl_h - 4.0, sy - lbl_h * 0.5)), 1)
            is_hi = rid == self.map_highlight_id
            _, c_stroke = MAP_PALETTE.get(reg.get("color", "teal"), (ft.Colors.PRIMARY_CONTAINER, ft.Colors.PRIMARY))
            pill.bgcolor = ft.Colors.with_opacity(0.92, ft.Colors.PRIMARY if is_hi else ft.Colors.SURFACE_CONTAINER_HIGH)
            pill.border = ft.Border.all(1.2, ft.Colors.ON_PRIMARY if is_hi else c_stroke)
            if isinstance(pill.content, ft.Text):
                pill.content.color = ft.Colors.ON_PRIMARY if is_hi else ft.Colors.ON_SURFACE
            pill.visible = True

    def _redraw_globe(self, fast: bool = False):
        if not self.on_map or self.map_stack[-1] != "world" or self._globe_canvas is None:
            return
        t0 = time.monotonic()
        self._globe_last_draw_t = t0
        self._globe_canvas.shapes = self._build_globe_shapes(fast=fast)
        self._update_globe_labels()
        if self._globe_stack is not None and isinstance(self.page, ft.Page):
            try:
                self._globe_stack.update()
            except RuntimeError:
                self.page.update()
        else:
            self.page.update()
        # How long a redraw took; the motion loops wait at least this long so a slow phone isn't flooded
        # with frames it can't keep up with.
        self._globe_draw_cost = time.monotonic() - t0

    def _globe_frame_interval(self) -> float:
        return max(0.028, min(0.12, self._globe_draw_cost * 1.25))

    def _on_globe_tap(self, e: ft.TapEvent):
        if not self.on_map or self._globe_flying or self.map_stack[-1] != "world" or not e.local_position:
            return
        self.globe_touched = True
        self._globe_motion_gen += 1
        cx, cy, radius = self._globe_geometry()
        hit = maps.hit_test_globe(
            e.local_position.x, e.local_position.y,
            self.globe_lon, self.globe_lat, cx, cy, radius, tolerance_px=6.0,
        )
        if hit:
            self._run(self._trigger_map_region, hit)
        else:
            self._redraw_globe(fast=False)

    def _on_globe_scale_start(self, e: ft.ScaleStartEvent):
        if not self.on_map or self._globe_flying or self.map_stack[-1] != "world":
            return
        self.globe_touched = True
        self._globe_motion_gen += 1
        self._globe_pinch_base_zoom = self.globe_zoom
        self._globe_last_focal = (e.local_focal_point.x, e.local_focal_point.y) if e.local_focal_point else None
        self._globe_vel_lon = 0.0
        self._globe_vel_lat = 0.0
        self._globe_last_drag_t = time.monotonic()

    def _on_globe_scale_update(self, e: ft.ScaleUpdateEvent):
        if not self.on_map or self._globe_flying or self.map_stack[-1] != "world":
            return
        now = time.monotonic()
        if e.pointer_count >= 2 or abs(e.scale - 1.0) > 1e-4:
            self.globe_zoom = max(GLOBE_MIN_ZOOM, min(GLOBE_MAX_ZOOM, self._globe_pinch_base_zoom * e.scale))

        dx = dy = 0.0
        if e.focal_point_delta is not None:
            dx, dy = e.focal_point_delta.x, e.focal_point_delta.y
        elif e.local_focal_point is not None and self._globe_last_focal is not None:
            dx = e.local_focal_point.x - self._globe_last_focal[0]
            dy = e.local_focal_point.y - self._globe_last_focal[1]
        if e.local_focal_point is not None:
            self._globe_last_focal = (e.local_focal_point.x, e.local_focal_point.y)

        if e.pointer_count <= 1 and (dx != 0.0 or dy != 0.0):
            _, _, radius = self._globe_geometry()
            dlon = -math.degrees(dx / max(40.0, radius))
            dlat = math.degrees(dy / max(40.0, radius))
            self.globe_lon = ((self.globe_lon + dlon + 180.0) % 360.0) - 180.0
            self.globe_lat = max(-GLOBE_MAX_LAT, min(GLOBE_MAX_LAT, self.globe_lat + dlat))
            dt = now - self._globe_last_drag_t
            if 0.002 <= dt <= 0.25:
                self._globe_vel_lon = 0.55 * self._globe_vel_lon + 0.45 * (dlon / dt)
                self._globe_vel_lat = 0.55 * self._globe_vel_lat + 0.45 * (dlat / dt)
            self._globe_last_drag_t = now

        if now - self._globe_last_draw_t >= self._globe_frame_interval():
            self._redraw_globe(fast=True)

    def _on_globe_scale_end(self, e: ft.ScaleEndEvent):
        if not self.on_map or self._globe_flying or self.map_stack[-1] != "world":
            return
        now = time.monotonic()
        if now - self._globe_last_drag_t > 0.09:
            self._globe_vel_lon = 0.0
            self._globe_vel_lat = 0.0
        elif math.hypot(self._globe_vel_lon, self._globe_vel_lat) < 10.0 and getattr(e, "velocity", None):
            _, _, radius = self._globe_geometry()
            self._globe_vel_lon = -math.degrees(e.velocity.x / max(40.0, radius))
            self._globe_vel_lat = math.degrees(e.velocity.y / max(40.0, radius))

        speed = math.hypot(self._globe_vel_lon, self._globe_vel_lat)
        if speed > 320.0:
            scale = 320.0 / speed
            self._globe_vel_lon *= scale
            self._globe_vel_lat *= scale
            speed = 320.0

        if speed >= 12.0 and isinstance(self.page, ft.Page):
            self._run(self._globe_momentum_loop)
        else:
            self._redraw_globe(fast=False)

    def _on_globe_scroll(self, e: ft.ScrollEvent):
        if not self.on_map or self._globe_flying or self.map_stack[-1] != "world" or not e.scroll_delta:
            return
        self.globe_touched = True
        self._globe_motion_gen += 1
        self.globe_zoom = max(
            GLOBE_MIN_ZOOM,
            min(GLOBE_MAX_ZOOM, self.globe_zoom * math.exp(-e.scroll_delta.y * 0.0015)),
        )
        self._redraw_globe(fast=False)

    async def _globe_idle_loop(self):
        gen = self._globe_motion_gen
        last_t = time.monotonic()
        while (
            self.on_map
            and self.map_stack == ["world"]
            and not self.globe_touched
            and not self._globe_flying
            and gen == self._globe_motion_gen
            and GLOBE_IDLE_SPIN_DPS > 0.0
        ):
            await asyncio.sleep(max(0.042, self._globe_frame_interval()))
            if (
                not self.on_map
                or self.map_stack != ["world"]
                or self.globe_touched
                or self._globe_flying
                or gen != self._globe_motion_gen
            ):
                break
            now = time.monotonic()
            dt = min(0.1, now - last_t)
            last_t = now
            self.globe_lon = ((self.globe_lon + GLOBE_IDLE_SPIN_DPS * dt + 180.0) % 360.0) - 180.0
            self._redraw_globe(fast=True)

    async def _globe_momentum_loop(self):
        gen = self._globe_motion_gen
        last_t = time.monotonic()
        while (
            self.on_map
            and self.map_stack == ["world"]
            and not self._globe_flying
            and gen == self._globe_motion_gen
        ):
            await asyncio.sleep(self._globe_frame_interval())
            if (
                not self.on_map
                or self.map_stack != ["world"]
                or self._globe_flying
                or gen != self._globe_motion_gen
            ):
                return
            now = time.monotonic()
            dt = min(0.08, now - last_t)
            last_t = now
            self.globe_lon = ((self.globe_lon + self._globe_vel_lon * dt + 180.0) % 360.0) - 180.0
            new_lat = self.globe_lat + self._globe_vel_lat * dt
            if new_lat >= GLOBE_MAX_LAT or new_lat <= -GLOBE_MAX_LAT:
                self.globe_lat = max(-GLOBE_MAX_LAT, min(GLOBE_MAX_LAT, new_lat))
                self._globe_vel_lat = 0.0
            else:
                self.globe_lat = new_lat
            decay = math.exp(-3.2 * dt)
            self._globe_vel_lon *= decay
            self._globe_vel_lat *= decay
            if math.hypot(self._globe_vel_lon, self._globe_vel_lat) < 2.5:
                self._redraw_globe(fast=False)
                return
            self._redraw_globe(fast=True)

    async def _trigger_map_region(self, region_id: str):
        if not self.on_map:
            return
        if self.map_stack[-1] == "world" and maps.has_sublevel(region_id):
            if self._globe_flying:
                return
            self.globe_touched = True
            self._globe_motion_gen += 1
            gen = self._globe_motion_gen
            self._globe_flying = True
            self._globe_pre_fly_zoom = self.globe_zoom
            self.map_highlight_id = region_id
            self._redraw_globe(fast=False)

            reg = maps.globe_region(region_id)
            target_lon, target_lat = (reg["focus"] if reg else (self.globe_lon, self.globe_lat))
            target_lat = max(-GLOBE_MAX_LAT, min(GLOBE_MAX_LAT, target_lat))
            start_lon = self.globe_lon
            start_lat = self.globe_lat
            start_zoom = self.globe_zoom
            target_zoom = max(start_zoom, 1.48)
            dlon = ((target_lon - start_lon + 180.0) % 360.0) - 180.0

            t0 = time.monotonic()
            while True:
                elapsed = time.monotonic() - t0
                u = min(1.0, elapsed / GLOBE_FLY_SECONDS)
                eased = 4.0 * u * u * u if u < 0.5 else 1.0 - ((-2.0 * u + 2.0) ** 3) / 2.0
                self.globe_lon = ((start_lon + dlon * eased + 180.0) % 360.0) - 180.0
                self.globe_lat = start_lat + (target_lat - start_lat) * eased
                self.globe_zoom = start_zoom + (target_zoom - start_zoom) * eased
                self._redraw_globe(fast=(u < 1.0))
                if u >= 1.0:
                    break
                await asyncio.sleep(self._globe_frame_interval())
                if not self.on_map or gen != self._globe_motion_gen:
                    self._globe_flying = False
                    return

            self._globe_flying = False
            if not self.on_map or gen != self._globe_motion_gen:
                return
            focus = self._map_focus_alignment("world", region_id)
            self.map_stack.append(region_id)
            self.map_highlight_id = None
            self._render_map_level(transition=("in", focus))
            self.page.update()
            await self._play_map_transition()
            return

        self.map_highlight_id = region_id
        self._render_map_level()
        self.page.update()
        await asyncio.sleep(0.15)
        if not self.on_map:
            return
        if maps.has_sublevel(region_id):
            focus = self._map_focus_alignment(self.map_stack[-1], region_id)
            self.map_stack.append(region_id)
            self.map_highlight_id = None
            self._render_map_level(transition=("in", focus))
            self.page.update()
            await self._play_map_transition()
        else:
            self.map_highlight_id = None
            self._render_map_level()
            self.page.update()
            self._open_map_cuisine_sheet(region_id)

    def _open_map_cuisine_sheet(self, node_id: str):
        node = cuisines.resolve(node_id) or cuisines.get(node_id)
        if not node:
            return
        leaf_id = node["id"]
        label = cuisines.chip_label(leaf_id)

        def pick_from_map(_):
            self.page.pop_dialog()
            self.on_map = False
            self._globe_motion_gen += 1
            self._globe_flying = False
            self.map_highlight_id = None
            self._pick_cuisine(leaf_id)
            self.show_home()

        self.page.show_dialog(ft.BottomSheet(
            show_drag_handle=True, scrollable=True,
            content=ft.SafeArea(
                ft.Container(
                    ft.Column([
                        heading(label, 22),
                        *self._cuisine_info_lines(node),
                        ft.Container(
                            gradient_button(f"Pick {label}", ft.Icons.RESTAURANT_MENU, pick_from_map),
                            padding=ft.Padding(left=0, right=0, top=8, bottom=0),
                        ),
                    ], spacing=10, tight=True, scroll=ft.ScrollMode.AUTO),
                    padding=ft.Padding(left=24, right=24, top=8, bottom=80), width=MAX_WIDTH,
                ),
            ),
        ))

    def _map_level_scale(self, lvl: dict) -> float:
        pw = float(self.page.width or 375.0)
        ph = float(self.page.height or 812.0)
        avail_w = max(340.0, min(pw - 16.0, float(MAX_WIDTH)))
        avail_h = max(480.0, ph - 120.0)
        return max(1.0, min(1.4, avail_w / float(lvl["width"]), avail_h / float(lvl["height"])))

    def _map_focus_alignment(self, level_id: str, region_id: str) -> ft.Alignment:
        """Where region_id sits on level_id's map, as an alignment (-1..1) of the map area: the point the
        zoom between levels grows out of or shrinks back into."""
        pw = float(self.page.width or 375.0)
        ph = float(self.page.height or 812.0)
        body_w = max(1.0, min(pw, float(MAX_WIDTH) + 16.0))
        body_h = max(1.0, ph - 112.0)
        if level_id == "world":
            # The globe turns the chosen continent to its centre before handing over.
            view_w, view_h = self._globe_view_size
            cx, cy, _ = self._globe_geometry()
            x = (cx - view_w / 2.0) / (body_w / 2.0)
            y = (cy - view_h / 2.0) / (body_h / 2.0)
        else:
            lvl = maps.get_level(level_id)
            reg = next((r for r in (lvl or {}).get("regions", []) if r["id"] == region_id), None)
            if not lvl or not reg:
                return ft.Alignment(0, 0)
            sc = self._map_level_scale(lvl)
            px, py = reg.get("label_pos") or reg["center"]
            x = (px * sc - float(lvl["width"]) * sc / 2.0) / (body_w / 2.0)
            y = (py * sc - float(lvl["height"]) * sc / 2.0) / (body_h / 2.0)
        return ft.Alignment(round(max(-1.0, min(1.0, x)), 3), round(max(-1.0, min(1.0, y)), 3))

    async def _play_map_transition(self):
        """Run the zoom set up by _render_map_level(transition=...): first frame is already on screen."""
        pending, self._map_pending = self._map_pending, None
        if not pending:
            return
        old, layer, direction, focus = pending
        await asyncio.sleep(0.03)  # let the starting state paint before animating away from it
        if self._map_layer is not layer:
            return
        old.scale = ft.Scale(MAP_ZOOM_IN_SCALE if direction == "in" else MAP_ZOOM_OUT_SCALE, alignment=focus)
        old.opacity = 0.0
        layer.scale = ft.Scale(1.0, alignment=focus)
        layer.opacity = 1.0
        self.page.update()
        await asyncio.sleep(MAP_ZOOM_MS / 1000.0 + 0.05)
        if self._map_layer is layer:
            old.visible = False
            self.page.update()

    def _render_map_level(self, transition: tuple[str, ft.Alignment] | None = None):
        level_id = self.map_stack[-1]
        pw = float(self.page.width or 375.0)
        ph = float(self.page.height or 812.0)
        avail_w = max(340.0, min(pw - 16.0, float(MAX_WIDTH)))
        avail_h = max(480.0, ph - 120.0)

        if level_id == "world":
            self.map_scale = max(1.0, min(1.4, avail_w / 360.0, avail_h / 520.0))
            view_w = round(avail_w, 1)
            view_h = round(max(440.0, ph - 112.0), 1)
            self._globe_view_size = (view_w, view_h)

            self._globe_canvas = cv.Canvas(shapes=[], width=view_w, height=view_h)
            globe_gesture = ft.GestureDetector(
                content=self._globe_canvas,
                on_tap_up=self._on_globe_tap,
                on_scale_start=self._on_globe_scale_start,
                on_scale_update=self._on_globe_scale_update,
                on_scale_end=self._on_globe_scale_end,
                on_scroll=self._on_globe_scroll,
                trackpad_scroll_causes_scale=True,
                width=view_w,
                height=view_h,
            )
            self._globe_labels = {}
            label_controls: list[ft.Control] = []
            for reg in maps.get_globe()["regions"]:
                rid = reg["id"]
                label = reg["label"]
                lbl_w = round(max(56.0, len(label) * 7.2 + 16.0), 1)
                lbl_h = 24.0
                pill = ft.Container(
                    ft.Text(
                        label,
                        size=12,
                        weight=ft.FontWeight.W_700,
                        color=ft.Colors.ON_SURFACE,
                        no_wrap=True,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    width=lbl_w,
                    height=lbl_h,
                    alignment=ft.Alignment.CENTER,
                    border_radius=12,
                    visible=False,
                    on_click=lambda _, r_id=rid: self._run(self._trigger_map_region, r_id),
                )
                self._globe_labels[rid] = pill
                label_controls.append(pill)

            self._globe_stack = ft.Stack(
                [globe_gesture, *label_controls],
                width=view_w,
                height=view_h,
                clip_behavior=ft.ClipBehavior.HARD_EDGE,
            )
            self._globe_canvas.shapes = self._build_globe_shapes(fast=False)
            self._update_globe_labels()
            map_body = ft.Container(
                self._globe_stack,
                expand=True,
                alignment=ft.Alignment.CENTER,
                bgcolor=ft.Colors.SURFACE,
                clip_behavior=ft.ClipBehavior.HARD_EDGE,
            )
            crumb_title = heading("Browse by map", 20)
            subtitle_text = "Spin the globe and tap a continent."
            level_heading = ""
            header_actions: list[ft.Control] = []
        else:
            self._globe_canvas = None
            self._globe_stack = None
            self._globe_labels = {}
            lvl = maps.get_level(level_id)
            if not lvl:
                return
            base_w = float(lvl["width"])
            base_h = float(lvl["height"])
            s = self._map_level_scale(lvl)
            self.map_scale = s
            canvas_w = round(base_w * s, 1)
            canvas_h = round(base_h * s, 1)
            tx = lambda x: x * s
            ty = lambda y: y * s

            shapes: list[cv.Shape] = []
            shapes.extend(self._poly_paths(
                lvl["background"],
                fill_color=ft.Colors.with_opacity(0.45, ft.Colors.SURFACE_CONTAINER_HIGH),
                stroke_color=ft.Colors.with_opacity(0.45, ft.Colors.OUTLINE_VARIANT),
                stroke_width=1.0,
                tx=tx,
                ty=ty,
            ))
            for bx0, by0, bx1, by1 in lvl.get("inset_boxes", []):
                rx, ry = tx(bx0), ty(by0)
                rw, rh = (bx1 - bx0) * s, (by1 - by0) * s
                shapes.append(cv.Rect(
                    rx, ry, width=rw, height=rh, border_radius=8,
                    paint=ft.Paint(
                        color=ft.Colors.with_opacity(0.55, ft.Colors.OUTLINE_VARIANT),
                        stroke_width=1.1,
                        style=ft.PaintingStyle.STROKE,
                    ),
                ))

            for reg in lvl["regions"]:
                rid = reg["id"]
                is_hi = rid == self.map_highlight_id
                c_fill, c_stroke = MAP_PALETTE.get(reg.get("color", "teal"), (ft.Colors.PRIMARY_CONTAINER, ft.Colors.PRIMARY))
                shapes.extend(self._poly_paths(
                    reg["polygons"],
                    fill_color=ft.Colors.PRIMARY if is_hi else ft.Colors.with_opacity(0.68, c_fill),
                    stroke_color=ft.Colors.ON_PRIMARY if is_hi else c_stroke,
                    stroke_width=2.2 if is_hi else 1.4,
                    tx=tx,
                    ty=ty,
                ))

            # Draw leader lines and anchor dots on canvas underneath call-out chips
            for reg in lvl["regions"]:
                callout = reg.get("callout")
                if not callout:
                    continue
                _, c_stroke = MAP_PALETTE.get(reg.get("color", "teal"), (ft.Colors.PRIMARY, ft.Colors.TERTIARY))
                ax, ay = tx(callout["anchor"][0]), ty(callout["anchor"][1])
                lx, ly = tx(callout["pos"][0]), ty(callout["pos"][1])
                shapes.append(cv.Line(
                    ax, ay, lx, ly,
                    paint=ft.Paint(color=c_stroke, stroke_width=1.6, style=ft.PaintingStyle.STROKE),
                ))
                shapes.append(cv.Circle(
                    ax, ay, radius=3.2,
                    paint=ft.Paint(color=c_stroke, style=ft.PaintingStyle.FILL),
                ))

            canvas_ctrl = cv.Canvas(shapes=shapes, width=canvas_w, height=canvas_h)
            gesture = ft.GestureDetector(
                content=canvas_ctrl,
                on_tap_up=self._on_map_canvas_tap,
                width=canvas_w,
                height=canvas_h,
            )

            stack_items: list[ft.Control] = [gesture]

            # On-map labels and call-out chips
            for reg in lvl["regions"]:
                rid = reg["id"]
                label = reg["label"]
                is_hi = rid == self.map_highlight_id
                c_fill, c_stroke = MAP_PALETTE.get(reg.get("color", "teal"), (ft.Colors.PRIMARY_CONTAINER, ft.Colors.PRIMARY))
                callout = reg.get("callout")
                if callout:
                    lx, ly = tx(callout["pos"][0]), ty(callout["pos"][1])
                    chip_w = max(56.0, len(label) * 7.0 + 18.0)
                    chip_h = 28.0
                    left = max(4.0, min(canvas_w - chip_w - 4.0, lx - chip_w * 0.5))
                    top = max(4.0, min(canvas_h - chip_h - 4.0, ly - chip_h * 0.5))
                    stack_items.append(ft.Container(
                        ft.Text(
                            label,
                            size=11.5,
                            weight=ft.FontWeight.W_600,
                            color=ft.Colors.ON_PRIMARY if is_hi else ft.Colors.ON_SURFACE,
                            no_wrap=True,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        left=round(left, 1),
                        top=round(top, 1),
                        width=round(chip_w, 1),
                        height=chip_h,
                        alignment=ft.Alignment.CENTER,
                        bgcolor=ft.Colors.PRIMARY if is_hi else ft.Colors.SURFACE_CONTAINER_HIGH,
                        border=ft.Border.all(1.5, ft.Colors.ON_PRIMARY if is_hi else c_stroke),
                        border_radius=14,
                        ink=True,
                        on_click=lambda _, r_id=rid: self._run(self._trigger_map_region, r_id),
                    ))
                else:
                    lpos = reg.get("label_pos") or reg["center"]
                    cx, cy = tx(lpos[0]), ty(lpos[1])
                    lbl_w = max(52.0, len(label) * 7.2 + 12.0)
                    lbl_h = 24.0
                    left = max(4.0, min(canvas_w - lbl_w - 4.0, cx - lbl_w * 0.5))
                    top = max(4.0, min(canvas_h - lbl_h - 4.0, cy - lbl_h * 0.5))
                    stack_items.append(ft.Container(
                        ft.Text(
                            label,
                            size=12,
                            weight=ft.FontWeight.W_700,
                            color=ft.Colors.ON_PRIMARY if is_hi else ft.Colors.ON_SURFACE,
                            no_wrap=True,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        left=round(left, 1),
                        top=round(top, 1),
                        width=round(lbl_w, 1),
                        height=lbl_h,
                        alignment=ft.Alignment.CENTER,
                        bgcolor=ft.Colors.with_opacity(0.84, ft.Colors.PRIMARY if is_hi else ft.Colors.SURFACE_CONTAINER_HIGH),
                        border=ft.Border.all(1.1, ft.Colors.ON_PRIMARY if is_hi else c_stroke),
                        border_radius=10,
                        on_click=lambda _, r_id=rid: self._run(self._trigger_map_region, r_id),
                    ))

            map_stack = ft.Stack(stack_items, width=canvas_w, height=canvas_h)
            viewer = ft.InteractiveViewer(
                content=ft.Container(map_stack, alignment=ft.Alignment.CENTER),
                min_scale=1.0,
                max_scale=4.5,
                boundary_margin=ft.Margin.all(0),
                expand=True,
            )
            map_body = ft.Container(
                viewer,
                expand=True,
                alignment=ft.Alignment.CENTER,
                bgcolor=ft.Colors.SURFACE,
            )

            crumbs = " > ".join(cuisines.path(level_id))
            crumb_title = heading(crumbs, 19)
            node = cuisines.get(level_id)
            subtitle_text = (node.get("subtitle") or "Tap a region or call-out to explore.") if node else ""
            # An optional extra line above the subtitle, e.g. China's "The Eight Great Cuisines (八大菜系)".
            level_heading = (node.get("heading") or "") if node else ""

            header_actions = []
            any_id = lvl.get("any_id")
            if any_id:
                any_node = cuisines.get(any_id)
                if any_node:
                    header_actions.append(ft.FilledTonalButton(
                        any_node["label"],
                        icon=ft.Icons.PUBLIC,
                        on_click=lambda _, aid=any_id: self._open_map_cuisine_sheet(aid),
                    ))

        top_bar = ft.Container(
            ft.Column([
                ft.Row([
                    ft.Row([
                        ft.IconButton(ft.Icons.ARROW_BACK, tooltip="Back", on_click=self._map_back),
                        crumb_title,
                    ], spacing=4, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    *header_actions,
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, wrap=True),
                ft.Container(
                    heading(level_heading, 16, weight=ft.FontWeight.W_600),
                    padding=ft.Padding(left=14, right=14, top=2, bottom=0),
                    visible=bool(level_heading),
                ),
                ft.Container(
                    ft.Text(subtitle_text, size=13, color=ft.Colors.ON_SURFACE_VARIANT),
                    padding=ft.Padding(left=14, right=14, top=0, bottom=2),
                ),
            ], spacing=2, tight=True),
            padding=ft.Padding(left=8, right=12, top=6, bottom=6),
            bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
            border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.with_opacity(0.08, ft.Colors.ON_SURFACE))),
        )

        layer = ft.Container(map_body, expand=True, clip_behavior=ft.ClipBehavior.HARD_EDGE)
        old = self._map_layer if transition else None
        self._map_layer = layer
        self._map_pending = None
        area: ft.Control = layer
        if old is not None:
            direction, focus = transition
            anim = ft.Animation(MAP_ZOOM_MS, ft.AnimationCurve.EASE_IN_OUT_CUBIC)
            for ctrl in (old, layer):
                ctrl.left = ctrl.top = ctrl.right = ctrl.bottom = 0
                ctrl.animate_scale = anim
                ctrl.animate_opacity = anim
                ctrl.visible = True
            old.scale = ft.Scale(1.0, alignment=focus)
            old.opacity = 1.0
            layer.scale = ft.Scale(MAP_ZOOM_OUT_SCALE if direction == "in" else MAP_ZOOM_IN_SCALE, alignment=focus)
            layer.opacity = 0.0
            area = ft.Container(
                ft.Stack([old, layer], expand=True),
                expand=True,
                clip_behavior=ft.ClipBehavior.HARD_EDGE,
                bgcolor=ft.Colors.SURFACE,
            )
            self._map_pending = (old, layer, direction, focus)

        self.root.content = ft.Column(
            [
                top_bar,
                area,
            ],
            spacing=0,
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        )

    def _pick_audience(self, label: str):
        self.audience = label
        self._style_audience()
        for tile in self.audience_tiles.values():
            tile.update()

    def _style_audience(self):
        for lab, tile in self.audience_tiles.items():
            on = lab == self.audience
            tile.bgcolor = ft.Colors.PRIMARY_CONTAINER if on else ft.Colors.SURFACE_CONTAINER_HIGH
            tile.border = ft.Border.all(2, ft.Colors.PRIMARY if on else ft.Colors.TRANSPARENT)

    def _on_diet_select(self, e):
        chosen = [c for c in self.diet_chips.values() if c.selected]
        if len(chosen) > prompts.MAX_RESTRICTIONS:
            e.control.selected = False
            e.control.update()
            snack(self.page, f"Pick up to {prompts.MAX_RESTRICTIONS} dietary needs.")

    def surprise(self, e):
        pick = random.choice(cuisines.leaves())
        self._pick_cuisine(pick["id"])
        snack(self.page, f"Surprise! Going {cuisines.chip_label(pick['id'])}.")

    def _hero(self) -> ft.Control:
        inner = ft.Column([
            ft.Row([ft.Row([ft.Image(src="logo_white.svg", width=40, height=36),
                            heading("ChefBot", 30, ft.Colors.WHITE, ft.FontWeight.W_800)], spacing=12),
                    ft.IconButton(ft.Icons.SETTINGS_OUTLINED, icon_color=ft.Colors.WHITE, tooltip="Settings",
                                  on_click=self.open_settings)],
                   alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            heading("What's for dinner?", 38, ft.Colors.WHITE, ft.FontWeight.W_700),
            ft.Text("Tell it what's in your kitchen, get a real recipe, then keep tweaking until it's perfect.",
                    size=15.5, color=ft.Colors.with_opacity(0.92, "#FFFFFF")),
        ], spacing=8, tight=True)
        return self._pad(ft.Container(
            inner, gradient=ft.LinearGradient(colors=GRADIENT, begin=ft.Alignment.TOP_LEFT,
                                              end=ft.Alignment.BOTTOM_RIGHT),
            border_radius=ft.BorderRadius(top_left=0, top_right=0, bottom_left=32, bottom_right=32)),
            top=14, bottom=30, extra=6)

    def show_home(self):
        self.conv = None
        self.on_map = False
        self._globe_motion_gen += 1
        self._globe_flying = False
        self.page.views[0].can_pop = True     # back on the home screen leaves the app
        self.padded = []
        self.page.appbar = None
        self.history.prune_photos(keep={n for c in self.working.values() for n in c.photos.values()}
                                       | self.kept_photos)
        self._refresh_recent()
        body = ft.Column(spacing=18, horizontal_alignment=ft.CrossAxisAlignment.STRETCH, controls=[
            card(section_title(ft.Icons.KITCHEN, "What have you got?"), self.ingredients_box,
                 ft.Row([self.photo_btn, small_gradient_button("Cook something up", ft.Icons.SOUP_KITCHEN,
                                                               self.start_recipe)],
                        wrap=True, spacing=10, run_spacing=10)),
            card(ft.Row([section_title(ft.Icons.PUBLIC, "Pick a cuisine"),
                         ft.Row([ft.TextButton("Browse cuisines", icon=ft.Icons.EXPLORE_OUTLINED,
                                               on_click=self.open_cuisine_picker),
                                 ft.TextButton("Browse by map", icon=ft.Icons.MAP_OUTLINED,
                                               on_click=self.open_map_browser),
                                 ft.TextButton("Surprise me", icon=ft.Icons.CASINO_OUTLINED,
                                               on_click=self.surprise)], spacing=4, wrap=True)],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN, wrap=True),
                 self.cuisine_chips_row),
            card(section_title(ft.Icons.GROUPS, "Who's eating?"),
                 ft.Row(list(self.audience_tiles.values()), wrap=True, spacing=10, run_spacing=10)),
            card(section_title(ft.Icons.HEALTH_AND_SAFETY, "Any dietary needs?"),
                 ft.Text("Pick up to three.", size=13, color=ft.Colors.ON_SURFACE_VARIANT),
                 ft.Row([self.dessert, *self.diet_chips.values()], wrap=True, spacing=8, run_spacing=8),
                 self.must_not),
            gradient_button("Cook something up", ft.Icons.SOUP_KITCHEN, self.start_recipe),
            ft.Text(DISCLAIMER, size=11.5, italic=True, color=ft.Colors.ON_SURFACE_VARIANT,
                    text_align=ft.TextAlign.CENTER),
            self.recent,
        ])
        self.root.content = ft.ListView(expand=True, controls=[
            self._hero(), self._pad(ft.Container(body), top=18, bottom=32)])
        self.page.update()

    def _refresh_recent(self):
        convs = self.history.load()
        rows: list[ft.Control] = [section_title(ft.Icons.MENU_BOOK, "Your recipes")] if convs else []
        for c in convs:
            raw_cid = c.settings.get("cuisine_id") or c.settings.get("cuisine", "")
            resolved = cuisines.resolve(raw_cid) if raw_cid and raw_cid != prompts.NO_CUISINE else None
            cuisine = cuisines.chip_label(resolved["id"]) if resolved else ""
            when = datetime.fromtimestamp(c.updated).strftime("%b %d")
            sub = " · ".join(x for x in [cuisine if cuisine != "Anything" else "", when] if x)
            rows.append(ft.Container(
                ft.Row([ft.Column([ft.Text(c.title, weight=ft.FontWeight.W_600, max_lines=2, size=15.5,
                                           overflow=ft.TextOverflow.ELLIPSIS, font_family=HEADING_FONT),
                                   ft.Text(sub, size=12.5, color=ft.Colors.ON_SURFACE_VARIANT)],
                                  spacing=2, expand=True, tight=True),
                        ft.IconButton(ft.Icons.DELETE_OUTLINE, tooltip="Delete", icon_size=20,
                                      on_click=lambda e, cid=c.id: self.delete_conversation(cid))]),
                padding=ft.Padding(left=18, right=6, top=10, bottom=10), border_radius=18, ink=True,
                bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
                on_click=lambda e, cid=c.id: self.open_conversation(cid)))
        self.recent.controls = rows

    def delete_conversation(self, conv_id: str):
        if conv_id in self.working:
            snack(self.page, "Still writing that one. Delete it once it's done.")
            return
        self.history.delete(conv_id)
        self._refresh_recent()
        self.recent.update()

    def open_conversation(self, conv_id: str):
        # One still being written in the background: show that same conversation, live reply and all.
        conv = self.working.get(conv_id) or next((c for c in self.history.load() if c.id == conv_id), None)
        if conv:
            self.show_chat(conv)

    async def read_photo(self, e):
        if self._need_key():
            return
        if self._on_phone():
            await self.open_camera()        # the gallery is one tap away there
        else:
            await self.pick_photo()

    async def pick_photo(self):
        """Choose an existing photo (the gallery on a phone, a file dialog elsewhere)."""
        files = await self.picker.pick_files(file_type=ft.FilePickerFileType.IMAGE, with_data=True,
                                             compression_quality=85, dialog_title="Photo of your fridge, pantry or groceries")
        if not files:
            return
        f = files[0]
        data = f.bytes
        if data is None and f.path:
            with open(f.path, "rb") as fh:
                data = fh.read()
        if not data:
            snack(self.page, "Couldn't read that photo.")
            return
        ext = (f.name.rsplit(".", 1)[-1] if "." in f.name else "jpeg").lower()
        mime = {"png": "image/png", "webp": "image/webp", "heic": "image/heic", "gif": "image/gif"}.get(ext, "image/jpeg")
        await self._read_ingredients(data, mime)

    # The in-app camera (phones). flet-camera shows a live preview; the shutter takes a JPEG.

    async def open_camera(self):
        import flet_camera as fc
        self.on_camera = True
        self.page.views[0].can_pop = False        # back closes the camera (see _on_back)
        self.camera = fc.Camera(expand=True, preview_enabled=True)
        self.shutter = ft.IconButton(ft.Icons.CAMERA, icon_size=44, icon_color=ft.Colors.BLACK,
                                     bgcolor=ft.Colors.WHITE, tooltip="Take the photo", disabled=True,
                                     style=ft.ButtonStyle(shape=ft.CircleBorder(), padding=18),
                                     on_click=lambda e: self._run(self._take_photo))
        self.camera_status = ft.Text("Starting the camera...", color=ft.Colors.WHITE, size=13)
        bar = ft.Container(
            ft.Column([self.camera_status,
                       ft.Row([ft.TextButton("Gallery", icon=ft.Icons.PHOTO_LIBRARY_OUTLINED,
                                             style=ft.ButtonStyle(color=ft.Colors.WHITE),
                                             on_click=lambda e: self._run(self._camera_to_gallery)),
                               self.shutter,
                               ft.TextButton("Cancel", icon=ft.Icons.CLOSE, style=ft.ButtonStyle(color=ft.Colors.WHITE),
                                             on_click=lambda e: self._close_camera())],
                              alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                              vertical_alignment=ft.CrossAxisAlignment.CENTER)],
                      horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10, tight=True),
            padding=ft.Padding(left=12, right=12, top=14, bottom=22),
            bgcolor=ft.Colors.with_opacity(0.55, "#000000"), left=0, right=0, bottom=0)
        self.page.appbar = None
        self.root.content = ft.Container(ft.Stack([ft.Container(self.camera, expand=True, alignment=ft.Alignment.CENTER),
                                                   bar], expand=True),
                                         bgcolor="#000000", expand=True)
        self.page.update()
        try:
            cams = await self.camera.get_available_cameras()
            if not cams:
                raise RuntimeError("no camera")
            back = next((c for c in cams if c.lens_direction == fc.CameraLensDirection.BACK), cams[0])
            await self.camera.initialize(back, fc.ResolutionPreset.HIGH, enable_audio=False)
        except Exception:
            # No camera, or permission refused: the gallery still works.
            self._close_camera()
            snack(self.page, "The camera isn't available, so here's your gallery instead.")
            await self.pick_photo()
            return
        if not self.on_camera:
            return                               # closed while it was starting
        self.camera_status.value = "Get everything in the shot."
        self.shutter.disabled = False
        self.page.update()

    def _close_camera(self):
        if getattr(self, "on_camera", False):
            self.on_camera = False
            self.show_home()

    async def _camera_to_gallery(self):
        self._close_camera()
        await self.pick_photo()

    async def _take_photo(self):
        self.shutter.disabled = True
        self.camera_status.value = "Got it..."
        self.page.update()
        try:
            data = await self.camera.take_picture()
        except Exception:
            self.shutter.disabled = False
            self.camera_status.value = "That didn't work. Try again?"
            self.page.update()
            return
        self._close_camera()
        if data:
            await self._read_ingredients(bytes(data), "image/jpeg")

    async def _read_ingredients(self, data: bytes, mime: str):
        """Ask the vision model what food is in the photo and add it to the ingredients box."""
        self.photo_btn.disabled, self.photo_btn.content = True, "Taking a look..."
        self.photo_btn.update()
        try:
            found = await self.chef.read_ingredients(data, mime)
        except api.ApiError as err:
            snack(self.page, str(err))
            found = None
        finally:
            self.photo_btn.disabled, self.photo_btn.content = False, PHOTO_LABEL
            self.photo_btn.update()
        if found is None:
            return
        if not found:
            snack(self.page, "I couldn't spot any food in that photo.")
            return
        current = (self.ingredients.value or "").strip()
        self.ingredients.value = f"{current}, {found}" if current else found
        self.ingredients.update()
        show_clear_button(self.ingredients, self.ingredients_clear)
        snack(self.page, "Here's what I saw. Fix anything I got wrong.")

    async def _remember_must_not(self):
        """Keep the "Never use..." text for next time (and after a restart) until it's cleared."""
        value = (self.must_not.value or "").strip()
        if value == self.saved_must_not or not self.prefs_loaded:
            return
        try:
            await self.prefs.set(PREF_MUST_NOT, value)
            self.saved_must_not = value
        except Exception:    # not worth interrupting a recipe over, but say so in the log
            log.warning("Couldn't remember the \"Never use...\" text", exc_info=True)

    def _clear_ingredients(self, e=None):
        self.ingredients.value = ""
        self.ingredients.update()
        show_clear_button(self.ingredients, self.ingredients_clear)

    async def _clear_must_not(self):
        self.must_not.value = ""
        show_clear_button(self.must_not)
        await self._remember_must_not()

    async def start_recipe(self, e):
        if self._need_key():
            return
        ingredients = (self.ingredients.value or "").strip()
        if not ingredients:
            snack(self.page, "Tell me some ingredients first (or photograph them).")
            return
        await self._remember_must_not()
        restrictions = [r for r, c in self.diet_chips.items() if c.selected]
        settings = {"cuisine_id": self.cuisine, "cuisine": self.cuisine, "audience": self.audience,
                    "dessert": bool(self.dessert.selected), "restrictions": restrictions,
                    "must_not": (self.must_not.value or "").strip()}
        cuisine_tag = "Anything" if self.cuisine == prompts.NO_CUISINE else cuisines.chip_label(self.cuisine)
        tags = [cuisine_tag, AUDIENCE_CARDS[self.audience][1]]
        if settings["dessert"]:
            tags.append("Dessert")
        tags += restrictions
        if settings["must_not"]:
            tags.append(f"Never: {settings['must_not']}")
        conv = Conversation(settings=settings, messages=[
            {"role": "system", "content": prompts.system_prompt(self.audience, self.cuisine,
                                                                settings["dessert"], restrictions)},
            {"role": "user", "content": prompts.first_message(ingredients, settings["must_not"]),
             "display": f"{ingredients}\n\n{'  ·  '.join(tags)}"},
        ])
        # The ingredients go with this recipe; the box starts empty next time ("Never use..." is kept).
        self.ingredients.value, self.ingredients_clear.visible = "", False
        self.show_chat(conv)
        await self.reply()

    # ------------------------------------------------------------ conversation screen

    def show_chat(self, conv: Conversation):
        self.conv = conv
        self.on_map = False
        self._globe_motion_gen += 1
        self._globe_flying = False
        self.stop_requested = False           # a Stop pressed in another chat doesn't carry over
        self.page.views[0].can_pop = False    # back in a chat goes home instead (see _on_back)
        self.padded = []
        self.title_text = heading(conv.title, 18)
        self.title_text.max_lines, self.title_text.overflow = 1, ft.TextOverflow.ELLIPSIS
        self.page.appbar = ft.AppBar(
            leading=ft.IconButton(ft.Icons.ARROW_BACK, tooltip="Back", on_click=lambda _: self.go_home()),
            title=self.title_text, bgcolor=ft.Colors.TRANSPARENT,
            actions=[ft.IconButton(ft.Icons.SETTINGS_OUTLINED, tooltip="Settings", on_click=self.open_settings)])
        # Build every message up front (not lazily) so scroll_to(scroll_key=...) can find any of them.
        self.thread = self._pad(ft.ListView(expand=True, spacing=16, auto_scroll=True, build_controls_on_demand=False,
                                            scroll_interval=150, on_scroll=self._on_thread_scroll), top=8, bottom=8)
        self.jump_btn = ft.Container(
            ft.FilledTonalButton("Jump to the bottom", icon=ft.Icons.ARROW_DOWNWARD,
                                 on_click=lambda _: self._run(self.jump_to_bottom)),
            alignment=ft.Alignment.CENTER, left=0, right=0, bottom=12, visible=False)
        self.cards = {}
        self.heights: dict[int, float] = {}    # id(message control) -> rendered height (from on_size_change)
        self.thread_end, self.viewport = 0.0, 0.0    # last known scroll range of the conversation
        self.user_tools = {}
        for i, m in enumerate(conv.messages):
            if m["role"] == "user":
                self._add_to_thread(self._user_bubble(m.get("display") or m["content"], index=i))
            elif m["role"] == "assistant":
                photo = None
                if str(i) in conv.photos:
                    path = self.history.photo_path(conv.photos[str(i)])
                    photo = path.read_bytes() if path.exists() else None
                self.cards[i] = self._assistant_card(m["content"], photo, index=i)
                self._add_to_thread(self.cards[i])
        self.status_text = ft.Text("", size=14, weight=ft.FontWeight.W_500, color=ft.Colors.ON_SURFACE_VARIANT)
        self.status = self._pad(ft.Container(
            ft.Row([ft.ProgressRing(width=18, height=18, stroke_width=2.5), self.status_text,
                    ft.TextButton("Stop", icon=ft.Icons.STOP_CIRCLE_OUTLINED, on_click=self._stop)], spacing=12),
            visible=False), top=4, extra=4)
        self.tweaks = ft.Row(scroll=ft.ScrollMode.AUTO, spacing=8, controls=[
            self._tweak_chip(icon, label, msg) for icon, label, msg in QUICK_TWEAKS])
        self.composer = ft.TextField(
            hint_text="Ask for changes: no cucumber, more garlic...", expand=True, multiline=True,
            min_lines=1, max_lines=5, shift_enter=True, on_submit=self.send_followup, filled=True,
            border=soft_border(26))
        self.send_btn = ft.IconButton(ft.Icons.ARROW_UPWARD, tooltip="Send", on_click=self.send_followup,
                                      bgcolor=ft.Colors.PRIMARY, icon_color=ft.Colors.ON_PRIMARY)
        self.editing_index = None
        self.edit_banner = ft.Row([ft.Icon(ft.Icons.EDIT_OUTLINED, size=16, color=ft.Colors.PRIMARY),
                                   ft.Text("Editing your last message", size=13, expand=True),
                                   ft.TextButton("Cancel", on_click=self.cancel_edit)], visible=False)
        self.root.content = ft.Column(expand=True, spacing=0, controls=[
            ft.Stack([self.thread, self.jump_btn], expand=True),
            self.status,
            self._pad(ft.Container(ft.Column([self.tweaks, self.edit_banner, ft.Row([self.composer, self.send_btn])],
                                             spacing=10, tight=True)), top=8, bottom=12),
        ])
        if conv.id in self.live_bubbles:          # came back while the reply is still being written
            self._add_to_thread(self.live_bubbles[conv.id])
        self.page.update()
        self._show_busy()
        if conv.id in self.live_bubbles:
            self._set_status("Still writing...")

    def _tweak_chip(self, icon: str, label: str, msg: str) -> ft.Chip:
        if label not in BETA_TWEAKS:
            return ft.Chip(label=label, leading=ft.Icon(icon, size=18),
                           on_click=lambda e: self._run(self.send_text, msg))
        badge = ft.Container(ft.Text("BETA", size=10, weight=ft.FontWeight.W_800, color=ft.Colors.ON_TERTIARY),
                             bgcolor=ft.Colors.TERTIARY, border_radius=6,
                             padding=ft.Padding(left=5, right=5, top=1, bottom=1))
        return ft.Chip(label=ft.Row([ft.Text(label), badge], spacing=6, tight=True), leading=ft.Icon(icon, size=18),
                       on_click=lambda e: self._warn_then_send(msg))

    def _warn_then_send(self, msg: str):
        def go(_):
            self.page.pop_dialog()
            self._run(self.send_text, msg)
        self.page.show_dialog(ft.AlertDialog(
            icon=ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=ft.Colors.TERTIARY, size=32),
            title=heading("Beta: historical recipes", 22),
            content=ft.Text(HISTORY_WARNING, size=14.5, width=420),
            actions=[ft.TextButton("Cancel", on_click=lambda _: self.page.pop_dialog()),
                     ft.FilledButton("I understand, rewrite it", on_click=go)]))

    async def _on_back(self, e):
        """The system back button (Android) while a chat or map is open: go back, don't leave the app."""
        if getattr(self, "on_camera", False):
            self._close_camera()
            await e.control.confirm_pop(False)
        elif getattr(self, "on_map", False):
            self._map_back()
            await e.control.confirm_pop(False)
        elif self.conv is not None:
            self.go_home()
            await e.control.confirm_pop(False)
        else:
            await e.control.confirm_pop(True)

    def go_home(self):
        self.show_home()         # a reply in progress keeps going and is saved when it's done (see reply)

    def _user_bubble(self, text: str, index: int | None = None) -> ft.Control:
        bubble = ft.Container(
            ft.Text(text, color=ft.Colors.WHITE, size=15, selectable=True),
            gradient=ft.LinearGradient(colors=GRADIENT, begin=ft.Alignment.TOP_LEFT, end=ft.Alignment.BOTTOM_RIGHT),
            border_radius=ft.BorderRadius(top_left=22, top_right=22, bottom_left=22, bottom_right=6),
            padding=ft.Padding(left=18, right=18, top=12, bottom=12),
            margin=ft.Margin(left=64, right=0, top=0, bottom=0))
        if index is None:
            return bubble
        copy = ft.IconButton(ft.Icons.CONTENT_COPY, tooltip="Copy", icon_size=18,
                             on_click=lambda e: self._run(self.copy_user_message, index, e.control))
        row = ft.Row([copy], spacing=0, alignment=ft.MainAxisAlignment.END)
        if index >= 2:                          # the opening request isn't editable here
            tools = ft.Row([ft.IconButton(ft.Icons.EDIT_OUTLINED, tooltip="Edit", icon_size=18,
                                          on_click=lambda e: self._run(self.edit_message, index)),
                            ft.IconButton(ft.Icons.DELETE_OUTLINE, tooltip="Delete", icon_size=18,
                                          on_click=lambda e: self._run(self.delete_message, index))],
                           spacing=0, visible=False)
            self.user_tools[index] = tools
            row.controls.insert(0, tools)
        return ft.Column([bubble, row], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.END)

    def _refresh_user_tools(self):
        """Edit/delete show only under your latest message, and not while ChefBot is answering."""
        last = max((i for i, m in enumerate(self.conv.messages) if m["role"] == "user"), default=-1) if self.conv else -1
        for i, row in self.user_tools.items():
            show = i == last and not self.busy
            if row.visible != show:
                row.visible = show
                row.update()

    def _cut_from(self, index: int) -> tuple[list[dict], dict[str, str]]:
        """Remove message `index` and everything after it. Returns what was removed (for undo)."""
        conv = self.conv
        removed = conv.messages[index:]
        photos = {k: v for k, v in conv.photos.items() if int(k) >= index}
        del conv.messages[index:]
        for k in photos:
            del conv.photos[k]
        conv.title = _latest_title(conv)
        self.history.save(conv)
        return removed, photos

    async def edit_message(self, index: int):
        """Put the message back in the box. Nothing is removed until the edited version is sent."""
        if self.busy:
            return
        self.editing_index = index
        self.composer.value = self.conv.messages[index]["content"]
        self.composer.update()
        self.edit_banner.visible = True
        self.edit_banner.update()
        await self.composer.focus()

    def cancel_edit(self, e=None):
        self.editing_index = None
        self.composer.value = ""
        self.composer.update()
        self.edit_banner.visible = False
        self.edit_banner.update()

    async def delete_message(self, index: int):
        if self.busy:
            return
        conv = self.conv
        removed, photos = self._cut_from(index)
        self.show_chat(conv)

        def undo(_):
            if self.conv is conv and len(conv.messages) == index:
                conv.messages.extend(removed)
                conv.photos.update(photos)
                conv.title = _latest_title(conv)
                self.history.save(conv)
                self.show_chat(conv)
        self.page.show_dialog(ft.SnackBar(ft.Text("Message deleted."), duration=6000,
                                          action=ft.SnackBarAction(label="Undo", on_click=undo)))

    def _assistant_card(self, text: str, photo: bytes | None = None, index: int | None = None) -> ft.Container:
        """A ChefBot reply. `index` is its place in conv.messages; replies still streaming get it later."""
        md = ft.Markdown(text, selectable=True, extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                         md_style_sheet=md_style(), code_style_sheet=md_code_style(), code_theme=MD_CODE_THEME)
        photo_slot = ft.Container(visible=bool(photo))
        if photo:
            photo_slot.content = self._dish_photo(photo)
        actions = ft.Row(wrap=True, spacing=2, run_spacing=0, visible=False)
        c = card(photo_slot,
                 ft.Row([ft.Image(src="logo.svg", width=28, height=28),
                         ft.Text("ChefBot", weight=ft.FontWeight.W_700, font_family=HEADING_FONT, size=15)],
                        spacing=10),
                 md, actions, padding=20)
        c.data = {"md": md, "photo": photo_slot, "actions": actions}
        if index is not None:
            self._fill_actions(c, index, text, has_photo=bool(photo))
        return c

    def _fill_actions(self, c: ft.Container, index: int, text: str, has_photo: bool):
        """The buttons under a reply: they act on that reply only."""
        row: ft.Row = c.data["actions"]
        if c.key is None:       # set once: a new key makes Flutter rebuild the card and lose its place
            c.key = ft.ScrollKey(f"msg-{index}")
        btn = lambda icon, tip, fn: ft.IconButton(icon, tooltip=tip, icon_size=20,
                                                   on_click=lambda e: self._run(fn, index, e.control))
        row.controls = [
            btn(ft.Icons.CONTENT_COPY, "Copy as Markdown", self.copy_message),
            btn(ft.Icons.PICTURE_AS_PDF_OUTLINED, "Save as PDF", self.save_pdf),
            btn(ft.Icons.HTML, "Save as web page (.html)", self.save_html),
            btn(ft.Icons.EMAIL_OUTLINED, "Email", self.email_message),
            btn(ft.Icons.SHARE_OUTLINED, "Share", self.share_message),
        ]
        if extract_title(text):
            row.controls.append(ft.TextButton(
                "New picture" if has_photo else "Picture this dish", icon=ft.Icons.PHOTO_CAMERA_OUTLINED,
                on_click=lambda e: self._run(self.make_picture, index, e.control)))
        row.visible = True

    def _set_status(self, text: str | None):
        self.status.visible = bool(text)
        self.status_text.value = text or ""
        self.status.update()

    def _stop(self, e):
        self.stop_requested = True

    @property
    def busy(self) -> bool:
        """Whether the chat on screen has a reply or picture in progress."""
        return self.conv is not None and self.conv.id in self.working

    def _set_busy(self, conv: Conversation, busy: bool):
        if busy:
            self.working[conv.id] = conv
        else:
            self.working.pop(conv.id, None)
        if self.conv is conv:
            self._show_busy()

    def _show_busy(self):
        for c in (self.composer, self.send_btn, self.tweaks):
            c.disabled = self.busy
            c.update()
        self._refresh_user_tools()

    async def send_followup(self, e):
        text = (self.composer.value or "").strip()
        if text:
            text = text[0].upper() + text[1:]     # the field can't auto-capitalize (see _build_home_controls)
            self.composer.value = ""
            self.composer.update()
            await self.send_text(text)

    async def send_text(self, text: str):
        if self.busy or not self.conv or self._need_key():
            return
        conv = self.conv
        cut = None
        if self.editing_index is not None:      # replace the message being edited (and the reply to it)
            index, self.editing_index = self.editing_index, None
            removed, photos = self._cut_from(index)
            cut = (index, removed, photos)
            self.kept_photos |= set(photos.values())
            self.show_chat(conv)
        conv.messages.append({"role": "user", "content": text})
        self._add_to_thread(self._user_bubble(text, index=len(conv.messages) - 1))
        self.thread.update()
        got_reply = await self.reply()
        if cut is None:
            return
        index, removed, photos = cut
        self.kept_photos -= set(photos.values())
        if got_reply:
            return
        # The edited version got no reply (no signal, out of credit...): put the original back exactly as it was,
        # so a failed edit never loses anything. The edit stays in the box to try again.
        del conv.messages[index:]
        conv.messages.extend(removed)
        conv.photos.update(photos)
        conv.title = _latest_title(conv)
        self.history.save(conv)
        if self.conv is conv:
            self.show_chat(conv)
            self.composer.value = text
            self.editing_index = index
            self.edit_banner.visible = True
            self.page.update()

    async def _cycle_status(self, conv: Conversation, got_text: asyncio.Event):
        lines = THINKING_LINES[:]
        random.shuffle(lines)
        i = 0
        while self.busy and self.conv is conv and not got_text.is_set():
            self._set_status(lines[i % len(lines)] + "...")
            i += 1
            try:
                await asyncio.wait_for(got_text.wait(), timeout=2.5)
            except asyncio.TimeoutError:
                pass

    def _add_to_thread(self, control: ft.Control):
        """Add a message to the conversation, keeping track of its height so we can scroll to it."""
        def remember(e):
            self.heights[id(control)] = e.height
        control.size_change_interval = 200
        control.on_size_change = remember
        self.thread.controls.append(control)

    def _offset_of(self, target: ft.Control | None) -> float:
        """Where `target` starts in the conversation, in pixels from the top (None: the end of it)."""
        offset = self.thread.padding.top if self.thread.padding else 0
        for c in self.thread.controls:
            if c is target:
                break
            offset += self.heights.get(id(c), 0) + self.thread.spacing
        return offset

    def _on_thread_scroll(self, e: ft.OnScrollEvent):
        """Offer "Jump to the bottom" only when there's a good way left to scroll."""
        self.thread_end, self.viewport = e.max_scroll_extent, e.viewport_dimension
        far = e.max_scroll_extent - e.pixels > max(600, (self.page.height or 800) * 0.8)
        if far != self.jump_btn.visible:
            self.jump_btn.visible = far
            self.jump_btn.update()

    async def jump_to_bottom(self):
        self.jump_btn.visible = False
        self.jump_btn.update()
        await self._scroll_to_end(400)

    async def _scroll_to_end(self, duration: int = 0):
        """Scroll to the end of the conversation; auto_scroll then follows new text again.

        Flet 1.0.5 quirks: never toggle auto_scroll (that resets the list to the top), scroll_to(offset=-1) can land
        at the top, and scroll_to(scroll_key=...) does nothing. So scroll to measured pixel positions."""
        measured = self._offset_of(None) - self.viewport
        await self.thread.scroll_to(offset=max(self.thread_end, measured, 0.0), duration=duration)

    async def reply(self) -> bool:
        """Stream the model's answer into a new card. If you leave the chat, it keeps going and the complete reply
        is saved (reopening the chat shows it live). Returns True if a reply was saved.

        If the connection dies while ChefBot is in the background (on a phone: Android froze or killed the
        stream despite the keep-alive), the partial reply is dropped and it starts again once, when you're back."""
        conv = self.conv
        on_screen = lambda: self.conv is conv
        self.stop_requested = False
        self._set_busy(conv, True)
        bubble = self._assistant_card("")
        self.live_bubbles[conv.id] = bubble
        md: ft.Markdown = bubble.data["md"]
        self._add_to_thread(bubble)
        self.thread.update()
        await self._scroll_to_end()      # if they were looking further up (at a new picture, say), follow the reply
        self.keepalive.ask_permission()  # the first time: so the "writing" notification can show
        retried = False
        try:
            while True:
                times_away = self.times_away
                with self.keepalive.holding(WRITING):
                    text, err, stopped = await self._stream_reply(conv, md)
                if retried or stopped or not isinstance(err, api.ConnectionLost):
                    break
                # A frozen app hears that it went away only after it thaws, maybe after the error: let those
                # events arrive before deciding whether being away was the cause.
                await asyncio.sleep(self.RETRY_SETTLE)
                if not self.away and self.times_away == times_away:
                    break                # lost it while on screen: say so, as before
                retried = True
                await self._wait_to_retry(conv, md)
        finally:
            self.live_bubbles.pop(conv.id, None)
        error = str(err) if err else None
        unsent = None
        if text:
            conv.messages.append({"role": "assistant", "content": text})
            conv.title = extract_title(text) or conv.title
            self.history.save(conv)
        elif conv.messages and conv.messages[-1]["role"] == "user" and len(conv.messages) > 2:
            unsent = conv.messages.pop()["content"]    # nothing came back: give the follow-up back to retry
        self._set_busy(conv, False)
        if self.away:                  # in another app: say it's done (tapping it brings ChefBot back)
            if error:
                self.keepalive.notify(f"Not finished: {conv.title}", error)
            elif text and not stopped:
                self.keepalive.notify(f"Ready: {conv.title}", "Tap to open your recipe.")

        if not on_screen():            # finished in the background
            if self.conv is None:      # on the home screen: show it in the list
                self._refresh_recent()
                self.recent.update()
            if error:
                snack(self.page, f"{conv.title}: {error}")
            elif text:
                snack(self.page, f"Ready: {conv.title}")
            return bool(text)

        if text:
            md.value = text
            index = len(conv.messages) - 1
            self.cards[index] = bubble
            self._fill_actions(bubble, index, text, has_photo=False)
            bubble.update()
            self.title_text.value = conv.title
            self.title_text.update()
            self._refresh_user_tools()
        elif unsent is not None:
            self.show_chat(conv)
            self.composer.value = unsent
            self.composer.update()
        else:
            self.thread.controls.remove(bubble)
            self.thread.update()
        self._set_status(None)
        if error:
            snack(self.page, error)
        elif stopped and text:
            snack(self.page, "Stopped. The partial recipe is kept; ask me to finish it if you like.")
        return bool(text)

    async def _stream_reply(self, conv: Conversation, md: ft.Markdown) -> tuple[str, api.ApiError | None, bool]:
        """One attempt at streaming a reply into `md`. Returns (text so far, error, stopped by the user)."""
        on_screen = lambda: self.conv is conv
        got_text = asyncio.Event()
        cycler = asyncio.create_task(self._cycle_status(conv, got_text))
        text, last_paint, error, stopped = "", 0.0, None, False
        try:
            async for chunk in self.chef.stream_chat(conv.chat_messages(), self.model, self.effort):
                if self.stop_requested and on_screen():
                    stopped = True
                    break
                if chunk.kind == "text":
                    if not text:
                        got_text.set()
                        if on_screen():
                            self._set_status("Writing it up...")
                    text += chunk.text
                    if on_screen() and time.monotonic() - last_paint > 0.12:
                        md.value, last_paint = text, time.monotonic()
                        md.update()
        except api.ApiError as err:
            error = err
        finally:
            got_text.set()
            cycler.cancel()
        return text, error, stopped

    async def _wait_to_retry(self, conv: Conversation, md: ft.Markdown):
        """The connection died while ChefBot was away: clear the half-written reply, wait until ChefBot is back on
        screen (Android won't let the keep-alive start from the background), then let reply() go again."""
        md.value = ""
        if self.conv is conv:
            md.update()
        if self.away:
            log.warning("Reply for %r lost its connection in the background; retrying on return", conv.title)
            if self.conv is conv:
                self._set_status("Lost the connection while you were away. I'll start again when you're back...")
            self.keepalive.notify(f"Interrupted: {conv.title}", "Open ChefBot and it will start again.")
            await self.back.wait()
        else:
            log.warning("Reply for %r lost its connection while ChefBot was away; retrying", conv.title)
        snack(self.page, "The connection dropped while you were away, so I started that reply again.")

    # ------------------------------------------------------------ actions on one reply

    def _message(self, index: int) -> tuple[str, str, bytes | None]:
        """(title, markdown, photo) for one reply."""
        text = self.conv.messages[index]["content"]
        title = extract_title(text) or self.conv.title
        photo = None
        name = self.conv.photos.get(str(index))
        if name:
            path = self.history.photo_path(name)
            photo = path.read_bytes() if path.exists() else None
        return title, text, photo

    async def _flash(self, button: ft.Control, ok: bool = True):
        """Brief check mark on the button that was pressed."""
        if not isinstance(button, ft.IconButton):
            return
        old = button.icon
        button.icon = ft.Icons.CHECK if ok else ft.Icons.ERROR_OUTLINE
        button.update()
        await asyncio.sleep(1.6)
        button.icon = old
        button.update()

    async def _make_pdf(self, title: str, text: str, photo: bytes | None) -> bytes:
        if export.cjk_needed(title + text):
            self._set_status("Getting fonts for the non-Latin names (first time only)...")
        fonts = await asyncio.to_thread(export.ensure_cjk_fonts, title + text, self.history.folder / "fonts")
        self._set_status("Making the PDF...")
        try:
            return await asyncio.to_thread(export.recipe_pdf, title, text, photo, fonts)
        finally:
            self._set_status(None)

    async def copy_message(self, index: int, button=None):
        await self.clipboard.set(self.conv.messages[index]["content"])
        snack(self.page, "Copied as Markdown.")
        await self._flash(button)

    async def copy_user_message(self, index: int, button=None):
        """Copies what the bubble shows (the friendly summary for the opening request, not the raw prompt)."""
        m = self.conv.messages[index]
        await self.clipboard.set(m.get("display") or m["content"])
        snack(self.page, "Copied.")
        await self._flash(button)

    async def _save(self, data: bytes, file_name: str) -> bool:
        try:
            path = await self.picker.save_file(dialog_title="Save", file_name=file_name, src_bytes=data)
        except Exception as err:
            snack(self.page, f"Couldn't save: {err}")
            return False
        if not self.page.web and not path:
            return False             # cancelled the save dialog
        snack(self.page, f"Saved {file_name}.")
        return True

    async def save_pdf(self, index: int, button=None):
        title, text, photo = self._message(index)
        pdf = await self._make_pdf(title, text, photo)
        if await self._save(pdf, f"{export.file_stem(title)}.pdf"):
            await self._flash(button)

    async def save_html(self, index: int, button=None):
        title, text, photo = self._message(index)
        page = export.recipe_html(title, text, photo).encode("utf-8")
        if await self._save(page, f"{export.file_stem(title)}.html"):
            await self._flash(button)

    async def _share(self, title: str, text: str, photo: bytes | None, subject: str,
                     body: str) -> ft.ShareResult | None:
        """Open the system share sheet with the recipe PDF (and photo) attached. None if sharing isn't possible
        here (the recipe is copied instead)."""
        try:
            pdf = await self._make_pdf(title, text, photo)
            files = [ft.ShareFile.from_bytes(pdf, mime_type="application/pdf", name=f"{export.file_stem(title)}.pdf")]
            if photo:
                files.append(ft.ShareFile.from_bytes(photo, mime_type=export.image_mime(photo),
                                                     name=f"{export.file_stem(title)}.{export.image_mime(photo).split('/')[1]}"))
            return await self.share.share_files(files, subject=subject, text=body)
        except Exception:
            await self.clipboard.set(text)
            snack(self.page, "Sharing isn't available here, so I copied the recipe instead.")
            return None

    async def share_message(self, index: int, button=None):
        title, text, photo = self._message(index)
        await self._share(title, text, photo, title, f"{title}: a recipe from ChefBot")

    def _on_phone(self) -> bool:
        return not self.page.web and self.page.platform in (ft.PagePlatform.ANDROID, ft.PagePlatform.IOS)

    async def _email_with_mail_app(self, title: str, text: str, photo: bytes | None):
        """On a phone: the share sheet, where the user picks their mail app. It gets the subject, the full recipe
        as the message, and the PDF and photo as attachments."""
        result = await self._share(title, text, photo, f"Recipe: {title}", export.email_text(title, text))
        # Android reports which app was picked (or that the sheet was closed), not whether the email went out. In
        # practice the result arrives when the user comes back to ChefBot, i.e. after sending.
        if result is None or result.status == ft.ShareResultStatus.UNAVAILABLE:
            return
        if result.status == ft.ShareResultStatus.DISMISSED:
            snack(self.page, "Not sent: you closed the share sheet.")
            return
        snack(self.page, "Sent by your phone's mail app.")

    async def email_message(self, index: int, button=None):
        title, text, photo = self._message(index)
        use_relay = bool(self.relay_url and self.relay_secret)
        can_send = use_relay or bool(self.smtp_user and self.smtp_password)
        if self._on_phone() and not can_send:
            await self._email_with_mail_app(title, text, photo)
            return
        to_field = ft.TextField(label="Send to", value=self.email_to, autofocus=True,
                                keyboard_type=ft.KeyboardType.EMAIL, prefix_icon=ft.Icons.EMAIL_OUTLINED)
        remember = ft.Checkbox(label="Remember this address", value=True)
        note = ft.Text(
            f"Sends a formatted email with {export.attachments_phrase(bool(photo))} attached." if can_send else
            "Opens a new message in your mail app with the whole recipe. Mail links can't carry attachments, so "
            "use PDF to save one and attach it yourself.",
            size=12.5, color=ft.Colors.ON_SURFACE_VARIANT)
        sending = ft.ProgressBar(visible=False)
        problem = ft.Text("", color=ft.Colors.ERROR, size=13, visible=False, selectable=True)

        async def remember_address(to: str):
            if remember.value and to != self.email_to:
                self.email_to = to
                await self.prefs.set(PREF_EMAIL_TO, to)

        async def send(_):
            to = (to_field.value or "").strip()
            if "@" not in to:
                to_field.error = "Enter an email address"
                to_field.update()
                return
            await remember_address(to)
            sending.visible, problem.visible, send_button.disabled = True, False, True
            dialog.update()
            try:
                pdf = await self._make_pdf(title, text, photo)
                if use_relay:
                    await asyncio.to_thread(export.send_via_relay, self.relay_url, self.relay_secret, to, title,
                                            text, photo, pdf)
                else:
                    msg = export.build_email(self.smtp_user, to, title, text, photo, pdf)
                    host, _, port = self.smtp_server.partition(":")
                    await asyncio.to_thread(export.send_email, msg, host or "smtp.gmail.com", int(port or 465),
                                            self.smtp_user, self.smtp_password)
            except Exception as err:
                sending.visible, send_button.disabled = False, False
                problem.value, problem.visible = _email_error(err), True
                dialog.update()
                return
            # Say so plainly, in the dialog itself (a passing snackbar is easy to miss).
            dialog.content.controls = [ft.Row([ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN_400, size=28),
                                               ft.Text(f"Sent to {to}.", size=16, weight=ft.FontWeight.W_600,
                                                       expand=True)], spacing=12),
                                       ft.Text("It usually arrives within a minute. The first one may land in spam.",
                                               size=12.5, color=ft.Colors.ON_SURFACE_VARIANT)]
            dialog.actions = [ft.FilledButton("Done", on_click=lambda _: self.page.pop_dialog())]
            dialog.update()

        async def open_mail_app(_):
            to = (to_field.value or "").strip()
            await remember_address(to)
            self.page.pop_dialog()
            if self._on_phone():
                await self._email_with_mail_app(title, text, photo)
                return
            # Some Windows mail apps reject long mailto links, so only there is the text shortened.
            limit = MAILTO_LIMIT_WINDOWS if self.page.platform == ft.PagePlatform.WINDOWS else None
            await self.urls.launch_url(export.mailto_link(to, title, text, limit))

        def settings(_):
            self.page.pop_dialog()
            self.open_settings()

        send_button = ft.FilledButton("Send", icon=ft.Icons.SEND, on_click=send)
        actions = [ft.TextButton("Cancel", on_click=lambda _: self.page.pop_dialog())]
        if can_send:
            actions += [ft.TextButton("Use my mail app", on_click=open_mail_app), send_button]
        else:
            if self.dev_mode:
                actions.append(ft.TextButton("Set up sending", on_click=settings))
            actions.append(ft.FilledButton("Open in mail app", icon=ft.Icons.OPEN_IN_NEW, on_click=open_mail_app))
        dialog = ft.AlertDialog(
            title=heading("Email this recipe", 22),
            content=ft.Column([ft.Text(title, weight=ft.FontWeight.W_600), to_field, remember, note, sending,
                               problem],
                              tight=True, spacing=14, width=420),
            actions=actions)
        self.page.show_dialog(dialog)

    def _dish_photo(self, image: bytes) -> ft.Control:
        """A dish picture in a reply. Tapping it opens it full screen."""
        return ft.Container(ft.Image(src=image, fit=ft.BoxFit.COVER, border_radius=18, height=300),
                            border_radius=18, ink=True, tooltip="View full screen",
                            on_click=lambda e: self.show_full_photo(image))

    def _downloads_folder(self):
        """Where a download goes without asking: the phone's shared Download folder, or ~/Downloads on a computer.
        None on the web (the browser handles downloads)."""
        from pathlib import Path
        if self.page.web:
            return None
        if self.page.platform == ft.PagePlatform.ANDROID:
            return Path(os.environ.get("EXTERNAL_STORAGE", "/storage/emulated/0")) / "Download"
        return Path.home() / "Downloads"

    async def download_photo(self, image: bytes) -> bool:
        """Save the original picture (full resolution, as the image model made it) straight to Downloads.
        True if it was saved."""
        title = self.conv.title if self.conv else "ChefBot dish"
        name = f"{export.file_stem(title)}.{export.image_mime(image).split('/')[1].replace('jpeg', 'jpg')}"
        mime = export.image_mime(image)
        if self.page.platform == ft.PagePlatform.ANDROID and not self.page.web:
            try:     # the fast way: straight into Android's media index, so the Gallery shows it right away
                await asyncio.to_thread(android.save_to_downloads, name, mime, image)
                return True
            except Exception:    # fall back to a plain file write below
                log.warning("MediaStore save failed; trying a plain file write", exc_info=True)
        folder = self._downloads_folder()
        if folder is not None:
            try:
                path = export.free_path(folder, name)
                await asyncio.to_thread(path.write_bytes, image)
                if self.page.platform == ft.PagePlatform.ANDROID:
                    await asyncio.to_thread(android.media_scan, str(path), mime)
                return True
            except OSError:      # e.g. the phone refused: fall back to the save dialog
                log.warning("Couldn't write to %s; opening the save dialog", folder, exc_info=True)
        return await self._save(image, name)

    def show_full_photo(self, image: bytes):
        """The picture on black, filling the screen, with pinch-to-zoom. It's a dialog, so the phone's back button
        closes it (and only it)."""
        close = ft.IconButton(ft.Icons.CLOSE, icon_size=28, icon_color=ft.Colors.WHITE, tooltip="Close",
                              bgcolor=ft.Colors.with_opacity(0.6, "#000000"),
                              on_click=lambda e: self.page.pop_dialog())
        download = ft.IconButton(ft.Icons.DOWNLOAD, icon_size=28, icon_color=ft.Colors.WHITE,
                                 tooltip="Save to Downloads", bgcolor=ft.Colors.with_opacity(0.6, "#000000"))
        saved_note = ft.Container(ft.Text("Saved to Downloads", color=ft.Colors.WHITE, size=14,
                                          weight=ft.FontWeight.W_600),
                                  bgcolor=ft.Colors.with_opacity(0.6, "#000000"), border_radius=18,
                                  padding=ft.Padding(left=14, right=14, top=8, bottom=8), visible=False)

        async def save(_):
            # Feedback has to be in here: a snackbar would sit behind this full-screen view.
            download.disabled = True
            download.update()
            if await self.download_photo(image):
                download.icon, download.icon_color = ft.Icons.CHECK, ft.Colors.GREEN_400
                download.tooltip = "Saved"
                saved_note.visible = True
                saved_note.update()
            else:
                download.disabled = False      # cancelled or failed: allow another try
            download.update()

        download.on_click = save
        viewer = ft.InteractiveViewer(ft.Image(src=image, fit=ft.BoxFit.CONTAIN), min_scale=1, max_scale=5,
                                      alignment=ft.Alignment.CENTER)
        self.page.show_dialog(ft.AlertDialog(
            content=ft.Container(
                ft.Stack([ft.Container(viewer, alignment=ft.Alignment.CENTER, left=0, top=0, right=0, bottom=0),
                          ft.Container(ft.SafeArea(close), top=8, right=8),
                          ft.Container(ft.SafeArea(ft.Row([saved_note, download], spacing=10, tight=True)),
                                       bottom=8, right=8)]),
                width=self.page.width, height=self.page.height, bgcolor="#000000"),
            content_padding=0, inset_padding=0, bgcolor="#000000",
            shape=ft.RoundedRectangleBorder(radius=0)))

    async def make_picture(self, index: int, button=None):
        if self.busy:
            snack(self.page, "Hang on, I'm still cooking.")
            return
        if self._need_key():
            return
        conv = self.conv
        title, text, _ = self._message(index)
        self._set_busy(conv, True)
        self._set_status("Plating it up for the camera...")
        try:
            with self.keepalive.holding(PICTURE):
                image = await self.chef.dish_photo(title)
        except api.ApiError as err:
            snack(self.page, str(err))
            return
        finally:
            if self.conv is conv:
                self._set_status(None)
            self._set_busy(conv, False)
        self.history.save_photo(conv, index, image)
        self.history.save(conv)
        if self.conv is conv and index in self.cards:
            c = self.cards[index]
            slot: ft.Container = c.data["photo"]
            slot.content = self._dish_photo(image)
            slot.visible = True
            self._fill_actions(c, index, text, has_photo=True)
            # Show the new picture right away, at the top of its reply (see _scroll_to_end for why it's done by
            # measured position). auto_scroll stops following while we're away from the end.
            c.update()
            await asyncio.sleep(0.5)        # let the taller card lay out and report its new height
            await self.thread.scroll_to(offset=max(0.0, self._offset_of(c) - 8), duration=500)


def _latest_title(conv: Conversation) -> str:
    for m in reversed(conv.messages):
        if m["role"] == "assistant" and extract_title(m["content"]):
            return extract_title(m["content"])
    return "New recipe"


def _email_error(err: Exception) -> str:
    import smtplib
    if isinstance(err, export.EmailError):
        return f"Not sent: {err}"
    if isinstance(err, smtplib.SMTPAuthenticationError):
        return "The mail server didn't accept the address and app password. Check them in Settings."
    if isinstance(err, (smtplib.SMTPRecipientsRefused,)):
        return "The mail server refused that address."
    return f"Couldn't send the email ({type(err).__name__}: {err})."


async def main(page: ft.Page):
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    await ChefBotApp(page).start()


if __name__ == "__main__":
    ft.run(main)
