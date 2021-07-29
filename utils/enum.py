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
            return "anime character's name from MyAnimeList"
        elif dict == cls.FIFA:
            return "FIFA player name"
        else:
            raise ValueError("Invalid dictionary type")

CTS = {'heal': 1, 'kill': 1, 'sub_time': 1, 'add_time': 1, 'poison': 3}
class Card(str, Enum, metaclass=EnumMeta):
    """Gamemodes"""

    HEAL = "heal"
    KILL = "kill"
    SUB_TIME = "sub_time"
    ADD_TIME = "add_time"
    POISON = "poison"
    @classmethod
    def add_effect(cls, card, player):
        player.effect_chain.append((card, CTS[card]))
    @classmethod
    def to_emoji(cls, card):
        if card == cls.HEAL:
            return ":adhesive_bandage:"
        elif card == cls.KILL:
            return ":dagger:"
        elif card == cls.POISON:
            return ":biohazard:"
    
    @classmethod
    def word(cls, card, cter, player_id):
        emj = cls.to_emoji(card)
        if card == cls.HEAL:
            return f'<@!{player_id}> + 1 :hearts: {emj}.\n'
        elif card == cls.KILL:
            return f'<@!{player_id}> - 1 :hearts: {emj}.\n'
        elif card == cls.ADD_TIME:
            return f'<@!{player_id}> + 10 seconds {emj}.\n'
        elif card == cls.SUB_TIME:
            return f'<@!{player_id}> - 10 seconds {emj}.\n'
        elif card == cls.POISON:
            return f'<@!{player_id}> has been poisoned {emj}.\n-7 seconds every turn, {cter} turn(s) remaining.\n'
        else:
            raise ValueError("Invalid card")

    @classmethod
    def process_effect(cls, player) -> str:
        message = ""
        teff_chain = []
        for card, cter in player.effect_chain:
            if card == cls.SUB_TIME:
                if player.time_left > 10:
                    player.time_left -= 10
            elif card == cls.ADD_TIME:
                player.time_left += 10
            elif card == cls.KILL:
                if player.lives > 1:
                    player.lives -= 1
            elif card == cls.HEAL:
                player.lives += 1
            elif card == cls.POISON:
                player.time_left -= 7
            else:
                raise ValueError("Invalid card")
            message += cls.word(card, cter - 1, player.id)
            if cter > 1:
                teff_chain.append((card, cter - 1))
        player.effect_chain = teff_chain
        return message


