import pickle
import matplotlib.pyplot as plt

from sources.constants import *


# pickle 을 통해 데이터 파일로부터 딕셔너리 데이터를 불러온다
data_object_file = open(VISUALIZATION_INPUT_PATH, "rb")
data = pickle.load(data_object_file)
data_object_file.close()

# 불러온 데이터에서 필요한 정보만 골라낸다
stats_default_by_keywords = data["default_keyword"]

# 언어별 데이터의 갯수를 구하기 위한 과정
# 분석 결과가 저장될 딕셔너리를 만든다
data_count_by_languages = dict()

# 데이터별 통계를 순회한다. 소스코드 하나하나를 순회함.
for stat in stats_default_by_keywords:
    # 데이터의 언어가 딕셔너리의 키 리스트에 없으면 키를 추가하고 값을 0으로 초기화한다
    if stat[0] not in data_count_by_languages.keys():
        data_count_by_languages[stat[0]] = 0

    # 데이터의 언어 값에 1을 누적한다.
    data_count_by_languages[stat[0]] += 1


# 언어별 키워드의 평균 갯수를 구하기 위한 과정
# 분석 결과가 저장될 딕셔너리를 만든다
average_keywords_count_by_languages = dict()

# 아래의 과정에서는 언어별 전체 키워드의 갯수를 구한다
# 데이터별 통계를 순회한다. 소스코드 하나하나를 순회함
for stat in stats_default_by_keywords:
    # 데이터의 언어가 딕셔너리의 키 리스트에 없으면 키를 추가하고 값을 0으로 초기화한다
    if stat[0] not in average_keywords_count_by_languages.keys():
        average_keywords_count_by_languages[stat[0]] = 0

    # 데이터의 언어 값에 데이터의 키워드 갯수를 누적한다
    average_keywords_count_by_languages[stat[0]] += len(stat[3])

# 아래의 과정에서는 구한 전체 키워드의 갯수를 데이터의 개수로 나누어서 평균을 구한다
for kc_by_l_key in average_keywords_count_by_languages.keys():
    average_keywords_count_by_languages[kc_by_l_key] = \
        average_keywords_count_by_languages[kc_by_l_key] / data_count_by_languages[kc_by_l_key]


# 언어별 가장 많이 사용된 상위 7개의 키워드를 구하기 위한 과정
# 분석 중 임시로 사용할 딕셔너리이다
frequent_keywords_by_language_temp = dict()

# 아래의 과정에서는 언어별로 사용된 키워드(키)들을 사용된 횟수(값)과 함께 쌍으로 저장한다.
# 데이터별 통계를 순회한다. 소스코드 하나하나를 순회함
for stat in stats_default_by_keywords:
    # 데이터의 언어가 딕셔너리 키 리스트에 없으면 키를 추가하고 값을 빈 딕셔너리로 초기화한다.
    if stat[0] not in frequent_keywords_by_language_temp.keys():
        frequent_keywords_by_language_temp[stat[0]] = dict()

    # 데이터의 키워드 리스트를 순회한다
    for keywords in stat[3]:
        # 현재 키워드가 딕셔너리에 없으면 추가하고 0으로 초기화한다.
        if keywords not in frequent_keywords_by_language_temp[stat[0]].keys():
            frequent_keywords_by_language_temp[stat[0]][keywords] = 0

        # 현재 키워드의 값에 1을 누적한다.
        frequent_keywords_by_language_temp[stat[0]][keywords] += 1

# 아래의 과정에서 키워드들을 사용된 횟수를 기준으로 정렬하고 상위 7개를 뽑아온다.
frequent_keywords_by_language = dict()
for language in frequent_keywords_by_language_temp.keys():
    frequent_keywords_by_language[language] = \
        {
            key: value
            for key, value in sorted(frequent_keywords_by_language_temp[language].items(), key=lambda item: item[1])[-7:]
        }


# 이 아래부터는 그래프를 그리기 위한 과정이다
# plt.figure 로 새로운 그래프를 만든다
plt.figure(figsize=(7, 5))

