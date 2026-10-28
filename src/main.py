"""ChefBot: tell it what's in your fridge, get a recipe, then keep refining it in conversation."""
import asyncio
import os
import random
import time
from datetime import datetime

import flet as ft

from chefbot import api, export, prompts
from chefbot.history import Conversation, History
from chefbot.recipe import extract_title

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
PREF_DEV_MODE = "chefbot.dev_mode"          # "on" shows the hidden email-sending settings (tap Settings 7 times)
DEV_MODE_TAPS = 7
PREFS_FAILED = ("ChefBot couldn't read its saved settings (your key is still safe). Close ChefBot and open it "
                "again.")
ALL_PREFS = (PREF_KEY, PREF_MODEL, PREF_EFFORT, PREF_THEME, PREF_EMAIL_TO, PREF_SMTP_USER, PREF_SMTP_PASSWORD,
             PREF_SMTP_SERVER, PREF_RELAY_URL, PREF_RELAY_SECRET, PREF_DEV_MODE)
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

CUISINE_NAMES = {   # prompt label -> short chip label
    prompts.NO_CUISINE: "Anything",
    "American": "American",
    "American (Cajun)": "Cajun",
    "Chinese (Cantonese - Most common style in US)": "Cantonese",
    "Chinese (Hong Kong)": "Hong Kong",
    "Chinese (Sichuan)": "Sichuan",
    "Chinese (Shandong)": "Shandong",
    "Chinese (Jiangsu)": "Jiangsu",
    "French": "French",
    "Greek": "Greek",
    "North Indian": "North Indian",
    "South Indian": "South Indian",
    "Italian": "Italian",
    "Japanese (Kansai)": "Japanese · Kansai",
    "Japanese (Kanto)": "Japanese · Kanto",
    "Korean": "Korean",
    "Mexican": "Mexican",
    "Peruvian": "Peruvian",
    "Spanish": "Spanish",
    "Thai": "Thai",
    "Turkish": "Turkish",
    "Vietnamese": "Vietnamese",
}
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


def soft_border(radius: int) -> ft.OutlineInputBorder:
    """Rounded, borderless text field outline (the fill color does the work)."""
    return ft.OutlineInputBorder(border_radius=radius, side=ft.BorderSide(0, ft.Colors.TRANSPARENT))


def snack(page: ft.Page, message: str):
    page.show_dialog(ft.SnackBar(ft.Text(message)))


def md_style() -> ft.MarkdownStyleSheet:
    h = lambda size: ft.TextStyle(font_family=HEADING_FONT, size=size, weight=ft.FontWeight.W_700)
    return ft.MarkdownStyleSheet(h1_text_style=h(24), h2_text_style=h(21), h3_text_style=h(18),
                                 h4_text_style=h(16), p_text_style=ft.TextStyle(size=15, height=1.5),
                                 block_spacing=10)


