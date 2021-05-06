from sources.constants import *


class KeywordCreator:
    """ KeywordCreator class. Creates keyword-related data and save it(if needed) into files. """

    KEYWORD_MODE_ALL = 0
    KEYWORD_MODE_USED_ONLY = 1

    def __init__(self, mode):
        """
        Constructor of KeywordCreator class.
        Creates keywords list and case-ignored keywords list
        """

        keywords_path = ""
        keywords_display_name_path = ""

        if mode == self.KEYWORD_MODE_ALL:
            keywords_path = ALL_KEYWORDS_PATH
            keywords_display_name_path = ALL_KEYWORDS_DISPLAY_NAME_PATH
        elif mode == self.KEYWORD_MODE_USED_ONLY:
            keywords_path = os.path.join(MODEL_PATH, PREDICT_MODEL, "keywords_regex.txt")
            keywords_display_name_path = os.path.join(MODEL_PATH, PREDICT_MODEL, "keywords_display_name.txt")

        # 키워드 파일을 연다.
        keywords_file = open(keywords_path, "r", encoding="UTF-8")
        keywords_display_name_file = open(keywords_display_name_path, "r", encoding="UTF-8")

        # 키워드 파일을 라인별로 읽는다.
        keywords_by_lines = keywords_file.readlines()
        keywords_display_name_by_lines = keywords_display_name_file.readlines()

        # 읽는 작업이 끝났으므로 파일을 닫는다.
        keywords_file.close()
        keywords_display_name_file.close()

        # 라인별로 newline 문자와 CASE_IGNORE_FLAG 를 없애서 리스트에 추가한다.
        self.keywords_regex_list = [
            keyword.rstrip().replace(CASE_IGNORE_FLAG, "")
            for keyword in keywords_by_lines
        ]
        self.keywords_display_name_list = [
            keyword.rstrip()
            for keyword in keywords_display_name_by_lines
        ]
        # keyword 에 CASE_IGNORE_FLAG 가 있다면 그것을 없애고 리스트에 추가.
        self.case_ignore = [
            keyword.rstrip().replace(CASE_IGNORE_FLAG, "")
            for keyword in keywords_by_lines
            if keyword.count(CASE_IGNORE_FLAG) > 0
        ]

    def get_regex(self):
        """
        Used to reduce code length. Returns KeywordCreator.keywords_list

        :return: list of keywords.
        :rtype: list[str]
        """
        return self.keywords_regex_list

    def get_display_name(self):
        """
        Used to reduce code length. Returns KeywordCreator.keywords_display_name_list

        :return: list of keywords' display names.
        :rtype: list[str]
        """
        return self.keywords_display_name_list

    def is_case_ignore(self, keyword):
        """
        Check the given keyword is case-ignored.

        :param keyword: target keyword to check if it is case-ignored keyword.
        :return: True if given keyword is case-ignored, False otherwise.
        :rtype: bool
        """
        return keyword in self.case_ignore

    def save(self, model_id):
        """
        Writes new keywords data file only with used keywords, in model path.

        :param str model_id: target model's path
        """

        # 사용되지 않은 키워드들을 제외하고 사용된 키워드만 따로 파일에 저장하는 함수

        keywords_regex_file = open(os.path.join(MODEL_PATH, model_id, "keywords_regex.txt"), "w")

        for index, keyword in enumerate(self.keywords_regex_list):
            if keyword in self.case_ignore:
                keywords_regex_file.write(f"{keyword}{CASE_IGNORE_FLAG}")
            else:
                keywords_regex_file.write(keyword)

            if index != len(self.keywords_regex_list) - 1:
                keywords_regex_file.write("\n")

        keywords_regex_file.close()

        keywords_display_name_file = open(os.path.join(MODEL_PATH, model_id, "keywords_display_name.txt"), "w")

        for index, keyword in enumerate(self.keywords_display_name_list):
            keywords_display_name_file.write(keyword)

            if index != len(self.keywords_display_name_list) - 1:
                keywords_display_name_file.write("\n")

        keywords_display_name_file.close()

    def remove_redundant_keywords(self, redundant_keyword_indexes):
        """
        Removes all redundant keywords from current KeywordCreator instance

        :param list[int] redundant_keyword_indexes: index of redundant params
        :return:
        """

        # redundant_param_indexes 를 큰 값이 앞에 오도록 정렬한다
        redundant_keyword_indexes.sort(reverse=True)

        # redundant_param_indexes 를 순회하여 각 redundant keyword 를 제거한다
        for redundant_keyword_index in redundant_keyword_indexes:
            if self.keywords_regex_list[redundant_keyword_index] in self.case_ignore:
                self.case_ignore.remove(self.keywords_regex_list[redundant_keyword_index])

            del self.keywords_regex_list[redundant_keyword_index]
            del self.keywords_display_name_list[redundant_keyword_index]
