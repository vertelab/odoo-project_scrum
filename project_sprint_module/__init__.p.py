from . import models


def post_init_hook(env):
    """Scanna filsystemet och säkerställ access-regler."""
    env["sprint.module"].scan_filesystem()
    _ensure_access_rules(env)


def _ensure_access_rules(env):
    """Säkerställ att access-regler finns för sprint.module och sprint.repo."""
    for model_name, group_xmlid in [
        ("sprint.module", "base.group_user"),
        ("sprint.module", "project.group_project_manager"),
        ("sprint.repo", "base.group_user"),
        ("sprint.repo", "project.group_project_manager"),
    ]:
        model = env["ir.model"].search([("model", "=", model_name)], limit=1)
        if not model:
            continue
        group = env.ref(group_xmlid, raise_if_not_found=False)
        if not group:
            continue
        name = f"{model_name}.{group_xmlid.split('.')[-1]}"
        if not env["ir.model.access"].search([("name", "=", name)], limit=1):
            env["ir.model.access"].create({
                "name": name,
                "model_id": model.id,
                "group_id": group.id,
                "perm_read": True,
                "perm_write": True,
                "perm_create": True,
                "perm_unlink": True,
            })
