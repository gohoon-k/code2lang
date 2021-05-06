from sources.data_processing.data_initializer import DataInitializer
from sources.constants import *

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from keras.models import load_model
import numpy as np


class Code2Lang:
    """ Actual class which predicting real data. """

    def __init__(self, data=None, paths=None):
        """
        Creates Code2Lang instance. Inits model and predict data. Only one argument(data or paths) is allowed to this function.

        :param list[str] data: list of data.
        :param list[str] paths: list of paths which points data file.
        """

        # 두 매개변수 중 하나만 입력 가능하도록 필터링
        # 입력이 없었을 경우
        if data is None and paths is None:
            print("No arguments passed!!")
            return

        # 두 매개변수에 모두 입력이 들어왔을 경우
        if data is not None and paths is not None:
            print("Only one argument is allowed!!")
            return

        # raw 데이터를 모델에 입력 가능한 형태로 변환하기 위한 DataInitializer 인스턴스를 선언
        data_initializer = DataInitializer(DataInitializer.KEYWORD_MODE_USED_ONLY)

        # 모델을 가져옴
        self.model = load_model(os.path.join(MODEL_PATH, PREDICT_MODEL, MODEL_NAME))

        # 데이터를 로드함
        raw_data = []
        if data is not None:
            raw_data = data
        elif paths is not None:
            for path in paths:
                with open(path, "r") as file:
                    raw_data.append(file.read())

        # 변환 데이터를 생성함
        input_data = [data_initializer.create_x_data(data=each) for each in raw_data]

        self.predict_data = np.asarray(input_data)
        self.result = None

    def exec(self):
        """
        Executes predicting operation.

        :return list[dict]: predict result
        """

        # 실제 예측을 수행함
        predict_result = self.model.predict(self.predict_data)

        # 예측 결과를 만들고 리턴함
        self.result = \
            [
                {
                    language: str(predict_result[data_index][index] * 100)
                    for index, language in enumerate(SUPPORTED_LANGUAGES)
                }
                for data_index, _ in enumerate(predict_result)
            ]
        return self.result
