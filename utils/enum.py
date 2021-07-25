from enum import Enum, EnumMeta


class EnumMeta(EnumMeta):
    def __contains__(cls, item):
        try:
            cls(item)
        except ValueError:
            return False
        else:
            return True

    def list(cls):
        return list(map(lambda c: c.value, cls))


class State(int, Enum, metaclass=EnumMeta):
    """Game states"""

    IDLE = 0
    READY = 1
    PLAYING = 2
    LAST = 3


class Mode(str, Enum, metaclass=EnumMeta):
    """Gamemodes"""

    BULLET = "bullet"
    BLITZ = "blitz"
    ULTRA_BULLET = "ultrabullet"
    SCRABBLE = "scrabble"

    @classmethod
    def time(cls, mode):
        if mode == cls.BULLET or mode == cls.SCRABBLE:
            return 60
        elif mode == cls.BLITZ:
            return 180
        elif mode == cls.ULTRA_BULLET:
            return 30
        else:
            raise ValueError("Invalid mode")

class Dictionary(str, Enum, metaclass=EnumMeta):
    """Dictionary types"""

    ENGLISH = "english"
    VIETNAMESE = "vietnamese"
    URBAN = "urban"
    MAL = "mal"
    FIFA = "fifa"

    @classmethod
    def to_str(cls, dict):
        if dict == cls.ENGLISH:
            return "English"
        elif dict == cls.VIETNAMESE:
            return "Vietnamese"
        elif dict == cls.URBAN:
            return "Urban Dictionary"
        elif dict == cls.MAL:
            return "MAL"
        elif dict == cls.FIFA:
            return "FIFA"
        else:
            raise ValueError("Invalid dictionary type")

    @classmethod
    def word(cls, dict):
        if dict == cls.ENGLISH:
            return "English word"
        elif dict == cls.VIETNAMESE:
            return "Vietnamese word"
        elif dict == cls.URBAN:
            return "Urban Dictionary phrase"
        elif dict == cls.MAL:
            return "anime name from MyAnimeList"
        elif dict == cls.FIFA:
            return "FIFA player name"
        else:
            raise ValueError("Invalid dictionary type")