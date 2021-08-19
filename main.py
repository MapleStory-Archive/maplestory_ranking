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
        # print(f'요청에 실패한 페이지: {page}') 
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

class SearchData():
    def __init__(self, target_lv):
        self.target_lv = target_lv
    
    def section(self, pivot):
        former_pivot = 0
        first = True

        while True:
            req_data = request_data(pivot)

            # 리스트가 비어있는 경우 검사
            if not req_data:
                print('SearchData.section>> 리스트가 비어있습니다.')
                break
            else:
                sample_lv = parse_data(req_data[0])['level'] # 대표값으로 0번째 인덱스 설정
            
            # 현재 확인중인 페이지의 레벨이 더 커서 페이지가 증가하는 방향
            if sample_lv > self.target_lv:
                print(f'SearchData.section>> 탐색한레벨이 타겟보다 큽니다. 현재데이터:{sample_lv}')
                former_pivot = pivot
                pivot *= 2

                if first:
                    first_drc = True
                now_drc = True

            # 현재 확인중인 페이지의 레벨이 더 작아서 페이지가 감소하는 방향
            elif sample_lv < self.target_lv:
                print(f'SearchData.section>> 탐색한레벨이 타겟보다 작습니다. 현재데이터:{sample_lv}')
                former_pivot = pivot
                pivot //= 2

                if first:
                    first_drc = False
                now_drc = False

            # 페이지와 레벨이 같은 경우
            else:
                return pivot

            # 탐색 방향이 바뀌고 구간이 정해진 경우
            if not first and first_drc != now_drc:
                break
            
            # 첫시도 토글 종료
            if first:
                first = not first
        
        return former_pivot, pivot

    # TODO: sample_page 페이지중에서 0번째 인덱스만 확인하는거 수정하기
    def sample_page(self, a, b):
        if a > b:
            a, b = b, a

        pivot = a + (b - a) // 2

        req_data = request_data(pivot)
        sample_lv = parse_data(req_data[0])['level']

        print(f'SearchData.sample_page>> a:{a}, b:{b}, sample_lv:{sample_lv}')
        
        if self.target_lv > sample_lv:
            return self.sample_page(a, pivot)
        elif self.target_lv < sample_lv:
            return self.sample_page(pivot, b)
        else:
            return pivot

    @staticmethod
    def critical_page(target_lv, sub_lv, a, b):
        pivot = a + (b - a) // 2
        req_data = request_data(pivot)

        if not req_data:
            pivot_lv = None
            print("SearchData.search_ciritical_page>> 요청한 데이터가 비어있습니다")
            input('SearchData.search_ciritical_page>> 진행하려면 엔터...')
        else:
            pivot_lv = parse_data(req_data[0])['level']

        print(f'SearchData.critical_page>> a: {a}, b: {b}, pivot: {pivot}, pivot_lv: {pivot_lv}')

        if b - a == 1: return a
        elif pivot_lv == target_lv:
            return SearchData.critical_page(pivot_lv, sub_lv, pivot, b)
        elif pivot_lv == sub_lv:
            return SearchData.critical_page(target_lv, pivot_lv, a, pivot)

    @staticmethod
    def critical_index(target_lv, pivot):
        req_data = request_data(pivot)

        for i in range(len(req_data)):
            char_data = parse_data(req_data[i])

            if char_data['level'] < target_lv:
                return pivot, i-1
        return pivot+1, 0

class RakeData:
    def __init__(self):
        self.type_of_class = list()

    def class_data(self, pivot, index):
        print(f'RakeData.class_data>> now_page {pivot}')
        req_data = request_data(pivot)

        # 역순으로 진행
        for i in reversed(range(index+1)):
            char_data = parse_data(req_data[i])
            
            # 딕셔너리에 없으면 추가
            if char_data['class'] not in self.type_of_class.keys():
                # 초보자는 제외
                if char_data['class'] == '초보자' or char_data['class'] == '시티즌' or char_data['class'] == '노블레스':
                    continue
                
                # 개인페이지 요청
                try:
                    html = requests.get(f"https://maple.gg/u/{char_data['name']}", headers=headers)
                except requests.exceptions.ConnectionError as p:
                    print(f'error name: {p}(서버와의연결오류)')
                    # print(f'요청에 실패한 페이지: {page}') 
                    return p
                soup = bs(html.content, 'html.parser')
                rank_of_class = int(''.join(soup.select_one('#user-profile > section > div.row.row-normal > div.col-lg-8 > div.row.row-normal.user-additional > div:nth-child(5) > span').text[:-1].split(',')))
                self.type_of_class.append({'직업': char_data['class'], '인원수': rank_of_class})
                
                print(f"RakeData.class_data>> {self.type_of_class}")

        if len(self.type_of_class) >= 45: return self.type_of_class
        return self.class_data(pivot-1, 19)

        # 딕셔너리 파일쓰기
        
    
    def server_data(self):
        pass


def search():
    target_lv = 250
    sub_lv = target_lv - 1

    search_tg = SearchData(target_lv)
    search_sub = SearchData(sub_lv)
    
    tg_section = search_tg.section(3000)
    if type(tg_section) == tuple:
        tg_sample = search_tg.sample_page(*tg_section)
    else:
        tg_sample = tg_section

    sub_section = search_sub.section(tg_sample)
    if type(sub_section) == tuple:
        sub_sample = search_sub.sample_page(*sub_section)
    else:
        sub_sample = sub_section
    
    crt_page = SearchData.critical_page(target_lv, sub_lv, tg_sample, sub_sample)
    crt_index = SearchData.critical_index(target_lv, crt_page)

    return crt_index


def file_write(class_rank_list):
    class_rank_list = sorted(class_rank_list, key=lambda x: x['인원수'], reverse=True)
    
    with open('./rank/test.csv', 'wt+', encoding='ANSI', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['직업', '인원수'])

        writer.writeheader()   
        for obj in class_rank_list:
            writer.writerow(obj)

if __name__ == "__main__":
    print(search())