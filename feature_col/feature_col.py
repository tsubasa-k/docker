import os, sys
from os.path import abspath
module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)
import warnings
warnings.filterwarnings('ignore')
from keras.models import load_model
from art import config
from art.utils import load_dataset, get_file
from art.estimators.classification import KerasClassifier
from art.attacks.poisoning import FeatureCollisionAttack
from art.attacks.evasion import FastGradientMethod

import numpy as np
import tensorflow as tf

tf.compat.v1.disable_eager_execution()
#%matplotlib inline
import matplotlib.pyplot as plt
np.random.seed(301)
#_____________________________________________
myinput = []
#myinput[0] label
#myinput[1] h5檔名稱
#myinput[2] model url
#myinput[3] data url
#myinput[4] csv url
#myinput[5] image RGB max
#myinput[6] image resize x_size
#myinput[7] image resize y_size
#myinput[8] feature layer

try:
    while True:
        text = input()
        myinput.append(text)
except EOFError:
    pass
print(myinput)
#_____________________________________________
import requests

def download_data_from_cloud(url, local_filename):
    response = requests.get(url)
    if response.status_code == 200:
        with open(local_filename, 'wb') as f:
            f.write(response.content)
        print("資料下載完成")
    else:
        print("無法下載資料")

# 資料在這個網址上提供下載
data_url = myinput[3]
csv_url = myinput[4]
local_filename = "data.zip"
csv_filename = "input.csv"

download_data_from_cloud(data_url, local_filename)
download_data_from_cloud(csv_url, csv_filename)

#在本地端解壓縮
#_____________________________________________
import zipfile

def unzip_file(zip_filename, extract_path):
    with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
        zip_ref.extractall(extract_path)

# 下載了名為 "data.zip" 的 zip 檔案，並想要解壓縮到 "data" 資料夾中
zip_filename = "data.zip"
extract_path = "data"

# 確保解壓縮目錄存在，若不存在則建立
if not os.path.exists(extract_path):
    os.makedirs(extract_path)

unzip_file(zip_filename, extract_path)

#使用csv檔案讀取資料夾的內容
#_____________________________________________
import pandas as pd
from PIL import Image

# 讀取 CSV 檔案
data_df = pd.read_csv("input.csv")

file_name_column = "filename"
filename = data_df[file_name_column]
x_filename = []
for i in range(filename.shape[0]):
    x_filename.append(filename[i])
#讀取資料內容

current_directory = os.getcwd()
contents = x_filename

#存取x_test
folder_path = "data"
x_test = []

for content in contents:
    # 讀取照片
    file_name = content
    file_name = folder_path + "/" + file_name
    image_path = os.path.join(current_directory, file_name)
    image = Image.open(image_path)

    # 將照片轉換為NumPy數組
    image = image.resize((int(myinput[6]),int(myinput[7])))
    image_array = np.array(image).astype(np.float64)
    #image_array /= 255.0 
    x_test.append(image_array)

x_test = np.array(x_test)
data_num = x_test.shape[0]
print("測試資料數量 : {}".format(data_num))
#存取y_test
y_test = []
data_df = pd.read_csv("input.csv")

file_name_column = "label"
filename = data_df[file_name_column]
for i in range(filename.shape[0]):
    y_test.append(filename[i])

y_test = np.array(y_test)
#轉one-hot
y_test = np.eye(np.max(y_test) + 1)[y_test]

print("資料存取完成")
#_____________________________________________
url = myinput[2]
local_filename = myinput[1]

response = requests.get(url)
with open(local_filename, 'wb') as f:
    f.write(response.content)

classifier_model = load_model(myinput[1])

classifier = KerasClassifier(clip_values=(0, int(myinput[5])), model=classifier_model, use_logits=False, preprocessing=(0.5, 1))

class_descr = myinput[0].split(' ')

#_____________________________________________
#將輸入的資料(目前為x_test)分成x_train,x_test；y_test分成y_train,y_test
num_train = int(x_test.shape[0] / 3)
num_test = x_test.shape[0] - num_train 

x_train = x_test[0:num_train]
y_train = y_test[0:num_train]
x_test = x_test[num_train:num_test + num_train]
y_test = y_test[num_train:num_test + num_train]

