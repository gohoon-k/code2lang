from bs4 import BeautifulSoup
from sources.constants import *

import requests

import os
import time


USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " \
             "AppleWebKit/537.36 (KHTML, like Gecko) " \
             "Chrome/87.0.4280.88 Safari/537.36"
HEADERS = {"User-Agent": USER_AGENT}

# 페이지별 질문의 개수를 정한다. 15, 30, 50 중 하나의 값이어야 한다.
LENGTH_PER_PAGE = 30
# 하나의 페이지에서 몇 개의 질문을 스크랩할지 정한다.
SCRAP_PER_PAGE = LENGTH_PER_PAGE

# 시작 페이지를 정한다
START_PAGE = 35
# 몇 페이지를 스크랩할지 정한다.
SCRAP_PAGE_COUNT = 2

# 스크랩 완료된 페이지를 기록. 물론 질문은 계속 리젠되므로 딱히 의미는 없다.
# PAGE 1 ~ 2, PER 30 COMPLETE in 2020-12-24
# PAGE 11 ~ 12, PER 30 COMPLETE in 2020-12-28
# PAGE 31 ~ 32, PEr 30 COMPLETE in 2020-12-31

# 스크랩할 페이지의 기본 도메인 주소
BASE_URL = "https://stackoverflow.com"

# 스크랩할 언어 태그. c%2b%2b 는 cpp 와 동일하다.
KEY_LANGUAGES = ['c%2b%2b', 'html', 'java', 'javascript', 'kotlin', 'python']

# 스크랩 결과를 저장할 경로를 설정
BASE_PATH = os.path.join(SC_SCRAP_OUTPUT_PATH, f"Z-{CURRENT_DATE_TIME}")

# BASE_PATH 가 존재하지 않는 경로이면 해당 경로를 만든다
if not os.path.isdir(BASE_PATH):
    os.mkdir(BASE_PATH)

