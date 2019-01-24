import abc


class Validator(metaclass=abc.ABCMeta):

    @classmethod
    @abc.abstractmethod
    def validate(cls, data):
        pass
