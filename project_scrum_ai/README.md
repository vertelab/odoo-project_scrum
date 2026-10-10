# AI for project_scrum (project_scrum_ai)

AI-brygga för `project_scrum` — powerbox-coworkers för User Stories +
Scrum-master-agent för Project.

## Powerbox-coworkers (oförändrade)

| Coworker | Roll |
|----------|------|
| **Enterprise Architect — User Stories** | Förvandlar verbala processbeskrivningar till användarberättelser + Mermaid-diagram |
| **Enterprise Architect — Projekt** | Definierar projektbeskrivning och mål från verbala beskrivningar |

Båda är `powerbox`-coworkers med egen metod (arkitektur, inte
projektgenomförande). De slås **inte** ihop med Project — de svarar på
"vad ska vi bygga och varför", Project svarar på "hur genomför vi det".

## Agent — Scrum-master

Sedan version 0.4 levereras sprint-förmågan som en **specialist-agent**
länkad till coworkern **Project** (`project_ai`).

| Agent | Roll | Verktyg | Skills |
|-------|------|---------|--------|
| **Scrum-master** | Backlog och nedbrytning, kapacitet och velocity, sprint-hälsokontroll (försenat, oassignat, blockerare) | task_get, task_update_fields, task_set_status, cost_context_get/set | skill_cost_context |

Länkrad: `coworker_agent_scrum_master` →
`project_ai.coworker_project_task_manager`, `role=member`, `sequence=30`.

### Mönstret — additiv förmågeexpansion

`project_scrum_ai` äger sin agent och sin länkrad. Avinstalleras modulen
försvinner Scrum-mastern — Project och de andra agenterna förblir intakta.
`depends` innehåller `project_ai` eftersom länkraden refererar coworkerns
xmlid.

Se `project_ai/docs/additiv-formageexpansion.md`.

## Gränsdragning mellan agenterna

| Fråga | Agent |
|-------|-------|
| Vad ska lösas? Är problemställningen komplett? | Projektanalytiker |
| Hur bryter vi ner det i sprintar och moment? | Scrum-master |
| Vilka krav ställer PRD-dokumentet? | PRD-analytiker |
| Hur bygger vi det i Odoo? | Odoo-utvecklare |

## Odoo 18-regler

- Vyer: `list` (aldrig `tree`), inga defensiva `<delete>`.
- Uppgradering: `--update project_scrum_ai` (inte `--init`).
