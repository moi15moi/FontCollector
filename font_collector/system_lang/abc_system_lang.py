from abc import ABC, abstractmethod


class ABCSystemLang(ABC):
    default_lang = "en"
    @staticmethod
    @abstractmethod
    def get_lang() -> str:
        """
        Returns:
            The system language code, formatted as BCP 47. Ex: "en"
            If the system language couldn't be found, it will fallback to "en"
        """
        pass
