from bs4 import BeautifulSoup
from sources.constants import TAG_SCRAP_OUTPUT_PATH

import requests
import time
import pickle

# 필요한 상수들을 정의한다

# html request 를 보내기 위한 헤더 중 User-Agent 의 값
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " \
             "AppleWebKit/537.36 (KHTML, like Gecko) " \
             "Chrome/87.0.4280.88 Safari/537.36"

# html request 를 보낼 때 사용되는 헤더
HEADERS = {"User-Agent": USER_AGENT}

# 스크랩을 시작할 페이지
START_PAGE = 1
# 스크랩할 페이지의 양
PAGE_COUNT = 50

# 결과가 저장될 딕셔너리
result: dict = {}

# START_PAGE ~ START_PAGE + PAGE_COUNT 까지 반복.
for page_index in range(START_PAGE, START_PAGE + PAGE_COUNT):

    print(f"working page: {page_index}")

    # page_index 를 URL 에 삽입하여 완성된 링크를 만든다
    CURRENT_URL = f"https://stackoverflow.com/questions?tab=newest&pagesize=30&page={page_index}"

    # request 를 전송하여 html 소스를 받아온다
    html = requests.get(CURRENT_URL, headers=HEADERS).text

    # html 소스를 bs4 라이브러리를 사용해 분석한다
    bs_object = BeautifulSoup(html, "html.parser")

    # 질문의 목록을 가져온다
    # div#questions 를 찾고 그 안에서 div.question-summary 를 찾는다
    questions = bs_object.find("div", attrs={"id": "questions"}).findAll("div", attrs={"class": "question-summary"})

    # 질문 목록을 순회한다
    for question in questions:

        # 질문 안에 있는 모든 태그를 찾아서 순회한다
        for tag in question.findAll("a", attrs={"rel": "tag"}):

            # 현재 태그의 텍스트를 가져와서 그것이 결과 딕셔너리의 키 리스트에 포함되어있지 않다면 추가하고 그 값을 0으로 초기화한다
            if tag.text not in result.keys():
                result[tag.text] = 0

            # 딕셔너리를 현재 태그의 텍스트를 키로 접근하여 그 값에 1을 누적한다
            result[tag.text] += 1

    # 3초를 쉬어서 too much request 를 회피한다
    time.sleep(3)

# result 딕셔너리를 값의 역순으로 정렬한다
result = {item[0]: item[1] for item in sorted(result.items(), key=lambda item: item[1], reverse=True)}

# result 딕셔너리를 csv 파일에 기록한다
result_file = open(f"{TAG_SCRAP_OUTPUT_PATH}/tag_scraping_result.csv", "w", encoding="utf-8")
for item in result.items():
    result_file.write(f"{item[0]},{item[1]}\n")
result_file.close()

# 딕셔너리 자체를 저장
result_pickle_file = open(f"{TAG_SCRAP_OUTPUT_PATH}/tag_scraping_result.dat", "wb")
pickle.dump(result, result_pickle_file)
result_pickle_file.close()
