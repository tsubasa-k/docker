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
import cv2

tf.compat.v1.disable_eager_execution()
#%matplotlib inline
import matplotlib.pyplot as plt
np.random.seed(301)
#_____________________________________________
myinput = []
demo_times = 5
sigma = 0.5
#myinput[0] label  //evasion沒有用到
#myinput[1] h5檔名稱
#myinput[2] model url
#myinput[3] data url
#myinput[4] csv url
#myinput[5] image RGB max
#myinput[6] image resize x_size
#myinput[7] image resize y_size
#myinput[8] feature layer //evasion沒有用到

try:
    while True:
        text = input()
        myinput.append(text)
except EOFError:
    pass
print(myinput)
#_____________________________________________
#print(x_test.shape)
#print(x_test[0])
#if isinstance(y_test, np.ndarray):
    #print("這是 NumPy 陣列 (np.array)")
    #print(y_test.shape)
#elif isinstance(y_test, list):
    #print("這是 Python 列表 (list)")
#else:
    #print("這不是 NumPy 陣列也不是 Python 列表")
#雲端上下載zip資料檔
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


#建立資料夾
script_path = os.path.abspath(sys.argv[0])
script_dir = os.path.dirname(script_path)

save_dir = './evasion_images'
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

#evasion attack_______________________________
url = myinput[2]
local_filename = myinput[1]

response = requests.get(url)
with open(local_filename, 'wb') as f:
    f.write(response.content)

classifier_model = load_model(myinput[1])

classifier = KerasClassifier(clip_values=(0, int(myinput[7])), model=classifier_model, use_logits=False, preprocessing=(0.5, 1))

predictions = classifier_model.predict(x_test)

#print(predictions)
#print(np.argmax(y_test, axis=1))
#print(np.argmax(predictions, axis=1))
accuracy = np.sum(np.argmax(predictions, axis=1) == np.argmax(y_test, axis=1)) / len(y_test)
benign_accuracy = accuracy
print("Accuracy on benign test examples: {}%".format(accuracy * 100))

for i in range(demo_times):
    plt.imshow(x_test[i]/int(myinput[5]))
    plt.axis('off')
    file_name = str(i) + 'before.png'
    file_path = os.path.join(save_dir, file_name)
    plt.savefig(file_path)
#_____________________________________________
attack = FastGradientMethod(estimator=classifier, eps=0.5)
x_test_adv = attack.generate(x=x_test)

predictions = classifier_model.predict(x_test_adv)
accuracy = np.sum(np.argmax(predictions, axis=1) == np.argmax(y_test, axis=1)) / len(y_test)
after_accuracy = accuracy
print("Accuracy after attack test examples: {}%".format(accuracy * 100))

for i in range(demo_times):
    plt.imshow(x_test_adv[i]/int(myinput[5]))
    plt.axis('off')
    file_name = str(i) + 'after.png'
    file_path = os.path.join(save_dir, file_name)
    plt.savefig(file_path)


#four defense test
#_____________________________________________
def mean_filter(image, kernel_size):
    blurred = cv2.blur(image, (kernel_size, kernel_size))
    return blurred

kernel_size = 3
#print(x_test_adv.shape)
image_arrays = np.array(x_test_adv)
x_test_mean = []
for image in image_arrays:
    x_test_mean.append(mean_filter(image, kernel_size))

x_test_mean = np.array(x_test_mean)

predictions = classifier_model.predict(x_test_mean)
accuracy = np.sum(np.argmax(predictions, axis=1) == np.argmax(y_test, axis=1)) / len(y_test)
mean_accuracy = accuracy
print("Accuracy after mean defense test examples: {}%".format(accuracy * 100))

for i in range(demo_times):
    plt.imshow(x_test_mean[i]/int(myinput[5]))
    file_name = str(i) + 'mean.png'
    file_path = os.path.join(save_dir, file_name)
    plt.savefig(file_path)

#_____________________________________________
def median_filter(image, kernel_size):
    filtered = cv2.medianBlur(image, kernel_size)
    return filtered

image_arrays = np.array(x_test_adv)
x_test_median = []

for image in image_arrays:
    x_test_median.append(median_filter(image, kernel_size))

