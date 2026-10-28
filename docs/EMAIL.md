# Email setup

By default ChefBot needs no setup to email a recipe. On a phone, the Email button opens the share sheet: pick your
mail app and it gets a draft with the subject, the whole recipe, and the PDF (and dish photo) attached. On a
computer it opens a new message in your mail app with the whole recipe (mail links can't carry attachments, so
save the PDF and attach it yourself).

Everything below is an optional **developer setting** that lets ChefBot send a formatted email itself. It's
hidden: open **Settings** and tap the word "Settings" at the top 7 times (again to hide it). Then the Email
button sends directly, and "Use my mail app" is still there. Two ways:

## Recommended: the ChefBot mail relay (about 10 minutes, once)

A tiny Google Apps Script that sends the email from your Google account. It works on any network, and no
password is stored in the app: ChefBot only knows the script's web address and a secret phrase. It's the same
setup as OverBoard's report relay.

### 1. Make the script

Sign in to Google as the account the emails should come from (a spare Gmail account works well).
A private/incognito window avoids mixing up accounts.

1. Go to [script.google.com](https://script.google.com) ▸ **New project**. Rename it (top left) to
   `ChefBot mail relay`.
2. Delete what's in `Code.gs`, paste in all of [`tools/mail-relay.gs`](../tools/mail-relay.gs), and press **Save**.
3. In ChefBot, turn on developer mode (above), then **Settings ▸ Email sending ▸ Generate** next to *Relay secret*. That makes a random secret and copies
   it to the clipboard.
4. Back in the script: **Project Settings** (gear icon) ▸ **Script properties** ▸ **Add script property**.
   Name: `RELAY_SECRET`, value: paste the secret. **Save script properties**.

### 2. Check it

In the **Editor** (`< >`), choose **checkSetup** in the function menu and press **▶ Run**. Google asks for
permission: choose the account, then **Advanced ▸ Go to ChefBot mail relay (unsafe) ▸ Allow**. ("Unsafe" only means
Google hasn't reviewed this script. It's your own script in your own account.) A test email arrives in that inbox.

### 3. Put it online

1. **Deploy ▸ New deployment** ▸ gear next to *Select type* ▸ **Web app**.
2. **Execute as:** *Me*. **Who has access:** *Anyone*. (The secret is what keeps others out.)
3. **Deploy** and copy the **Web app URL** (ends in `/exec`).
4. In ChefBot: **Settings ▸ Email ▸ Relay web address**: paste it. **Save**.

Opening the URL in a browser should show `{"ok":true,"hello":"ChefBot mail relay"}`.

Limits: 40 emails a day (a gmail.com account allows about 100). Change `MAX_PER_DAY` in the script to adjust.
To change the script later: **Deploy ▸ Manage deployments ▸ ✏️ ▸ Version: New version ▸ Deploy** (same URL).

## Alternative: a Gmail app password

Fill in *Send from* and *Gmail app password* in Settings. The app password must be made **on the same account**
as *Send from* (myaccount.google.com/apppasswords; it needs 2-Step Verification, and Google doesn't offer it for
some accounts). Some networks also block outgoing mail. If the relay is set up, ChefBot uses the relay instead.
