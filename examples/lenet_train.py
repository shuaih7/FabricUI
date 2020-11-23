import os
import tensorflow as tf
from inspection2.models.lenet import LeNet_5
from inspection2.data.params import DataParamCls


batch_size = 128
epochs = 10
is_shuffle = True

log_dir = r"C:\projects\inspection2\lenet\log"
model_dir = r"C:\projects\inspection2\lenet\model"
data_dir  = r"C:\projects\inspection2\dataset\mnist"
#data_dir = r"E:\Deep_Learning\inspection2\lenet_5\dataset"


model = LeNet_5(input_shape=(28,28,1), name="lenet_test", model_dir=model_dir, log_dir=log_dir)

data_param = DataParamCls()
data_param.x_train_path = data_dir
data_param.y_train_path = data_dir
data_param.x_valid_path = data_dir
data_param.y_valid_path = data_dir
data_param.shuffle_size = 1000
data_param.num_parallel_calls = 4
data_param.num_classes  = 10

model.load_data(data_param)
model.train(batch_size=batch_size, epochs=epochs, steps_per_epoch=469, validation_steps=79, shuffle_size=1000)

