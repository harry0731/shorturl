# shorturl  

這個專案使用Python來實現短網址服務  
在Ubuntu 18.04以及20.04上經過測試  
![alt Demo](assets/Demo.png?raw=true "Demo")  
[Demo](http://188.166.219.73/)  

# **安裝流程**
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
### 啟動uWSGI Server
```  
$ uwsgi --ini uwsgi.ini
```  
### 假如request被防火牆擋住可以用以下指令開啟防火牆
```
$ ufw allow http
```

# **使用說明**  
直接呼叫Server位址有網頁可以使用  
Shorten按鈕功能為將長網址縮短  
Preview按鈕功能為預覽短網址(將短網址還原)  

也有API可以呼叫  
### **縮短網址API** 
```  
POST /shortURL HTTP/1.1
Accept: application/json
Content-Type: application/json

{
    "url": "https://www.google.com/",
}
```  
回傳資訊  
```
{
   "State": "Success",
   "short_url": "http://188.166.219.73/xD0R"
}
```  

### **預覽網址API** 
不用GET改用POST該短網址  
```  
POST /(url_key) HTTP/1.1
```  
回傳資訊  
```
{
   "State": "Success",
   "url": "https://www.google.com/"
}
```  

### **短網址自動轉址** 
```  
GET /(url_key) HTTP/1.1
```  

### **注意事項**  
* 太長的網址會被拒絕轉換  
網址最大長度設定可在uwsgi.ini中更改(預設為2000)  
* 違法的網址也會拒絕轉換  
開頭非http https ftp...等等


# **如何測試**  
本專案使用pytest做為測試工具  
在專案根目錄下執行以下指令
```  
$ pytest
```  

# **Scaling**  
* 在MongoDB的存取部分有做Double Check避免不同台Worker同時存入相同的hash value
* 使用MongoDB Sharding來因應更大的使用流量  
* 使用Nginx做Load balance來分流多台機器上的uWSGI Server  