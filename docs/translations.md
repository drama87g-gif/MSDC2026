Translations and RTL Guide
--------------------------
Files:
- frontend/src/i18n/en.json
- frontend/src/i18n/ar.json

Adding translations:
1. Add keys to en.json and ar.json with matching keys.
2. Use useTranslation hook in React components: const { t } = useTranslation(); then t('key').

RTL support:
- When switching to Arabic, set document.dir = 'rtl' (done in AdmissionsPage).
- Ensure CSS uses logical properties (margin-inline-start, margin-inline-end) or add a small RTL stylesheet:
  body[dir="rtl"] { direction: rtl; }
  .container { text-align: right; }

Fonts:
- For Arabic, include a font that supports Arabic glyphs in index.html or via CSS.

Extending:
- Add translations for all UI strings across modules.
- For server-side messages, consider Django's gettext and compilemessages for backend translations.