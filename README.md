# shorturl  
This is a project using python to creat a shorten url sevice  
[Demo](http://188.166.219.73/)

Install Docker
```
apt-get install apt-transport-https ca-certificates curl gnupg-agent software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"
apt-get update
apt-get install docker-ce docker-ce-cli containerd.io
```
Install Dependencies
```
apt install python3-pip
git clone https://github.com/harry0731/shorturl.git
cd shorturl
pip3 install -r requirements.txt
```

```
docker run -itd --name redis-shorturl -p 6379:6379 redis
```
```
docker run -itd --name mongo -p 27017:27017 mongo
```
edit uwsgi.ini, default, config.ini files  
```
# uwsgi.ini
chdir=<current project path>
wsgi-file=<current project path>/main.py

# default
uwsgi_param UWSGI_CHDIR <current project path>

# config.ini 
SERVER_URL_PREFIX=<current server ip or your domain>
```
```  
apt-get install nginx
cp default /etc/nginx/sites-available/default
service nginx restart

uwsgi --ini uwsgi.ini
```
```
ufw allow http
```
```
firewall-cmd --zone=public --add-port=80/tcp --permanent
firewall-cmd --reload
```

How to test  
```  
pytest
```