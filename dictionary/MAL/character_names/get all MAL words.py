import re
import pathlib
import os
import time
import unidecode
import random


from requests import get
from bs4 import BeautifulSoup

PATH = pathlib.Path().absolute()

def remove_accent(accented_string):
    """
    remove accent in animes' and characters' name
    """
    unaccented_string = unidecode.unidecode(accented_string)
    return unaccented_string

def get_anime_list():
    for number in range(1,27):          # iterate to
        letter = chr(ord('@')+number)   # next letters
        position = 0
        name_list = []
        while 1:
            URL = "https://myanimelist.net/anime.php?letter=" + letter + '&show=' + str(position)
            #print(URL)
            page_html = get(URL).text
            page = BeautifulSoup(page_html, features="html.parser")
            rows = page.find_all('a', class_="hoverinfo_trigger fw-b fl-l") # parts with the names
            if (len(rows) == 0): # 404 not found
                break
            for r in rows:
                long_name = str(r.find_all('strong')) 
                name = long_name[len('[<strong>'):-len('</strong>]')] + '\n' # extract the name only
                name = remove_accent(name)
                name_list.append(name)
            position += 50 # iterate to next pages
            time.sleep(1) # delay between accesses to not get restricted
        output = ''.join(name_list)

        newpath = str(PATH) + '/anime_names' # create new directory if not exists
        if not os.path.exists(newpath):
            os.makedirs(newpath)
        
        with open('dictionary/MAL/anime_names/' + letter + '.txt', 'w', encoding='utf-8') as f:
            print(output, file=f)
        print(letter + ' done\n') # currently can not done all the letters in one batch because MAL restricts heavy access

def get_character_list():
    with open('retain_position.txt', 'r') as f:
        position = int(f.read())
    f.close()
    while 1:
        name_list = []
        URL = f"https://myanimelist.net/character.php?limit={position}"
        #print(URL)
        page_html = get(URL).text
        page = BeautifulSoup(page_html, features="html.parser")
        rows = page.find_all('a', class_="fs14 fw-b") # parts with the names
        if (len(rows) == 0): # 404 not found
            break
        for r in rows:
            name = r.text
            name = remove_accent(name)
            name = name.replace(',', '')
            #print(name)
            name_list.append(name + '\n')
        position += 50 # iterate to next pages
        time.sleep(1+random.random()) # delay between accesses to not get restricted
        output = ''.join(name_list)
        print(position)
        with open('MAL_data_alter.txt', 'a+', encoding = 'utf-8') as f:
            f.write(output)
        f.close()
        with open('retain_position.txt', 'w+') as f:
            f.write(str(position))
        f.close()
    
if __name__ == "__main__":
    get_character_list()