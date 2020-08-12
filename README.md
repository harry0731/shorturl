# shorturl  

這個專案使用Python來實現短網址服務  
[Demo](http://188.166.219.73/)  

## 安裝流程
### Docker
本專案會需要使用到Docker來快速建立MongoDB資料庫以及Redis做為系統Cache  
Docker在Ubuntu, Mint, 或是 Debian系統下的安裝流程  
```
$ apt-get install apt-transport-https ca-certificates curl gnupg-agent software-properties-common
$ curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
$ add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"
$ apt-get update
$ apt-get install docker-ce docker-ce-cli containerd.io
```  

### Python 3
```  
$ apt-get install python3 python3-pip
```  
### Nginx  
```  
$ apt-get install nginx
```  
### 專案下載以及安裝所需相關套件
```  
$ git clone https://github.com/harry0731/shorturl.git
$ cd shorturl
$ pip3 install -r requirements.txt
```
### 建立Redis 做為系統Cache
```
$ docker run -itd --name redis-shorturl -p 6379:6379 redis
```  
### 建立MongoDB 做為系統Database
```
$ docker run -itd --name mongo -p 27017:27017 mongo
```
### 修改 uwsgi.ini, default, config.ini 三個檔案  
```
# uwsgi.ini
chdir=<目前專案路徑>
wsgi-file=<目前專案路徑>/main.py

# default
uwsgi_param UWSGI_CHDIR <目前專案路徑>

# config.ini 
SERVER_URL_PREFIX=<目前Server的Domain或是ip>
```  
### 設定Nginx
```  
$ cp default /etc/nginx/sites-available/default
$ service nginx restart
```  
### 啟動uWSGI服務
```  
$ uwsgi --ini uwsgi.ini
```  
### 假如request被防火牆擋住可以用以下指令開啟防火牆
```
$ ufw allow http
```

## 如何測試  
本專案使用pytest做為測試工具  
在專案根目錄下執行以下指令
```  
$ pytest
```