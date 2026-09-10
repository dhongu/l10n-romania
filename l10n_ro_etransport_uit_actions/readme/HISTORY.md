## 19.0.1.0.0 (2026-09-10)

- Initial release: delete, confirm and change-vehicle events for an existing UIT, with status polling.

## 19.0.1.1.0 (2026-09-10)

- Extension point `_get_parent()` on the event and the wizard, so the batch module can attach
  events to a transfer batch without duplicating the logic.
