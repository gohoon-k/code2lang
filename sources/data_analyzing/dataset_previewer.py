from sources.data_processing.data_initializer import DataInitializer
from sources.constants import *

data_initializer = DataInitializer(DataInitializer.KEYWORD_MODE_USED_ONLY)
train_data = data_initializer.load_data(TRAIN_DATASET_PATH)
validation_data = data_initializer.load_data(VALIDATION_DATASET_PATH)


def create_csv(path, data):
    dataset_preview = open(path, "w")
    for x_train_each, y_train_each in zip(data[0], data[1]):
        dataset_preview.write(",".join([str(value) for value in y_train_each]))
        dataset_preview.write(",,")
        dataset_preview.write(",".join([str(value) for value in x_train_each]))
        dataset_preview.write("\n")
    dataset_preview.close()


create_csv(TRAIN_DATASET_PREVIEW_PATH, train_data)
create_csv(VALIDATION_DATASET_PREVIEW_PATH, validation_data)
