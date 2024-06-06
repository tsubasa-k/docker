#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os, sys
from os.path import abspath
from tensorflow.keras.models import load_model

module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)

import warnings
warnings.filterwarnings('ignore')
from art import config
from art.estimators.classification import KerasClassifier
import tensorflow as tf
import numpy as np
from art.utils import load_dataset, get_file
import matplotlib.pyplot as plt
    
tf.compat.v1.disable_eager_execution()



# In[2]:


from art.utils import load_dataset
(x_train, y_train), (x_test, y_test), min_, max_ = load_dataset('cifar10')


# In[3]:
myinput = []
demo_times = 5

#myinput[0] lmodel url

try:
    while True:
        text = input()
        myinput.append(text)
except EOFError:
    pass
print(myinput)


#drive
path = get_file('cifar_alexnet.h5',extract=False, path=config.ART_DATA_PATH,
                url=myinput[0])
model = load_model(path)
classifier = KerasClassifier(clip_values=(min_, max_), model=model, use_logits=False, 
                             preprocessing=(0.5, 1))

#mark 1  url


# In[3]:


#local 
#model = load_model('C:/Users/New/cifar10_model2.h5')
#model1 or model 2



#classifier = KerasClassifier(clip_values=(min_, max_), model=model, use_logits=True)


# In[4]:


from art.attacks.poisoning.backdoor_attack import PoisoningAttackBackdoor
target = np.array([0,0,0,0,1,0,0,0,0,0])
source = np.array([0,0,0,1,0,0,0,0,0,0])




# Backdoor Trigger Parameters
patch_size = 8
x_shift = 32 - patch_size - 5
y_shift = 32 - patch_size - 5

# Define the backdoor poisoning object. Calling backdoor.poison(x) will insert the trigger into x.
from art.attacks.poisoning import perturbations
def mod(x):
    original_dtype = x.dtype
    x = perturbations.insert_image(x, backdoor_path="./htbd.png",
                                   channels_first=False, random=False, x_shift=x_shift, y_shift=y_shift,
                                   size=(patch_size,patch_size), mode='RGB', blend=1)
    return x.astype(original_dtype)
backdoor = PoisoningAttackBackdoor(mod)


# In[5]:


from art.attacks.poisoning import HiddenTriggerBackdoor
poison_attack = HiddenTriggerBackdoor(classifier, eps=16/255, target=target, source=source, feature_layer= classifier.layer_names[-1], backdoor=backdoor, learning_rate=0.01, decay_coeff = .1, decay_iter = 1000, max_iter=5000, batch_size=25, poison_percent=.015)

poison_data, poison_indices = poison_attack.poison(x_train, y_train)
print("Number of poison samples generated:", len(poison_data))


# In[6]:


# fig, axes = plt.subplots(nrows=2, ncols=5, figsize=(12, 6))
# print ("poisoned data should be similar to origin one ")
# for i, ax in enumerate(axes.flat):
#     ax.imshow(poison_data[i])
#     ax.axis('off') 

#plt.tight_layout()
#plt.show()


# In[7]:


# Create finetuning dataset
dataset_size = 250
num_classes = 10
num_per_class = dataset_size/num_classes

poison_dataset_inds = []

for i in range(num_classes):
    class_inds = np.where(np.argmax(y_train,axis=1) == i)[0]
    num_select = int(num_per_class)
    if np.argmax(target) == i:
        num_select = int(num_select - min(num_per_class,len(poison_data)))
        poison_dataset_inds.append(poison_indices)
        
    if num_select != 0:
        poison_dataset_inds.append(np.random.choice(class_inds, num_select, replace=False))
    
poison_dataset_inds = np.concatenate(poison_dataset_inds)

poison_x = np.copy(x_train)
poison_x[poison_indices] = poison_data
poison_x = poison_x[poison_dataset_inds]

poison_y = np.copy(y_train)[poison_dataset_inds]


# In[8]:


# # Create finetuning dataset
# dataset_size = 2500
# num_classes = 10
# num_per_class = dataset_size/num_classes

# poison_dataset_inds = []

# for i in range(num_classes):
#     class_inds = np.where(np.argmax(y_train,axis=1) == i)[0]
#     num_select = int(num_per_class)
#     print(class_inds,num_select)
#     num_to_sample = min(num_select, len(class_inds))
#     if np.argmax(target) == i:
#         num_select = int(num_select - min(num_per_class,len(poison_data)))
#         poison_dataset_inds.append(poison_indices)
        
