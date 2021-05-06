from sources.data_processing.keyword_creator import KeywordCreator
from sources.constants import MODE, SUPPORTED_LANGUAGES

import re
import os

import numpy as np
from numpy import ndarray


class DataInitializer:
    """ Data processing class. Reads all files and creates data fragments. """

    KEYWORD_MODE_ALL = 0
    KEYWORD_MODE_USED_ONLY = 1

    def __init__(self, mode):
        """ Constructor of DataInitializer class """

        keyword_mode = -1

        if mode == self.KEYWORD_MODE_ALL:
            keyword_mode = KeywordCreator.KEYWORD_MODE_ALL
        elif mode == self.KEYWORD_MODE_USED_ONLY:
            keyword_mode = KeywordCreator.KEYWORD_MODE_USED_ONLY

        self.keywords_creator = KeywordCreator(keyword_mode)

    def create_x_data(self, path=None, data=None):
        """
        Creates processed train data with given one scraped_raw train data.
        Input must be one of path or data. Passing both of path and data is forbidden.

        :param str path: path of data file
        :param str data: data itself
        :return: list of train data row
        :rtype: list[int]
        """

        # 입력이 없었을 경우
        if path is None and data is None:
            print("No argument passed!!")
            return None

        # 경로와 데이터에 모두 입력이 있었을 경우
        if path is not None and data is not None:
            print("Only one argument allowed to this function!!")
            return None

        data_content = ""

        # 입력이 훈련 데이터의 파일 경로일 경우
        if path is not None and type(path) is str:
            # 파일을 읽는다...
            data_file = open(str(path), "r", encoding="UTF-8")
            data_content_by_lines = data_file.readlines()
            data_file.close()

            data_content = " \n".join(data_content_by_lines)
        # 입력이 훈련 데이터 그 자체일 경우
        elif data is not None and type(data) is str:
            data_content = data

        # x 입력 한 줄을 만든다. 초기화는 빈 리스트로.
        data_row_x = []

        # 모든 키워드를 순회하여 입력을 만든다.
        for keyword_each in self.keywords_creator.get_regex():

            # 정규식 컴파일 옵션을 설정한다. 해당 키워드가 대소문자 무시인지 아닌지를 판별하여 설정.
            if self.keywords_creator.is_case_ignore(keyword_each):
                option = re.IGNORECASE | re.MULTILINE
            else:
                option = re.MULTILINE

            # MODE 는 키워드의 포함 횟수를 학습에 포함할지에 대한 여부이다.
            # 0일 경우 해당 키워드가 데이터에 존재하면 1, 그렇지 않으면 0으로 설정된다.
            if MODE == 0:
                find_result = re.findall(keyword_each, data_content, option)
                invalid_count = self.count_invalid(keyword_each, data_content, option)
                if len(find_result) - invalid_count > 0:
                    data_row_x.append(1)
                else:
                    data_row_x.append(0)
            # MODE 가 1일 경우 해당 키워드가 출현한 횟수를 저장한다.
            # 이렇게 하면 출현 빈도를 학습에 포함시키게 되므로 경우에 따라 학습이 부정확해질 수 있다.
            elif MODE == 1:
                find_result = re.findall(keyword_each, data_content, option)
                invalid_count = self.count_invalid(keyword_each, data_content, option)

                data_row_x.append(len(find_result) - invalid_count)

        # 문장의 끝으로 세미콜론을 찍는지, 혹은 블록의 시작으로 콜론을 찍는지 중괄호를 여는지에 대한 플래그를 추가한다.
        data_row_x.append(self.check_flags(data_content, r";$"))
        data_row_x.append(self.check_flags(data_content, r":$"))
        data_row_x.append(self.check_flags(data_content, r"{$"))

        return data_row_x

    @staticmethod
    def count_invalid(key, data_content, option):
        """
        Counts invalid keywords such as keywords in comments, out of tag, script tag, etc.

        :param str key: search key
        :param str data_content: search target
        :param int option: regex compile option
        :return: counts of keywords in quote
        :rtype: int
        """
        # 유효하지 않은 키워드의 수를 계산하기 위한 함수

        pattern = re.compile(key, option)
        count = 0

        # 기본적인 // 주석을 제외
        single_line_comments = re.findall(r'//.*', data_content)
        for single_line_comment in single_line_comments:
            count += len(re.findall(pattern, single_line_comment))

        # 파이썬에서의 #을 이용한 주석을 제외. #include 와 같은 것은 남기기 위해 # 뒤에 한 개의 공백을 둔 것만 제외한다.
        single_line_comments_python = re.findall(r'#[\s!].*', data_content)
        for single_line_comment_python in single_line_comments_python:
            count += len(re.findall(pattern, single_line_comment_python))

        # 두 줄 이상의 주석 /* */ 을 제외
        multi_line_comments = re.finditer(r'/\*((.|[\r\n])*?)\*/', data_content)
        for multi_line_comment in multi_line_comments:
            count += len(re.findall(pattern, multi_line_comment.group(0)))

        # html 에서의 주석인 <!-- --> 를 제외.
        html_comments = re.finditer(r'<!--((.|[\r\n])*?)-->', data_content)
        for html_comment in html_comments:
            count += len(re.findall(pattern, html_comment.group(0)))

        # 큰 따옴표로 묶인 문자열을 제외
        big_quotes = re.findall(r'([\"][^\"]*[\"])', data_content)
        for quote_contents in big_quotes:
            count += len(re.findall(pattern, quote_contents))

        # 작은 따옴표로 묶인 문자열을 제외
        small_quotes = re.findall(r'([\'][^\']*[\'])', data_content)
        for quote_contents in small_quotes:
            count += len(re.findall(pattern, quote_contents))

        # HTML 에서 태그와 태그 사이, 혹은 태그 안에 있는 문자열을 제외.
        # 이 경우 java, kotlin 등의 비 html 소스코드에서 부등호를 공백 없이 쓸 경우 매치되는 문제가 있다. 이건 구별할 수 없으므로 넘어가도록 한다.
        out_of_tags = re.findall(r'((?!script)(?=[^\s])[>]([^<]+)[<](?=[^\sA-Z]))', data_content)
        for out_of_tag_contents in out_of_tags:
            real_content = out_of_tag_contents[1]
            count += len(re.findall(pattern, real_content))

        def get_match_count(contents):
            match_count = 0
            for content in contents:
                match_count += len(re.findall(pattern, content[0]))
            return match_count

        # 스크립트 태그를 찾아 제외
        count += get_match_count(re.findall(r'(<script(.|[\r\n])*?>(.|[\r\n])*?</script>)', data_content))
        count += get_match_count(re.findall(r'(<style(.|[\r\n])*?>(.|[\r\n])*?</style>)', data_content))

        # liquid 스크립트를 찾아 제외
        count += get_match_count(re.findall(r'([{]%(.|[\r\n])*?%[}])', data_content))
        count += get_match_count(re.findall(r'([{][{](.|[\r\n])*?[}][}])', data_content))

        # php 스크립트를 찾아 제외
        count += get_match_count(re.findall(r'([<][?]php (.|[\r\n])*?[?][>])', data_content))

        # jsp 스크립트를 찾아 제외
        count += get_match_count(re.findall(r'([<]%(.|[\r\n])*?%[>])', data_content))

        return count

    @staticmethod
    def check_flags(data_content, flag):
        """
        Check that the flag is present at the end of line.

        :param str data_content: target contents by line.
        :param str flag: flag to check.
        :return: 1 if True, 0 otherwise.
        :rtype: int
        """

        # 주어진 flag 를 regex 인스턴스로 컴파일한다
        pattern = re.compile(flag, re.MULTILINE)

        # 주어진 flag 가 data_content 에 몇 번 포함되어있는지 찾는다
        all_count = len(re.findall(pattern, data_content))

        # data_content 에서 유효하지 않은 flag 갯수를 구한다
        invalid_count = DataInitializer.count_invalid(flag, data_content, re.MULTILINE)

        # 특히, 플래그가 :$ 이거나 {$ 일 경우에는 몇 가지 작업을 더 수행한다
        if flag == ":$":
            invalid_count += len(re.findall(r'case\s.+?:$', data_content))
            invalid_count += len(re.findall(r'public:$', data_content))
            invalid_count += len(re.findall(r'private:$', data_content))
        if flag == "{$":
            invalid_count += len(re.findall(r'=\s*{$', data_content))

        # 전체 갯수에서 유효하지 않은 갯수를 뺀 값이 1 이상이면 1을 반환, 그렇지 않으면 0을 반환한다
        if all_count - invalid_count > 0:
            return 1

        return 0

    def load_data(self, target_path):
        """
        Loads all train data with given path. Returned as Tuple of numpy array.

        :param target_path: path of train data.
        :type target_path: str
        :return: tuple holds all train data list. x is in 0, y is in 1.
        :rtype: tuple[ndarray, ndarray]
        """
        # 각 훈련 데이터를 빈 리스트로 초기화.
        x_train = []
        y_train = []

        print(f"  loading data from {target_path}")

        # 디렉터리가 언어별로 분류되어있으므로 지원 언어를 순회하여 각 데이터를 불러온다.
        for language_each in SUPPORTED_LANGUAGES:
            data_path = f"{target_path}/{language_each}"
            # 데이터 파일의 리스트를 만든다. 이름은 딱히 관계 없다.
            datalist = [
                name
                for name in os.listdir(data_path)
                if os.path.isfile(os.path.join(data_path, name)) and name.count(".result.txt") == 0
            ]
            # keywords.txt 는 데이터가 아니라 키워드 파일이므로 있으면 제외한다.
            if datalist.count("keywords.txt") > 0:
                datalist.remove("keywords.txt")

            # 현재 언어를 one-hot encoding 으로 인코딩한다. (라벨)
            current_lang_encoded = self.one_hot_encode(language_each)

            # 특정 언어 폴더 내에 있는 모든 데이터 파일들(소스코드들)을 순회하여 x 데이터를 만들어 x_train 에 추가하고
            # 현재 언어가 라벨(정답)이므로 one-hot 인코딩을 수행하여 y_train 에 추가한다.
            for index, data in enumerate(datalist):
                if index != 0:
                    print("\r", end="")
                gauge_max = 30
                current_gauge = int((index + 1) / len(datalist) * gauge_max)
                progress = int((index + 1) / len(datalist) * 100)
                print(f"    {language_each:13s} {data:17s}[{'=' * current_gauge}{' ' * (gauge_max - current_gauge)}] {progress:3d}%", end="")

                x_train.append(self.create_x_data(path=f"{data_path}/{data}"))
                y_train.append(current_lang_encoded)

            print()

        # 결과를 텐서플로에 입력 가능한 numpy 배열로 변환하여 입력한다.
        return np.asarray(x_train), np.asarray(y_train)

    def get_redundant_params(self, train_data):
        """
        Finds out all redundant params(always 0 in all train set) in train data.

        :param ndarray train_data: train data which created by this object instance.
        :return: all redundant params
        :rtype: tuple(list[str], list[int])
        """

        redundant_params = []
        redundant_param_indexes = []
        # 훈련 데이터의 길이로 순회하지 않는 이유는 훈련 데이터의 경우 키워드의 존재여부 말고도 다른 param 들도 있기 때문이다.
        for paramIndex in range(len(self.keywords_creator.get_display_name())):
            is_redundant = True
            # 한번이라도 해당 param 의 값이 1이 나왔으면 is_redundant 를 False 로 만들고 루프를 종료.
            for train_data_each in train_data:
                if train_data_each[paramIndex] == 1:
                    is_redundant = False
                    break
            # 무의미한 param 이면 리스트에 추가
            if is_redundant:
                redundant_params.append(self.keywords_creator.get_display_name()[paramIndex])
                redundant_param_indexes.append(paramIndex)

        return redundant_params, redundant_param_indexes

    @staticmethod
    def remove_redundant_params(redundant_param_indexes, data):
        """
        Removes all redundant params in data.

        :param list[int] redundant_param_indexes: index of redundant params
        :param data: dataset
        :return: dataset
        :rtype ndarray
        """

        # redundant_param_indexes 를 큰 값이 앞에 오도록 정렬한다
        redundant_param_indexes.sort(reverse=True)

        # ndarray 인 데이터를 리스트로 변환한다
        data_in_list = data.tolist()

        # redundant_param_indexes 를 순회하여 각 데이터에서 redundant param 을 제거한다
        for redundant_param_index in redundant_param_indexes:
            for data_each in data_in_list:
                del data_each[redundant_param_index]

        return np.asarray(data_in_list)

    @staticmethod
    def one_hot_encode(target_language):
        """
        One-hot encodes the given target_language

        :param str target_language: target to one-hot encode.
        :return: one-hot encoded result
        :rtype: list[int]
        """

        # 언어 목록의 크기와 동일한, 0으로 채워진 리스트를 만든다
        result = [0 for _ in SUPPORTED_LANGUAGES]
        # 주어진 타겟 언어의 위치에 해당하는 값만 1로 바꾼다.
        result[SUPPORTED_LANGUAGES.index(target_language)] = 1

        return result
