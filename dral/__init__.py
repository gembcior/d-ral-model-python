# pkgutil-style namespace package: this "dral" top-level package is shared
# with the separate d-ral generator distribution (dral/core, dral/adapter, ...).
# Keep this file identical across both distributions - see d-ral/dral/__init__.py.
__path__ = __import__("pkgutil").extend_path(__path__, __name__)
