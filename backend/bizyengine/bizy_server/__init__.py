from .execution import upload_worker
from .server import BizyAirServer

bizy_server = BizyAirServer()

if bizy_server:
    print("\n\n\033[92m[BizyAir]\033[0m Model hosting service initialized.\n\n")
