from sources.data_processing.data_initializer import DataInitializer
from sources.constants import *

import os
import copy

import pickle

# 키워드 사용 데이터를 만들기 위한 DataInitializer 인스턴스와 전체 키워드 정보를 가져옴
data_initializer = DataInitializer(DataInitializer.KEYWORD_MODE_ALL)
keywords_regex = data_initializer.keywords_creator.get_regex()
keywords_display_names = data_initializer.keywords_creator.get_display_name()

# 결과 리스트들을 만든다.
stats_raw_by_keywords = list()
stats_raw_by_keywords_count = list()
stats_default_by_keywords = list()
stats_default_by_keywords_count = list()

print("start analyzing!!\n")

# 데이터 폴더 안의 각 버전 디렉터리의 이름을 가져온다
data_versions = [
    data_ver
    for data_ver in os.listdir(ANALYZE_TARGET_PATH)
    if os.path.isdir(os.path.join(ANALYZE_TARGET_PATH, data_ver))
]
# 데이터 폴더 안의 버전 디렉터리의 이름을 순회
for data_version in data_versions:
    # 지원 언어들을 순회함
    for language in SUPPORTED_LANGUAGES:
        print(f"working: {data_version} - {language}... ", end="")

        # 데이터 폴더 안의, 버전 디렉터리 안의, 특정 언어의 경로를 저장함
        # 예시 값: scraping/scraped_workspace/20201231-114219/kotlin
        PATH_LANGUAGE = os.path.join(ANALYZE_TARGET_PATH, data_version, language)
        # PATH_LANGUAGE 안의 모든 소스파일의 경로를 리스트로 만든다
        sources = [
            os.path.join(PATH_LANGUAGE, name)
            for name in os.listdir(PATH_LANGUAGE)
            if os.path.isfile(os.path.join(PATH_LANGUAGE, name))
        ]
        # 현재 language 의 모든 소스파일을 순회한다
        for source in sources:
            source_file_name = os.path.basename(source)

            # 가끔 데이터 폴더에 데이터와 관계 없는 desktop.ini 파일이 들어가는 경우가 있으므로 그것을 제외한다
            if source_file_name == "desktop.ini":
                continue

            # 소스파일을 열어서 읽고 source_data 에 저장한다
            source_file = open(source, "r", encoding="utf-8")
            source_data = source_file.read()
            source_file.close()

            # DataInitializer 를 통해 키워드 사용 데이터를 만든다
            source_x = data_initializer.create_x_data(data=source_data)

            # 소스파일의 정보를 파일이름으로부터 만든다.
            # 예시 값: ["65397653", "01"], 왼쪽 값은 질문 ID, 오른쪽 값은 소스코드 번호
            source_info = source_file_name.replace(".txt", "").split("-")

            # 소스파일 하나의 통계 정보를 만들어 리스트에 추가한다.
            stats_raw_by_keywords.append(
                [language, source_info[0], int(source_info[1]), source_x]
            )

        print("complete.")

print()


# 분석 결과를 one-hot 인코딩 순으로 정렬
print("sorting with one-hot encoding... ", end="")
stats_raw_by_keywords.sort(key=lambda stat_each: ",".join([str(keyword) for keyword in stat_each[3]]))
print("complete")


# 키워드가 3개 이상인 경우만 남기고 삭제
print("removing if keyword count < 3... ", end="")
before_length = len(stats_raw_by_keywords)
stats_raw_by_keywords = [
    stat
    for stat in stats_raw_by_keywords
    if stat[3][:-3].count(1) > 2
]
print(f"complete, removed {before_length - len(stats_raw_by_keywords)} items.")


# 중복된 키워드를 가진 소스들을 삭제
print("removing duplicated keyword sources... ", end="")
before_length = len(stats_raw_by_keywords)
stat_index = 0
while stat_index < len(stats_raw_by_keywords):
    try:
        if stats_raw_by_keywords[stat_index][3] == stats_raw_by_keywords[stat_index + 1][3]:
            stats_raw_by_keywords.remove(stats_raw_by_keywords[stat_index + 1])
            continue
    except IndexError:
        break

    stat_index += 1
print(f"complete, removed {before_length - len(stats_raw_by_keywords)} items.")


