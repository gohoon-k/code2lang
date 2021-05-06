from sources.constants import TAG_SCRAP_OUTPUT_PATH, VISUALIZATION_OUTPUT_PATH

import matplotlib.pyplot as plt
import pickle


# 태그 스크래핑 후 분석 결과(counts_of_questions_by_languages.png)를 출력하는 코드.

input_file = open(f"{TAG_SCRAP_OUTPUT_PATH}/tag_scraping_result.dat", "rb")
visualize_input = pickle.load(input_file)

languages = ["python", "javascript", "java", "html", "c#", "r", "c++", "c", "kotlin"]

filtered = {key: visualize_input[key] for key in languages}

# 이 아래부터는 그래프를 그리기 위한 과정이다
# plt.figure 로 새로운 그래프를 만든다
plt.figure(figsize=(7, 5))
plt.tight_layout()

# y 축 최대값을 정한다
plt.ylim(0, max(list(filtered.values())) + 20)
# 막대 그래프를 그린다
plt.bar(filtered.keys(), filtered.values())
# x, y 축 레이블을 정한다
plt.xlabel("language")
plt.ylabel("count of questions")
# x 축의 눈금 데이터를 정한다
plt.xticks(range(len(filtered.keys())), filtered.keys(), rotation=25)
# 그래프의 제목을 정한다
plt.title("count of questions which has 'specific language' tag.")

# 데이터 레이블을 표시한다
for value_index, real_value in enumerate(filtered.values()):
    plt.annotate(f"{real_value}", xy=(value_index, real_value + 3), ha="center", va="bottom")

# 그래프를 저장하고 화면에 표시한다
plt.savefig(f"{VISUALIZATION_OUTPUT_PATH}/counts_of_questions_by_languages.png", dpi=300)
plt.show()


