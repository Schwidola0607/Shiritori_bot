import os 
filename = "players_data.txt"
f = open(os.path.join(os.path.dirname(__file__),filename))
players_list = []
while True:
    line = f.readline()
    players_list.append(line.strip())
    if not line:
        break
for i in range(len(players_list)):
    pos = players_list[i].find(' ') - 1
    if pos == -2:
        continue
    if '0' <= players_list[i][pos] and players_list[i][pos] <= '9':
        s = players_list[i][pos] + ' '
        players_list[i] = players_list[i].split(s)[1]
        print(players_list[i])
with open('players_data.txt', 'w') as f:
    for item in players_list:
        f.write("%s\n" % item)