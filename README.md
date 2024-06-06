# docker
利用docker-compose建立多個容器，透過執行docker-compose.yml來實現，以下示範建立五個anaconda容器，分別為anaconda1到anaconda5。
輸入指令docker-compose build，這將使用你的 Dockerfile 來構建容器鏡像
![image](https://github.com/tsubasa-k/docker/assets/61736148/7553c2aa-8839-47d8-962d-9d3913b54eb8)

輸入指令docker-compose up -d 來運行容器。默認情況下，Docker Compose 將啟動你在 docker-compose.yml 文件中定義的服務。如果你希望容器在後台運行，可以使用 -d 選項：
![image](https://github.com/tsubasa-k/docker/assets/61736148/51a638d6-6199-4e5e-9f5b-8931c1a38d2e)

docker-compose.yml裡的內容:

<img width="569" alt="螢幕擷取畫面 2023-09-16 133416" src="https://github.com/tsubasa-k/docker/assets/61736148/c9dbcc83-9728-4f45-8cc9-32207eeee6f5">


輸入指令docker ps -a 以檢查當前所有已經建立的容器，包括開啟或關閉的，圖中NAMES的anaconda1到anaconda5是剛建立好的容器，目前狀態STATUS為開啟狀態(Up，Exited為關閉狀態)

<img width="588" alt="螢幕擷取畫面 2023-09-12 235610" src="https://github.com/tsubasa-k/docker/assets/61736148/9644a17d-49aa-462b-a7dd-9444f9359474">


輸入docker-compose stop關閉容器，而這裡發現有容器無法關閉的情況。使用恨多方式，甚至是強制停止或刪除都不行
![image](https://github.com/tsubasa-k/docker/assets/61736148/78f36f4c-f1d0-44a8-a41e-c24ecb35bd44)
![image](https://github.com/tsubasa-k/docker/assets/61736148/b6b7f0d9-acfb-4a52-a63f-5807b4429cc8)

解決方式: 原因是發現linux中有一個安全模塊叫做AppArmor的，會對docker的權限產生影響，所以我們簡單地把AppArmor模塊停掉或刪掉，就可以刪除docker container了。
![image](https://github.com/tsubasa-k/docker/assets/61736148/995e67f1-3351-40f7-871b-9d711c21c28b)

解決後: 可以停止容器
![image](https://github.com/tsubasa-k/docker/assets/61736148/8cb48631-c4fa-41bb-8223-14166851c0b9)

輸入docker-compose down可以移除所有已經建立好的容器
<img width="317" alt="螢幕擷取畫面 2023-09-16 132443" src="https://github.com/tsubasa-k/docker/assets/61736148/625d78e6-8fb0-428e-ab9e-efca8ff0a5c7">


makefile內容:

<img width="421" alt="螢幕擷取畫面 2023-09-16 134211" src="https://github.com/tsubasa-k/docker/assets/61736148/c2250c90-8776-43f1-9768-11f52b81651b">


透過執行makefile來選擇執行哪項檢測功能，這裡先輸入make查詢要執行的檢測function名稱，並執行function2來做示範(之後可以改成需要的功能檢測名稱，如:DataPoisoning_Test、EvasionAttack_Test等)

![image](https://github.com/tsubasa-k/docker/assets/61736148/05e4fb45-6043-40b4-b870-54fda71ac58d)



### 這裡以feature_collection_attack來做示範
執行指令python feature_col.py < input3

<img width="585" alt="image" src="https://github.com/tsubasa-k/docker/assets/61736148/f5514e08-155d-4d8f-b5a6-3fb4d131201f">
<img width="582" alt="image" src="https://github.com/tsubasa-k/docker/assets/61736148/843a6924-9796-4b89-8a44-f8bc9b09d9ee">


執行完程式會生成images資料夾，將生成的圖片存到此資料夾作為結果呈現


<img width="441" alt="image" src="https://github.com/tsubasa-k/docker/assets/61736148/04e09dc4-6201-4b24-877a-b86327385df5">
<img width="437" alt="image" src="https://github.com/tsubasa-k/docker/assets/61736148/66aa61a2-3d7a-4981-98d0-5d0808fc4374">


並透過容器介面可以存取images裡的圖片可以進行刪除等動作

<img width="478" alt="image" src="https://github.com/tsubasa-k/docker/assets/61736148/673d138c-0b24-49a6-95ce-d49ab31f662f">

移除後:

<img width="527" alt="image" src="https://github.com/tsubasa-k/docker/assets/61736148/1b1d044b-4842-4281-a338-ded337c49ef9">

移除後images裡的圖片

<img width="440" alt="image" src="https://github.com/tsubasa-k/docker/assets/61736148/d368ae1a-c303-47a7-b2d8-f67890c15008">





