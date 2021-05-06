import pickle
import matplotlib.pyplot as plt
import math

from sources.data_processing.keyword_creator import KeywordCreator
from sources.constants import *


# relations_between_keywords_and_languages.png 를 그리는 코드.

# 여기서는 순서가 중요하다. constants 의 SUPPORTED_LANGUAGES 를 사용하지 않으니 주의.
LANGUAGES = ["html", "cpp", "java", "javascript", "kotlin", "python"]

# 시각화할 데이터의 입력파일로부터 시각화에 쓸 데이터를 가져온다
data_object_file = open(VISUALIZATION_INPUT_PATH, "rb")
data = pickle.load(data_object_file)["raw_keyword"]
data_object_file.close()

# 가져온 데이터의 형태는 analyzer_v2.py, raw_keyword.csv 를 참고할 것.
# 가져온 데이터는 리스트이며, 각 리스트 아이템도 리스트다. 2차원 리스트라는 말.
# 각 리스트 아이템의 리스트 아이템 중 0번째 아이템은 언어이다.
# 1번째 아이템은 해당 데이터가 포함된 질문의 ID 이고, 2번째 아이템은 번호이다.
# 마지막 아이템(3번째 아이템)은 머신러닝에 입력될 x 데이터 자체 리스트로, 키워드가 있으면 1이고 없으면 0인 데이터가 키워드 별로 200개 남짓 존재한다.
# 정확한 형태를 보고싶다면 출력해볼 것!
# 즉 아래의 두 줄은 언어별 데이터의 갯수를 가져와 딕셔너리에 저장하는 과정이다.
stats_first_column = [row[0] for row in data]
stats_data_counts = {key: stats_first_column.count(key) for key in LANGUAGES}

# 이번 시각화 작업에서는 X 데이터를 만드는 과정은 없으므로 DataInitializer 대신 KeywordCreator 인스턴스를 만든다.
keyword_creator = KeywordCreator(KeywordCreator.KEYWORD_MODE_ALL)

# 언어별 키워드의 등장 횟수를 저장할 리스트를 만든다.
# 딕셔너리가 적합할 수 있지만 키로 정할 것이 딱히 없고 순서가 변하지 않으므로 리스트로 했다.
keyword_appearance_count = list()

# 아래의 반복문에서는 해당 키워드가 언어별로 몇 개의 소스코드에서 등장했는지를 저장한다.
# 키워드의 정규표현식은 모든 키워드를 통틀어 유일하므로 그것으로 순회를 시작한다.
for index, keyword in enumerate(keyword_creator.get_regex()):
    # 언어별 등장 횟수를 저장할 새로운 딕셔너리를 만든다.
    new_dict = {key: 0 for key in LANGUAGES}

    # 모든 스탯을 순회하여 현재 키워드가 사용된 횟수를 언어별로 분류하여 저장한다.
    # stat[3] 은 키워드 사용 여부의 목록이고, stat[0] 은 언어이다.
    for stat in data:
        if stat[3][index] == 1:
            new_dict[stat[0]] += 1

    # 등장 횟수가 저장된 딕셔너리를 리스트에 추가한다
    keyword_appearance_count.append(new_dict)


# 언어별 키워드의 등장 비율을 저장할 리스트를 만든다.
# 등장 횟수에 전체 소스파일의 개수를 나누어서 저장하게 된다.
keyword_appearance_ratio = list()

# 키워드 하나하나의 언어별 등장 횟수 딕셔너리가 저장된 리스트 keyword_appearance_count 를 순회
for keyword_dict in keyword_appearance_count:
    # 언어별 등장 비율을 저장할 새로운 딕셔너리를 만든다
    new_dict = dict()

    # 언어별 등장 횟수 딕셔너리의 키(언어)를 순회하여 언어별 등장 비율을 계산해 저장한다
    for language in keyword_dict.keys():
        new_dict[language] = keyword_dict[language] / stats_data_counts[language]

    # 언어별 등장 비율 리스트에 저장된 언어별 비율 딕셔너리를 추가한다
    keyword_appearance_ratio.append(new_dict)

# 아래부터는 그래프를 그리기 위한 작업이다.
# 아래의 4 리스트들은 각각 6각형의 6개의 꼭짓점의 x/y 좌표, 6각형의 6개의 변의 중심점의 x/y 좌표이다.
VERTEX_POINTS_X = [1 / 2, 1, 1 / 2, -1 / 2, -1, -1 / 2, 1 / 2]
VERTEX_POINTS_Y = [math.sqrt(3), 0, -math.sqrt(3), -math.sqrt(3), 0, math.sqrt(3), math.sqrt(3)]

TARGET_POINTS_X = [0, 3 / 4, 3 / 4, 0, -3 / 4, -3 / 4]
TARGET_POINTS_Y = [math.sqrt(3), math.sqrt(3) / 2, -math.sqrt(3) / 2, -math.sqrt(3), -math.sqrt(3) / 2, math.sqrt(3) / 2]

# 언어별 단위벡터를 만든다. 이 단위 벡터들에 언어별 등장 비율을 곱(벡터 * 상수)하고,
# 곱해진 모든 언어별 벡터를 합성하여 최종 키워드의 언어 사이 관계를 계산한다.
language_unit_vector = {
    key: (TARGET_POINTS_X[index], TARGET_POINTS_Y[index])
    for index, key in enumerate(LANGUAGES)
}

