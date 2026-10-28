# ChefBot

Tell it what's in your kitchen, get a real recipe, then keep refining it in conversation:
"no cucumber", "make it for six", "how would this have been made in 1817?"

ChefBot is the 2026 rewrite of [RecipeGPT](https://github.com/BPMData/RecipeGPT), a Streamlit app I wrote
entirely by hand in 2023–24. That repo stays as it was. The audiences, the regional cuisines with their classic
seasonings, and the dietary rules in `src/chefbot/prompts.py` are carried over from it.

## What's new

- **Memory.** A recipe is a conversation. Ask for changes and ChefBot rewrites the whole recipe with them applied.
- **Saved recipes.** Every conversation (and its dish photo) is kept on the device.
- **Runs anywhere.** One Python codebase ([Flet](https://flet.dev)) runs on desktop, in a browser, and as an
  Android app.
- **New models.** Recipes come from GLM 5.3 (Z.ai) through [OpenRouter](https://openrouter.ai), sent to Z.ai's
  own servers first. Kimi K3.1 Pro and GLM 5.3 Flash are in Settings. Ingredient photos are read by GLM 5.3 Flash;
  dish pictures come from Gemini 3.1 Flash Lite Image.
- **Fixed allergen rules.** "Free of major food allergens" now covers all nine U.S. allergens (FALCPA plus sesame,
  added by the FASTER Act), and dietary rules override a cuisine's classic ingredients.
- **"Never use..." is remembered** between recipes and restarts (an allergy doesn't go away) until you clear it.
- **Under every reply:** Copy (as Markdown), Save as PDF, Save as web page (.html), Email, Share, and
  Picture this dish. Each acts on that reply only.
- **Email** uses your own mail app, no setup needed. On a phone it opens the share sheet with the whole recipe
  and the PDF and photo attached; on a computer it opens a new message with the recipe text. A hidden developer
  setting (tap "Settings" 7 times) lets ChefBot send formatted emails itself through a small Google Apps Script
  relay or a Gmail app password ([docs/EMAIL.md](docs/EMAIL.md)).
- **Edit or delete your last message.** Edit puts it back in the box (nothing changes until you send); Delete
  has Undo.
- **The 1817 version (beta)** rewrites a dish as a period recipe, after a clear warning that AI invents history.
- **PDFs** keep Korean, Chinese and Japanese names: the matching Noto font is downloaded the first time it's
  needed (10–18 MB, once) and cached on the device.

## Run it

```bash
python3 -m venv .venv
.venv/bin/pip install "flet[all]==1.0.5" "httpx>=0.28" markdown fpdf2 pytest pypdf
.venv/bin/flet run src/main.py            # desktop window
.venv/bin/flet run --web src/main.py      # in a browser
```

The first launch asks for an OpenRouter API key (openrouter.ai/keys). It's stored only on the device. For
development you can set `OPENROUTER_API_KEY` instead.

## Tests

```bash
.venv/bin/python -m pytest                            # offline: prompts, titles, history, streaming
OPENROUTER_API_KEY=... .venv/bin/python tools/smoke.py  # live: a recipe, then a follow-up edit
```

## Android

```bash
.venv/bin/flet build apk
```

The first build downloads the Flutter SDK, Android SDK and a JDK (several GB). The APK lands in `build/apk/`;
copy it to the phone and sideload it.

## How the models were picked (Oct 2026)

Blind taste tests on random requests, judged by a model that wasn't competing:

| Setup | Score (1–10) | Time | Cost per recipe |
|---|---|---|---|
| GLM 5.3 Flash, low / medium thinking | 4.1 / 4.8 | ~20 s | $0.0005 |
| GLM 5.3 Flash, high | 5.6 | 32 s | $0.0007 |
| GLM 5.3, medium | 5.8 | 16 s | $0.005 |
| GLM 5.3, high | 5.3 | 22 s | $0.007 |
| Kimi K3.1 Pro, medium / high | 6.6 / 5.8 | 51 s / 92 s | $0.016 / $0.026 |

Beyond the cheapest settings it's a statistical tie, so the model and thinking level are user settings. On Z.ai's
own servers, GLM's default thinking is long enough that a small token cap produces blank recipes, so ChefBot
always sets thinking explicitly and allows 32,000 tokens.

## Layout

```
src/main.py              the app (home screen, recipe conversation, settings)
src/chefbot/prompts.py   audiences, cuisines, dietary rules, prompt text
src/chefbot/api.py       OpenRouter: streaming recipes, photo reading, dish pictures
src/chefbot/history.py   saved conversations and photos
src/chefbot/recipe.py    reading the "Recipe Title:" line
src/chefbot/export.py    Markdown, HTML page, PDF and email versions of a reply
tools/make_static_fonts.py  cuts the fixed-weight fonts PDFs use
src/assets/              logo and bundled fonts (Fraunces, DM Sans; SIL Open Font License)
```

ChefBot is an AI, not a dietitian. Double-check recipes yourself, and never rely on it for serious allergies.
