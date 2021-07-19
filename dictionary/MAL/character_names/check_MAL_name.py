from dict_trie import Trie
import os 
filename = "MAL_data.txt"
f = open(os.path.join(os.path.dirname(__file__),filename), encoding = 'utf-8')
players_list = []
while True:
    line = f.readline().lower()
    players_list.append(line.strip())
    if not line:
        break

# for i in range(40):
#     print(players_list[i])
trie = Trie(players_list)
def check_MAL_name(word: str) -> bool:
    return word in trie

def test_check_MAL_name() -> bool:
    assert check_MAL_name('Uzumaki Naruto') == True, "Split overkill"
    assert check_MAL_name("Goku") == True, "Bruh2"
    assert check_MAL_name("manhdinh") == False, "Bruh3"
    assert check_MAL_name("Lionel Messi") == False, "Split failed"