# 키워드별 관계 벡터가 저장될 리스트를 만든다
keyword_vectors = list()
# 모든 언어에서 한 번도 등장한 적이 없는 키워드(의미 없는 키워드)를 따로 저장한다
redundant_keywords = list()

# 특정 키워드의 언어별 등장 횟수 딕셔너리가 저장된 keyword_appearance_ratio 리스트를 순회한다
for index, keyword_dict in enumerate(keyword_appearance_ratio):
    # 현재 키워드의 관계 벡터를 만든다. 어차피 마지막에 전부 더해질 예정이므로 딕셔너리를 쓰지 않았다.
    vectors_by_language = list()

    # 현재 키워드가 의미 없는 키워드(모든 언어를 통틀어 한 번도 등장한 적 없는 키워드)인지 판별하는 코드
    is_keyword_redundant = True
    for language in keyword_dict.keys():
        if keyword_dict[language] > 0:
            is_keyword_redundant = False
            break
    # 한 번이라도 등장한 적이 있으면 플래그 값이 False 가 된다
    if is_keyword_redundant:
        redundant_keywords.append(index)

    # 언어별 단위벡터에 현재 언어에서의 등장 비율을 곱해 vectors_by_language 리스트에 추가한다
    for language in keyword_dict.keys():
        vectors_by_language.append(
            (
                language_unit_vector[language][0] * keyword_dict[language],
                language_unit_vector[language][1] * keyword_dict[language]
            )
        )

    # 최종적으로 모든 벡터의 합을 구한다
    keyword_vector = [0, 0]
    for vector in vectors_by_language:
        keyword_vector[0] += vector[0]
        keyword_vector[1] += vector[1]

    # 만들어진 최종 관계벡터를 keyword_vectors 리스트에 추가한다
    keyword_vectors.append(keyword_vector)


# 아래부터는 실제로 그래프를 그리는 과정이다
# plt.figure 로 새로운 그래프를 만든다. 정사각형으로 하면 뭔가 찌그러진 것 처럼 보이므로 높이를 약간 줄였다.
fig = plt.figure(figsize=(25, 23))

# 제목 텍스트를 만든다. plt.title 을 쓰지 않은 이유가 있으므로 text 를 쓸 것.
plt.text(0, 2.2, "Relations between keywords and languages", fontsize=75, ha="center", va="center")

# x, y 축은 필요하지 않으므로 숨긴다
plt.axis("off")
# 푸른 색, 5의 굵기로 6각형을 그린다
plt.plot(VERTEX_POINTS_X, VERTEX_POINTS_Y, 'b', linewidth=5)

# 6각형의 중심으로부터 6각형의 각 꼭짓점까지 점선을 회색으로 그린다.
for index in range(0, 6):
    plt.plot((0, VERTEX_POINTS_X[index]), (0, VERTEX_POINTS_Y[index]), linestyle="--", color="gray", linewidth=3)

# 6각형의 각 변에 어떤 언어인지 쓴다.
for language_index in range(len(LANGUAGES)):
    # 6각형의 위쪽 변과 아래쪽 변이 아니면 변에서 조금 더 떨어져있어야 잘 보이므로 그렇게 설정한다
    if language_index not in [0, 3]:
        position = 1.25
    else:
        position = 1.1

    # 각 변의 중심점으로부터 position 을 곱한 만큼의 위치에 텍스트를 그린다.
    plt.text(
        TARGET_POINTS_X[language_index] * position,
        TARGET_POINTS_Y[language_index] * position,
        LANGUAGES[language_index],
        fontsize=60,
        color="xkcd:indigo",
        ha="center",
        va="center"
    )

# 마지막으로 키워드들의 관계벡터에 따라 키워드 텍스트를 그린다
# 키워드들의 display name 을 가져온다
keywords = keyword_creator.get_display_name()
# 키워드별 관계 벡터가 저장되어있는 keyword_vectors 리스트를 순회한다
for index, vectors_by_language in enumerate(keyword_vectors):
    # 키워드가 의미 없는 것이 아니면 텍스트를 그린다
    if index not in redundant_keywords:
        # 관계 벡터를 그대로 그리면 너무 가운데에 몰려있는 경향이 있어서 x, y 모두 1.1을 곱해서 처리했다.
        # 중앙에 있을 수록 여러 언어에서 나타난 키워드로 특징이 적은 것이므로 글씨 크기를 작게 표현했다.
        # 글씨 크기는 벡터의 길이에 50을 곱하여 사용했다.
        plt.text(
            vectors_by_language[0] * 1.1,
            vectors_by_language[1] * 1.1,
            keywords[index],
            fontsize=math.sqrt(math.pow(vectors_by_language[0], 2) + math.pow(vectors_by_language[1], 2)) * 50,
            color="xkcd:navy",
            ha="center",
            va="center"
        )

# 그린 그래프를 저장하고 화면에 출력한다
plt.savefig(f"{VISUALIZATION_OUTPUT_PATH}/relations_between_keywords_and_languages.png", dpi=500)
plt.show()
