import pkgutil
import importlib

for _, nombre_modulo, es_paquete in pkgutil.walk_packages(__path__, prefix=__name__ + "."):
    if not es_paquete:
        importlib.import_module(nombre_modulo)
