import redis
import urllib.parse as parse
import hashlib
import base62
import pymongo


class urlShortener:
    def __init__(self, config):
        self.config = config
        self.redis = redis.StrictRedis(
            host=self.config["redis"]["host"],
            port=self.config["redis"]["port"],
            decode_responses=True)
        self.mongo = pymongo.MongoClient(
            host=self.config["mongodb"]["host"],
            port=int(self.config["mongodb"]["port"]))
        self.mdb = self.mongo[self.config["mongodb"]["collection"]]
    
    def _short(self, url, count):
        """
        MD5 hash and take first 40bit encdoe with base62
        """
        if count + 3 < len(hashlib.md5(url.encode('utf-8')).digest()):
            return base62.encodebytes(hashlib.md5(url.encode('utf-8')).digest()[count:count+3])
        else:
            return None

    def valid_url(self, url):
        """
        Check with too long string or missed protocol
        """
        if (len(url) > self.config["DEFAULT"]["MAX_URL_LEN"]):
            return {"State":"Failed", 
                    "Error_msg":"Please don't use url longer than " + str(self.config["DEFAULT"]["MAX_URL_LEN"]) + " character."}
        parsed_url = parse.urlparse(url.decode())
        if parsed_url.scheme == '':
            return {"State":"Failed", 
                    "Error_msg":"Please use correct protocol such as 'http', 'https' or 'ftp'."}
        return {"State":"Success"}

    def get_from_redis(self, url_key):
        """
        Check the given url_key is in cache or not
        """
        return self.redis.get(url_key)

    def get_from_mongo(self, url_key):
        """
        Check the given url_key is in database or not
        """
        return self.mdb.find_one({"url_key": url_key})


    def _set_to_redis(self, url_key, url):
        """
        Set the given key-val to db, if failed return error message.
        """
        try:
            self.redis.set(url_key, url)
            return {"State":"Success"}
        except:
            return {"State":"Failed", 
                    "Error_msg": "Insert to database failed"}

    def _is_collision(self, url_key, url):
        """
        Check if the given url_key has collision
        """
        assert self.redis.get(url_key) is not None
        if self.redis.get(url_key) != url:
            return True
        return False

    def use_rand_key(self, url):
        """
        The work flow of general usage.
        """
        # In general mode, generate the relative key first.
        url_key = None
        count = 0
        while url_key == None:
            # generate short url
            # check if existed
            # check in collisio
            url_key = self._short(url, count)
            # Check if the generated key has been used
            if self.get_from_mongo(url_key) is not None:
                # key is in db, check collision
                if self._is_collision(url_key, url):
                    # collision, insert it and replace the old one.
                    set_res = self._set_to_redis(url_key, url)
                    if set_res["State"] != "Success":
                        return set_res
                else:
                    # TODO
                    pass
        else:
            # key is not in db, insert it.
            set_res = self._set_to_redis(url_key, url)
            if set_res["State"] != "Success":
                return set_res

        return {"State":"Sucess", 
                "short_url":"%s/%s" % (self.config["DEFAULT"]["SERVER_URL_PREFIX"], url_key)} 