# 定義參數列表
PARAMS := function1 function2 function3 function4 function5

# 定義預設目標
.DEFAULT_GOAL := help

# 定義幫助信息
.PHONY: help
help:
	@echo "Available targets:" 
	@echo "  make function1  - Execute code for function1" 
	@echo "  make function2  - Execute code for function2"
	@echo "  make function3  - Execute code for function1" 
	@echo "  make function4  - Execute code for function2"
	@echo "  make function5  - Execute code for function1" 
	@echo "  make function6  - Execute code for function2"

# 定義各個目標，根據輸入的參數執行對應的Shell腳本
function1:
	@echo "Executing code for function1: Data_Augmentation"
	@docker exec -it -w /app Data_Augmentation /bin/bash
function2:
	@echo "Executing code for function2: Model_Similarity"
	@docker exec -it -w /app Model_Similarity /bin/bash
function3:
	@echo "Executing code for function3: Evasion_Attack"
	@docker exec -it -w /app Evasion_Attack /bin/bash
function4:
	@echo "Executing code for function4: Feature_Collision_Attack"
	@docker exec -it -w /app Feature_Collision_Attack /bin/bash
function5:
	@echo "Executing code for function5: Hidden_Backdoor_Attack"
	@docker exec -it -w /app Hidden_Backdoor_Attack /bin/bash
