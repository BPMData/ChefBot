/**
 * ChefBot mail relay: sends recipe emails from the Google account this script runs under.
 * Setup: docs/EMAIL.md. The app POSTs JSON here; the shared secret keeps strangers from using it.
 *
 * Script properties:
 *   RELAY_SECRET  required. Long random text; the same value goes in ChefBot's Settings.
 */
var MAX_PER_DAY = 40;        // a gmail.com account can send about 100 emails a day; stay well under it
var MAX_BYTES = 20 * 1024 * 1024;

function doGet() {
  return json_({ ok: true, hello: 'ChefBot mail relay' });
}

function doPost(e) {
  try {
    if (!e || !e.postData || e.postData.contents.length > MAX_BYTES) return json_({ ok: false, error: 'Too big.' });
    var req = JSON.parse(e.postData.contents);
    var props = PropertiesService.getScriptProperties();
    var secret = props.getProperty('RELAY_SECRET');
    if (!secret) return json_({ ok: false, error: 'The relay has no RELAY_SECRET set yet.' });
    if (req.secret !== secret) return json_({ ok: false, error: 'Wrong relay secret.' });
    if (!/^[^@\s,;]+@[^@\s,;]+\.[^@\s,;]+$/.test(req.to || '')) return json_({ ok: false, error: 'That email address looks wrong.' });

    var lock = LockService.getScriptLock();
    lock.waitLock(10000);
    try {
      var today = 'day:' + Utilities.formatDate(new Date(), 'UTC', 'yyyy-MM-dd');
      var sent = Number(props.getProperty(today) || 0);
      if (sent >= MAX_PER_DAY) return json_({ ok: false, error: 'The relay has sent its ' + MAX_PER_DAY + ' emails for today.' });

      var options = { name: 'ChefBot', htmlBody: String(req.html || ''), inlineImages: {}, attachments: [] };
      if (req.photo) {
        options.inlineImages.dish = Utilities.newBlob(Utilities.base64Decode(req.photo), req.photoType || 'image/png', 'dish');
      }
      if (req.pdf) {
        options.attachments.push(Utilities.newBlob(Utilities.base64Decode(req.pdf), 'application/pdf', req.pdfName || 'recipe.pdf'));
      }
      MailApp.sendEmail(req.to, String(req.subject || 'Recipe from ChefBot').slice(0, 200), String(req.text || ''), options);

      props.setProperty(today, String(sent + 1));
      props.getKeys().forEach(function (k) { if (k.indexOf('day:') === 0 && k !== today) props.deleteProperty(k); });
    } finally {
      lock.releaseLock();
    }
    return json_({ ok: true });
  } catch (err) {
    return json_({ ok: false, error: String(err && err.message || err) });
  }
}

/** Run from the editor once: asks for permission and sends a test email to this account. */
function checkSetup() {
  var secret = PropertiesService.getScriptProperties().getProperty('RELAY_SECRET');
  if (!secret || secret.length < 20) throw new Error('Add a script property RELAY_SECRET (20+ random characters) first.');
  var me = Session.getEffectiveUser().getEmail();
  MailApp.sendEmail(me, 'ChefBot relay works', 'If you can read this, the ChefBot mail relay is set up. ' +
    'Emails left today: ' + MailApp.getRemainingDailyQuota());
  Logger.log('OK: test email sent to ' + me + '. Now deploy it as a web app (docs/EMAIL.md step 3).');
}

function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
