import json
import requests
from bs4 import BeautifulSoup as bs
# maple.gg에서 파일 뽑은후 csv으로 저장
#TODO: 전체 반복문 추가, JSON파일 하나당 200캐릭터, MIN_LEVEL까지 반복 조건
MIN_LEVEL = 260

condition = True
rank_index, file_index = 0, 3
page = 151
data = []

while condition:
    # request, bs
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'}
    try:
        html = requests.get(f'https://maple.gg/rank/total?page={page}', headers=headers)
    except requests.exceptions.ConnectionError as p:
        print(f'error name: {p}')
        condition = False
        break
    soup = bs(html.content, 'html.parser')

    # parsing(name,rank,server,level,job,guild,popularity) -> list(dictionary)
    # [0]: 오지환, [1]: 태주 ....
    char_list = soup.select('section.container > section.box > div.box-content > table.table > tbody > tr')

    for character in char_list:
        # 최소레벨 조건 검사
        char_level = int(character.select_one('td:nth-child(2) > div:nth-child(2) > div.font-size-0 > span:nth-child(1)').string[-3:])
        if char_level < MIN_LEVEL:
            condition = False
            break
        # data에 캐릭터 attributes 작성
        else:
            data.append({})
            data[rank_index]['rank'] = int(''.join(character.select_one('th.text-center').string.split(','))) # rank
            data[rank_index]['server'] = character.select_one('td.align-middle > div.d-inline-block > img')['alt'] # server
            data[rank_index]['name'] = character.select_one('td.align-middle > div.d-inline-block > a > img')['alt'] # name
            data[rank_index]['level'] = char_level # level
            data[rank_index]['class'] = character.select_one('td:nth-child(2) > div:nth-child(2) > div.font-size-0 > span:nth-child(3)').string # class
            data[rank_index]['popularity'] = int(''.join(character.select_one('td.align-middle.d-none.d-sm-table-cell.text-center').string.split(','))) # popularity
            # guild : 길드마크 있음, 길드마크 없음, 길드가 없음
            try:
                data[rank_index]['guild'] = character.select_one('td:nth-child(4) > a > img')['alt'] # 길드마크 있음
            except:
                try:
                    data[rank_index]['guild'] = character.select_one('td:nth-child(4) > a').string.strip() # 길드마크 없음
                except:
                    data[rank_index]['guild'] = None
        rank_index += 1
    print(f'page {page} clear...')

    # file_wirte
    # 20캐릭터(1페이지)*50페이지
    if rank_index % 1000 == 0 or not condition: # 20, 40, 60, ...
        data_file = open(f'rank/maplestory_rank_page_{file_index}.json', 'w', encoding='utf-8')
        json.dump(data, data_file, ensure_ascii=False, indent=4)
        data_file.close()

        file_index += 1
        rank_index = 0
        data = []

    page += 1