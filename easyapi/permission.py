import abc
import functools


class AbcPermission(metaclass=abc.ABCMeta):

    @classmethod
    @abc.abstractmethod
    def check(cls, *args, **kwargs):
        """
        检查逻辑 可重载
        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def fail(cls):
        raise NotImplementedError

    @classmethod
    def permission(cls, *args, **kwargs):
        def f_wrapper(f):
            @functools.wraps(f)
            def wrapper(*k_args, **k_kwargs):
                if cls.check(*args, **kwargs):
                    return f(*k_args, **k_kwargs)
                else:
                    return cls.fail()
            return wrapper
        return f_wrapper
