import abc


class Validator(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def validate(self, data):
        pass
