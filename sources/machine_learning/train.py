from sources.constants import *
from sources.data_processing.data_initializer import DataInitializer
from sources.machine_learning.reduced_logger import ReducedLogger

import tensorflow as tf
from keras import Sequential
from keras.layers import Dense

import time

print("starting train.py script...")

# 모델을 저장할 경로가 유효하지 않으면 디렉터리를 생성
if not os.path.isdir(MODEL_PATH):
    os.mkdir(MODEL_PATH)

# 모델을 저장할 날짜 기반의 이름을 가진 디렉터리를 생성
if not os.path.isdir(f"{MODEL_PATH}/{CURRENT_DATE_TIME}"):
    print(f"generating model path: {MODEL_PATH}/{CURRENT_DATE_TIME}")
    os.mkdir(f"{MODEL_PATH}/{CURRENT_DATE_TIME}")

# 데이터를 초기화하는 DataInitializer 객체를 생성
print("generating DataInitializer instance...")
data_initializer = DataInitializer(DataInitializer.KEYWORD_MODE_ALL)

# 데이터 집합을 로드
print("generating train datasets...")
train_data = data_initializer.load_data(TRAIN_DATASET_PATH)
print("generating validation datasets...")
validation_data = data_initializer.load_data(VALIDATION_DATASET_PATH)

# 키워드 파일에 있으나 한 번도 사용되지 않은 키워드가 있는지 확인
print("finding unused keywords... ", end="")
redundant_keywords = data_initializer.get_redundant_params(train_data[0])
print("complete, ", end="")
if len(redundant_keywords[0]) > 0:
    print(f"total {len(redundant_keywords[0])} unused keywords:")
    print(f"  {redundant_keywords[0]}")

    print("removing unused keywords from keywords list... ", end="")
    data_initializer.keywords_creator.remove_redundant_keywords(redundant_keywords[1])
    print("complete.")

data_initializer.keywords_creator.save(f"{CURRENT_DATE_TIME}")

# data_initializer 로부터 훈련 및 검증 데이터를 가져옴
x_train = data_initializer.remove_redundant_params(redundant_keywords[1], train_data[0])
y_train = train_data[1]
x_validation = data_initializer.remove_redundant_params(redundant_keywords[1], validation_data[0])
y_validation = validation_data[1]

# 모델 생성에 필요한 상수를 만든다
INPUT_SIZE = len(x_train[0])
SUPPORTED_LANGUAGE_SIZE = len(SUPPORTED_LANGUAGES)

wait_secs = 5
print(f"train will starts after {wait_secs} seconds...", end="")
for index in range(wait_secs):
    time.sleep(1)
    print("\r", end="")
    print(f"train will starts after {wait_secs - index - 1} seconds...", end="")

print("\r", end="")

# 모델을 Sequential 클래스로 만든다.
# 레이어는 입력이 KEYWORDS_SIZE 개, 출력이 SUPPORTED_LANGUAGE_SIZE 개가 되고, 각 언어일 확률이 최종 목적이므로 softmax 를 사용한다.
main_model = Sequential([
    Dense(
        input_dim=INPUT_SIZE,
        units=SUPPORTED_LANGUAGE_SIZE,
        activation="softmax"
    )
])

# 모델을 컴파일한다. 카테고리별로 분류하므로 비용함수를 CategoricalCrossentropy 를 사용하고
# optimizer 를 Adam(학습률 0.05)으로 설정한다.
main_model.compile(
    loss=tf.keras.losses.CategoricalCrossentropy(),
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.05),
    metrics=["accuracy"]
)

train_parameters = {
    "batch_size": 100,
    "epochs": 210
}
logger = ReducedLogger()
logger.set_model(main_model)
logger.set_params(train_parameters)

log_dir = f"{PROJECT_ROOT}/train_logs/{CURRENT_DATE_TIME}"
tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=log_dir, histogram_freq=1)

# 최종적으로 모델을 학습시킨다
history = main_model.fit(
    x_train,
    y_train,
    verbose=0,
    callbacks=[logger, tensorboard_callback],
    validation_data=(x_validation, y_validation),
    batch_size=train_parameters["batch_size"],
    epochs=train_parameters["epochs"]
)

print()
print(f"Evaluating...")
print(f"{main_model.evaluate(x_validation, y_validation)}")

# 학습시킨 모델을 저장한다.
model_path = os.path.join(MODEL_PATH, CURRENT_DATE_TIME, MODEL_NAME)
main_model.save(model_path)
