import pkgutil
from importlib import import_module

from fastapi import APIRouter


def api_discover() -> list[APIRouter]:
    routers = []
    pkg = import_module("back_admin.api")

    for api_pkg in pkgutil.iter_modules(pkg.__path__):
        if api_pkg.name == "crud":
            continue

        module_name = f"back_admin.api.{api_pkg.name}"
        try:
            module = import_module(module_name)
        except (ModuleNotFoundError, AttributeError) as ex:
            raise ex

        if not getattr(module, "__path__", None):
            continue

        for package_module in pkgutil.iter_modules(module.__path__):
            if not package_module.ispkg:
                try:
                    endpoints = import_module(module_name + "." + package_module.name)
                    routers.append(endpoints.router)
                except (ModuleNotFoundError, AttributeError) as ex:
                    raise ex

    return routers


def crud_discover() -> list[APIRouter]:
    routers = []
    pkg = import_module("back_admin.api.crud")

    for api_pkg in pkgutil.iter_modules(pkg.__path__):
        module_name = f"back_admin.api.crud.{api_pkg.name}"
        try:
            module = import_module(module_name)
        except (ModuleNotFoundError, AttributeError) as ex:
            raise ex

        routers.append(module.crud().get_router())

    return routers
