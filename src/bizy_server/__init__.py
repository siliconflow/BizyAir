from .modelhost import ModelHostServer

modelhost_server = ModelHostServer()
if modelhost_server:
    print("\n\n\033[92m[BizyAir]\033[0m Model hosting service initialized.\n\n")
