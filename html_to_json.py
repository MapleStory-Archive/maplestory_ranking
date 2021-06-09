import json
import requests
from bs4 import BeautifulSoup as bs

# maple.gg에서 파일 뽑은후 json으로 저장
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'}
# request
html = requests.get(f'https://maple.gg/rank/total?page={1}', headers=headers)
# bs
soup = bs(html.content, 'html.parser')

# parsing(name,rank,*server*,level,job,guild,popularity)
char_list = soup.select('section.container > section.box > div.box-content > table.table > tbody > tr')

# list(dictionary)
# file_wirte
    # 20캐릭터씩 10페이지 = 200캐릭터