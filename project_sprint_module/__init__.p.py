from . import models

# #if VERSION >= "18.0"
def post_init_hook(env):
    """Förladda sprint.module med alla installerade Odoo-moduler vid installation."""
    env["sprint.module"].import_installed_modules()
# #endif
