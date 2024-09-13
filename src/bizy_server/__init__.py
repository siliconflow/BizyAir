import threading

from .execution import upload_worker
from .modelhost import ModelHostServer

modelhost_server = ModelHostServer()
threading.Thread(
    target=upload_worker,
    daemon=True,
    args=(modelhost_server, modelhost_server.upload_queue),
).start()
if modelhost_server:
    print("\n\n\033[92m[BizyAir]\033[0m Model hosting service initialized.\n\n")
