from tensorflow.keras.applications.vgg16 import VGG16
from tensorflow.keras.applications.vgg19 import VGG19
from tensorflow.keras.models import Model, Sequential
from tensorflow.keras.layers import Conv2D, GlobalAveragePooling2D, MaxPooling2D
from tensorflow.keras.layers import Flatten, Concatenate, Dense
from tensorflow.keras.layers import LSTM, GRU, SimpleRNN
from keras.models import load_model
from tensorflow.keras.layers import Input, Dense

#_____________________________________________
myinput = []
#myinput[0] label  //similarity沒有用到
#myinput[1] h5檔名稱
#myinput[2] model url
#myinput[3] data url //similarity沒有用到
#myinput[4] csv url //similarity沒有用到
#myinput[5] image RGB max //similarity沒有用到
#myinput[6] image resize x_size //similarity沒有用到
#myinput[7] image resize y_size //similarity沒有用到
#myinput[8] feature layer //similarity沒有用到

try:
    while True:
        text = input()
        myinput.append(text)
except EOFError:
    pass
print(myinput)
#_____________________________________________


def is_cnn_model(model):
    has_conv_layer = False
    has_pooling_layer = False
    has_fc_layer = False

    for layer in model.layers:
        if isinstance(layer, Conv2D):
            has_conv_layer = True
        elif isinstance(layer, MaxPooling2D) or isinstance(layer, GlobalAveragePooling2D):
            has_pooling_layer = True
        elif isinstance(layer, Dense):
            has_fc_layer = True

    return has_conv_layer and has_pooling_layer and has_fc_layer

def is_rnn_model(model):
    has_rnn = False

    for layer in model.layers:
        if isinstance(layer, (LSTM, GRU, SimpleRNN)):
            has_rnn = True
            break

    return has_rnn


def is_resnet_model(model):
    has_resnet_conv = False
    has_resnet_block = False

    for layer in model.layers:
        if isinstance(layer, Conv2D) and layer.kernel_size == (7, 7):
            has_resnet_conv = True
        elif isinstance(layer, Conv2D) and layer.kernel_size == (1, 1):
            has_resnet_block = True

    return has_resnet_conv and has_resnet_block

def is_inception_model(model):
    has_conv_layer = False
    has_pooling_layer = False
    has_concat_layer = False

    for layer in model.layers:
        if isinstance(layer, Conv2D):
            has_conv_layer = True
        elif isinstance(layer, MaxPooling2D):
            has_pooling_layer = True
        elif isinstance(layer, Concatenate):
            has_concat_layer = True

    return has_conv_layer and has_pooling_layer and has_concat_layer

def is_vgg_model(model):
    vgg16_model = VGG16(include_top=False, weights=None)
    vgg19_model = VGG19(include_top=False, weights=None)
    
    vgg16_layers = vgg16_model.layers
    vgg19_layers = vgg19_model.layers
    model_layers = model.layers

    # 判斷模型的層數是否一致
    if len(vgg16_layers) != len(model_layers) and len(vgg19_layers) != len(model_layers):
        return False

    # 逐層比較模型的結構
    for vgg_layer, model_layer in zip(vgg16_layers, model_layers):
        if vgg_layer.__class__.__name__ != model_layer.__class__.__name__:
            break
    else:
        return True

    for vgg_layer, model_layer in zip(vgg19_layers, model_layers):
        if vgg_layer.__class__.__name__ != model_layer.__class__.__name__:
            return False

    return True
#_____________________________________________


def check_model_architecture(model):
    # 檢查層的連接方式
    if isinstance(model, Sequential):
        connection_type = "序列式連接方式"
    elif isinstance(model, Model):
        connection_type = "函數式連接方式"
    else:
        connection_type = "未知的連接方式"

    print("模型連接方式:", connection_type)
    return connection_type

#_____________________________________________
import requests

url = myinput[2]
local_filename = myinput[1]
response = requests.get(url)
with open(local_filename, 'wb') as f:
    f.write(response.content)
model = load_model(myinput[1])

if is_cnn_model(model):
    if is_resnet_model(model):
        print("模型使用的是ResNet架構")
        architecture = "模型使用的是ResNet架構"
    elif is_inception_model(model):
        print("模型使用的是Inception架構")
        architecture = "模型使用的是Inception架構"
    elif is_vgg16_model(model):
        print("模型使用的是VGG16或VGG19架構")
        architecture = "模型使用的是VGG16或VGG19架構"
    elif is_rnn_model(model):
        print("模型使用的是RNN架構")
        architecture = "模型使用的是RNN架構"
    else:
        print("模型使用的是常見的CNN架構")
        architecture = "模型使用的是常見的CNN架構"
else:
    print("模型不符合影像辨識模型的常見架構")
    architecture = "模型不符合影像辨識模型的常見架構"
    
connection_type = check_model_architecture(model)

#_____________________________________________
import datetime
current_time = datetime.datetime.now()
formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

file_name = "Readme.txt"
with open(file_name, "a") as file:
    file.write("_____________________________________________\n")
    file.write("測試項目 : Model Similarity\n")
    file.write("測試時間 : {}\n".format(formatted_time))
    file.write("模型名稱 : {}\n".format(myinput[1]))
    file.write("{}\n".format(connection_type))
    file.write("{}\n".format(architecture))
    file.write("\n")

print("txt檔建立完成")