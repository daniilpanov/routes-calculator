import pkgutil
from importlib import import_module


def api_discover(v: int = 1) -> list:
    routers = []
    pkg = import_module('src.api.v' + str(v))

    for api_pkg in pkgutil.iter_modules(pkg.__path__):
        module_name = f'src.api.v{v}.{api_pkg.name}'
        try:
            module = import_module(module_name)
        except (ModuleNotFoundError, AttributeError) as ex:
            raise ex

        for package_module in pkgutil.iter_modules(module.__path__):
            if not package_module.ispkg:
                try:
                    endpoints = import_module(module_name + '.' + package_module.name)
                    routers.append(endpoints.router)
                except (ModuleNotFoundError, AttributeError) as ex:
                    raise ex

    return routers
