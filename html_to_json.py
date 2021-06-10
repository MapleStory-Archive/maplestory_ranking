import json
import requests
from bs4 import BeautifulSoup as bs
# maple.gg에서 파일 뽑은후 json으로 저장

#TODO: 전체 반복문 추가, JSON파일 하나당 200캐릭터, MIN_LEVEL까지 반복 조건

# request, bs
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'}
html = requests.get(f'https://maple.gg/rank/total?page={1}', headers=headers)
soup = bs(html.content, 'html.parser')

# parsing(name,rank,*server*,level,job,guild,popularity) -> list(dictionary)
# [0]: 오지환, [1]: 태주 ....
char_list = soup.select('section.container > section.box > div.box-content > table.table > tbody > tr')

data = []
rank_number = 0
for character in char_list:
    data.append({})
    data[rank_number]['rank'] = character.select_one('th.text-center').string # rank
    data[rank_number]['server'] = character.select_one('td.align-middle > div.d-inline-block > img')['alt'] # server
    data[rank_number]['name'] = character.select_one('td.align-middle > div.d-inline-block > a > img')['alt'] # name
    data[rank_number]['level'] = character.select_one('td:nth-child(2) > div:nth-child(2) > div.font-size-0 > span:nth-child(1)').string[-3:] # level
    data[rank_number]['class'] = character.select_one('td:nth-child(2) > div:nth-child(2) > div.font-size-0 > span:nth-child(3)').string # class
    data[rank_number]['popularity'] = ''.join(character.select_one('td.align-middle.d-none.d-sm-table-cell.text-center').string.split(',')) # popularity
    # guild : 길드마크 있음, 길드마크 없음, 길드가 없음
    try:
        data[rank_number]['guild'] = character.select_one('td:nth-child(4) > a > img')['alt'] # 길드마크 있음
    except:
        try:
            data[rank_number]['guild'] = character.select_one('td:nth-child(4) > a').string.strip() # 길드마크 없음
        except:
            data[rank_number]['guild'] = None

    rank_number += 1



# file_wirte
# 20캐릭터(1페이지)*10페이지
with open('test.json', 'w', encoding='utf-8') as data_file:
    json.dump(data, data_file, ensure_ascii=False, indent=4)