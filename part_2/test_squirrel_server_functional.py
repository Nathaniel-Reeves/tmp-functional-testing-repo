import http.client
import json
import os
import pytest
import shutil
import subprocess
import sys
import time
import urllib
import sqlite3

from squirrel_db import SquirrelDB

todo = pytest.mark.skip(reason="todo: pending spec")

def describe_squirrel_server():

    @pytest.fixture(autouse=True)
    def setup_and_cleanup_database():
        # Setup the database
        shutil.copyfile('squirrel_db.db.template', 'squirrel_db.db')
        yield
        # cleanup the database
        os.remove('squirrel_db.db')

    @pytest.fixture(autouse=True, scope='session')
    def start_and_stop_squirrel_server():
        # Run the Server in a new process
        proc = subprocess.Popen([sys.executable, 'squirrel_server.py'])
        time.sleep(0.1)
        yield
        # Stop the Server
        proc.kill()

    @pytest.fixture
    def http_client():
        conn = http.client.HTTPConnection('localhost:8080')
        return conn

    def describe_GET_squirrels():

        def it_returns_200_status_code(http_client):
            http_client.request('GET', '/squirrels')
            response = http_client.getresponse()
            http_client.close()

            assert response.status == 200

        def it_returns_json_content_type_header(http_client):
            http_client.request('GET', '/squirrels')
            response = http_client.getresponse()
            http_client.close()

            assert response.getheader('Content-Type') == 'application/json'

        def it_returns_empy_json_array(http_client):
            http_client.request('GET', '/squirrels')
            response = http_client.getresponse()
            http_client.close()

            assert json.loads(response.read()) == []

        def it_returns_json_array_with_one_squirrel(http_client):
            # insert a new squirrel
            db = SquirrelDB()
            db.createSquirrel('Test_Squirrel', '42')

            http_client.request('GET', '/squirrels')
            response = http_client.getresponse()
            response_body = json.loads(response.read())
            http_client.close()

            assert response_body == [{"id": 1, "name": "Test_Squirrel", "size": '42'}]

    def describe_POST_squirrels():

        def it_returns_201_status_code(http_client):
            data = urllib.parse.urlencode({"name": "Test_Squirrel", "size": '42'})
            headers = {"content-type": "application/x-www-form-urlencoded"}

            http_client.request('POST', '/squirrels', data, headers)
            response = http_client.getresponse()
            http_client.close()

            assert response.status == 201

