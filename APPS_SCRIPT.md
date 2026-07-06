# Google Sheets logging — setup

The game logs each play to your sheet via a Google Apps Script Web App.

**Sheet:** https://docs.google.com/spreadsheets/d/1eDI_s8cI7Llzftq_E7sst9ufX-pY7QMmId5jMEariio/edit

## 1. Add the script

1. Open the sheet above.
2. Menu: **Extensions → Apps Script**.
3. Delete any placeholder code, paste the code below into `Code.gs`, and **Save**.

```javascript
// Sheets logger for KICK & WIN.
// Columns: Date | Email | Prize | utm_campaign | utm_source | utm_medium | utm_content
var SHEET_ID = '1eDI_s8cI7Llzftq_E7sst9ufX-pY7QMmId5jMEariio';
var SHEET_NAME = 'Sheet1'; // change if your tab has a different name

function doPost(e) {
  try {
    var p = (e && e.parameter) ? e.parameter : {};
    var ss = SpreadsheetApp.openById(SHEET_ID);
    var sheet = ss.getSheetByName(SHEET_NAME) || ss.getSheets()[0];

    // Add a header row once, if the sheet is empty.
    if (sheet.getLastRow() === 0) {
      sheet.appendRow(['Date', 'Email', 'Prize',
        'utm_campaign', 'utm_source', 'utm_medium', 'utm_content']);
    }

    var now = Utilities.formatDate(new Date(), 'Asia/Jakarta', 'yyyy-MM-dd HH:mm:ss');
    sheet.appendRow([
      now,
      p.email || '',
      p.prize || '',
      p.utm_campaign || '',
      p.utm_source || '',
      p.utm_medium || '',
      p.utm_content || ''
    ]);

    return ContentService
      .createTextOutput(JSON.stringify({ ok: true }))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService
      .createTextOutput(JSON.stringify({ ok: false, error: String(err) }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

// Optional: lets you open the /exec URL in a browser to confirm it's live.
function doGet() {
  return ContentService.createTextOutput('KICK & WIN logger is running.');
}
```

## 2. Deploy as a Web App

1. Top-right: **Deploy → New deployment**.
2. Click the gear icon → select type **Web app**.
3. Settings:
   - **Description:** `KICK & WIN logger`
   - **Execute as:** `Me`
   - **Who has access:** `Anyone`  ← required so the game (browser) can post to it
4. **Deploy** → authorize the script when prompted (allow access to your Google account/Sheets).
5. Copy the **Web app URL** — it ends in `/exec`.

## 3. Paste the URL into the game

In `index.html`, find:

```javascript
const SHEETS_ENDPOINT = "PASTE_YOUR_APPS_SCRIPT_WEB_APP_URL_HERE";
```

Replace the placeholder with your `/exec` URL. Save. Done.

## Notes

- The game posts with `mode: "no-cors"`, so the browser can't read the response — that's fine, the row still gets written. To confirm it works, play once and check the sheet.
- Each play writes one row when the result screen appears. Fields: local timestamp (Asia/Jakarta), email, prize won, and the four UTM params captured from the page URL.
- If you change the script later, use **Deploy → Manage deployments → Edit → New version** so the same `/exec` URL keeps working.
- **One email per game** is enforced client-side via `localStorage`. This blocks the same browser from replaying with a used email, but a determined user could clear storage or switch device/browser. If you need hard dedup, add a check in `doPost` that scans column B for an existing email before appending.
