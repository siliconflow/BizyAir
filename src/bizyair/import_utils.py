import importlib
import traceback
import platform

system = platform.system()


def check_module_availability(module_name):
    spec = importlib.util.find_spec(module_name)

    if spec:
        try:
            importlib.import_module(module_name)
        except ImportError as e:
            print(traceback.format_exc())
            return False
    else:
        return False

    return True
