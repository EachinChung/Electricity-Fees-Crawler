## 简介
[![_](https://img.shields.io/badge/python-3.7.7-informational.svg)](https://www.python.org/)
[![_](https://img.shields.io/badge/mysql-8.0.20-9cf.svg)](https://www.mysql.com/)

中山大学南方学院的电费爬虫

## 项目使用说明
### 安装依赖库
- 项目依赖 [requirements.txt](requirements.txt)

```
➜ pip3 install -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt
```

### 配置 env
- 请在根目录创建 .env 文件

```
# 文件夹根目录
BASE=xxxxx

# MySQL 账户密码
MYSQL_USER=xxxxx
MYSQL_PASSWORD=xxxxx
```

### 初始化 MySQL
```
➜ mysql -u root -p < nfu.sql
➜ mysql -u root -p < dormitory.sql
```


### 开始运行程序
```
➜ python3 main.py
```

## 开源协议
本项目基于 [MIT](https://zh.wikipedia.org/wiki/MIT%E8%A8%B1%E5%8F%AF%E8%AD%89) 协议。