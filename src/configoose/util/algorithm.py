from functools import partial, singledispatch
import types

_property = property


@singledispatch
def property(func):
    return _property(func)


class algorithm_meta(type):
    def __new__(meta, class_name, bases, new_attrs):
        cls = type.__new__(meta, class_name, bases, new_attrs)
        return cls

    def __call__(cls, *args, **kwargs):
        instance = cls.__new__(cls)
        instance.kwargs = kwargs
        instance.__dict__.update(kwargs)
        return instance.run(*args)

    def __get__(cls, obj, objtype=None):
        # This allows to use the algoritm type as a method
        if obj is None:
            return cls
        return partial(_algorithm_as_method, cls, obj)

    # This makes 'property' available through the algorithm class
    # to allow client code to just import algorithm.
    property = staticmethod(property)


def _algorithm_as_method(cls, obj, *args, **kwargs):
    instance = cls.__new__(cls)
    instance.o = obj
    instance.kwargs = kwargs
    instance.__dict__.update(kwargs)
    return instance.run(*args)


@property.register(algorithm_meta)
def _(cls):
    return _property(partial(_algorithm_as_method, cls))


class algorithm(metaclass=algorithm_meta):
    def run(self, *args):
        return self
