import pkgutil
from importlib import import_module


def api_discover() -> list:
    routers = []
    pkg = import_module("back_admin.api")

    for api_pkg in pkgutil.iter_modules(pkg.__path__):
        module_name = f"back_admin.api.{api_pkg.name}"
        try:
            endpoints = import_module(module_name)
            routers.append(endpoints.router)
        except (ModuleNotFoundError, AttributeError) as ex:
            raise ex

    return routers