#_____________________________________________
#下毒前測試
test_loss, test_acc = classifier_model.evaluate(x_test, y_test, verbose=0)
benign_accuracy = test_acc
print("下毒前accuracy:",test_acc)
#_____________________________________________
target_class = class_descr[0] # one of label
target_label = np.zeros(len(class_descr))
target_label[class_descr.index(target_class)] = 1
target_instance = np.expand_dims(x_test[np.argmax(y_test, axis=1) == class_descr.index(target_class)][3], axis=0)
feature_layer = classifier.layer_names[int(myinput[8])]
#_____________________________________________
base_class = class_descr[1] # one of label
base_idxs = np.argmax(y_test, axis=1) == class_descr.index(base_class)
base_instances = np.copy(x_test[base_idxs][:10])
base_labels = y_test[base_idxs][:10]
#print(base_instances.shape)
x_test_pred = np.argmax(classifier.predict(base_instances), axis=1)
nb_correct_pred = np.sum(x_test_pred == np.argmax(base_labels, axis=1))
print("New test data to be poisoned (10 images):")
print("Correctly classified: {}".format(nb_correct_pred))
print("Incorrectly classified: {}".format(10-nb_correct_pred))
#_____________________________________________
#製造下毒資料
attack = FeatureCollisionAttack(classifier, target_instance, feature_layer, max_iter=10, similarity_coeff=256, watermark=0.3)
poison, poison_labels = attack.poison(base_instances)

poison_pred = np.argmax(classifier.predict(poison), axis=1)
#_____________________________________________
#建立下毒照片的資料夾
script_path = os.path.abspath(sys.argv[0])
script_dir = os.path.dirname(script_path)
plt.imshow(target_instance[0]/int(myinput[5]))

save_dir = './feature_col'
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

file_name = 'target_instance.png'
file_path = os.path.join(save_dir, file_name)
plt.savefig(file_path)
#存取下毒照片
for i in range(0, 10):
    pred_label, true_label = class_descr[poison_pred[i]], class_descr[np.argmax(poison_labels[i])]
    fig=plt.imshow(poison[i]/int(myinput[5]))
    file_name = 'poison'+str(i)+'.jpg'
    file_path = os.path.join(save_dir, file_name)
    plt.savefig(file_path)
for i in range(0, 10):
    pred_label, true_label = class_descr[x_test_pred[i]], class_descr[np.argmax(base_labels[i])]
    fig=plt.imshow(base_instances[i]/int(myinput[5]))
    file_name = 'base'+str(i)+'.jpg'
    file_path = os.path.join(save_dir, file_name)
    plt.savefig(file_path)
print(script_dir)
#_____________________________________________
#用下毒資料訓練
#print(x_train.shape)
#print(base_instances.shape)
adv_train = np.vstack([x_train, poison])
adv_labels = np.vstack([y_train, poison_labels])
classifier.fit(adv_train, adv_labels, nb_epochs=5, batch_size=4)

#下毒後測試
test_loss, test_acc = classifier_model.evaluate(x_test, y_test, verbose=0)
after_accuracy = test_acc
print("下毒後accuracy:",test_acc)

#_____________________________________________
import datetime
current_time = datetime.datetime.now()
formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

file_name = "Readme.txt"
with open(file_name, "a") as file:
    file.write("_____________________________________________\n")
    file.write("測試項目 : Feature Collision Attack\n")
    file.write("測試時間 : {}\n".format(formatted_time))
    file.write("模型名稱 : {}\n".format(myinput[1]))
    file.write("測試資料數量 : {}\n".format(data_num))
    file.write("此項模型檢測是將模型做特徵碰撞攻擊\n")
    file.write("針對您輸入的特徵層數做下毒攻擊\n")
    file.write("--->\n")
    file.write("將您提供的資料做特徵碰撞\n")
    file.write("將被修改後的圖片加入模型訓練後，得到以下數據\n")
    file.write("Accuracy benign poisoning: {}%\n".format(benign_accuracy * 100))
    file.write("Accuracy after poisoning: {}%\n".format(after_accuracy * 100))
    file.write("圖片範例可參閱feature_col資料夾\n")
    file.write("\n")

print("txt檔建立完成")