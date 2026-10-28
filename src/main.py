"""ChefBot: tell it what's in your fridge, get a recipe, then keep refining it in conversation."""
import asyncio
import os
import random
import time
from datetime import datetime

import flet as ft

from chefbot import api, prompts
from chefbot.history import Conversation, History
from chefbot.recipe import extract_title

PREF_KEY = "chefbot.openrouter_key"
PREF_MODEL = "chefbot.model"
PREF_EFFORT = "chefbot.effort"
PREF_THEME = "chefbot.theme"

# ---------------------------------------------------------------- look and feel

FONTS = {   # open-licensed (OFL) Google Fonts, bundled in src/assets/fonts with their licenses
    "Fraunces": "fonts/Fraunces.ttf",
    "DM Sans": "fonts/DMSans.ttf",
}
HEADING_FONT, BODY_FONT = "Fraunces", "DM Sans"
SEED = "#E8590C"
GRADIENT = ["#FF8A3D", "#E8452C"]
BG_LIGHT, BG_DARK = "#FFF6EC", "#110E0C"
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
     "techniques, and note any modern substitutions."),
    (ft.Icons.ECO, "Vegetarian", "Make it vegetarian."),
    (ft.Icons.TIMER, "Faster", "Make it faster, under 30 minutes, without losing what makes it good."),
    (ft.Icons.SHOPPING_CART, "Shopping list",
     "Give me a shopping list for this, grouped by store section. Don't rewrite the recipe."),
    (ft.Icons.WINE_BAR, "Pairing", "What should I drink with this? Don't rewrite the recipe."),
]
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
        self.show_home()      # draw first; saved settings arrive a moment later

        prefs = await self._load_prefs()
        self.key = (prefs.get(PREF_KEY) or os.environ.get("OPENROUTER_API_KEY", "")).strip()
        model, effort, theme = prefs.get(PREF_MODEL), prefs.get(PREF_EFFORT), prefs.get(PREF_THEME)
        self.model = model if model in api.MODELS else api.DEFAULT_MODEL
        self.effort = effort if effort in api.EFFORTS else api.DEFAULT_EFFORT
        self.theme = theme if theme in THEMES else "dark"
        p.theme_mode = THEMES[self.theme]
        self.chef = api.ChefBotAPI(self.key) if self.key else None
        p.update()
        if not self.key:
            self.open_settings(first_run=True)

    async def _load_prefs(self) -> dict:
        """Read saved settings. On a slow first load the storage service can take a few seconds to come up."""
        for attempt in range(4):
            try:
                return {k: await self.prefs.get(k) for k in (PREF_KEY, PREF_MODEL, PREF_EFFORT, PREF_THEME)}
            except RuntimeError:
                await asyncio.sleep(0.5 * (attempt + 1))
        return {}

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

        async def save(_):
            self.key = (key_field.value or "").strip()
            self.model, self.effort = model_dd.value or api.DEFAULT_MODEL, effort_dd.value or api.DEFAULT_EFFORT
            self.theme = (list(theme_seg.selected) or ["dark"])[0]
            for k, v in ((PREF_KEY, self.key), (PREF_MODEL, self.model), (PREF_EFFORT, self.effort),
                         (PREF_THEME, self.theme)):
                await self.prefs.set(k, v)
            self.chef = api.ChefBotAPI(self.key) if self.key else None
            self.page.theme_mode = THEMES[self.theme]
            self.page.pop_dialog()
            self.page.update()
            snack(self.page, "Settings saved." if self.key else "No API key yet: ChefBot can't cook without one.")

        intro = ("Paste an OpenRouter API key to get started (openrouter.ai/keys). It's stored only on this "
                 "device.") if first_run else "Your key is stored only on this device."
        self.page.show_dialog(ft.AlertDialog(
            modal=first_run, scrollable=True, title=heading("Settings", 22),
            content=ft.Column(tight=True, spacing=16, width=440, controls=[
                ft.Text(intro, size=13), key_field, ft.Row([model_dd]), ft.Row([effort_dd]),
                ft.Text("Appearance", size=13, color=ft.Colors.ON_SURFACE_VARIANT), theme_seg,
                ft.Text("Fridge photos are read by GLM 5.3 Flash; dish pictures come from Gemini 3.1 Flash Lite "
                        "Image.", size=12, color=ft.Colors.ON_SURFACE_VARIANT),
            ]),
            actions=[ft.TextButton("Cancel", on_click=lambda _: self.page.pop_dialog()),
                     ft.FilledButton("Save", on_click=save)],
        ))

    def _need_key(self) -> bool:
        if self.chef:
            return False
        self.open_settings(first_run=True)
        return True

    # ------------------------------------------------------------ home screen

    def _build_home_controls(self):
        self.ingredients = ft.TextField(
            hint_text="Potatoes, carrots, tomatoes...", multiline=True, min_lines=4, max_lines=8,
            filled=True, border=soft_border(16), capitalization=ft.TextCapitalization.SENTENCES, text_size=16)
        self.photo_btn = ft.FilledTonalButton("Snap my fridge instead", icon=ft.Icons.PHOTO_CAMERA_OUTLINED,
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
                               show_checkmark=False)
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
        self.padded = []
        self.page.appbar = None
        self._refresh_recent()
        body = ft.Column(spacing=18, horizontal_alignment=ft.CrossAxisAlignment.STRETCH, controls=[
            card(section_title(ft.Icons.KITCHEN, "What have you got?"), self.ingredients,
                 ft.Row([self.photo_btn])),
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
                                             compression_quality=85, dialog_title="Photo of your fridge or groceries")
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
        self.photo_btn.disabled, self.photo_btn.content = True, "Looking in your fridge..."
        self.photo_btn.update()
        try:
            found = await self.chef.read_ingredients(data, mime)
        except api.ApiError as err:
            snack(self.page, str(err))
            found = None
        finally:
            self.photo_btn.disabled, self.photo_btn.content = False, "Snap my fridge instead"
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
            snack(self.page, "Tell me some ingredients first (or snap your fridge).")
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
        self.padded = []
        self.title_text = heading(conv.title, 18)
        self.title_text.max_lines, self.title_text.overflow = 1, ft.TextOverflow.ELLIPSIS
        self.page.appbar = ft.AppBar(
            leading=ft.IconButton(ft.Icons.ARROW_BACK, tooltip="Back", on_click=lambda _: self.go_home()),
            title=self.title_text, bgcolor=ft.Colors.TRANSPARENT,
            actions=[
                ft.IconButton(ft.Icons.PHOTO_CAMERA_OUTLINED, tooltip="Picture of the dish",
                              on_click=self.make_picture),
                ft.IconButton(ft.Icons.CONTENT_COPY, tooltip="Copy recipe", on_click=self.copy_recipe),
                ft.IconButton(ft.Icons.IOS_SHARE, tooltip="Share recipe", on_click=self.share_recipe),
            ])
        self.thread = self._pad(ft.ListView(expand=True, spacing=16, auto_scroll=True), top=8, bottom=8)
        for i, m in enumerate(conv.messages):
            if m["role"] == "user":
                self.thread.controls.append(self._user_bubble(m.get("display") or m["content"]))
            elif m["role"] == "assistant":
                photo = None
                if str(i) in conv.photos:
                    path = self.history.photo_path(conv.photos[str(i)])
                    photo = path.read_bytes() if path.exists() else None
                self.thread.controls.append(self._assistant_card(m["content"], photo))
        self.status_text = ft.Text("", size=14, weight=ft.FontWeight.W_500, color=ft.Colors.ON_SURFACE_VARIANT)
        self.status = self._pad(ft.Container(
            ft.Row([ft.ProgressRing(width=18, height=18, stroke_width=2.5), self.status_text,
                    ft.TextButton("Stop", icon=ft.Icons.STOP_CIRCLE_OUTLINED, on_click=self._stop)], spacing=12),
            visible=False), top=4, extra=4)
        self.tweaks = ft.Row(scroll=ft.ScrollMode.AUTO, spacing=8, controls=[
            ft.Chip(label=label, leading=ft.Icon(icon, size=18),
                    on_click=lambda e, msg=msg: self.page.run_task(self.send_text, msg))
            for icon, label, msg in QUICK_TWEAKS])
        self.composer = ft.TextField(
            hint_text="Ask for changes: no cucumber, more garlic...", expand=True, multiline=True,
            min_lines=1, max_lines=5, shift_enter=True, on_submit=self.send_followup, filled=True,
            border=soft_border(26), capitalization=ft.TextCapitalization.SENTENCES)
        self.send_btn = ft.IconButton(ft.Icons.ARROW_UPWARD, tooltip="Send", on_click=self.send_followup,
                                      bgcolor=ft.Colors.PRIMARY, icon_color=ft.Colors.ON_PRIMARY)
        self.root.content = ft.Column(expand=True, spacing=0, controls=[
            self.thread,
            self.status,
            self._pad(ft.Container(ft.Column([self.tweaks, ft.Row([self.composer, self.send_btn])],
                                             spacing=10, tight=True)), top=8, bottom=12),
        ])
        self.page.update()

    def go_home(self):
        if self.busy:
            self.stop_requested = True
        self.show_home()

    def _user_bubble(self, text: str) -> ft.Control:
        return ft.Container(
            ft.Text(text, color=ft.Colors.WHITE, size=15, selectable=True),
            gradient=ft.LinearGradient(colors=GRADIENT, begin=ft.Alignment.TOP_LEFT, end=ft.Alignment.BOTTOM_RIGHT),
            border_radius=ft.BorderRadius(top_left=22, top_right=22, bottom_left=22, bottom_right=6),
            padding=ft.Padding(left=18, right=18, top=12, bottom=12),
            margin=ft.Margin(left=64, right=0, top=0, bottom=0))

    def _assistant_card(self, text: str, photo: bytes | None = None) -> ft.Container:
        md = ft.Markdown(text, selectable=True, extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                         md_style_sheet=md_style())
        parts: list[ft.Control] = []
        if photo:
            parts.append(ft.Image(src=photo, fit=ft.BoxFit.COVER, border_radius=18, height=300))
        parts.append(ft.Row([ft.Image(src="logo.svg", width=28, height=28),
                             ft.Text("ChefBot", weight=ft.FontWeight.W_700, font_family=HEADING_FONT, size=15)],
                            spacing=10))
        parts.append(md)
        c = card(*parts, padding=20)
        c.data = md
        return c

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

    async def send_followup(self, e):
        text = (self.composer.value or "").strip()
        if text:
            self.composer.value = ""
            self.composer.update()
            await self.send_text(text)

    async def send_text(self, text: str):
        if self.busy or not self.conv or self._need_key():
            return
        self.conv.messages.append({"role": "user", "content": text})
        self.thread.controls.append(self._user_bubble(text))
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

    async def reply(self):
        conv = self.conv
        self.stop_requested = False
        self._set_busy(True)
        bubble = self._assistant_card("")
        md: ft.Markdown = bubble.data
        self.thread.controls.append(bubble)
        self.thread.update()
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
            conv.title = extract_title(text) or conv.title
            self.title_text.value = conv.title
            self.title_text.update()
            self.history.save(conv)
        else:
            self.thread.controls.remove(bubble)
            if conv.messages and conv.messages[-1]["role"] == "user" and len(conv.messages) > 2:
                conv.messages.pop()     # let them resend the follow-up
            self.thread.update()
        self._set_status(None)
        self._set_busy(False)
        if error:
            snack(self.page, error)
        elif self.stop_requested and text:
            snack(self.page, "Stopped. The partial recipe is kept; ask me to finish it if you like.")

    def _latest_recipe(self) -> tuple[int, str] | None:
        if not self.conv:
            return None
        for i in range(len(self.conv.messages) - 1, -1, -1):
            m = self.conv.messages[i]
            if m["role"] == "assistant" and extract_title(m["content"]):
                return i, m["content"]
        return None

    async def copy_recipe(self, e):
        found = self._latest_recipe()
        if not found:
            snack(self.page, "No recipe yet.")
            return
        await self.clipboard.set(found[1])
        snack(self.page, "Recipe copied.")

    async def share_recipe(self, e):
        found = self._latest_recipe()
        if not found:
            snack(self.page, "No recipe yet.")
            return
        try:
            await self.share.share_text(found[1], subject=self.conv.title)
        except Exception:
            await self.clipboard.set(found[1])
            snack(self.page, "Sharing isn't available here, so I copied the recipe instead.")

    async def make_picture(self, e):
        found = self._latest_recipe()
        if not found or self.busy:
            snack(self.page, "No recipe yet." if not found else "Hang on, I'm still cooking.")
            return
        if self._need_key():
            return
        index, content = found
        conv = self.conv
        self._set_busy(True)
        self._set_status("Plating it up for the camera...")
        try:
            image = await self.chef.dish_photo(extract_title(content) or conv.title)
        except api.ApiError as err:
            self._set_status(None)
            self._set_busy(False)
            snack(self.page, str(err))
            return
        self.history.save_photo(conv, index, image)
        self.history.save(conv)
        self.busy = False
        if self.conv is conv:
            self.show_chat(conv)


async def main(page: ft.Page):
    await ChefBotApp(page).start()


if __name__ == "__main__":
    ft.run(main)
