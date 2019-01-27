import abc


class AbcValidator(metaclass=abc.ABCMeta):

    @classmethod
    @abc.abstractmethod
    def validate(cls, data):
        pass
