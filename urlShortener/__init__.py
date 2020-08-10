import redis
import urllib.parse as parse
import hashlib
import base62
import pymongo


class urlShortener:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.redis = redis.StrictRedis(
            host=self.config["redis"]["host"],
            port=int(self.config["redis"]["port"]),
            decode_responses=True)
        self.mongo = pymongo.MongoClient(
            host=self.config["mongodb"]["host"],
            port=int(self.config["mongodb"]["port"]))
        self.mdb = self.mongo[self.config["mongodb"]["collection"]][self.config["mongodb"]["collection"]]
        self.logger.debug("urlShortener initial")
    
    def _short(self, url, count):
        """
        MD5 hash and take first 40bit encdoe with base62
        """
        if count + 3 < len(hashlib.md5(url.encode('utf-8')).digest()):
            result = base62.encodebytes(hashlib.md5(url.encode('utf-8')).digest()[count:count+3])
            self.logger.debug(f"shorten hash url: {url}, count: {count}, result: {result}")
            return result
        else:
            self.logger.debug("shorten hash url count > md5 bits")
            return None

    def valid_url(self, url):
        """
        Check with too long string or missed protocol
        """
        if (len(url) > int(self.config["DEFAULT"]["MAX_URL_LEN"])):
            self.logger.debug(f"url: {url} length illigal")
            return {"State":"Failed", 
                    "Error_msg":"Please don't use url longer than " + str(self.config["DEFAULT"]["MAX_URL_LEN"]) + " character."}
        parsed_url = parse.urlparse(url)
        if parsed_url.scheme == '':
            self.logger.debug(f"url: {url} format illigal")
            return {"State":"Failed", 
                    "Error_msg":"Please use correct protocol such as 'http', 'https' or 'ftp'."}
        return {"State":"Success"}

    def get_url(self, url_key):
        self.logger.debug(f"get url, url_key: {url_key}")
        result = self._get_from_redis(url_key)
        if result == None:
            result = self._get_from_mongo(url_key)
            if result != None:
                self._set_to_redis(url_key, result["url"])
                return result["url"]
            else:
                return None
        else:
            return result

    def _get_from_redis(self, url_key):
        """
        Check the given url_key is in cache or not
        """
        return self.redis.get(url_key)

    def _get_from_mongo(self, url_key):
        """
        Check the given url_key is in database or not
        """
        return self.mdb.find_one({"url_key": url_key})

    def _set_to_redis(self, url_key, url):
        """
        Set the given key-val to cache
        """
        try:
            self.redis.set(url_key, url)
            return True
        except:
            return False
    
    def _set_to_mongo(self, url_key, url):
        """
        Set the given key-val to db, if failed return error message.
        """
        data = {"url_key": url_key, "url": url}
        self.logger.debug(f"insert data to mongodb: {data}")
        try:
            self.mdb.insert_one(data)
            r = self._get_from_mongo(url_key)
            print(r)
            if r != None and r["url"] == url:
                self.logger.debug("insert data to mongodb success")
                return {"State":"Success"}
            else:
                self.logger.debug("insert data to mongodb failed")
                return {"State":"Failed", 
                        "Error_msg": "Insert to database failed"}
        except:
            self.logger.debug("insert data to mongodb failed")
            return {"State":"Failed", 
                    "Error_msg": "Insert to database failed"}

    def generate_shorturl(self, url):
        """
        The work flow of general usage.
        """
        # In general mode, generate the relative key first.
        url_key = None
        count = 0
        while url_key == None:
            # generate short url
            url_key = self._short(url, count)
            if url_key != None:
                # Check if the generated key has been used
                collision_check = self._get_from_mongo(url_key)
                if collision_check != None:
                    # key is in db, check collision
                    if collision_check["url"] == url:
                        self.logger.debug("URL already existed")
                        return {"State":"Success", 
                                "short_url":"%s/%s" % (self.config["DEFAULT"]["SERVER_URL_PREFIX"], url_key)} 
                    else:
                        # collision occured generate new hah
                        count += 1
                        continue
                else:
                    # key is not in db, insert it.
                    set_res = self._set_to_mongo(url_key, url)
                    if set_res["State"] != "Success":
                        # insert faild try with new hash
                        self.logger.debug("insert to db faild")
                        count += 1
                        continue
                    else:
                        # insert succe, put data in cache
                        cache = self._set_to_redis(url_key, url)
                        self.logger.debug(f"Cache Success: {cache}")
                        return {"State":"Success", 
                                "short_url":"%s/%s" % (self.config["DEFAULT"]["SERVER_URL_PREFIX"], url_key)}
            else:
                # Used all md5 bits
                self.logger.debug("Used all md5 bits")
                break
        return {"State":"Failed", 
                "Error_msg": "Couldn't find appropriate short url"}
        

        