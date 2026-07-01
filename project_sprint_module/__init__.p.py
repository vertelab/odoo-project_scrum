from . import models

# #if VERSION >= "18.0"
def post_init_hook(env):
    """Scanna filsystemet efter odoo-* repon och skapa sprint.module-poster."""
    env["sprint.module"].scan_filesystem()
# #endif
