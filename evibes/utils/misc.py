from importlib import import_module


def create_object(module_name, class_name, *args, **kwargs):
    module = import_module(module_name)

    cls = getattr(module, class_name)

    return cls(*args, **kwargs)
