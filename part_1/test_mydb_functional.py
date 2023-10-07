import os.path
import pickle
import pytest

from mydb import MyDB

todo = pytest.mark.skip(reason="todo: pending spec")

@pytest.fixture()
def db_filename():
    return "mydatabase.db"

@pytest.fixture(autouse=True)
def cleanup(db_filename):
    # before each test case
    yield
    # after each test case
    if os.path.isfile(db_filename):
        os.remove(db_filename)

def describe_MyDB():

    def describe_init():

        def it_assigns_fname_attribute(db_filename):
            db = MyDB(db_filename)
            assert db.fname == db_filename

        def it_creates_empty_database_if_it_does_not_exist(db_filename):
            assert not os.path.isfile(db_filename)
            db = MyDB(db_filename)
            assert os.path.isfile(db_filename)

        def it_does_not_create_database_if_it_already_exists(db_filename):
            with open(db_filename, "wb") as f:
                pickle.dump(["Stuff", "More Stuff"], f)
            assert os.path.isfile(db_filename)
            db = MyDB(db_filename)
            with open(db_filename, "rb") as f:
                assert pickle.load(f) == ["Stuff", "More Stuff"]

    def describe_loadStrings():

        def it_loads_strings_from_database(db_filename):
            with open(db_filename, "wb") as f:
                pickle.dump(["a", "b", "c"], f)
            db = MyDB(db_filename)
            assert db.loadStrings() == ["a", "b", "c"]

        def it_returns_empty_list_if_database_is_empty(db_filename):
            db = MyDB(db_filename)
            assert db.loadStrings() == []

    def describe_saveStrings():

        def it_saves_strings_to_database(db_filename):
            db = MyDB(db_filename)
            db.saveStrings(["a", "b", "c"])
            with open(db_filename, "rb") as f:
                assert pickle.load(f) == ["a", "b", "c"]

    def describe_saveString():

        def it_saves_the_given_string_to_the_database(db_filename):
            db = MyDB(db_filename)
            with open(db_filename, "rb") as f:
                assert pickle.load(f) == []
            db.saveString("hello")
            with open(db_filename, "rb") as f:
                assert pickle.load(f) == ["hello"]
            db.saveString("goodbye")
            with open(db_filename, "rb") as f:
                assert pickle.load(f) == ["hello", "goodbye"]