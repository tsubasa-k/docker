=== Contents of data_aug/Readme.txt ===
_____________________________________________
測試項目 : Data Augment
測試時間 : 2023-09-04 14:20:04
模型名稱 : res50_32x32.h5
測試資料數量 : 352
此項模型測試評估測試模型對於經過外部干擾的圖像的表現
--->
模擬外部干擾的操作如下
旋轉 (0度到180度)
寬度位移 (0-30%)
高度位移 (0-30%)
剪切 (0-20%)
縮放 (0.8到1.2倍)

檢測模型的準確性是否會受到影響
Accuracy benign test examples: 60.22727272727273%
Accuracy after test examples: 55.58035714285714%
圖片範例可參閱augmented_images資料夾



=== Contents of hidden_backdoor/Readme.txt ===
_____________________________________________
測試項目 : Hidden Backdoor Attack
測試時間 : 2023-09-04 14:28:34
模型名稱 : model1         #model_name
測試資料數量 : 300
此模型測試使用的是Hidden Backdoor Attack的攻擊方式
攻擊者透過在目標系統中插入隱藏的後門
藉由觸發隱藏後門
導致模型分類準確率下降
--->
在此測試中我們會呈現攻擊前的準確率
另外提供帶有特定標記以及帶有惡意標記測試樣本的準確率，供您參考針對此攻擊的的防禦效果
Accuracy on benign test examples: 84.73%
Accuracy on benign trigger test examples: 87.9%
Accuracy on poison trigger test examples: 72.8%



=== Contents of model_similarity/Readme.txt ===
_____________________________________________
測試項目 : Model Similarity
測試時間 : 2023-09-04 14:21:24
模型名稱 : res50_32x32.h5
函數式連接方式
模型使用的是ResNet架構