class ChefBotApp:
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
        self.user_tools: dict[int, ft.Row] = {}     # edit/delete buttons under user messages
        self.editing_index: int | None = None
        self.urls = ft.UrlLauncher()
        self.prefs_loaded = False
        self.prefs_failed = False      # saved settings couldn't be read: never show or save a blank form over them
        self.cards: dict[int, ft.Container] = {}   # message index -> its card, on the conversation screen
        self.chef: api.ChefBotAPI | None = None
        self.conv: Conversation | None = None
        self.busy = False
        self.stop_requested = False
        self.cuisine = prompts.NO_CUISINE
        self.audience = prompts.DEFAULT_AUDIENCE
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
        theme_seg = ft.SegmentedButton(
            selected=[self.theme], allow_multiple_selection=False,
            segments=[ft.Segment(value="dark", label="Dark", icon=ft.Icons.DARK_MODE_OUTLINED),
                      ft.Segment(value="light", label="Light", icon=ft.Icons.LIGHT_MODE_OUTLINED),
                      ft.Segment(value="system", label="System", icon=ft.Icons.BRIGHTNESS_AUTO_OUTLINED)])
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
                      PREF_MODEL: model_dd.value or api.DEFAULT_MODEL, PREF_EFFORT: effort_dd.value or api.DEFAULT_EFFORT,
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
        self.ingredients = ft.TextField(
            hint_text="Potatoes, carrots, tomatoes...", multiline=True, min_lines=4, max_lines=8,
            filled=True, border=soft_border(16), capitalization=ft.TextCapitalization.SENTENCES, text_size=16)
        self.photo_btn = ft.FilledTonalButton(PHOTO_LABEL, icon=ft.Icons.PHOTO_CAMERA_OUTLINED,
                                              on_click=self.read_photo)
        self.cuisine_chips = {
            label: ft.Chip(label=short, selected=label == self.cuisine, show_checkmark=False,
                           on_select=lambda e, lab=label: self._pick_cuisine(lab))
            for label, short in CUISINE_NAMES.items()}
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
        self.must_not = ft.TextField(hint_text="Never use... (e.g. peanuts, cilantro)", filled=True,
                                     border=soft_border(16), prefix_icon=ft.Icons.BLOCK)
        self.recent = ft.Column(spacing=10, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)

    def _pick_cuisine(self, label: str):
        self.cuisine = label
        for lab, chip in self.cuisine_chips.items():
            chip.selected = lab == label
            chip.update()

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
        pick = random.choice([c for c in prompts.CUISINES if c != prompts.NO_CUISINE])
        self._pick_cuisine(pick)
        snack(self.page, f"Surprise! Going {CUISINE_NAMES[pick]}.")

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
        self.page.views[0].can_pop = True     # back on the home screen leaves the app
        self.padded = []
        self.page.appbar = None
        self.history.prune_photos()
        self._refresh_recent()
        body = ft.Column(spacing=18, horizontal_alignment=ft.CrossAxisAlignment.STRETCH, controls=[
            card(section_title(ft.Icons.KITCHEN, "What have you got?"), self.ingredients,
                 ft.Row([self.photo_btn, small_gradient_button("Cook something up", ft.Icons.SOUP_KITCHEN,
                                                               self.start_recipe)],
                        wrap=True, spacing=10, run_spacing=10)),
            card(ft.Row([section_title(ft.Icons.PUBLIC, "Pick a cuisine"),
                         ft.TextButton("Surprise me", icon=ft.Icons.CASINO_OUTLINED, on_click=self.surprise)],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                 ft.Row(list(self.cuisine_chips.values()), wrap=True, spacing=8, run_spacing=8)),
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
            cuisine = CUISINE_NAMES.get(c.settings.get("cuisine", ""), "")
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
        self.history.delete(conv_id)
        self._refresh_recent()
        self.recent.update()

    def open_conversation(self, conv_id: str):
        conv = next((c for c in self.history.load() if c.id == conv_id), None)
        if conv:
            self.show_chat(conv)

    async def read_photo(self, e):
        if self._need_key():
            return
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
        snack(self.page, "Here's what I saw. Fix anything I got wrong.")

    async def start_recipe(self, e):
        if self._need_key():
            return
        ingredients = (self.ingredients.value or "").strip()
        if not ingredients:
            snack(self.page, "Tell me some ingredients first (or photograph them).")
            return
        restrictions = [r for r, c in self.diet_chips.items() if c.selected]
        settings = {"cuisine": self.cuisine, "audience": self.audience, "dessert": bool(self.dessert.selected),
                    "restrictions": restrictions, "must_not": (self.must_not.value or "").strip()}
        tags = [CUISINE_NAMES[self.cuisine], AUDIENCE_CARDS[self.audience][1]]
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
        self.show_chat(conv)
        await self.reply()

    # ------------------------------------------------------------ conversation screen

    def show_chat(self, conv: Conversation):
        self.conv = conv
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
            border=soft_border(26), capitalization=ft.TextCapitalization.SENTENCES)
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
        self.page.update()
        self._refresh_user_tools()

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
        """The system back button (Android) while a chat is open: go to the home screen, don't leave the app."""
        if self.conv is not None:
            self.go_home()
            await e.control.confirm_pop(False)
        else:
            await e.control.confirm_pop(True)

    def go_home(self):
        if self.busy:
            self.stop_requested = True
        self.show_home()

    def _user_bubble(self, text: str, index: int | None = None) -> ft.Control:
        bubble = ft.Container(
            ft.Text(text, color=ft.Colors.WHITE, size=15, selectable=True),
            gradient=ft.LinearGradient(colors=GRADIENT, begin=ft.Alignment.TOP_LEFT, end=ft.Alignment.BOTTOM_RIGHT),
            border_radius=ft.BorderRadius(top_left=22, top_right=22, bottom_left=22, bottom_right=6),
            padding=ft.Padding(left=18, right=18, top=12, bottom=12),
            margin=ft.Margin(left=64, right=0, top=0, bottom=0))
        if index is None or index < 2:          # the opening request isn't editable here
            return bubble
        tools = ft.Row([ft.IconButton(ft.Icons.EDIT_OUTLINED, tooltip="Edit", icon_size=18,
                                      on_click=lambda e: self._run(self.edit_message, index)),
                        ft.IconButton(ft.Icons.DELETE_OUTLINE, tooltip="Delete", icon_size=18,
                                      on_click=lambda e: self._run(self.delete_message, index))],
                       spacing=0, alignment=ft.MainAxisAlignment.END, visible=False)
        self.user_tools[index] = tools
        return ft.Column([bubble, tools], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.END)

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
                         md_style_sheet=md_style())
        photo_slot = ft.Container(visible=bool(photo))
        if photo:
            photo_slot.content = ft.Image(src=photo, fit=ft.BoxFit.COVER, border_radius=18, height=300)
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

    def _set_busy(self, busy: bool):
        self.busy = busy
        for c in (self.composer, self.send_btn, self.tweaks):
            c.disabled = busy
            c.update()
        self._refresh_user_tools()

    async def send_followup(self, e):
        text = (self.composer.value or "").strip()
        if text:
            self.composer.value = ""
            self.composer.update()
            await self.send_text(text)

    async def send_text(self, text: str):
        if self.busy or not self.conv or self._need_key():
            return
        if self.editing_index is not None:      # replace the message being edited (and the reply to it)
            index, self.editing_index = self.editing_index, None
            self._cut_from(index)
            self.show_chat(self.conv)
        self.conv.messages.append({"role": "user", "content": text})
        self._add_to_thread(self._user_bubble(text, index=len(self.conv.messages) - 1))
        self.thread.update()
        await self.reply()

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

    async def reply(self):
        conv = self.conv
        self.stop_requested = False
        self._set_busy(True)
        bubble = self._assistant_card("")
        md: ft.Markdown = bubble.data["md"]
        self._add_to_thread(bubble)
        self.thread.update()
        await self._scroll_to_end()      # if they were looking further up (at a new picture, say), follow the reply
        got_text = asyncio.Event()
        cycler = asyncio.create_task(self._cycle_status(conv, got_text))
        text, last_paint, error = "", 0.0, None
        try:
            async for chunk in self.chef.stream_chat(conv.chat_messages(), self.model, self.effort):
                if self.stop_requested or self.conv is not conv:
                    break
                if chunk.kind == "text":
                    if not text:
                        got_text.set()
                        self._set_status("Writing it up...")
                    text += chunk.text
                    if time.monotonic() - last_paint > 0.12:
                        md.value, last_paint = text, time.monotonic()
                        md.update()
        except api.ApiError as err:
            error = str(err)
        finally:
            got_text.set()
            cycler.cancel()
        if self.conv is not conv:      # user left the screen; keep what we got
            if text:
                conv.messages.append({"role": "assistant", "content": text})
                conv.title = extract_title(text) or conv.title
                self.history.save(conv)
            self.busy = False
            return
        if text:
            md.value = text
            md.update()
            conv.messages.append({"role": "assistant", "content": text})
            index = len(conv.messages) - 1
            self.cards[index] = bubble
            self._fill_actions(bubble, index, text, has_photo=False)
            bubble.update()
            conv.title = extract_title(text) or conv.title
            self.title_text.value = conv.title
            self.title_text.update()
            self.history.save(conv)
        elif conv.messages and conv.messages[-1]["role"] == "user" and len(conv.messages) > 2:
            unsent = conv.messages.pop()["content"]    # nothing came back: give the follow-up back to retry
            self.show_chat(conv)
            self.composer.value = unsent
        else:
            self.thread.controls.remove(bubble)
            self.thread.update()
        self._set_status(None)
        self._set_busy(False)
        if error:
            snack(self.page, error)
        elif self.stop_requested and text:
            snack(self.page, "Stopped. The partial recipe is kept; ask me to finish it if you like.")

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

    async def _share(self, title: str, text: str, photo: bytes | None, subject: str, body: str):
        """Open the system share sheet with the recipe PDF (and photo) attached."""
        try:
            pdf = await self._make_pdf(title, text, photo)
            files = [ft.ShareFile.from_bytes(pdf, mime_type="application/pdf", name=f"{export.file_stem(title)}.pdf")]
            if photo:
                files.append(ft.ShareFile.from_bytes(photo, mime_type=export.image_mime(photo),
                                                     name=f"{export.file_stem(title)}.{export.image_mime(photo).split('/')[1]}"))
            await self.share.share_files(files, subject=subject, text=body)
        except Exception:
            await self.clipboard.set(text)
            snack(self.page, "Sharing isn't available here, so I copied the recipe instead.")

    async def share_message(self, index: int, button=None):
        title, text, photo = self._message(index)
        await self._share(title, text, photo, title, f"{title}: a recipe from ChefBot")

    def _on_phone(self) -> bool:
        return not self.page.web and self.page.platform in (ft.PagePlatform.ANDROID, ft.PagePlatform.IOS)

    async def _email_with_mail_app(self, title: str, text: str, photo: bytes | None):
        """On a phone: the share sheet, where the user picks their mail app. It gets the subject, the full recipe
        as the message, and the PDF and photo as attachments."""
        await self._share(title, text, photo, f"Recipe: {title}", export.email_text(title, text))

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
            sending.visible = True
            sending.update()
            problem.visible = False
            problem.update()
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
                sending.visible = False
                sending.update()
                problem.value, problem.visible = _email_error(err), True
                problem.update()
                return
            self.page.pop_dialog()
            snack(self.page, f"Sent to {to}.")

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

        actions = [ft.TextButton("Cancel", on_click=lambda _: self.page.pop_dialog())]
        if can_send:
            actions += [ft.TextButton("Use my mail app", on_click=open_mail_app),
                        ft.FilledButton("Send", icon=ft.Icons.SEND, on_click=send)]
        else:
            if self.dev_mode:
                actions.append(ft.TextButton("Set up sending", on_click=settings))
            actions.append(ft.FilledButton("Open in mail app", icon=ft.Icons.OPEN_IN_NEW, on_click=open_mail_app))
        self.page.show_dialog(ft.AlertDialog(
            title=heading("Email this recipe", 22),
            content=ft.Column([ft.Text(title, weight=ft.FontWeight.W_600), to_field, remember, note, sending,
                               problem],
                              tight=True, spacing=14, width=420),
            actions=actions))

    async def make_picture(self, index: int, button=None):
        if self.busy:
            snack(self.page, "Hang on, I'm still cooking.")
            return
        if self._need_key():
            return
        conv = self.conv
        title, text, _ = self._message(index)
        self._set_busy(True)
        self._set_status("Plating it up for the camera...")
        try:
            image = await self.chef.dish_photo(title)
        except api.ApiError as err:
            snack(self.page, str(err))
            return
        finally:
            self._set_status(None)
            self._set_busy(False)
        self.history.save_photo(conv, index, image)
        self.history.save(conv)
        if self.conv is conv and index in self.cards:
            c = self.cards[index]
            slot: ft.Container = c.data["photo"]
            slot.content = ft.Image(src=image, fit=ft.BoxFit.COVER, border_radius=18, height=300)
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
        return str(err)
    if isinstance(err, smtplib.SMTPAuthenticationError):
        return "The mail server didn't accept the address and app password. Check them in Settings."
    if isinstance(err, (smtplib.SMTPRecipientsRefused,)):
        return "The mail server refused that address."
    return f"Couldn't send the email ({type(err).__name__}: {err})."


async def main(page: ft.Page):
    await ChefBotApp(page).start()


if __name__ == "__main__":
    ft.run(main)
