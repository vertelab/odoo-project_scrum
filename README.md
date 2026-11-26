# project_scrum

... adds scrum functionality (like User Stories, sprints, scrum roles, etc) to the default Odoo project management module (which it also depends on naturally).

In order to run "project_scrum" you need to have the pyhton library "Beautiful Soup" (python-bs4) installed on your system.
You can do that by the following command: sudo apt-get install python-bs4

The project_scrum module depends on an OCA module (https://github.com/OCA/project/tree/14.0/project_category). This will replace the project category model. The user can create a Task from Sprint by clicking on the Action in the formview. This task is intended to be used as test-case.


```
# https://www.youtube.com/watch?v=a5y50EwZj8I
# Project Scrum for Odoo 8.
# Mars 18, 2019
```

## Porteringsstatus — Odoo 19.0

Den här grenen är Odoo 19.0. Tabellen beskriver bara 19.0.

| Modul | Funktionsbeskrivning | Porteringsstatus |
|---|---|---|
| `project_scrum` | Scrum i projekt: user stories, sprintar, scrum-roller | installerad · 20 p-filer |
| `project_scrum_ai` | Powerbox för user stories + mermaid-graf | blockerad — `ai_agent_core` kräver `web_pwa_push`, `web_mermaid_ai` saknar 19.0-gren; `installable: False` |
| `project_scrum_external_tickets` | Externa ärenden kopplade till user stories | installerad · 6 p-filer |
| `project_scrum_portfolio` | Portfölj- och timebox-hantering | installerad · 6 p-filer |
| `project_sprint_module` | Sida för modullista per sprint | installerad · 11 p-filer |
| `project_task_id` | Löpnummer på uppgifter (globalt eller per projekt) | installerad · 2 p-filer |
| `project_task_weight` | Omfattningsmått (weight) på uppgifter | installerad · 5 p-filer |

## Vad "portad" betyder

Installerad i `pfile_<utgåva>` utan ERROR/CRITICAL, minst en testmetod grön,
och p-filerna i synk mellan 18.0/19.0/20.0. Att modulen finns i filträdet
räknas inte.

## Grind

`.pfiles-ci` deklarerar `editions: 18.0 19.0 20.0` och
`deps: odoo-web odoo-project`. Fem CI-filer krävs (`.github/workflows/pfiles.yml`
plus fyra skript i `.github/`); saknas någon fäller `editions`-jobbet med
`exit 2` innan någon modul granskats.

Lokal förkontroll: `git config core.hooksPath .githooks`.
