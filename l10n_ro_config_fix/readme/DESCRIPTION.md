``l10n_ro_config`` (OCA) ascunde in Settings orice camp al carui `name` contine
substring-ul `"l10n_ro"`, din orice modul, atunci cand compania curenta nu are
`chart_template == "ro"` (`res.company._check_is_l10n_ro_record`). Acel criteriu
ignora `account_fiscal_country_id`, asa ca o companie romaneasca din punct de
vedere fiscal, dar care nu a comutat explicit pe `chart_template` "ro", pierde
tacit toate setarile `l10n_ro_*` definite de alte module (ex. tipul de export
ANAF, standardul de reevaluare valutara).

Acest modul largeste criteriul de "inregistrare romaneasca" folosit de
`l10n_ro_config` ca sa includa si `account_fiscal_country_id.code == 'RO'`,
fara sa modifice codul OCA.
