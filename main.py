import csv
import requests
from bs4 import BeautifulSoup as bs
import os

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'}
CSV_FIELDNAME = ['rank', 'server', 'name', 'level', 'class', 'popularity', 'guild']

# 인풋: maple.gg 랭킹 페이지(1이상의 정수)
# 아웃풋: 해당하는 페이지(캐릭터 20개)의 table row를 list로 리턴
# memo: 에러발생시 에러 리턴
def request_data(page):
    try:
        html = requests.get(f'https://maple.gg/rank/total?page={page}', headers=headers)
    except requests.exceptions.ConnectionError as p:
        print(f'error name: {p}(서버와의연결오류)')
        # print(f'요쳉에 실패한 페이지: {page}') 
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

# memo1: 파일링크 공유
# memo2: 파일객체가 열린상태로 인스턴스 생성. 사용 후 꼭 객체를 닫아줄 것.
class Writefile:
    def __init__(self):
        self.CSV_FOLDER_DIR = './rank'
        self.CSV_FILE_DIR = self.CSV_FOLDER_DIR + '/kms_rank.csv'
        self.writer = csv.DictWriter(self.fp, fieldnames=CSV_FIELDNAME)

    # 인풋: 단일 캐릭터 정보 dict
    # 아웃풋: 딕셔너리를 csv에 작성후 마지막으로 작성한 index 리턴
    # MEMO: 정수 몇개를 포함한 딕셔너리이기 때문에 여러번 파일을 열고 닫는것 보다 한꺼번에 쓰는게 더 효율적 
    def write_data(self, char_attr):
        self.writer.writerow(char_attr)
        return char_attr['rank']

    # 아웃풋: 파일 존재여부 검사후 파일 객체 오픈
    def open_file(self):
        if not os.path.isdir(self.CSV_FOLDER_DIR):
            os.makedirs(self.CSV_FOLDER_DIR)
        if not os.path.isfile(self.CSV_FILE_DIR):
            self.fp = open(self.CSV_FILE_DIR, 'wt+', encoding="ANSI", newline='')
            csv.DictWriter(self.fp, fieldnames=CSV_FIELDNAME).writeheader()
        else:
            self.fp = open(self.CSV_FILE_DIR, 'wt+', encoding="ANSI", newline='')

    # 아웃풋: 파일 객체 닫기
    def close_file(self):
        self.fp.close()

def search_page(target, a, b):
    if a > b: a, b = b, a
    pivot = a + (b - a) // 2

    req_data = request_data(pivot)
    if req_data:
        char_data = parse_data(req_data[0])
    else:
        print('데이터가 비어있습니다.')
        return

    # Break Point
    print(f'현재데이터: {char_data["level"]} a: {a}, b: {b}, pivot: {pivot}')

    if target > char_data['level']:
        return search_page(target, a, pivot)
    elif target < char_data['level']:
        return search_page(target, pivot, b)
    else:
        return pivot

def search_section(target, pivot):
    former_pivot = 0
    first_toggle = True

    while True:
        req_data = request_data(pivot)
        
        if req_data:
            chars_data = parse_data(req_data[0])
            level = chars_data['level']
        else:
            # TODO: 재요청하는 방법 찾기
            print('리스트가 비어있습니다. 재요청 하세요')
            print(req_data)
            break
        
        if level == target:
            print(f'현재데이터와 타겟이 동일합니다 현재데이터:{level}')
            return pivot
        if level > target:
            former_pivot = pivot
            pivot *= 2

            if first_toggle:
                toggle = True
            my_toggle = True

            print(f'현재데이터가 타겟보다 큽니다. 현재데이터:{level}')
        elif level < target:
            former_pivot = pivot
            pivot //= 2

            if first_toggle:
                toggle = False
            my_toggle = False

            print(f'현재데이터가 타겟보다 작습니다 현재데이터:{level}')

        # Break Point
        if not first_toggle and my_toggle != toggle:
            break

        if first_toggle:
            first_toggle = False
    return search_page(target, pivot, former_pivot)

def search_critical_page(a, b, a_level, b_level):
    if a > b:
        a, b = b, a
        a_level, b_level = b_level, a_level

    pivot = a + (b - a) // 2
    req_data = request_data(pivot)
    if req_data: 
        pivot_level = parse_data(req_data[0])['level']
    else: 
        pivot_level = None

    # Break Point
    print(f'a:{a}, b:{b}, pivot:{pivot}, pivot_level:{pivot_level}')
    
    if b - a == 1: return a
    elif pivot_level == a_level:
        return search_critical_page(pivot, b, pivot_level, b_level)
    elif pivot_level == b_level:
        return search_critical_page(a, pivot, a_level, b_level)


# 인풋: table row에서 레벨이 변하는 페이지(암거나 넣는건 ㄴㄴ)
# 아웃풋: 레벨이 변하는 인덱스 리턴
def search_critical_index(pivot):
    req_data = request_data(pivot)

    for i in range(len(req_data)):
        char_data = parse_data(req_data[i])

        if not i:
            pivot_level = char_data['level']
        
        if char_data['level'] < pivot_level:
            return pivot, i
    
    return pivot + 1, 0
        


if __name__ == "__main__":
    a_level = 235
    b_level = a_level - 1
    a_pivot = search_section(a_level, 1)
    b_pivot = search_section(b_level, a_pivot)

    critical_page = search_critical_page(a_pivot, b_pivot, a_level, b_level)
    print(search_critical_index(critical_page))
