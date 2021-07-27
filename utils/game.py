import os
import time
import threading
from unidecode import unidecode
from functools import reduce
from utils import http
from utils.enum import State, Mode, Dictionary
from utils.player import Player
from bs4 import BeautifulSoup

RAPID_API_KEY = os.environ.get("WORDS_API_KEY")
DEFAULT_LIVES = 3
SCRABBLE_SCORE = {
    "a": 1,
    "c": 3,
    "b": 3,
    "e": 1,
    "d": 2,
    "g": 2,
    "f": 4,
    "i": 1,
    "h": 4,
    "k": 5,
    "j": 8,
    "m": 3,
    "l": 1,
    "o": 1,
    "n": 1,
    "q": 10,
    "p": 3,
    "s": 1,
    "r": 1,
    "u": 1,
    "t": 1,
    "w": 4,
    "v": 4,
    "y": 4,
    "x": 8,
    "z": 10,
}


def get_scrabble_score(word: str) -> int:
    """Return the score of a word using scrabble points"""
    return reduce(
        lambda a, b: (SCRABBLE_SCORE[a] if a in SCRABBLE_SCORE else 0)
        + (SCRABBLE_SCORE[b] if b in SCRABBLE_SCORE else 0),
        list(word),
    )


class Game:
    """
    A class to represent a shiritori game.
    """

    def __init__(self, bot, start_message, message, mode, dictionary) -> None:
        self.bot = bot
        self.start_message = start_message
        self.message = message
        self.channel = message.channel
        self.state = State.READY
        self.mode = mode
        self.dictionary = dictionary
        self.players = {}
        self.in_game = []
        self.current_index = 0
        self.current_player = None
        self.timer = None
        self.start_time = 0
        self.used_words = []
        self.original_words = []
        return

    def out_of_time(self) -> None:
        """
        Reduce time for current player
        """
        self.current_player.time_left -= time.time() - self.start_time
        self.bot.dispatch("no_time_left", self.message, self.current_player)
        self.remove_player(self.current_player, True)
        return

    def start_countdown(self) -> None:
        """
        Start the countdown
        """
        self.timer = threading.Timer(self.current_player.time_left, self.out_of_time)
        self.start_time = time.time()
        self.timer.start()
        return

    def stop_countdown(self) -> None:
        """
        Stop the countdown
        """
        if self.timer:
            self.timer.cancel()
            self.current_player.time_left -= time.time() - self.start_time
        return

    def get_time_left(self) -> int:
        """
        Return the time left for the current player
        """
        return self.current_player.time_left - (time.time() - self.start_time)

    def add_player(self, user) -> None:
        """
        Add a player to the game.
        """
        if user.id in self.players:
            return
        self.players[user.id] = Player(user, DEFAULT_LIVES, Mode.time(self.mode))
        self.bot.dispatch("player_join", self.message, user)
        return

    def remove_player(self, user, internal=False) -> None:
        """
        Remove a player from the game.
        """
        if self.state == State.PLAYING or self.state == State.LAST:
            self.in_game.remove(user.id)
            if not internal:
                self.bot.dispatch("player_left", self.message, user)
            if self.current_player.id == user.id:
                self.stop_countdown()
                self.next_player()
        else:
            try:
                self.players.pop(user.id)
            except KeyError:
                pass
        return

    async def check_word(self, word: str) -> bool:
        """
        Check if word is valid
        """
        if len(self.used_words) > 0:
            current_letter = (
                self.used_words[-1][-1]
                if self.dictionary != Dictionary.VIETNAMESE
                else self.used_words[-1].split()[-1]
            )
            if (
                word[0] if self.dictionary != Dictionary.VIETNAMESE else word.split()[0]
            ) != current_letter:  # basic shiritori rule
                return False
            if word in self.used_words:  # basic shiritori rule
                return False
        if (
            self.dictionary == Dictionary.VIETNAMESE and len(word.split()) < 2
        ):  # basic Vietnamese shiritori rule (i guess???)
            return False
        if self.dictionary == Dictionary.ENGLISH:
            if " " in word:
                return False
            if any(not c.isalnum() for c in word):
                return False
            response = await http.get(
                f"https://wordsapiv1.p.rapidapi.com/words/{word}",
                res_method="json",
                headers={
                    "x-rapidapi-key": RAPID_API_KEY,
                    "x-rapidapi-host": "wordsapiv1.p.rapidapi.com",
                },
            )
            if "results" not in response or response["results"] == []:
                return False
            pt = [p for w in response["results"] for p in w["pertainsTo"] if "pertainsTo" in w]
            if len(pt) > 0 or len(list(set(pt).intersection(self.original_words))) > 0:
                return False
            self.original_words.extend(pt)
            return True
        elif self.dictionary == Dictionary.VIETNAMESE:
            response = await http.get(
                f"https://vtudien.com/viet-viet/dictionary/nghia-cua-tu-{word}",
                res_method="text",
            )
            soup = BeautifulSoup(response, "html.parser")
            return soup.find("h2") != None
        elif self.dictionary == Dictionary.URBAN:
            response = await http.get(
                f"https://api.urbandictionary.com/v0/define?term={word}",
                res_method="json",
            )
            return "list" in response and response["list"] != []
        elif self.dictionary == Dictionary.MAL:
            response = await http.get(
                f"https://myanimelist.net/character.php?cat=character&q={word}",
                res_method="text",
            )
            soup = BeautifulSoup(response, "html.parser")
            result = soup("td", {"class": "borderClass"})
            if not result or result == [] or result[0].text == "No results found":
                return False
            result = soup(
                "td", {"class": "borderClass bgColor1", "width": "175"}
            ) + soup("td", {"class": "borderClass bgColor2", "width": "175"})
            return (
                len(
                    list(
                        filter(
                            lambda x: unidecode(
                                x.find("a").text.replace(",", "")
                            ).lower()
                            == unidecode(word),
                            result,
                        )
                    )
                )
                > 0
            )
        elif self.dictionary == Dictionary.FIFA:
            response = await http.get(
                f"https://sofifa.com/players?keyword={word}", res_method="text"
            )
            soup = BeautifulSoup(response, "html.parser")
            players = soup("div", {"class": "bp3-text-overflow-ellipsis"})
            return (
                len(
                    list(
                        filter(
                            lambda player: unidecode(word)
                            == unidecode(player.text.split()[-1]).lower(),
                            players,
                        )
                    )
                )
                > 0
            )
        else:
            return False

    async def handle_word(self, message) -> None:
        """
        Handle word from current player
        """
        word = message.content.lower().strip()
        if self.state == State.PLAYING or self.state == State.LAST:
            if await self.check_word(word):
                self.stop_countdown()
                self.used_words.append(word)
                if self.mode == Mode.SCRABBLE:
                    self.current_player.score += get_scrabble_score(word)
                if self.state == State.LAST:
                    self.bot.dispatch("game_over", message, self.current_player)
                    self.state = State.IDLE
                    return
                self.next_player()
            else:
                self.current_player.lives -= 1
                if self.current_player.lives == 0:
                    self.bot.dispatch("no_lives_left", message, self.current_player)
                    self.remove_player(self.current_player, True)
                    return
                self.bot.dispatch("invalid_word", message)
        return

    def next_player(self) -> None:
        """
        Move to next player
        """
        if len(self.in_game) == 0:
            self.bot.dispatch("game_over", self.message)
            self.state = State.IDLE
            return
        if len(self.in_game) == 1:
            self.state = State.LAST
        self.current_index = (
            self.current_index + 1 if self.current_index < len(self.in_game) - 1 else 0
        )
        self.current_player = self.players[self.in_game[self.current_index]]
        self.bot.dispatch(
            "new_turn",
            self.message,
            (
                self.used_words[-1][-1]
                if self.dictionary != Dictionary.VIETNAMESE
                else self.used_words[-1].split()[-1]
            )
            if len(self.used_words) > 0
            else None,
        )
        self.start_countdown()
        return

    def start(self) -> None:
        """
        Start a shiritori game
        """
        self.state = State.PLAYING
        self.in_game = list(self.players.keys())
        self.current_player = self.players[self.in_game[self.current_index]]
        self.start_countdown()

    def abort(self) -> None:
        """
        Abort the current game
        """
        self.state = State.IDLE
        self.stop_countdown()

    def leaderboard(self) -> None:
        """
        Send the leaderboard
        """
        return sorted(
            self.players.values(),
            key=lambda x: x.score if self.mode == Mode.SCRABBLE else x.time_left,
            reverse=True,
        )