# y 축 최대값을 정한다
plt.ylim(0, max(list(data_count_by_languages.values())) + 20)
# 막대 그래프를 그린다
plt.bar(data_count_by_languages.keys(), data_count_by_languages.values())
# x, y 축 레이블을 정한다
plt.xlabel("language")
plt.ylabel("data count")
# x 축의 눈금 데이터를 정한다
plt.xticks(range(len(data_count_by_languages.keys())), data_count_by_languages.keys())
# 그래프의 제목을 정한다
plt.title("data counts by languages")

# 데이터 레이블을 표시한다
for value_index, real_value in enumerate(data_count_by_languages.values()):
    plt.annotate(f"{real_value}", xy=(value_index, real_value + 3), ha="center", va="bottom")

# 그래프를 저장하고 화면에 표시한다
plt.savefig(f"{VISUALIZATION_OUTPUT_PATH}/data_counts_by_languages.png", dpi=300)
plt.show()


# 새로운 그래프를 만든다
plt.figure(figsize=(7, 5))

# y 축 최대값을 정한다
plt.ylim(0, max(list(average_keywords_count_by_languages.values())) + 3)
# 막대 그래프를 그린다
plt.bar(average_keywords_count_by_languages.keys(), average_keywords_count_by_languages.values())
# x, y 축 레이블을 정한다
plt.xlabel("language")
plt.ylabel("average of keywords count")
# x 축의 눈금 데이터를 정한다
plt.xticks(range(len(average_keywords_count_by_languages.keys())), average_keywords_count_by_languages.keys())
# 그래프의 제목을 정한다
plt.title("average of keywords count by languages")

# 데이터 레이블을 표시한다
for value_index, real_value in enumerate(average_keywords_count_by_languages.values()):
    plt.annotate(f"{real_value:.02f}", xy=(value_index, real_value + 0.5), ha="center", va="bottom")

# 그래프를 저장하고 화면에 표시한다
plt.savefig(f"{VISUALIZATION_OUTPUT_PATH}/average_of_keywords_counts_by_languages.png", dpi=300)
plt.show()


# 새로운 그래프를 만든다.
plt.figure(figsize=(10, 14))
# 전체 그래프들의 제목을 정한다
plt.suptitle("top 7 frequent keywords by languages", fontsize=20)
# 레이아웃 세팅, 레이블끼리 겹치거나 하지 않도록 한다
plt.tight_layout()

# 언어별 상위 7개의 키워드 딕셔너리에서 키(언어)를 가져와 인덱스와 함께 순회한다(foreachIndexed)
for index, language in enumerate(sorted(frequent_keywords_by_language.keys())):
    # 현재 순회중인 언어의 상위 7개 키워드가 담긴 딕셔너리를 가져온다
    current_dictionary = frequent_keywords_by_language[language]
    # y 축 최대값을 정하기 위한 것으로, 값들의 최대값에서 1.2를 더한 값을 저장한다
    current_max = int(max(list(current_dictionary.values())) * 1.2)

    # 전체 화면을 2 * 3으로 쪼개고 그 중 index + 1 번째 그래프를 선택한다
    plt.subplot(3, 2, index + 1)
    # 선택된 그래프의 y 축 최대값을 정한다
    plt.ylim(0, current_max)
    # 막대 그래프를 그린다
    plt.bar(current_dictionary.keys(), current_dictionary.values())
    # x 축 레이블을 그린다
    plt.xticks(range(len(current_dictionary.keys())), current_dictionary.keys(), rotation=45)
    # 선택된 서브 그래프의 제목을 정한다.
    plt.title(language)

    # 데이터 레이블을 그린다.
    for value_index, real_value in enumerate(current_dictionary.values()):
        plt.annotate(f"{real_value}", xy=(value_index, real_value + int(current_max * 0.075)), ha="center", va="bottom")

plt.subplots_adjust(hspace=0.5)

# 그래프를 이미지로 저장하고 화면에 출력한다
plt.savefig(f"{VISUALIZATION_OUTPUT_PATH}/top_7_frequent_keywords_by_languages.png", dpi=300)
plt.show()
