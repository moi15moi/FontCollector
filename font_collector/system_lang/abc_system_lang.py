from abc import ABC, abstractmethod


class ABCSystemLang(ABC):
    default_lang = "en"
    @staticmethod
    @abstractmethod
    def get_lang() -> str:
        """
        Return an str of the system language. Ex: "en"
        If the system language couldn't be found, it will fallback to "en"
        """
        pass