# KEY_LANGUAGES 에 대해 forEachIndexed 로 순회한다
for lang_index, language in enumerate(KEY_LANGUAGES):
    # c++는 링크와 이름이 다르므로 따로 처리한다
    language_path = language
    if language_path == "c%2b%2b":
        language_path = "cpp"

    # 현재 언어의 경로가 존재하지 않는 경로이면 해당 경로를 만든다
    if not os.path.isdir(os.path.join(BASE_PATH, language_path)):
        os.mkdir(os.path.join(BASE_PATH, language_path))

    # 현재 진행중인 언어에 대한 로그를 출력한다.
    print(f"work start in language: {language_path} ({KEY_LANGUAGES.index(language) + 1}/{len(KEY_LANGUAGES)})")

    # 스크랩할 페이지 수만큼 반복을 시작한다
    for page_index in range(0, SCRAP_PAGE_COUNT):
        # 각종 옵션들로 스크랩할 페이지의 링크를 만들고 링크로부터 html 소스를 가져온다
        base_html = requests.get(
            f"{BASE_URL}/questions/tagged/{language}?tab=newest&page={page_index + START_PAGE}&pagesize={LENGTH_PER_PAGE}",
            headers=HEADERS
        ).text

        # html 소스를 bs4 라이브러리를 이용해 분석한다
        base_bs_object = BeautifulSoup(base_html, "html.parser")

        # 모든 질문의 목록을 담고있는 div#questions 엘리먼트 한 개를 가져온다
        div_questions = base_bs_object.find("div", attrs={"id": "questions"})
        # 질문 하나하나를 나타내는 div.question-summary 엘리먼트들을 가져온다
        question_summaries = div_questions.findAll("div", attrs={"class": "question-summary"})

        # 가져온 div.question-summary 들 중 앞에서 SCRAP_PER_PAGE 개만 잘라서 반복한다
        for question_index, question_summary in enumerate(question_summaries[:SCRAP_PER_PAGE]):
            # 질문 상세정보로 이어지는 a.question-hyperlink 엘리먼트 하나를 찾는다
            question_link = question_summary.find("a", attrs={"class": "question-hyperlink"})

            # 가져온 링크로 질문 상세정보 페이지의 html 소스를 가져온다
            question_html = requests.get(f"{BASE_URL}{question_link['href']}", headers=HEADERS).text
            # 질문 상세정보 html 소스를 bs4 라이브러리를 이용해 분석한다
            question_bs_object = BeautifulSoup(question_html, "html.parser")

            # 상세정보 페이지 속 소스코드가 담겨있는 태그를 찾는다
            # text=True 옵션을 주는 pre > code 태그 안에 있는 것이 그냥 소스코드가 아닌 syntax highlighting 이 적용된 코드이기 때문.
            pre_tags = question_bs_object.findAll("pre", text=True)
            code_count = len(pre_tags)

            # 진행도 로그 출력을 위한 부분, 현재 진행도를 확인한다
            current_progress = \
                lang_index * (SCRAP_PAGE_COUNT * SCRAP_PER_PAGE) + page_index * SCRAP_PER_PAGE + question_index
            max_progress = (SCRAP_PAGE_COUNT * SCRAP_PER_PAGE * len(KEY_LANGUAGES))

            question_id = question_summary['id'].replace('question-summary-', '')

            # 로그 텍스트를 정의
            log = f"working in progress: " \
                f"id({question_id}), " \
                "code({0}/{1}), " \
                f"question({question_index + 1}/{len(question_summaries)}), " \
                f"page({page_index + 1}/{SCRAP_PAGE_COUNT}), " \
                f"language({KEY_LANGUAGES.index(language) + 1}/{len(KEY_LANGUAGES)})" \
                f" -> {current_progress / max_progress * 100:.2f}%"

            # 질문에 소스코드가 하나도 없으면 로그를 출력하고 다음 루프로 넘어간다
            if len(pre_tags) == 0:
                print(log.format(0, 0), end="")

            # 질문에 소스코드가 하나 이상이면 소스코드 하나하나로 아래의 새로운 루프를 시작한다
            for index, pre_tag in enumerate(pre_tags):
                # 두 번째 이상의 루프이면 출력했던 라인을 지우고 다시 쓴다.
                # 이를 통해 한 질문에서 여러번 로그를 출력하지만 한 잘문에서 한 줄의 로그만 출력된다.
                if index > 0:
                    print("\r", end="")

                # pre 태그에서 code 엘리먼트를 찾는다. code 를 바로 찾지 않은 이유도 있으므로 반드시 pre 태그 안의 code 만 찾을 것
                code_tag = pre_tag.find("code")

                # 소스코드를 저장할 파일을 연다. 인코딩은 utf-8 로 정한다.
                new_file = open(
                    f"{os.path.join(BASE_PATH, language_path)}/{question_id}-{index:02d}.txt",
                    "w",
                    encoding="utf-8"
                )

                # pre 태그 안에 code 태그가 있었다면 code 태그의 내용을, 그렇지 않다면 pre 태그의 내용을 파일에 쓴다
                if code_tag is not None:
                    new_file.write(code_tag.text)
                else:
                    new_file.write(pre_tag.text)

                # 파일 쓰기가 끝났으므로 닫는다
                new_file.close()

                # 로그를 출력하고 다음 루프로 넘어간다
                print(log.format(index + 1, code_count), end="")

            # 한 개의 질문에서의 소스코드 스크랩이 끝났다. 마지막 로그가 개행을 하지 않고 끝났으므로 개행을 해준다.
            print()

            # 질문 하나당 3초를 쉬어서 Too much request 를 조금이라도 막아보자... 의미가 있는지는 잘 모르겠다.
            time.sleep(3)

        # 한 개의 페이지에서 소스코드 스크랩이 끝났다. 15초를 다시 쉬어서 Too much request 를 조금이라도 막아보자.
        time.sleep(15)

    # 한 개의 언어에서 소스코드 스크랩이 끝났다. 빈 라인의 출력으로 구분한다.
    print()
