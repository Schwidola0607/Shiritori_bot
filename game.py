import requests
import json
from dict_trie import Trie
from fifa.check_fifa import check_players_name
from dictionary.MAL.character_names.check_MAL_name import check_MAL_name
from players import Players
DEFAULT_TIME = 1800
DEFAULT_DICT_TYPE = 0
"""0 for english, 1 for urban, 2 for MAL, 3 for fifa"""
from PyDictionary import PyDictionary
Dictionary = PyDictionary()

class Game:
    """a class to represent the current instance of a game"""
    state = 0 #0 - not begin, 1 - waiting for players, 2 - start/on progress, 3 - has just ended
    dict_type = DEFAULT_DICT_TYPE #0 - casual shiritori, 1 - urbandict shiritori
    BOOL_SCRABBLE = False
    
    list_of_players = []
    list_of_used_words = Trie()
    leaderboard = []
    current_letter = ""
    position = 0
    archive_leaderboard = []
    def __init__(self, dict_type: int):
        self.state = 0
        self.dict_type = dict_type
        self.BOOL_SCRABBLE = False
        self.list_of_players = []
        self.list_of_used_words = Trie()
        self.leaderboard = []
        self.current_letter = ""
        self.current_position = 0
        self.archive_leaderboard = []
    def add_new_players(self, gamer: Players):
        """add a new player when joined"""
        self.list_of_players.append(gamer)
        self.leaderboard.append(gamer)
    def add_new_word(self, word: str):
        """new word to list_of_used_word after a turn"""
        self.list_of_used_words.add(word)
        self.current_turn_Player().add_score(word)
        self.current_letter = word[-1]
    def start_game(self):
        """method to start game"""
        i = 0
        for player in self.list_of_players:
            player.position = i
            i += 1        
            self.state = 2
        self.current_turn_Player().countdown()
    def check_word_validity(self, word: str):
        """check for a word validitiy according to the Shiritori's rule"""
        if (self.current_letter != '' and word[0].lower() != self.current_letter.lower()): # basic shiritori rule
            return 0
        if word in self.list_of_used_words: # basic shiritori rule
            return 0

        if self.dict_type == 0: # normal
            if ' ' in word:
                return 0
            if any(not c.isalnum() for c in word):
                return 0
            temporary_dict = Dictionary.meaning(word)
            return temporary_dict is not None
        elif self.dict_type == 1: # urban
            response = requests.get("https://api.urbandictionary.com/v0/define?term=" + word).text
            dict_response = json.loads(response)
            
            if ('error' in dict_response): # url is redirected
                new_url = requests.get("https://www.urbandictionary.com/define.php?term="+ word).url
                new_word = new_url.rsplit('term=', 1)[1] # get the word redirected to (after the 'term=' part in the url)
                word = new_word
                response = requests.get("https://api.urbandictionary.com/v0/define?term=" + word).text
                dict_response = json.loads(response)

            def_list = dict_response['list']
            return len(def_list) != 0

        elif self.dict_type == 2: # MAL
            return check_MAL_name(word)
        elif self.dict_type == 3: #fifa
            return check_players_name(word)

    def find_player(self, name: str) -> Players:
        for gamer in self.list_of_players:
            if gamer.name == name:
                return gamer
        return False
    def game_owner(self) -> Players:
        """return the game owner"""
        return self.list_of_players[0]   
    def get_player_list_size(self) -> int:
        """return the current number of players"""
        return len(self.list_of_players)
    def current_turn_Player(self):
        """return this turn's Player"""
        return self.list_of_players[self.current_position]
    def kick(self, gamer: Players):
        """disqualify a player based on time, or the number of invalid times"""
        """kick a player from a game instance"""
        if self.state == 2:
            pos = gamer.position
            for i in range(pos + 1, self.get_player_list_size()):
                self.list_of_players[i].position -= 1
            if pos <= self.current_position:
                self.current_position -= 1
        if self.state == 1:
            self.leaderboard.remove(gamer)
        self.list_of_players.remove(gamer)
    def next_turn(self):
        """move to next Player's turn"""
        self.current_position = self.current_position + 1
        if self.current_position == self.get_player_list_size():
            self.current_position = 0
        self.current_turn_Player().countdown()
    def check_end(self):
        """end game condition"""
        for gamer in self.list_of_players:
            if gamer.get_remaining_time() < 0:
                self.list_of_players.remove(gamer)
        return self.state == 2 and self.get_player_list_size() == 1
    def end(self):
        """method to end the game"""
        self.state = 3
        self.dict_type = DEFAULT_DICT_TYPE
        self.archive_leaderboard.append([self.leaderboard, self.BOOL_SCRABBLE])
        self.BOOL_SCRABBLE = False
        self.list_of_players = []
        self.list_of_used_words = Trie()
        self.leaderboard = []
        self.current_letter = ""
        self.current_position = 0

    def get_winner(self) -> Players:
        """return the winner"""
        if self.BOOL_SCRABBLE == False:
            return self.list_of_players[0]
        else:
            return max(self.leaderboard, key = lambda x: x.score)

    def display_leaderboard(self) -> list:
        """return leaderboard based on scrabble score"""
        if self.state == 2:
            if self.BOOL_SCRABBLE == True:
                self.leaderboard.sort(key = lambda x: x.score, reverse = True)
            return self.leaderboard
        elif self.state == 3:
            print(self.archive_leaderboard[-1])
            if self.archive_leaderboard[-1][1] == True:
                self.archive_leaderboard[-1][0].sort(key = lambda x: x.score, reverse = True)
            return self.archive_leaderboard[-1][0]
            


