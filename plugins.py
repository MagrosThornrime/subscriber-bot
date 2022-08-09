from my_plugins.plugins_abc import Plugin


plugins = {}


def register(name: str = ""):
    def wrapper(func: callable):
        plugin_name = name if name else func.__name__
        plugins[plugin_name] = func
        return func
    return wrapper


def get_plugins() -> dict[str, Plugin]:
    return plugins