x_test_median = np.array(x_test_median)

predictions = classifier_model.predict(x_test_median)
accuracy = np.sum(np.argmax(predictions, axis=1) == np.argmax(y_test, axis=1)) / len(y_test)
median_accuracy = accuracy
print("Accuracy after median defense test examples: {}%".format(accuracy * 100))

for i in range(demo_times):
    plt.imshow(x_test_median[i]/int(myinput[5]))
    file_name = str(i) + 'median.png'
    file_path = os.path.join(save_dir, file_name)
    plt.savefig(file_path)

#_____________________________________________
def gaussian_filter(image, kernel_size, sigma):
    blurred = cv2.GaussianBlur(image, (kernel_size, kernel_size), sigma)
    return blurred

image_arrays = np.array(x_test_adv)
x_test_gaussian = []
for image in image_arrays:
    x_test_gaussian.append(gaussian_filter(image, kernel_size, sigma))

x_test_gaussian = np.array(x_test_gaussian)

predictions = classifier_model.predict(x_test_gaussian)
accuracy = np.sum(np.argmax(predictions, axis=1) == np.argmax(y_test, axis=1)) / len(y_test)
gaussian_accuracy = accuracy
print("Accuracy after gaussian defense test examples: {}%".format(accuracy * 100))

for i in range(demo_times):
    plt.imshow(x_test_gaussian[i]/int(myinput[5]))
    file_name = str(i) + 'gaussian.png'
    file_path = os.path.join(save_dir, file_name)
    plt.savefig(file_path)

#_____________________________________________
def bilateral_filter(image, d, sigma_color, sigma_space):
    filtered = cv2.bilateralFilter(image, d, sigma_color, sigma_space)
    return filtered

image_arrays = np.array(x_test_adv)
x_test_bilateral = []
for image in image_arrays:
    x_test_bilateral.append(bilateral_filter(image, 5 , 10 , 10))

x_test_bilateral = np.array(x_test_bilateral)

predictions = classifier_model.predict(x_test_bilateral)
accuracy = np.sum(np.argmax(predictions, axis=1) == np.argmax(y_test, axis=1)) / len(y_test)
bilateral_accuracy = accuracy
print("Accuracy after bilateral defense test examples: {}%".format(accuracy * 100))

for i in range(demo_times):
    plt.imshow(x_test_bilateral[i]/int(myinput[5]))
    file_name = str(i) + 'bilateral.png'
    file_path = os.path.join(save_dir, file_name)
    plt.savefig(file_path)


#_____________________________________________
import datetime
current_time = datetime.datetime.now()
formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

file_name = "Readme.txt"
with open(file_name, "a") as file:
    file.write("_____________________________________________\n")
    file.write("測試項目 : Evasion Attack\n")
    file.write("測試時間 : {}\n".format(formatted_time))
    file.write("模型名稱 : {}\n".format(myinput[1]))
    file.write("測試資料數量 : {}\n".format(data_num))
    file.write("此模型測試使用的是Fast Gradient Method（快速梯度法，簡稱 FGM）的攻擊方式\n")
    file.write("FGM透過微小的圖像數值調整，以對抗神經網絡模型\n")
    file.write("從而導致模型在原本正確分類的情況下錯誤地進行分類\n")
    file.write("--->\n")
    file.write("在此測試中我們會呈現攻擊前和攻擊後的準確率\n")
    file.write("另外提供4種不同平滑圖像處理的準確率，供您參考針對FGM的防禦方法\n")
    file.write("Accuracy on benign test examples: {}%\n".format(benign_accuracy * 100))
    file.write("Accuracy after attack test examples: {}%\n".format(after_accuracy * 100))
    file.write("Accuracy after mean defense test examples: {}%\n".format(mean_accuracy * 100))
    file.write("Accuracy after median defense test examples: {}%\n".format(median_accuracy * 100))
    file.write("Accuracy after gaussian defense test examples: {}%\n".format(gaussian_accuracy * 100))
    file.write("Accuracy after bilateral defense test examples: {}%\n".format(bilateral_accuracy * 100))
    file.write("圖片範例可參閱evasion_images資料夾\n")
    file.write("\n")

print("txt檔建立完成")
    