import os
import pytest
from mydb import MyDB
from unittest.mock import call


todo = pytest.mark.skip(reason="todo: pending spec")

def describe_MyDB():

    @pytest.fixture(autouse=True)
    def verify_filesystem_is_not_touched():
        yield
        assert not os.path.isfile("mydatabase.db")

    def describe_init():
        def it_assigns_fname_attribute(mocker):
            mocker.patch("os.path.isfile", return_value=True)
            db = MyDB("mydatabase.db")
            assert db.fname == "mydatabase.db"

        def it_creates_empty_database_if_it_does_not_exist(mocker):
            # set up stubs & mocks first
            mock_isfile = mocker.patch("os.path.isfile", return_value=False)
            mock_open = mocker.patch("builtins.open", mocker.mock_open())
            mock_dump = mocker.patch("pickle.dump")

            # execute on the test subject
            db = MyDB("mydatabase.db")

            # assert what happened
            mock_isfile.assert_called_once_with("mydatabase.db")
            mock_open.assert_called_once_with("mydatabase.db", "wb")
            mock_dump.assert_called_once_with([], mock_open.return_value)

        def it_does_not_create_databse_if_it_already_exists(mocker):
            # set up stubs & mocks first
            mock_isfile = mocker.patch("os.path.isfile", return_value=True)
            mock_open = mocker.patch("builtins.open", mocker.mock_open())
            mock_dump = mocker.patch("pickle.dump")

            # execute on the test subject
            db = MyDB("mydatabase.db")

            # assert what happened
            mock_isfile.assert_called_once_with("mydatabase.db")
            mock_open.assert_not_called()
            mock_dump.assert_not_called()

    def describe_loadStrings():

        def it_loads_strings_from_database(mocker):
            # set up stubs & mocks first
            mock_isfile = mocker.patch("os.path.isfile", return_value=True)
            mock_open = mocker.patch("builtins.open", mocker.mock_open())
            mock_load = mocker.patch("pickle.load", return_value=["a", "b", "c"])

            # execute on the test subject
            db = MyDB("mydatabase.db")
            arr = db.loadStrings()

            # assert what happened
            mock_isfile.assert_called_with("mydatabase.db")
            mock_open.assert_called_with("mydatabase.db", "rb")
            mock_load.assert_called_with(mock_open.return_value)
            assert arr == ["a", "b", "c"]

        def it_returns_empty_list_if_database_is_empty(mocker):
            # set up stubs & mocks first
            mock_isfile = mocker.patch("os.path.isfile", return_value=True)
            mock_open = mocker.patch("builtins.open", mocker.mock_open())
            mock_load = mocker.patch("pickle.load", return_value=[])

            # execute on the test subject
            db = MyDB("mydatabase.db")
            arr = db.loadStrings()

            # assert what happened
            mock_isfile.assert_called_with("mydatabase.db")
            mock_open.assert_called_with("mydatabase.db", "rb")
            mock_load.assert_called_with(mock_open.return_value)
            assert arr == []

        # def it_returns_an_error_if_database_does_not_exist(mocker):
        #     # set up stubs & mocks first
        #     mock_isfile = mocker.patch("os.path.isfile", return_value=False)
        #     mock_open = mocker.patch("builtins.open", mocker.mock_open())
        #     mock_load = mocker.patch("pickle.load", return_value=[])

        #     # execute on the test subject
        #     db = MyDB("mydatabase.db")
        #     with pytest.raises(FileNotFoundError):
        #         arr = db.loadStrings()

        #     # assert what happened
        #     mock_isfile.assert_called_with("mydatabase.db")
        #     mock_open.assert_not_called()
        #     mock_load.assert_not_called()


    def describe_saveStrings():

        def it_saves_strings_to_database(mocker):
            # set up stubs & mocks first
            mock_isfile = mocker.patch("os.path.isfile", return_value=True)
            mock_open = mocker.patch("builtins.open", mocker.mock_open())
            mock_dump = mocker.patch("pickle.dump", return_value=["a", "b", "c"])

            # execute on the test subject
            db = MyDB("mydatabase.db")
            db.saveStrings(["a", "b", "c"])

            # assert what happened
            mock_isfile.assert_called_with("mydatabase.db")
            mock_open.assert_called_with("mydatabase.db", "wb")
            mock_dump.assert_called_with(["a", "b", "c"], mock_open.return_value)

    def describe_saveString():

        # def it_saves_single_string_to_database(mocker):
        #     # set up stubs & mocks first
        #     mock_isfile = mocker.patch("os.path.isfile", return_value=True)
        #     mock_open = mocker.patch("builtins.open", mocker.mock_open())
        #     mock_load = mocker.patch(
        #         "pickle.load", return_value=["a", "b", "c"])
        #     mock_dump = mocker.patch("pickle.dump")


        #     # execute on the test subject
        #     db = MyDB("mydatabase.db")
        #     db.saveString("d")

        #     # assert what happened
        #     mock_isfile.assert_called_with("mydatabase.db")
        #     mock_open.assert_called_with("mydatabase.db", "wb")
        #     mock_dump.assert_called_with(["a", "b", "c", "d"], mock_open.return_value)
        #     mock_load.assert_called_with(mock_open.return_value)

        def it_saves_the_given_string_to_the_database(mocker):
            # set up stubs & mocks first
            mock_isfile = mocker.patch("os.path.isfile", return_value=True)
            mock_open = mocker.patch("builtins.open", mocker.mock_open())
            mock_dump = mocker.patch("pickle.dump")
            mock_load = mocker.patch(
                "pickle.load", return_value=["a", "b", "c"])

            # execute on the test subject
            db = MyDB("mydatabase.db")
            db.saveString("hello")

            # assert what happened
            assert mock_open.call_count == 2
            assert mock_open.call_args_list == [call("mydatabase.db", "rb"), call("mydatabase.db", "wb")]
            mock_load.assert_called_once_with(mock_open.return_value)
            mock_dump.assert_called_once_with(
                ["a", "b", "c", "hello"], mock_open.return_value)
