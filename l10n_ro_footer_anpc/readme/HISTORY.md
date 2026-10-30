## 19.0.0.0.6 (2026-10-30)

- Migrate recognized legacy SAL/SOL blocks in website-specific copies without
  resetting the website layout or reactivating disabled views. Preserve unknown
  customized badge contents and log them for manual review.
- Render the managed SAL badge through a shared template so later module updates
  update its image and link even when a website keeps a customized footer layout.
- Verify migration idempotency, native repeated view loading, inactive copies,
  preserved custom contents and future shared-template changes with Odoo ORM tests.

## 19.0.0.0.5 (2026-10-22)

- Odoo Apps banner title: *ANPC footer* (was *ANPC Website Footer*), the same as the module name.

## 19.0.0.0.4 (2026-10-20)

- Order ANPC 270/2026 (Monitorul Oficial no. 420 of 19 May 2026): only the SAL
  pictogram remains, linked to `https://reclamatiisal.anpc.ro/` and shown in a
  250 x 50 px box with the official ANPC image. The SOL pictogram and the link to the
  EU ODR platform, closed on 20 July 2025, are removed.
- The ANPC block follows the copyright row (`col-md`, Bootstrap 5 `text-md-end`
  instead of the Bootstrap 4 `text-sm-right`); the image gets `alt` text and a valid
  `width`; the link gets `rel="noopener"`.
- Test that the homepage rendered for a public visitor shows the SAL link.

## 19.0.0.0.3 (2026-10-09)

- Odoo Apps banner (`static/description/main_screenshot.png`), generated from `banner.json`.

## 19.0.0.0.2 (2026-09-30)

- Own module icon in the flat style of the Terrabit modules, instead of the missing or generic one.