# 사용된 키워드의 수 기준으로 정렬
print("sorting raw list with keyword count... ", end="")
stats_raw_by_keywords_count = copy.deepcopy(stats_raw_by_keywords)
stats_raw_by_keywords_count.sort(
    key=lambda stat_each: len([keyword for keyword in stat_each[3] if keyword == 1])
)
print("complete")


# raw 데이터에서 keyword display name 으로 변환
print("generating default list... ", end="")
stats_default_by_keywords = copy.deepcopy(stats_raw_by_keywords)
for stat in stats_default_by_keywords:
    stat[3] = [
        keyword
        for keyword in keywords_display_names
        if stat[3][keywords_display_names.index(keyword)] == 1
    ]
print("complete")


# keyword display name 의 abc 순으로 정렬
print("sorting default list with keywords abc... ", end="")
stats_default_by_keywords.sort(
    key=lambda stat: ", ".join(stat[3])
)
print("complete")


# 사용된 키워드의 수를 기준으로 정렬
print("sorting default list with keywords count...", end="")
stats_default_by_keywords_count = copy.deepcopy(stats_default_by_keywords)
stats_default_by_keywords_count.sort(
    key=lambda stat: len(stat[3])
)
print("complete\n")


# 완성된 4 개의 리스트를 csv 에 기록하는 함수
def write_stats(file, target, raw=False):
    for i, target_each in enumerate(target):
        if raw:
            keyword_joined = ",".join([f"{keywords}" for keywords in target_each[3]])
        else:
            keyword_joined = ",".join([f"\"{keywords}\"" for keywords in target_each[3]])
        write_target = f"{target_each[0]},{target_each[1]},{target_each[2]},{keyword_joined}"
        file.write(write_target)
        if i < len(target) - 1:
            file.write("\n")


# 실제로 위의 함수를 호출하여 리스트 4 개를 각각 csv 파일에 기록함
print("writing csv files... ", end="")
with open(os.path.join(ANALYZE_OUTPUT_PATH, "default_keyword.csv"), "w", encoding="utf-8") as file_default_keyword:
    write_stats(file_default_keyword, stats_default_by_keywords)

with open(os.path.join(ANALYZE_OUTPUT_PATH, "default_keyword_count.csv"), "w", encoding="utf-8") as file_default_keyword_count:
    write_stats(file_default_keyword_count, stats_default_by_keywords_count)

with open(os.path.join(ANALYZE_OUTPUT_PATH, "raw_keyword.csv"), "w", encoding="utf-8") as file_raw_keyword:
    write_stats(file_raw_keyword, stats_raw_by_keywords, True)

with open(os.path.join(ANALYZE_OUTPUT_PATH, "raw_keyword_count.csv"), "w", encoding="utf-8") as file_raw_keyword_count:
    write_stats(file_raw_keyword_count, stats_raw_by_keywords_count, True)
print("complete")


# 완성된 리스트를 dat 파일로 기록하는 과정
print("writing statistics.dat files... ", end="")
object_file = open(f"{ANALYZE_OUTPUT_PATH}/statistics.dat", "wb")
pickle.dump({
    "default_keyword": stats_default_by_keywords,
    "default_keyword_count": stats_default_by_keywords_count,
    "raw_keyword": stats_raw_by_keywords,
    "raw_keyword_count": stats_raw_by_keywords_count
}, object_file)
object_file.close()
print("complete\n")


# 적절하지 않은 소스 파일을 걸러내기 위한 작업
# source_ids 는 유효한 소스파일들의 id 를 저장함
source_ids = set()
# checked_ids 는 한 번 체크하고 넘어간 소스파일들의 id 를 저장함. 파일이 중복되어 존재할 경우를 걸러내기 위한 리스트.
checked_ids = set()
# redundant_ids 는 이미 redundant 폴더에 있는 소스파일들의 id 를 저장함.
redundant_ids = set()

# source_ids 를 생성
print("generating question_ids... ", end="")
for stat in stats_default_by_keywords:
    source_ids.add(f"{stat[1]}-{int(stat[2]):02d}")
print(f"complete, total {len(source_ids)} source ids.")

