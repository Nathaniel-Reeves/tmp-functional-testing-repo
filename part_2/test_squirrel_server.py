import io
import json
import pytest
from squirrel_server import SquirrelServerHandler
from squirrel_db import SquirrelDB

todo = pytest.mark.skip(reason='TODO: pending spec')


class FakeRequest():
    def __init__(self, mock_wfile, method, path, body=None):
        self._mock_wfile = mock_wfile
        self._method = method
        self._path = path
        self._body = body

    def sendall(self, x):
        return

    def makefile(self, *args, **kwargs):
        if args[0] == 'rb':
            if self._body:
                headers = 'Content-Length: {}\r\n'.format(len(self._body))
                body = self._body
            else:
                headers = ''
                body = ''
            request = bytes(
                '{} {} HTTP/1.0\r\n{}\r\n{}'.format(self._method, self._path, headers, body), 'utf-8')
            return io.BytesIO(request)
        elif args[0] == 'wb':
            return self._mock_wfile

@pytest.fixture
def dummy_client():
    return ('127.0.0.1', 80)

@pytest.fixture
def dummy_server():
    return None

@pytest.fixture
def mock_db_init(mocker):
    return mocker.patch.object(SquirrelDB, '__init__', return_value=None)

@pytest.fixture
def mock_db_getSquirrels(mocker, mock_db_init):
    return mocker.patch.object(SquirrelDB, 'getSquirrels', return_value=['squirrel'])

@pytest.fixture
def mock_db_getSquirrel(mocker, mock_db_init):
    return mocker.patch.object(SquirrelDB, 'getSquirrel', return_value='squirrel')

@pytest.fixture
def mock_db_getSquirrel_invalid(mocker, mock_db_init):
    return mocker.patch.object(SquirrelDB, 'getSquirrel', return_value=None)

@pytest.fixture
def mock_db_createSquirrel(mocker, mock_db_init):
    return mocker.patch.object(SquirrelDB, 'createSquirrel', return_value=None)

@pytest.fixture
def mock_db_updateSquirrel(mocker, mock_db_init):
    return mocker.patch.object(SquirrelDB, 'updateSquirrel', return_value=None)

@pytest.fixture
def mock_db_deleteSquirrel(mocker, mock_db_init):
    return mocker.patch.object(SquirrelDB, 'deleteSquirrel', return_value=None)

@pytest.fixture(autouse=True)
def patch_wbufsize(mocker):
    # patch SquirrelServerHandler to make our FakeRequest work correctly
    mocker.patch.object(SquirrelServerHandler, 'wbufsize', 1)
    mocker.patch.object(SquirrelServerHandler, 'end_headers')

@pytest.fixture
def mock_response_methods(mocker):
    mock_send_response = mocker.patch.object(SquirrelServerHandler, 'send_response')
    mock_send_header = mocker.patch.object(SquirrelServerHandler, 'send_header')
    mock_end_headers = mocker.patch.object(SquirrelServerHandler, 'end_headers')
    return mock_send_response, mock_send_header, mock_end_headers

