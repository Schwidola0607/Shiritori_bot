from dict_trie import Trie
import os 
filename = "players_data.txt"
f = open(os.path.join(os.path.dirname(__file__),filename))
players_list = []
while True:
    line = f.readline()
    players_list.append(line.strip())
    if not line:
        break

# for i in range(40):
#     print(players_list[i])
trie = Trie(players_list)
def check_players_name(word: str) -> bool:
    return word in trie
def test_check_players_name() -> bool:
    assert check_players_name('Cristiano Ronaldo') == True, "Split overkill"
    assert check_players_name("Reus") == True, "Bruh2"
    assert check_players_name("manhdinh") == False, "Bruh3"
    assert check_players_name("M. Gotze") == False, "Split failed"