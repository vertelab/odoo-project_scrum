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

## Porteringsstatus

18.0 är baseline. 19.0/20.0 visar om p-filen har ett villkor för utgåvan
— inte om grenen finns. Blockerare är `depends` som saknas i 20.0
(kärna + alla 20.0-grenar).

| Modul | Beskrivning | Manifest | p-fil | 19.0 | 20.0 | Blockerare |
|---|---|---|---|---|---|---|
| project_scrum | Using Scrum to plan the work in teams | 1.24 | 20 | — | ✓ | — |
| project_scrum_ai | Add powerbox for User Stories | 0.3 | 6 | — | — | — |
| project_scrum_external_tickets | External Tickets for Project Scrum. | 1.0.0 | 5 | — | — | — |
| project_scrum_portfolio | Adding Portfilio management to Project Scrum. | 1.0 | 6 | — | — | — |
| project_sprint_module | Adds new page for module list. | 1.24 | 11 | — | — | — |
| project_task_id | Adds Id to task. | 1.2.0 | 1 | — | ✓ | — |
| project_task_weight | Measure the scope of the activity | 1.0 | 5 | — | — | — |
