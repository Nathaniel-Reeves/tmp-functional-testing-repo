import http.client
import json
import os
import pytest
import shutil
import subprocess
import sys
import time
import urllib

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

        def describe_GET_squirrels_with_valid_resourceName():

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

            def it_returns_json_array_with_many_squirrels(http_client):
                # instert new squirrels
                db = SquirrelDB()
                db.createSquirrel('Test_Squirrel_1', '42')
                db.createSquirrel('Test_Squirrel_2', '43')
                db.createSquirrel('Test_Squirrel_3', '44')

                http_client.request('GET', '/squirrels')
                response = http_client.getresponse()
                response_body = json.loads(response.read())
                http_client.close()

                assert response_body == [{"id": 1, "name": "Test_Squirrel_1", "size": '42'}, {"id": 2, "name": "Test_Squirrel_2", "size": '43'}, {"id": 3, "name": "Test_Squirrel_3", "size": '44'}]

            def descirbe_GET_squirrels_with_valid_resourceId():

                def it_returns_200_status_code(http_client):
                    # insert a new squirrel
                    db = SquirrelDB()
                    db.createSquirrel('Test_Squirrel', '42')
                    db.createSquirrel('Test_Squirrel_1', '42')
                    db.createSquirrel('Test_Squirrel_2', '42')
                    db.createSquirrel('Test_Squirrel_3', '42')

                    http_client.request('GET', '/squirrels/1')
                    response = http_client.getresponse()
                    http_client.close()

                    assert response.status == 200

                def it_returns_json_content_type_header(http_client):
                    # insert a new squirrel
                    db = SquirrelDB()
                    db.createSquirrel('Test_Squirrel', '42')
                    db.createSquirrel('Test_Squirrel_1', '42')
                    db.createSquirrel('Test_Squirrel_2', '42')
                    db.createSquirrel('Test_Squirrel_3', '42')

                    http_client.request('GET', '/squirrels/1')
                    response = http_client.getresponse()
                    http_client.close()

                    assert response.getheader('Content-Type') == 'application/json'

                def it_returns_json_array_with_one_squirrel(http_client):
                    # insert a new squirrel
                    db = SquirrelDB()
                    db.createSquirrel('Test_Squirrel', '42')
                    db.createSquirrel('Test_Squirrel_1', '42')
                    db.createSquirrel('Test_Squirrel_2', '42')
                    db.createSquirrel('Test_Squirrel_3', '42')

                    http_client.request('GET', '/squirrels/3')
                    response = http_client.getresponse()
                    response_body = json.loads(response.read())
                    http_client.close()

                    assert response_body == [{"id": 1, "name": "Test_Squirrel_2", "size": '42'}]

            def describe_GET_squirrels_with_invalid_resourceId():

                def it_returns_404_status_code(http_client):
                    http_client.request('GET', '/squirrels/999')
                    response = http_client.getresponse()
                    http_client.close()

                    assert response.status == 404

        def describe_GET_squirrels_with_invalid_resourceName():

            def it_returns_404_status_code(http_client):
                http_client.request('GET', '/invalid')
                response = http_client.getresponse()
                http_client.close()

                assert response.status == 404

    def describe_POST_squirrels():

        def describe_POST_squirrels_with_valid_resourceName():

            def describe_POST_squirrels_without_resourceId():

                def it_returns_201_status_code(http_client):
                    data = urllib.parse.urlencode({"name": "Test_Squirrel", "size": "42"})
                    headers = {"content-type": "application/x-www-form-urlencoded"}

                    http_client.request('POST', '/squirrels', data, headers)
                    response = http_client.getresponse()
                    http_client.close()

                    assert response.status == 201

                def it_inserts_data_into_database(http_client):
                    db = SquirrelDB()

                    data = urllib.parse.urlencode({"name": "Test_Squirrel", "size": "42"})
                    headers = {"content-type": "application/x-www-form-urlencoded"}

                    http_client.request('POST', '/squirrels', data, headers)
                    response = http_client.getresponse()
                    http_client.close()

                    assert db.getSquirrels() == [{'id': 1, 'name': 'Test_Squirrel', 'size': '42'}]

            def describe_POST_squirrels_with_resourceId():

                def it_returns_404_status_code(http_client):
                    data = urllib.parse.urlencode({"name": "Test_Squirrel", "size": '42'})
                    headers = {"content-type": "application/x-www-form-urlencoded"}

                    http_client.request('POST', '/squirrels/1', data, headers)
                    response = http_client.getresponse()
                    http_client.close()

                    assert response.status == 404

        def describe_POST_squirrels_with_invalid_resourceName():

            def it_returns_404_status_code(http_client):
                data = urllib.parse.urlencode({"name": "Test_Squirrel", "size": '42'})
                headers = {"content-type": "application/x-www-form-urlencoded"}

                http_client.request('POST', '/invalid', data, headers)
                response = http_client.getresponse()
                http_client.close()

                assert response.status == 404

    def describe_PUT_squirrels():

        def describe_PUT_squirrels_with_valid_resourceName():

            def describe_PUT_squirrels_with_valid_resourceId():

                def it_returns_204_status_code(http_client):
                    db = SquirrelDB()
                    db.createSquirrel('Test_Squirrel', '42')

                    data = urllib.parse.urlencode({"name": "Changed_Test_Squirrel", "size": '45'})
                    headers = {"content-type": "application/x-www-form-urlencoded"}

                    http_client.request('PUT', '/squirrels/1', data, headers)
                    response = http_client.getresponse()
                    http_client.close()

                    assert response.status == 204

                def it_updates_squirrel_data(http_client):
                    db = SquirrelDB()
                    db.createSquirrel('Test_Squirrel', '42')

                    assert db.getSquirrel(1) == {'id': 1, 'name': 'Test_Squirrel', 'size': '42'}


                    data = urllib.parse.urlencode(
                        {"name": "Changed_Test_Squirrel", "size": '45'})
                    headers = {
                        "content-type": "application/x-www-form-urlencoded"}

                    http_client.request('PUT', '/squirrels/1', data, headers)
                    response = http_client.getresponse()
                    http_client.close()

                    assert db.getSquirrel(1) == {'id': 1, 'name': 'Changed_Test_Squirrel', 'size': '45'}

            def describe_PUT_squirrels_with_invalid_resourceId():

                def it_returns_404_status_code(http_client):
                    data = urllib.parse.urlencode({"name": "Test_Squirrel", "size": '42'})
                    headers = {"content-type": "application/x-www-form-urlencoded"}

                    http_client.request('PUT', '/invalid/1', data, headers)
                    response = http_client.getresponse()
                    http_client.close()

                    assert response.status == 404

        def describe_PUT_squirrels_with_invalid_resourceName():

            def it_returns_404_status_code(http_client):
                data = urllib.parse.urlencode({"name": "Test_Squirrel", "size": '42'})
                headers = {"content-type": "application/x-www-form-urlencoded"}

                http_client.request('PUT', '/invalid/1', data, headers)
                response = http_client.getresponse()
                http_client.close()

                assert response.status == 404

    def describe_DELETE_squirrels():

        def describe_DELETE_squirrels_with_valid_resourceName():

            def describe_DELETE_squirrels_with_valid_resourceId():

                def it_returns_204_status_code(http_client):
                    db = SquirrelDB()
                    db.createSquirrel('Test_Squirrel', '42')

                    http_client.request('DELETE', '/squirrels/1')
                    response = http_client.getresponse()
                    http_client.close()

                    assert response.status == 204

                def it_deletes_squirrel_data(http_client):
                    db = SquirrelDB()
                    db.createSquirrel('Test_Squirrel', '42')
                    db.createSquirrel('Test_Squirrel_1', '42')
                    db.createSquirrel('Test_Squirrel_2', '42')

                    assert db.getSquirrels() == [
                        {
                            'id': 1,
                            'name': 'Test_Squirrel',
                            'size': '42'
                        }, {
                            'id': 2,
                            'name': 'Test_Squirrel_1',
                            'size': '42'
                        }, {
                            'id': 3,
                            'name': 'Test_Squirrel_2',
                            'size': '42'
                        }]

                    http_client.request('DELETE', '/squirrels/2')
                    response = http_client.getresponse()
                    http_client.close()

                    assert db.getSquirrels() == [{
                        'id': 1,
                        'name': 'Test_Squirrel',
                        'size': '42'
                    }, {
                        'id': 3,
                        'name': 'Test_Squirrel_2',
                       'size': '42'
                    }]

            def describe_DELETE_squirrels_with_invalid_resourceId():

                def it_returns_404_status_code(http_client):
                    http_client.request('DELETE', '/squirrels/999')
                    response = http_client.getresponse()
                    http_client.close()

                    assert response.status == 404

        def describe_DELETE_squirrels_with_invalid_resourceName():

            def it_returns_404_status_code(http_client):
                http_client.request('DELETE', '/invalid')
                response = http_client.getresponse()
                http_client.close()

                assert response.status == 404
