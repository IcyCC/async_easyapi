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

    def permission(cls, f, *args, **kwargs):
        @functools.wraps(f)
        def wrapper(*f_args, **f_kwargs):
            if cls.check(*args, **kwargs):
                return f(*f_args, **f_kwargs)
            else:
                return cls.fail()
        return wrapper
