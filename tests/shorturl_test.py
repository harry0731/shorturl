import os
import tempfile
import pytest
import json
from urllib.parse import urlparse

# this import from parent folder
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

import main
from urlShortener import urlShortener

# using testing db
main.config["mongodb"]["collection"] = "test_shorturl"

class FakeCache:
    def get(self, url_key):
        return None
    def set(self, url_key):
        return None

@pytest.fixture
def client_with_cache():
    main.app.config['TESTING'] = True
    # using testing db
    main.config["mongodb"]["collection"] = "test_shorturl"
    main.urlShortener = urlShortener(main.config, main.logger)
    with main.app.test_client() as client:
        yield client

@pytest.fixture
def client():
    main.app.config['TESTING'] = True
    # use fake redis cache to check db work fine
    main.shortener.redis = FakeCache()
    # using testing db
    main.config["mongodb"]["collection"] = "test_shorturl"
    main.urlShortener = urlShortener(main.config, main.logger)
    with main.app.test_client() as client:
        yield client

def test_redis_set(client_with_cache):
    r = main.shortener._set_to_redis("123", "321")
    assert r == True
    main.shortener.redis.flushdb()

def test_redis_get_with_value(client_with_cache):
    key = "foo"
    val = "7894"
    r = main.shortener._set_to_redis(key, val)
    v = main.shortener._get_from_redis(key)
    assert r == True
    assert v == val
    main.shortener.redis.flushdb()

def test_redis_get_with_no_value(client_with_cache):
    key = "nonono"
    main.shortener.redis.flushdb()
    v = main.shortener._get_from_redis(key)
    assert v == None
    main.shortener.redis.flushdb()

def test_index_website(client):
    rv = client.get('/')
    assert rv.status_code == 200

def test_shortURL_api(client):
    rv = client.post(
            '/shortURL',
            json={"url": "https://www.google.com/"}
        )
    assert rv.status_code == 200
    assert (json.loads(rv.data.decode("utf-8"))["short_url"]).endswith("xD0R")
    main.shortener.mdb.drop()

def test_shortURL_api_with_illegal_url(client):
    rv = client.post(
            '/shortURL',
            json={"url": "321.ggg"}
        )
    assert rv.status_code == 400
    assert (json.loads(rv.data.decode("utf-8"))["State"]) == "Failed"
    assert (json.loads(rv.data.decode("utf-8"))["Error_msg"]) == "Please use correct protocol such as 'http', 'https' or 'ftp'."

def test_redirect_shortURL(client):
    test_url = "https://www.google.com/"
    rv = client.post(
            '/shortURL',
            json={"url": test_url}
        )
    rrv = client.get(json.loads(rv.data.decode("utf-8"))["short_url"])
    assert rv.status_code == 200
    assert rrv.status_code == 302
    assert rrv.location == test_url
    main.shortener.mdb.drop()

def test_no_redirect_shortURL(client):
    test_url = "https://www.google.com/"
    rv = client.post(
            '/shortURL',
            json={"url": test_url}
        )
    rrv = client.post(json.loads(rv.data.decode("utf-8"))["short_url"])
    assert rv.status_code == 200
    assert rrv.status_code == 200
    assert (json.loads(rrv.data.decode("utf-8"))["url"]) == test_url
    main.shortener.mdb.drop()