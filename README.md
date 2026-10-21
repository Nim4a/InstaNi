<p align="center">
  <img src="preview.png" alt="InstaNi app icon" width="140">
</p>

# InstaNi

A personal, auto-built rebrand of the InstaPro Instagram mod. One GitHub Action takes the latest SamMods build, renames it to **InstaNi** with a new icon pack, re-signs it with the AOSP test key, and publishes the APK as a release.

[English](#english) · [فارسی](#فارسی)

## English

### Why the AOSP key

InstaPro is signed with the public AOSP test key. InstaNi is re-signed with the *same* key so the signature check inside the mod still passes — that is what keeps existing sessions logged in instead of forcing a fresh login.

### How the build works

```
Actions → Build InstaNi → Run workflow  (or push update-trigger.txt)
                  │
                  ▼
        download InstaPro APK  (INSTAPRO_URL secret, or the URL you paste)
                  │
                  ▼
     assemble_one.py  ·  axml_edit.py
     - rename package label → InstaNi
     - replace launcher icon pack (build/igicon/*)
     - keep the Instagram core untouched
                  │
                  ▼
     re-sign with build/certs/testkey-nopass.p12 (AOSP key)
                  │
                  ▼
     GitHub Release → out/InstaNi-latest.apk
```

| File | Role |
|---|---|
| `.github/workflows/ci.yml` | The whole build pipeline |
| `assemble_one.py` | Repacks and re-signs the APK |
| `axml_edit.py` | Edits `AndroidManifest.xml` (label, package name) |
| `build/igicon/` | Per-dpi launcher icon sets (legacy + adaptive) |
| `build/certs/testkey-nopass.p12` | AOSP test key — same as upstream |
| `update-trigger.txt` | Push it to trigger a build without opening Actions |

### Build it

1. **Actions → Build InstaNi → Run workflow**, paste the URL of the latest `InstaPro vXX By.SamMods.apk`, or set an `INSTAPRO_URL` secret first (Settings → Secrets and variables → Actions).
2. Wait a few minutes. `out/InstaNi-latest.apk` is published as a GitHub Release.
3. Install over the existing InstaNi icon — your account phone number is preserved.

> Personal build for my own phone. Not affiliated with Instagram, InstaPro or SamMods.

---

## فارسی

### InstaNi — آپدیت خودکار

**چرا کلید AOSP؟** امضا همیشه با کلید تست `AOSP` (یکسان با اصل SamMods) انجام می‌شود تا چک امضای بومی مود پاس شود و لاگ‌اوت ایجاد نکند.

**ساخت:**

1. دکمه **Actions → Build InstaNi → Run workflow** را بزن (یا فایل `update-trigger.txt` را در main پوش کن تا خودکار شروع شود).
2. **URL** آخرین فایل اینستاگرام مود (معمولاً `InstaPro vXX By.SamMods.apk`) را وارد کن، یا از پیش در **Settings → Secrets and variables → Actions** یک secret به نام `INSTAPRO_URL` تعریف کن.
3. صبر کن؛ پس از چند دقیقه فایل `out/InstaNi-latest.apk` به‌صورت یک **GitHub Release** منتشر می‌شود.

بعد از انتشار، فقط روی آیکون `InstaNi` نصب کن — با همان شماره حفظ می‌شود.

مدیریت تبلیغات سازنده، پاپ‌آپ آپدیت و قفل PIN توسط همین پچ‌ها انجام می‌شود؛ هسته اینستاگرام دست‌نخورده می‌ماند.
