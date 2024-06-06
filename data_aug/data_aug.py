import os, sys
from os.path import abspath
import warnings
warnings.filterwarnings('ignore')

from tensorflow.keras.models import load_model

from art import config
from art.utils import load_dataset, get_file
from art.estimators.classification import KerasClassifier
from art.attacks.evasion import FastGradientMethod

import numpy as np
#%matplotlib inline
import matplotlib.pyplot as plt
import tensorflow as tf
    
tf.compat.v1.disable_eager_execution()
#_____________________________________________
myinput = []
demo_times = 5

#myinput[0] label
#myinput[1] h5檔名稱
#myinput[2] model url
#myinput[3] data url
#myinput[4] csv url
#myinput[5] image RGB max
#myinput[6] image resize x_size
#myinput[7] image resize y_size
#myinput[8] feature layer //data_aug沒有用到

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

#建立資料夾
script_path = os.path.abspath(sys.argv[0])
script_dir = os.path.dirname(script_path)

save_dir = './augmented_images'
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

#_____________________________________________
url = myinput[2]
local_filename = myinput[1]

response = requests.get(url)
with open(local_filename, 'wb') as f:
    f.write(response.content)

classifier_model = load_model(myinput[1])

classifier = KerasClassifier(clip_values=(0, int(myinput[7])), model=classifier_model, use_logits=False, preprocessing=(0.5, 1))

predictions = classifier_model.predict(x_test)
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
#data aug
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# Create an instance of the ImageDataGenerator 
datagen = ImageDataGenerator(
    rotation_range=180,  # Random rotation within the range of 0-180 degrees
    width_shift_range=0.3,  # Randomly shift the width by 0-10% of the total width
    height_shift_range=0.3,  # Randomly shift the height by 0-10% of the total height
    shear_range=0.2,  # Random shear within the range of 0-20 degrees
    zoom_range=[0.8, 1.2]  # Random zooming within the range of 0.8-1.2
)
datagen.fit(x_test)
# Define the batch size for data augmentation
batch_size = 32
# Generate augmented data for training
augmented_data_generator = datagen.flow(
    x_test,
    y_test,
    batch_size=batch_size,
    shuffle=False
)
num_augmented_images = 1000  # Number of augmented images to generate
num_batches = int(num_augmented_images / batch_size)

augmented_x_test = []
augmented_y_test = []

for _ in range(num_batches):
    augmented_images, augmented_labels = augmented_data_generator.next()
    augmented_x_test.append(augmented_images)
    augmented_y_test.append(augmented_labels)

augmented_x_test = np.concatenate(augmented_x_test, axis=0)
augmented_y_test = np.concatenate(augmented_y_test, axis=0)

x_test = np.concatenate([x_test, augmented_x_test], axis=0)
y_test = np.concatenate([y_test, augmented_y_test], axis=0)

#_____________________________________________
predictions = classifier_model.predict(x_test)
accuracy = np.sum(np.argmax(predictions, axis=1) == np.argmax(y_test, axis=1)) / len(y_test)
after_accuracy = accuracy
print("Accuracy after test examples: {}%".format(accuracy * 100))

for i in range(demo_times):
    plt.imshow(augmented_x_test[i]/int(myinput[5]))
    plt.axis('off')
    file_name = str(i) + 'aug_after.png'
    file_path = os.path.join(save_dir, file_name)
    plt.savefig(file_path)

#_____________________________________________
import datetime
current_time = datetime.datetime.now()
formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

current_directory = os.getcwd()


file_name = "Readme.txt"
with open(file_name, "a") as file:
    file.write("_____________________________________________\n")
    file.write("測試項目 : Data Augment\n")
    file.write("測試時間 : {}\n".format(formatted_time))
    file.write("模型名稱 : {}\n".format(myinput[1]))
    file.write("測試資料數量 : {}\n".format(data_num))
    file.write("此項模型測試評估測試模型對於經過外部干擾的圖像的表現\n")
    file.write("--->\n")
    file.write("模擬外部干擾的操作如下\n")
    file.write("旋轉 (0度到180度)\n")
    file.write("寬度位移 (0-30%)\n")
    file.write("高度位移 (0-30%)\n")
    file.write("剪切 (0-20%)\n")
    file.write("縮放 (0.8到1.2倍)\n")
    file.write("\n")
    file.write("檢測模型的準確性是否會受到影響\n")
    file.write("Accuracy benign test examples: {}%\n".format(benign_accuracy * 100))
    file.write("Accuracy after test examples: {}%\n".format(after_accuracy * 100))
    file.write("圖片範例可參閱augmented_images資料夾\n")
    file.write("\n")

print("txt檔建立完成")
