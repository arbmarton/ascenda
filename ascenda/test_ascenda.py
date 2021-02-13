import os
import tempfile
import json

#import pytest


import ascenda
#import hotel



# @pytest.fixture
# def client():
#     app_context().config['TESTING'] = True

def test_destination_id():
    js = ascenda.ascenda.query_destination_id(5432)

    loadedjson = json.loads(js)

    for val in loadedjson:
        print(val["destination_id"])

        if val["destination_id"] != 5432:
            assert False

def test_hotel_id():
    ls = list()
    ls.append("iJhz")
    js = ascenda.ascenda.query_hotel_id(ls)

    loadedjson = json.loads(js)

    for val in loadedjson:
        print(val["id"])

        if val["id"] != "iJhz":
            assert False