# redundant_ids 를 생성
print("generating redundant_ids... ", end="")
for data_version in [sub_dir for sub_dir in os.listdir(f"{ANALYZE_REDUNDANT_PATH}") if os.path.isdir(f"{ANALYZE_REDUNDANT_PATH}")]:
    PATH_SUB_DIR_REDUNDANT = os.path.join(ANALYZE_REDUNDANT_PATH, data_version)
    for language in SUPPORTED_LANGUAGES:
        PATH_LANGUAGE_REDUNDANT = os.path.join(PATH_SUB_DIR_REDUNDANT, language)
        redundant_ids = set([
            name.replace(".txt", "")
            for name in os.listdir(PATH_LANGUAGE_REDUNDANT)
            if os.path.isfile(os.path.join(PATH_LANGUAGE_REDUNDANT, name))
        ])
print(f"complete, total {len(redundant_ids)} redundant ids.")


# 실제로 파일을 옮기거나 제거하는 작업. 중복된 파일들은 제거하고 유효하지 않은 파일들은 redundant 폴더로 이동한다.
print("removing/moving invalid files...")
# 출력을 위한 리스트
redundant_files = list()
duplicated_files = list()
# data_versions 는 위에 이미 선언되어 있다.
for data_version in data_versions:

    # 원본 파일의 경로와 이동될 타겟 경로를 설정한다
    DATA_VER_PATH = os.path.join(ANALYZE_TARGET_PATH, data_version)
    REDUNDANT_DATA_VER_PATH = os.path.join(ANALYZE_REDUNDANT_PATH, data_version)

    # 이동될 경로에 디렉터리가 없으면 만든다
    if not os.path.isdir(REDUNDANT_DATA_VER_PATH):
        os.mkdir(REDUNDANT_DATA_VER_PATH)

    # 언어별로 순회한다
    for language in SUPPORTED_LANGUAGES:

        # 원본 파일의 경로와 이동될 타겟 경로에 현재 언어를 추가한다
        PATH_LANGUAGE = os.path.join(DATA_VER_PATH, language)
        PATH_LANGUAGE_REDUNDANT = os.path.join(REDUNDANT_DATA_VER_PATH, language)

        # 이동될 경로에 디렉터리가 없으면 만든다
        if not os.path.isdir(PATH_LANGUAGE_REDUNDANT):
            os.mkdir(PATH_LANGUAGE_REDUNDANT)

        # 원본 경로에서 소스 파일들의 이름의 목록을 가져온다
        sources = [
            source
            for source in os.listdir(PATH_LANGUAGE)
            if os.path.isfile(os.path.join(PATH_LANGUAGE, source))
        ]
        # 소스 파일들을 순회한다
        for source in sources:
            if source == "desktop.ini":
                continue

            # 소스파일 이름에서 확장명을 제거한다
            current_id = source.replace(".txt", "")

            # 이미 이전에 체크한 적이 있거나 redundant 폴더에 있을 경우 현재 소스 파일을 지운다
            if current_id in checked_ids or current_id in redundant_ids:
                duplicated_files.append(current_id)
                os.remove(os.path.join(PATH_LANGUAGE, source))
            # 그게 아니지만 유효한 소스파일 리스트에 현재 소스파일이 없을 경우에는 redundant 폴더로 현재 소스파일을 이동한다
            elif current_id not in source_ids:
                redundant_files.append(current_id)
                os.rename(os.path.join(PATH_LANGUAGE, source), os.path.join(PATH_LANGUAGE_REDUNDANT, source))

            # 현재 언어의 모든 소스파일이 지워졌거나 이동되었을 경우 언어 폴더를 지운다. 그렇지만 이런 경우는 있으면 안된다...
            if len(os.listdir(PATH_LANGUAGE)) == 0:
                os.rmdir(PATH_LANGUAGE)

            # 체크한 적 있는 소스파일 리스트에 현재 파일을 추가한다.
            checked_ids.add(current_id)


# 제거/이동 결과를 출력하고 실행을 종료한다.
print(f"total {len(redundant_files)} redundant files found: ")
if len(redundant_files) > 0:
    print(redundant_files)
print(f"total {len(duplicated_files)} duplicated files found: ")
if len(duplicated_files) > 0:
    print(duplicated_files)
print()

print("finished analyzing.")
