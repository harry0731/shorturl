# shorturl  

這個專案使用Python來實現短網址服務  
在Ubuntu 18.04以及20.04上經過測試  
![alt Demo](assets/Demo.png?raw=true "Demo")  
[Demo](http://188.166.219.73/)  

# **安裝流程**  
### 1. Docker
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

### 2. Python 3
```  
$ apt-get install python3 python3-pip
```  
### 3. Nginx  
```  
$ apt-get install nginx
```  
### 4. 專案下載以及安裝所需相關套件
```  
$ git clone https://github.com/harry0731/shorturl.git
$ cd shorturl
$ pip3 install -r requirements.txt
```  
# **專案部屬流程**  
### 0. 注意事項  
專案內有三個設定檔  
分別為  
* config.ini  
專案內部設定
* default  
Nginx設定檔
* uwsgi.ini  
uWSGI設定檔  

底下的安裝流程皆使用預設選項，你可以根據自己需要做修正，比如說假如我想變更Redis服務所使用的port，你就可以在步驟1的地方改變redis container對外所使用的port，並且在config.ini內更改對應的參數redis->port，或是變更Nginx或是uWSGI的設定檔使其更加符合當下的Server運作環境，也或是可以連線至其他台Server上的Redis或是MongoDB等等的設定  
*PS: uwsgi.ini內的lazy-apps必須是true 否則與MongoDB的連線會有錯誤*

### 1. 建立Redis 做為系統Cache
```
$ docker run -itd --name redis-shorturl -p 6379:6379 redis
```  
### 2. 建立MongoDB 做為系統Database
```
$ docker run -itd --name mongo-shorturl -p 27017:27017 mongo
```
### 3. 修改 uwsgi.ini, default, config.ini 三個檔案  
```
# uwsgi.ini
chdir=<目前專案路徑>
wsgi-file=<目前專案路徑>/main.py

# default
uwsgi_param UWSGI_CHDIR <目前專案路徑>

# config.ini 
SERVER_URL_PREFIX=<目前Server的Domain或是ip>
```  
### 4. 設定Nginx
```  
$ cp default /etc/nginx/sites-available/default
$ service nginx restart
```  
### 5. 啟動uWSGI Server
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
![alt shortenurl](assets/shortenurl.gif?raw=true "shortenurl")  
Preview按鈕功能為預覽短網址(將短網址還原)  
![alt previewurl](assets/previewurl.gif?raw=true "previewurl") 

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
使用POST對該短網址進行請求即可取得原始網址
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
需要注意的是  
test_shortURL_api_small_amount以及test_shortURL_api_massive兩個測試所需要的時間相當長  test_shortURL_api_small_amount測試256^2組url  
test_shortURL_api_massive測試256^4組url
* 完整測試，不建議，時間太長
```  
$ pytest
```  
* 部分測試，不跑test_shortURL_api_massive，相對較快(37min)  
```
$ pytest -k "shorturl_test and not massive" 
```  
* 部分測試，不跑test_shortURL_api_massive以及test_shortURL_api_small_amount，最快(0.56sec)  
```
$ pytest -k "shorturl_test and not massive and not small_amount" 
```

# **Scaling**  
* 在MongoDB的存取部分有做Double Check避免不同台Worker同時存入相同的hash value
* 使用MongoDB Sharding來因應更大的使用流量  
* 使用Nginx做Load balance來分流多台機器上的uWSGI Server  