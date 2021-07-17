import time
import threading
scrabble_score = {"a": 1, "c": 3, "b": 3, "e": 1, "d": 2, "g": 2,
        "f": 4, "i": 1, "h": 4, "k": 5, "j": 8, "m": 3,
        "l": 1, "o": 1, "n": 1, "q": 10, "p": 3, "s": 1,
        "r": 1, "u": 1, "t": 1, "w": 4, "v": 4, "y": 4,
        "x": 8, "z": 10}
def get_score(word: str) -> int:
    """return the score of a word using scrabble points"""
    res = 0
    for letter in word:
        res += scrabble_score[letter.lower()]
    return res

class Players:
    """ a class to represent players"""
    name = ""
    score = 0
    invalid_left = 3
    time_left = 0
    timer_state = 0
    timer = threading.Timer
    start_time = 0
    position = 0
    def __init__(self, name: str, t: int):
        self.name = name
        self.time_left = t
    def add_score(self, word: str):
        """add score to a Player"""
        self.score += get_score(word)  
    def get_score(self) -> int:
        """get score of a Player"""
        return self.score 
    def get_remaining_time(self) -> int: 
        """get remaining time of a player units: second"""
        return self.time_left
    def reduce_clock(self):
        """substract one second from a Player's remaining time"""
        self.time_left -= 1
    def countdown(self):
        """countdown"""
        self.timer = threading.Timer(self.time_left, self.reduce_clock)
        self.start_time = time.time()
        self.timer.start()
    def stop_countdown(self):
        """stop the countdown timer"""
        self.timer.cancel()
        self.time_left -= time.time() - self.start_time