#     if num_to_sample > 0:
#         #poison_dataset_inds.append(np.random.choice(class_inds, int(class_inds.shape[0]/2), replace=False)) 
#         #poison_dataset_inds.append(np.random.choice(class_inds, num_select, replace=False))
#         poison_dataset_inds.append(np.random.choice(class_inds, num_to_sample, replace=False))
    
# poison_dataset_inds = np.concatenate(poison_dataset_inds)

# poison_x = np.copy(x_train)
# poison_x[poison_indices] = poison_data
# poison_x = poison_x[poison_dataset_inds]

# poison_y = np.copy(y_train)[poison_dataset_inds]


# In[9]:


finetune_classifier = KerasClassifier(clip_values=(min_, max_), model=model, use_logits=True)


# In[12]:


trigger_test_inds = np.where(np.all(y_test == source, axis=1))[0]

test_poisoned_samples, test_poisoned_labels  = backdoor.poison(x_test[trigger_test_inds], y_test[trigger_test_inds])



for i in range(4):
    predictions = finetune_classifier.predict(x_test)
    accuracy = np.sum(np.argmax(predictions, axis=1) == np.argmax(y_test, axis=1)) / len(y_test)
    print("Accuracy on benign test examples: {}%".format(accuracy * 100))
    
    predictions = finetune_classifier.predict(x_test[trigger_test_inds])
    b_accuracy = np.sum(np.argmax(predictions, axis=1) == np.argmax(y_test[trigger_test_inds], axis=1)) / len(trigger_test_inds)
    print("Accuracy on benign trigger test examples: {}%".format(b_accuracy * 100))
    
    predictions = finetune_classifier.predict(test_poisoned_samples)
    p_accuracy = np.sum(np.argmax(predictions, axis=1) == np.argmax(test_poisoned_labels,axis=1)) / len(test_poisoned_labels)
    print("Accuracy on poison trigger test examples: {}%".format(p_accuracy * 100))
    
    print()
    print("Training Epoch", i)
    

    finetune_classifier.fit(poison_x, poison_y, nb_epochs=1)


# In[13]:


print("Final Performance")
predictions = finetune_classifier.predict(x_test)
accuracy = np.sum(np.argmax(predictions, axis=1) == np.argmax(y_test, axis=1)) / len(y_test)
print("Accuracy on benign test examples: {}%".format(accuracy * 100))


predictions = finetune_classifier.predict(x_test[trigger_test_inds])
b_accuracy = np.sum(np.argmax(predictions, axis=1) == np.argmax(y_test[trigger_test_inds], axis=1)) / len(trigger_test_inds)
print("Accuracy on benign trigger test examples: {}%".format(b_accuracy * 100))


predictions = finetune_classifier.predict(test_poisoned_samples)
p_accuracy = np.sum(np.argmax(predictions, axis=1) == np.argmax(test_poisoned_labels,axis=1)) / len(test_poisoned_labels)
print("Accuracy on poison trigger test examples: {}%".format(p_accuracy * 100))



# In[ ]:





# In[ ]:

#_____________________________________________
import datetime
current_time = datetime.datetime.now()
formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

file_name = "Readme.txt"
with open(file_name, "a") as file:
    file.write("_____________________________________________\n")
    file.write("測試項目 : Hidden Backdoor Attack\n")
    file.write("測試時間 : {}\n".format(formatted_time))
    file.write("模型名稱 : {}\n".format(myinput[1]))
    file.write("測試資料數量 : {}\n".format(poison_x.shape[0]))
    file.write("此模型測試使用的是Hidden Backdoor Attack的攻擊方式\n")
    file.write("攻擊者透過在目標系統中插入隱藏的後門\n")
    file.write("藉由觸發隱藏後門\n")
    file.write("導致模型分類準確率下降\n")
    file.write("--->\n")
    file.write("在此測試中我們會呈現攻擊前的準確率\n")
    file.write("另外提供帶有特定標記以及帶有惡意標記測試樣本的準確率，供您參考針對此攻擊的的防禦效果\n")
    file.write("Accuracy on benign test examples: {}%\n".format(accuracy * 100))
    file.write("Accuracy on benign trigger test examples: {}%\n".format(b_accuracy * 100))
    file.write("Accuracy on poison trigger test examples: {}%\n".format(p_accuracy * 100))
    file.write("\n")

print("txt檔建立完成")
    


