Modul tranzitoriu — conţinutul s-a mutat în `l10n_ro_customs_dvi`
=================================================================

Modulul DVI a fost redenumit în **`l10n_ro_customs_dvi`**, pentru alinierea la convenţia `l10n_ro_`
a repo-ului: era singurul din 39 de module fără acest prefix, deşi are `category: Localization` şi
`countries: ["ro"]`. Numele `l10n_ro_dvi` nu putea fi folosit — aparţine modulului OCA, cu care ne
excludem reciproc.

Modulul de faţă **nu mai conţine cod şi nici date**. Declară o singură dependenţă,
`l10n_ro_customs_dvi`, şi există pentru un singur motiv: manifestele care îl listează ca dependenţă
(de exemplu addon-uri custom de client) continuă să se încarce fără să fie modificate.

Ce se întâmplă la actualizare
-----------------------------

Pe o bază unde modulul vechi era instalat, înregistrările din `ir_model_data` (view-uri, acţiuni,
meniu, ACL) sunt preluate automat de `l10n_ro_customs_dvi`, printr-un `pre_init_hook` care rulează
înainte de încărcarea datelor. Fără acest pas ar rezulta duplicate — două acţiuni şi două meniuri
„DVI" în interfaţă. Nu e nevoie de nicio intervenţie manuală.

Numele modulului din `ir_module_module` **nu** se schimbă, tocmai ca stub-ul de faţă să îşi păstreze
rândul lui şi să rămână instalabil.

> ⚠️ **Durata de viaţă: până la portarea pe 20.0.**
> Acest modul **nu se portează pe 20.0**. La portare se actualizează manifestele care îl declară ca
> dependenţă, direct pe `l10n_ro_customs_dvi`, iar stub-ul se abandonează pe 19.0.
> Decizie din 2026-09-23 — vezi `l10n_ro_ent/readme/roadmap/ROADMAP_dvi.md` §1.

Pentru module noi, depindeţi direct de `l10n_ro_customs_dvi`.
