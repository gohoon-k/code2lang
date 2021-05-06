import shutil
import random

from sources.constants import *


# 검증 집합이 저장될 경로가 없으면 만든다
if not os.path.isdir(VALIDATION_DATASET_PATH):
    os.mkdir(VALIDATION_DATASET_PATH)

# 훈련 집합이 저장될 경로가 없으면 만든다
if not os.path.isdir(TRAIN_DATASET_PATH):
    os.mkdir(TRAIN_DATASET_PATH)

# 지원 언어를 순회한다
for language in SUPPORTED_LANGUAGES:
    # 현재 언어에 맞는 저장 경로를 상수로 저장한다
    DATA_PATH_LANGUAGE = os.path.join(DATASET_CREATION_ROOT, language)
    VALIDATION_PATH_LANGUAGE = os.path.join(VALIDATION_DATASET_PATH, language)
    TRAIN_PATH_LANGUAGE = os.path.join(TRAIN_DATASET_PATH, language)

    # 난수들을 저장할 리스트를 만든다. 이 난수 리스트에 포함된 인덱스의 소스코드는 검증집합에 들어간다.
    randoms = list()

    # 현재 언어의 소스코드 목록을 가져온다
    data_list = [
        name
        for name in os.listdir(DATA_PATH_LANGUAGE)
        if os.path.isfile(os.path.join(DATA_PATH_LANGUAGE, name))
    ]

    # 랜덤 리스트의 길이가 (전체 소스코드의 수 * 검증 데이터 비율)보다 작을 경우 계속 반복한다
    # 이 과정을 통해 중복이 없는 (전체 소스코드의 수 * 검증 데이터 비율)개의 난수를 얻을 수 있다
    while len(randoms) < len(data_list) * VALIDATE_RATIO:
        # 0 이상 data_list 의 길이 미만의 새로운 난수를 발생시킨다.
        new = random.randrange(0, len(data_list))

        # 발생된 난수가 이미 리스트에 있다면 바로 다음 루프로 넘어간다
        if new in randoms:
            continue

        # 발생된 난수가 리스트에 없으면 리스트에 추가하고 다음 루프로 넘어간다
        randoms.append(new)

    # data_list 를 random 리스트에 있는 값을 인덱스로 하여 접근, 그 결과를 검증 집합 리스트에 추가한다
    validation_dataset = [data_list[index] for index in randoms]

    # data_list 를 random 리스트에 없는 값을 인덱스로 하여 접근, 그 결과를 훈련 집합 리스트에 추가한다
    train_dataset = [data_list[index] for index in range(len(data_list)) if index not in randoms]

    # 검증 집합 디렉터리 안에 현재 언어의 소스코드가 저장될 디렉터리가 없으면 만든다
    if not os.path.isdir(VALIDATION_PATH_LANGUAGE):
        os.mkdir(VALIDATION_PATH_LANGUAGE)

    # 훈련 집합 디렉터리 안에 현재 언어의 소스코드가 저장될 디렉터리가 없으면 만든다
    if not os.path.isdir(TRAIN_PATH_LANGUAGE):
        os.mkdir(TRAIN_PATH_LANGUAGE)

    # 데이터 디렉터리에 있는 소스파일을 검증 집합 디렉터리로 옮긴다
    for validation_data in validation_dataset:
        shutil.copyfile(
            os.path.join(DATA_PATH_LANGUAGE, validation_data),
            os.path.join(VALIDATION_PATH_LANGUAGE, validation_data)
        )

    # 데이터 디렉터리에 있는 소스파일을 훈련 집합 디렉터리로 옮긴다
    for train_data in train_dataset:
        shutil.copyfile(
            os.path.join(DATA_PATH_LANGUAGE, train_data),
            os.path.join(TRAIN_PATH_LANGUAGE, train_data)
        )
