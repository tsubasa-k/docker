# docker
利用docker-compose建立多個容器，透過執行docker-compose.yml來實現，以下示範建立兩個anaconda容器，分別為anaconda1和anaconda2
<img width="356" alt="image" src="https://github.com/tsubasa-k/docker/assets/61736148/5146708f-6220-410e-bf07-7508420a1cca">


輸入指令docker ps -a 以檢查當前所有已經建立的容器，包括開啟或關閉的，圖中NAMES的anaconda1和anaconda2是剛建立好的容器，目前狀態STATUS為開啟狀態(Up，Exited為關閉狀態)

<img width="583" alt="image" src="https://github.com/tsubasa-k/docker/assets/61736148/a410e390-c16e-49fb-812e-f7ade1375e08">



makefile內容:

<img width="359" alt="image" src="https://github.com/tsubasa-k/docker/assets/61736148/c14cbde5-e5b5-470c-b5e1-cca6672130a1">


透過執行makefile來選擇執行哪項檢測功能，這裡以執行function2來做示範(之後可以改成需要的功能檢測名稱，如:DataPoisoning_Test、EvasionAttack_Test等)
### 這裡以feature_collection_attack來做示範
執行指令python feature_col.py < input3

<img width="585" alt="image" src="https://github.com/tsubasa-k/docker/assets/61736148/f5514e08-155d-4d8f-b5a6-3fb4d131201f">
<img width="582" alt="image" src="https://github.com/tsubasa-k/docker/assets/61736148/843a6924-9796-4b89-8a44-f8bc9b09d9ee">


執行完程式會生成images資料夾，將生成的圖片存到此資料夾作為結果呈現


<img width="441" alt="image" src="https://github.com/tsubasa-k/docker/assets/61736148/04e09dc4-6201-4b24-877a-b86327385df5">
<img width="437" alt="image" src="https://github.com/tsubasa-k/docker/assets/61736148/66aa61a2-3d7a-4981-98d0-5d0808fc4374">


並透過容器介面可以存取images裡的圖片可以進行刪除等動作

<img width="478" alt="image" src="https://github.com/tsubasa-k/docker/assets/61736148/673d138c-0b24-49a6-95ce-d49ab31f662f">

<img width="527" alt="image" src="https://github.com/tsubasa-k/docker/assets/61736148/1b1d044b-4842-4281-a338-ded337c49ef9">

<img width="440" alt="image" src="https://github.com/tsubasa-k/docker/assets/61736148/d368ae1a-c303-47a7-b2d8-f67890c15008">





