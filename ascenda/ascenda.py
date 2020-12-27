import requests
import os.path
import json
import numbers
import multiprocessing
import concurrent.futures

from flask import Flask
from flask import Blueprint

from . import hotel


num_cores = multiprocessing.cpu_count()
request_lock = multiprocessing.Lock()

bp = Blueprint('ascenda', __name__)


# Datasources
urls = [
    "https://5f2be0b4ffc88500167b85a0.mockapi.io/suppliers/acme",
    "https://5f2be0b4ffc88500167b85a0.mockapi.io/suppliers/patagonia",
    "https://5f2be0b4ffc88500167b85a0.mockapi.io/suppliers/paperflies"
    ]

def request_json_data(url, jsons):
    js = requests.get(url).json()

    request_lock.acquire()
    jsons.append(js)
    request_lock.release()


def build_hotel_list():
    jsons = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_cores) as executor:
        futures = []
        for url in urls:
            futures.append(executor.submit(request_json_data, url=url, jsons=jsons))
        concurrent.futures.wait(futures)

    hotels = []

    # Can be paralellized, but thread safety is not trivial
    for current_json in jsons:
        for current_hotel in current_json:

            # First parse the hotel id and the destination id, to determine how many
            # hotels do we have data about
            current_id = ""
            possible_hotel_id_strings = ["id", "Id", "hotel_id"]
            for s in possible_hotel_id_strings:
                if s in current_hotel:
                    current_id = current_hotel[s]
                    break
            if current_id == "":
                continue    # Invalid data

            current_destination_id = -1
            possible_destination_id_strings = ["destination", "destination_id", "DestinationId"]
            for s in possible_destination_id_strings:
                if s in current_hotel:
                    current_destination_id = current_hotel[s]
                    break
            if current_destination_id == -1:
                continue    # Invalid data

            # Check if we already created a hotel with this id
            found = False
            for hot in hotels:
                if hot.id == current_id:
                    found = True
                    hot.corresponding_jsons.append(current_hotel)
                    break
            
            # Create a new hotel if it doesnt already exists
            if not found:
                hotels.append(hotel.Hotel())
                hotels[-1].id = current_id
                hotels[-1].destination_id = current_destination_id
                hotels[-1].corresponding_jsons.append(current_hotel)
        

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_cores) as executor:
        futures = []
        for hot in hotels:
            futures.append(executor.submit(hot.read_json_data()))
        concurrent.futures.wait(futures)

    # Dump to json
    # js = []
    # for hot in hotels:
    #     js.append(hot.to_json())

    # with open(os.getcwd() + '/' + "out" + ".json", 'w') as outfile:
    #     json.dump(js, outfile)

    return hotels

@bp.route('/hotel_id=<list:ids>/', methods = ['GET'])
def query_hotel_id(ids):
    hotels = build_hotel_list()  # All hotel objects

    ids = list(dict.fromkeys(ids)) # Remove duplicates

    retval = ""
    for id in ids:
        for hot in hotels:
            if hot.id == id:
                if retval != "":   # If its not the first item, insert a ','
                    retval += ", "

                retval += json.dumps(hot.to_json()) # Convert to string and add to return value
                break


    # Add the braces
    if retval != "":
        retval = "[" + retval
        retval += "]"

    return retval

@bp.route('/destination_id=<int:id>/', methods = ['GET'])
def query_destination_id(id):
    hotels = build_hotel_list()  # All hotel objects

    retval = ""
    for hot in hotels:
        if hot.destination_id == id:
            if retval != "":     # If its not the first item, insert a ','
                retval += ", "

            retval += json.dumps(hot.to_json()) # Convert to string and add to return value

    # Add the braces
    if retval != "":
        retval = "[" + retval
        retval += "]"

    return retval

@bp.route('/', methods= ['GET'])
def default_route():
    return "Hello"