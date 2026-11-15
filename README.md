# odoo-project_scrum — gren 19.0

> **Denna gren är avsiktligt tom.** Modulerna är INTE portade till Odoo 19.
> Grenen finns så att dev-miljöer (`hansolo19`) kan klona den utan att falla,
> men den påstår ingenting om att koden är portad.

## Baseline

| | |
|---|---|
| Källa | `20.0` |
| Moduler | **7** |
| Grenar i repot | `10.0`, `12.0`, `13.0`, `14.0`, `14.0-skogstyrelsen-optional-hide`, `14.0_project_scrum_translations`, `16.0`, `17.0`, `18.0`, `20.0`, `6.1`, `8.0`, `WIP-project_task_and-project_weight`, `master`, `master10`, `project_scrum_improvements` |

## Moduler

- `project_scrum`
- `project_scrum_ai`
- `project_scrum_external_tickets`
- `project_scrum_portfolio`
- `project_sprint_module`
- `project_task_id`
- `project_task_weight`

## Blockerare

✅ Inga externa beroenden saknas i Odoo 19-kärnan eller OCA 19.0.

Modulerna kan troligen portas utan att vänta på externa bidrag.

## Nästa steg

Portering sker på `*-pfile`-maskin med versionsagnostisk kod
(`.p.py` / `.p.xml`). Se `/skill:odoo-pfiles`.
