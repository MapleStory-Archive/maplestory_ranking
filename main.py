import csv
import requests
from bs4 import BeautifulSoup as bs
import os

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'}
CSV_FIELDNAME = ['rank', 'server', 'name', 'level', 'class', 'popularity', 'guild']


# 인풋: maple.gg 랭킹 페이지(1이상의 정수)
# 아웃풋: 해당하는 페이지(캐릭터 20개)의 table row를 list로 리턴
def reqeust_data(page):
    try:
        html = requests.get(f'https://maple.gg/rank/total?page={page}', headers=headers)
    except requests.exceptions.ConnectionError as p:
        print(f'error name: {p}(서버와의연결오류)')
        print(f'파싱에 실패한 페이지: {page}') 
        print(f'마지막으로 작성한 캐릭터 인덱스: {}')
        return p
        
    
    soup = bs(html.content, 'html.parser')
    return soup.select('section.container > section.box > div.box-content > table.table > tbody > tr')

# 인풋: table row 한개(한 캐릭터의 정보)
# 아웃풋: 해당하는 캐릭터의 랭크, 서버, 닉네임, 레벨, 직업, 인기도를 dict로 리턴
def parse_data(raw_data):
    char_attr = dict()
    char_attr['rank'] = int(''.join(raw_data.select_one('th.text-center').string.split(',')))
    char_attr['server'] = raw_data.select_one('td.align-middle > div.d-inline-block > img')['alt']
    char_attr['name'] = raw_data.select_one('td.align-middle > div.d-inline-block > a > img')['alt']
    char_attr['level'] = int(raw_data.select_one('td:nth-child(2) > div:nth-child(2) > div.font-size-0 > span:nth-child(1)').string[-3:])
    char_attr['class'] = raw_data.select_one('td:nth-child(2) > div:nth-child(2) > div.font-size-0 > span:nth-child(3)').string
    char_attr['popularity'] = int(''.join(raw_data.select_one('td.align-middle.d-none.d-sm-table-cell.text-center').string.split(',')))
    # 길드마크 유무에 따라 문서 구조 대응
    try:
        char_attr['guild'] = raw_data.select_one('td:nth-child(4) > a > img')['alt'] # 길드마크 있음
    except:
        try:
            char_attr['guild'] = raw_data.select_one('td:nth-child(4) > a').string.strip() # 길드마크 없음
        except:
            char_attr['guild'] = None # 길드가 없음
    
    return char_attr

# MEMO: 파일링크 공유
class Writefile:
    def __init__(self):
        self.CSV_FOLDER_DIR = './rank'
        self.CSV_FILE_DIR = self.CSV_FOLDER_DIR + '/kms_rank.csv'

    # 인풋: 캐릭터 정보 dict를 연결한 list
    # 아웃풋: 딕셔너리를 csv에 작성후 마지막으로 작성한 index 리턴
    # MEMO: 정수 몇개를 포함한 딕셔너리이기 때문에 여러번 파일을 열고 닫는것 보다 한꺼번에 쓰는게 더 효율적 
    def write_data(self, chars_attr):
        f = open(self.CSV_FILE_DIR, 'wt+', encoding='ANSI', newline='')
        csv.writer(f).writerows(chars_attr)
        f.close()
        return chars_attr[-1]['rank']

    # 아웃풋: 파일 존재여부 검사후 없다면 생성(후 헤드 작성)
    def is_scv(self):
        if not os.path.isdir(self.CSV_FOLDER_DIR):
            os.makedirs(self.CSV_FOLDER_DIR)
        if not os.path.isfile(self.CSV_FILE_DIR):
            f = open(self.CSV_FILE_DIR, 'wt+', encoding="ANSI", newline='')
            # TODO: fieldname으로 writehead하기
            csv.writer(f).writerow([i for i in CSV_FIELDNAME.keys()])
            f.close()
        return


# 인풋: 캐릭터 정보 dict를 연결한 list
# 아웃풋: 딕셔너리를 csv에 작성후 마지막으로 작성한 index 리턴
# MEMO: 정수 몇개를 포함한 딕셔너리이기 때문에 여러번 파일을 열고 닫는것 보다 한꺼번에 쓰는게 더 효율적 
def write_data(chars_attr):
    f = open(CSV_FILE_DIR, 'wt+', encoding='ANSI', newline='')
    csv.writer(f).writerows(chars_attr)
    f.close()
    return chars_attr[-1]['rank']

# 아웃풋: 파일 존재여부 검사후 없다면 생성(후 헤드 작성)
def is_csv():
    if not os.path.isdir(CSV_FOLDER_DIR):
        os.makedirs(CSV_FOLDER_DIR)
    if not os.path.isfile(CSV_FILE_DIR):
        f = open(CSV_FILE_DIR, 'wt+', encoding="ANSI", newline='')
        # fieldname으로 writehead하기
        csv.writer(f).writerow([i for i in CSV_FIELDNAME.keys()])
        f.close()
    return


if __name__ == "__main__":
    is_csv()
    