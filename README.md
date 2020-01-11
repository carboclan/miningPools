# miningPools
 
环境:

- mongodb (127.0.0.1 默认端口 无密码)
- redis (127.0.0.1 默认端口 无密码)
- python3.8.0 
需要先`pip install -r requirements.txt`

爬虫程序是 `python run.py`(需要5分钟跑一次.也就是5分钟更新一次数据)

提供api 是 `python app.py` 端口是5000... api地址是 `http://127.0.0.1:5000/`

某个id的历史价格记录:

示例:  http://127.0.0.1:5000/snapshot?id=bitdeer_200107903&ts1=1&ts2=1578819673