def describe_SquirrelServerHandler():

    def describe_do_GET():

        @pytest.fixture
        def fake_GET_squirrels_valid_resourceName(mocker):
            return FakeRequest(mocker.Mock(), 'GET', '/squirrels')

        @pytest.fixture
        def fake_GET_squirrel_invalid_resourceName(mocker):
            return FakeRequest(mocker.Mock(), 'GET', '/invalid')

        def describe_GET_squirrels_with_valid_resourceName():

            @pytest.fixture
            def fake_GET_squirrel_request_valid_resourceId(mocker):
                return FakeRequest(mocker.Mock(), 'GET', '/squirrels/1')

            @pytest.fixture
            def fake_GET_squirrel_request_invalid_resourceId(mocker):
                return FakeRequest(mocker.Mock(), 'GET', '/squirrels/invalid')

            def describe_GET_squirrels_collection_with_resourceId():

                def it_calls_getSquirrel(fake_GET_squirrel_request_valid_resourceId, dummy_client, dummy_server, mock_db_getSquirrel):
                    SquirrelServerHandler(
                        fake_GET_squirrel_request_valid_resourceId, dummy_client, dummy_server)
                    mock_db_getSquirrel.assert_called_once_with("1")

                def describe_GET_squirrels_collection_with_valid_resourceId():

                    def it_returns_200_status_code(
                            fake_GET_squirrel_request_valid_resourceId, dummy_client, dummy_server, mock_db_getSquirrel, mock_response_methods):
                        mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
                        SquirrelServerHandler(
                            fake_GET_squirrel_request_valid_resourceId, dummy_client, dummy_server)
                        mock_send_response.assert_called_once_with(200)

                    def it_returns_json_content_type_header(
                            fake_GET_squirrel_request_valid_resourceId, dummy_client, dummy_server, mock_db_getSquirrel, mock_response_methods):
                        mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
                        SquirrelServerHandler(
                            fake_GET_squirrel_request_valid_resourceId, dummy_client, dummy_server)
                        mock_send_header.assert_called_once_with("Content-Type", "application/json")

                    def it_calls_end_headers(
                            fake_GET_squirrel_request_valid_resourceId, dummy_client, dummy_server, mock_db_getSquirrel, mock_response_methods):
                        mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
                        SquirrelServerHandler(
                            fake_GET_squirrel_request_valid_resourceId, dummy_client, dummy_server)
                        mock_end_headers.assert_called_once()

                    def it_returns_response_body_with_squirrel_json_data(
                            fake_GET_squirrel_request_valid_resourceId, dummy_client, dummy_server, mock_db_getSquirrel, mock_response_methods):
                        mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
                        response = SquirrelServerHandler(
                            fake_GET_squirrel_request_valid_resourceId, dummy_client, dummy_server)
                        response.wfile.write.assert_called_with(
                            bytes(json.dumps('squirrel'), 'utf-8'))

                def describe_GET_squirrels_collection_without_valid_resourceId():

                    def it_returns_404_status_code(fake_GET_squirrel_request_invalid_resourceId, dummy_client, dummy_server, mock_db_getSquirrel_invalid, mock_response_methods):
                        mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
                        response = SquirrelServerHandler(fake_GET_squirrel_request_invalid_resourceId, dummy_client, dummy_server)
                        mock_send_response.assert_called_once_with(404)
                        mock_send_header.assert_called_once_with('Content-Type', 'text/plain')
                        mock_end_headers.assert_called_once()
                        response.wfile.write.assert_called_with(bytes('404 Not Found', 'utf-8'))

            def describe_GET_squirrels_collection_without_resourceId():

                def it_calls_getSquirrels(fake_GET_squirrels_valid_resourceName, dummy_client, dummy_server, mock_db_getSquirrels):
                    SquirrelServerHandler(
                        fake_GET_squirrels_valid_resourceName, dummy_client, dummy_server)
                    mock_db_getSquirrels.assert_called_once()

                def it_returns_200_status_code(fake_GET_squirrels_valid_resourceName, dummy_client, dummy_server, mock_db_getSquirrels, mock_response_methods):
                    mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
                    SquirrelServerHandler(
                        fake_GET_squirrels_valid_resourceName, dummy_client, dummy_server)
                    mock_send_response.assert_called_once_with(200)

                def it_returns_json_content_type_header(fake_GET_squirrels_valid_resourceName, dummy_client, dummy_server, mock_db_getSquirrels, mock_response_methods):
                    mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
                    SquirrelServerHandler(
                        fake_GET_squirrels_valid_resourceName, dummy_client, dummy_server)
                    mock_send_header.assert_called_once_with(
                        'Content-Type', 'application/json')

                def it_calls_end_headers(fake_GET_squirrels_valid_resourceName, dummy_client, dummy_server, mock_db_getSquirrels, mock_response_methods):
                    mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
                    SquirrelServerHandler(
                        fake_GET_squirrels_valid_resourceName, dummy_client, dummy_server)
                    mock_end_headers.assert_called_once_with()

                def it_returns_response_body_with_squirrels_json_data(fake_GET_squirrels_valid_resourceName, dummy_client, dummy_server, mock_db_getSquirrels):
                    response = SquirrelServerHandler(
                        fake_GET_squirrels_valid_resourceName, dummy_client, dummy_server)
                    # mock_db_getSquirrels returns a list of squirrels i.e. ['squirrel']
                    response.wfile.write.assert_called_with(
                        bytes(json.dumps(['squirrel']), 'utf-8'))

        def describe_GET_invalid_resourceName():

            def it_returns_404_status_code(fake_GET_squirrel_invalid_resourceName, dummy_client, dummy_server, mock_db_getSquirrel_invalid, mock_response_methods):
                mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
                response = SquirrelServerHandler(
                    fake_GET_squirrel_invalid_resourceName, dummy_client, dummy_server)
                mock_send_response.assert_called_once_with(404)
                mock_send_header.assert_called_once_with(
                    'Content-Type', 'text/plain')
                mock_end_headers.assert_called_once()
                response.wfile.write.assert_called_with(
                    bytes('404 Not Found', 'utf-8'))

    def describe_do_POST():

        @pytest.fixture
        def fake_POST_squirrels_valid_resourceName_valid_body(mocker):
            return FakeRequest(mocker.Mock(), 'POST', '/squirrels', body='name=Chippy&size=small')

        @pytest.fixture
        def fake_POST_squirrels_invalid_resourceName_valid_body(mocker):
            return FakeRequest(mocker.Mock(), 'POST', '/invalid', body='name=Chippy&size=small')

        def describe_POST_squirrels_collection_with_valid_resourceName():

            def describe_POST_squirrels_collection_with_valid_resourceId():

                def it_calls_getRequestData(mocker, fake_POST_squirrels_valid_resourceName_valid_body, dummy_client, dummy_server, mock_db_getSquirrel, mock_db_createSquirrel, mock_response_methods):
                    mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
                    mock_getRequestData = mocker.patch.object(
                        SquirrelServerHandler, "getRequestData", return_value={"name": "Chippy", "size": "small"})
                    response = SquirrelServerHandler(
                        fake_POST_squirrels_valid_resourceName_valid_body, dummy_client, dummy_server)
                    assert mock_getRequestData.call_count == 1

                def it_calls_createSquirrel(mocker, fake_POST_squirrels_valid_resourceName_valid_body, dummy_client, mock_db_getSquirrel, mock_db_createSquirrel, mock_response_methods):
                    mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
                    mock_getRequestData = mocker.patch.object(
                        SquirrelServerHandler, "getRequestData", return_value={"name": "Chippy", "size": "small"})
                    response = SquirrelServerHandler(
                        fake_POST_squirrels_valid_resourceName_valid_body, dummy_client, dummy_server)
                    mock_db_createSquirrel.assert_called_once_with('Chippy', 'small')

                def it_returns_201_status_code(mocker, fake_POST_squirrels_valid_resourceName_valid_body, dummy_client, mock_db_getSquirrel, mock_db_createSquirrel, mock_response_methods):
                    mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
                    mock_getRequestData = mocker.patch.object(
                        SquirrelServerHandler, "getRequestData", return_value={"name": "Chippy", "size": "small"})
                    response = SquirrelServerHandler(
                        fake_POST_squirrels_valid_resourceName_valid_body, dummy_client, dummy_server)
                    mock_send_response.assert_called_once_with(201)

                def it_calls_end_headers(mocker, fake_POST_squirrels_valid_resourceName_valid_body, dummy_client, mock_db_getSquirrel, mock_db_createSquirrel, mock_response_methods):
                    mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
                    mock_getRequestData = mocker.patch.object(
                        SquirrelServerHandler, "getRequestData", return_value={"name": "Chippy", "size": "small"})
                    response = SquirrelServerHandler(
                        fake_POST_squirrels_valid_resourceName_valid_body, dummy_client, dummy_server)
                    mock_end_headers.assert_called_once_with()

            def describe_POST_squirrels_collection_with_invalid_resourceId():

                def it_returns_404_status_code(fake_POST_squirrels_invalid_resourceName_valid_body, dummy_client, dummy_server, mock_db_getSquirrel_invalid, mock_response_methods):
                    mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
                    response = SquirrelServerHandler(
                        fake_POST_squirrels_invalid_resourceName_valid_body, dummy_client, dummy_server)
                    mock_send_response.assert_called_once_with(404)
                    mock_send_header.assert_called_once_with(
                        'Content-Type', 'text/plain')
                    mock_end_headers.assert_called_once()
                    response.wfile.write.assert_called_with(
                        bytes('404 Not Found', 'utf-8'))

        def describe_POST_squirrels_collection_with_invalid_resourceName():

            def it_returns_404_status_code(fake_POST_squirrels_invalid_resourceName_valid_body, dummy_client, dummy_server, mock_db_getSquirrel_invalid, mock_response_methods):
                mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
                response = SquirrelServerHandler(
                    fake_POST_squirrels_invalid_resourceName_valid_body, dummy_client, dummy_server)
                mock_send_response.assert_called_once_with(404)
                mock_send_header.assert_called_once_with(
                    'Content-Type', 'text/plain')
                mock_end_headers.assert_called_once()
                response.wfile.write.assert_called_with(
                    bytes('404 Not Found', 'utf-8'))

    def describe_do_PUT():

        @pytest.fixture
        def fake_PUT_squirrel_valid_resourceName_valid_resourceId_valid_body(mocker):
            return FakeRequest(mocker.Mock(), 'PUT', '/squirrels/1', body='name=Chippy&size=small')

        @pytest.fixture
        def fake_PUT_squirrel_invalid_resourceName_valid_body(mocker):
            return FakeRequest(mocker.Mock(), 'PUT', '/invalid', body='name=Chippy&size=small')

        def describe_PUT_squirrels_collection_with_valid_resourceName():

            @pytest.fixture
            def fake_PUT_squirrel_valid_resourceName_invalid_resourceId_valid_body(mocker):
                return FakeRequest(mocker.Mock(), 'PUT', '/squirrels/invalid', body='name=Chippy&size=small')

            @pytest.fixture
            def fake_PUT_squirrel_valid_resourceName_valid_resourceId_invalid_body1(mocker):
                return FakeRequest(mocker.Mock(), 'PUT', '/squirrels/1', body='name=Chippy')

            @pytest.fixture
            def fake_PUT_squirrel_valid_resourceName_valid_resourceId_invalid_body2(mocker):
                return FakeRequest(mocker.Mock(), 'PUT', '/squirrels/1', body='size=small')

            @pytest.fixture
            def fake_PUT_squirrel_valid_resourceName_valid_resourceId_invalid_body3(mocker):
                return FakeRequest(mocker.Mock(), 'PUT', '/squirrels/1', body='name_s=Chippy&size_s=small')

            def describe_PUT_squirrels_collection_with_resourceId():

                def it_calls_getSquirrel(fake_PUT_squirrel_valid_resourceName_valid_resourceId_valid_body, dummy_server, dummy_client, mock_db_getSquirrel, mock_db_updateSquirrel):
                    SquirrelServerHandler(fake_PUT_squirrel_valid_resourceName_valid_resourceId_valid_body, dummy_client, dummy_server)
                    mock_db_getSquirrel.assert_called_once_with("1")

                def describe_PUT_squirrels_collection_with_valid_resourceId():

                    def it_calls_getRequestData(mocker, fake_PUT_squirrel_valid_resourceName_valid_resourceId_valid_body, dummy_client, dummy_server, mock_db_getSquirrel, mock_db_updateSquirrel, mock_response_methods):
                        mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
                        mock_getRequestData = mocker.patch.object(
                            SquirrelServerHandler, "getRequestData", return_value={"name": "Chippy", "size": "small"})
                        response = SquirrelServerHandler(
                            fake_PUT_squirrel_valid_resourceName_valid_resourceId_valid_body, dummy_client, dummy_server)
                        assert mock_getRequestData.call_count == 1

                    def it_calls_updateSquirrel(mocker, fake_PUT_squirrel_valid_resourceName_valid_resourceId_valid_body, dummy_client, dummy_server, mock_db_getSquirrel, mock_db_updateSquirrel, mock_response_methods):
                        mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
                        mock_getRequestData = mocker.patch.object(
                            SquirrelServerHandler, "getRequestData", return_value={"name": "Chippy", "size": "small"})
                        response = SquirrelServerHandler(
                            fake_PUT_squirrel_valid_resourceName_valid_resourceId_valid_body, dummy_client, dummy_server)
                        mock_db_updateSquirrel.assert_called_once_with("1", "Chippy", "small")

                    def it_returns_204_status_code(mocker, fake_PUT_squirrel_valid_resourceName_valid_resourceId_valid_body, dummy_client, dummy_server, mock_db_getSquirrel, mock_db_updateSquirrel, mock_response_methods):
                        mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
                        mock_getRequestData = mocker.patch.object(
                            SquirrelServerHandler, "getRequestData", return_value={"name": "Chippy", "size": "small"})
                        response = SquirrelServerHandler(
                            fake_PUT_squirrel_valid_resourceName_valid_resourceId_valid_body, dummy_client, dummy_server)
                        mock_send_response.assert_called_once_with(204)

                    def it_calls_end_headers(mocker, fake_PUT_squirrel_valid_resourceName_valid_resourceId_valid_body, dummy_client, dummy_server, mock_db_getSquirrel, mock_db_updateSquirrel, mock_response_methods):
                        mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
                        mock_getRequestData = mocker.patch.object(
                            SquirrelServerHandler, "getRequestData", return_value={"name": "Chippy", "size": "small"})
                        response = SquirrelServerHandler(
                            fake_PUT_squirrel_valid_resourceName_valid_resourceId_valid_body, dummy_client, dummy_server)
                        mock_end_headers.assert_called_once()

                def describe_PUT_squirrels_collection_with_invalid_resourceName():

                    def it_returns_404_status_code(fake_PUT_squirrel_valid_resourceName_invalid_resourceId_valid_body, dummy_client, dummy_server, mock_db_getSquirrel_invalid, mock_response_methods):
                        mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
                        response = SquirrelServerHandler(
                            fake_PUT_squirrel_valid_resourceName_invalid_resourceId_valid_body, dummy_client, dummy_server)
                        mock_send_response.assert_called_once_with(404)
                        mock_send_header.assert_called_once_with(
                            'Content-Type', 'text/plain')
                        mock_end_headers.assert_called_once()
                        response.wfile.write.assert_called_with(
                            bytes('404 Not Found', 'utf-8'))

            def describe_PUT_squirrels_collection_with_invalid_resourceId():

                def it_returns_404_status_code(fake_PUT_squirrel_invalid_resourceName_valid_body, dummy_client, dummy_server, mock_db_getSquirrel_invalid, mock_response_methods):
                    mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
                    response = SquirrelServerHandler(
                        fake_PUT_squirrel_invalid_resourceName_valid_body, dummy_client, dummy_server)
                    mock_send_response.assert_called_once_with(404)
                    mock_send_header.assert_called_once_with(
                        'Content-Type', 'text/plain')
                    mock_end_headers.assert_called_once()
                    response.wfile.write.assert_called_with(
                        bytes('404 Not Found', 'utf-8'))

        def describe_PUT_squirrels_collection_with_invalid_resourceName():

            def it_returns_404_status_code(fake_PUT_squirrel_invalid_resourceName_valid_body, dummy_client, dummy_server, mock_db_getSquirrel_invalid, mock_response_methods):
                mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
                response = SquirrelServerHandler(
                    fake_PUT_squirrel_invalid_resourceName_valid_body, dummy_client, dummy_server)
                mock_send_response.assert_called_once_with(404)
                mock_send_header.assert_called_once_with(
                    'Content-Type', 'text/plain')
                mock_end_headers.assert_called_once()
                response.wfile.write.assert_called_with(
                    bytes('404 Not Found', 'utf-8'))

    def describe_do_DELETE():

        @pytest.fixture
        def fake_DELETE_squirrels_valid_resourceName_valid_resourceId(mocker):
            return FakeRequest(mocker.Mock(), 'DELETE', '/squirrels/1')

        @pytest.fixture
        def fake_DELETE_squirrels_valid_resourceName_invalid_resourceId(mocker):
            return FakeRequest(mocker.Mock(), 'DELETE', '/squirrels')

        @pytest.fixture
        def fake_DELETE_squirrels_invalid_resourceName_valid_resourceId(mocker):
            return FakeRequest(mocker.Mock(), 'DELETE', '/invalid/1')

        def describe_DELETE_squirrels_collection_with_valid_resourceName():

            def describe_DELETE_squirrels_collection_with_resourceId():

                def describe_DELETE_squirrels_collection_with_valid_resourceId():

                    def it_calls_deleteSquirrel(fake_DELETE_squirrels_valid_resourceName_valid_resourceId, dummy_client, dummy_server, mock_db_getSquirrel, mock_db_deleteSquirrel, mock_response_methods):
                        mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
                        response = SquirrelServerHandler(
                            fake_DELETE_squirrels_valid_resourceName_valid_resourceId, dummy_client, dummy_server)
                        mock_db_deleteSquirrel.assert_called_once_with("1")

                    def it_returns_204_status_code(fake_DELETE_squirrels_valid_resourceName_valid_resourceId, dummy_client, dummy_server, mock_db_getSquirrel, mock_db_deleteSquirrel, mock_response_methods):
                        mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
                        response = SquirrelServerHandler(
                            fake_DELETE_squirrels_valid_resourceName_valid_resourceId, dummy_client, dummy_server)
                        mock_send_response.assert_called_once_with(204)

                    def it_calls_end_headers(fake_DELETE_squirrels_valid_resourceName_valid_resourceId, dummy_client, dummy_server, mock_db_getSquirrel, mock_db_deleteSquirrel, mock_response_methods):
                        mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
                        response = SquirrelServerHandler(
                            fake_DELETE_squirrels_valid_resourceName_valid_resourceId, dummy_client, dummy_server)
                        mock_end_headers.assert_called_once()

                def describe_DELETE_squirrels_collection_with_invalid_resourceId():

                    def it_returns_404_status_code(fake_DELETE_squirrels_valid_resourceName_invalid_resourceId, dummy_client, dummy_server, mock_db_getSquirrel, mock_response_methods):
                        mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
                        response = SquirrelServerHandler(
                            fake_DELETE_squirrels_valid_resourceName_invalid_resourceId, dummy_client, dummy_server)
                        mock_send_response.assert_called_once_with(404)
                        mock_send_header.assert_called_once_with(
                            'Content-Type', 'text/plain')
                        mock_end_headers.assert_called_once()
                        response.wfile.write.assert_called_with(
                            bytes('404 Not Found', 'utf-8'))

        def describe_DELETE_squirrels_collection_with_invalid_resourceName():

            def it_returns_404_status_code(fake_DELETE_squirrels_invalid_resourceName_valid_resourceId, dummy_client, dummy_server, mock_db_getSquirrel, mock_response_methods):
                mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
                response = SquirrelServerHandler(
                    fake_DELETE_squirrels_invalid_resourceName_valid_resourceId, dummy_client, dummy_server)
                mock_send_response.assert_called_once_with(404)
                mock_send_header.assert_called_once_with(
                    'Content-Type', 'text/plain')
                mock_end_headers.assert_called_once()
                response.wfile.write.assert_called_with(
                    bytes('404 Not Found', 'utf-8'))
