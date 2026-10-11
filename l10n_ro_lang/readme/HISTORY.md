## 20.0.0.0.5 (2026-10-12)

- Migration to 20.0. `get_nearest_lang` keeps its signature and the language lookup in
  `http_routing` (`_match`, `res.lang._get_frontend`) behaves as in 19.0, so the override
  is unchanged; the test takes the website from `base.default_website` (the `website`
  model now lives in `base`).

## 19.0.0.0.5 (2026-10-11)

- Romanian is chosen for visitors from Romania only when it is an active language of the website; otherwise every website page failed with HTTP 500 (`TypeError: Expected bytes` when setting the `frontend_lang` cookie).

## 19.0.0.0.4 (2026-10-09)

- Odoo Apps banner (`static/description/main_screenshot.png`), generated from `banner.json`.

## 19.0.0.0.3 (2026-09-30)

- Own module icon in the flat style of the Terrabit modules, instead of the missing or generic one.
