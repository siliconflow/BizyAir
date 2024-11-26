import threading

from .execution import upload_worker
from .server import BizyAirServer

bizy_server = BizyAirServer()
# deprecated
threading.Thread(
    target=upload_worker,
    daemon=True,
    args=(bizy_server, bizy_server.upload_queue),
).start()
if bizy_server:
    print("\n\n\033[92m[BizyAir]\033[0m Model hosting service initialized.\n\n")
