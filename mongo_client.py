import datetime
import pymongo
from pymongo import MongoClient
from mongo_server import start_server, close_server
from getmac import get_mac_address as gma

EVENT_DATABASE_NAME = 'events'
WINDOWS_DATABASE_NAME = 'windows'

cloud_client = None
cloud_db_name = 'group5db'
cloud_collection = str(gma())

def open_client(timeout=30000):
    """
    Creates a MongoDB client connected to a MongoDB server.

    :param port: The port number of the intended MongoDB server. Defaults to 27017.
    :param timeout: The maximum amount of time before terminating connection attempts. Default to 30,000ms.
    :return: The MongoDB client object instance.
    :raise: An Exception if the client cannot connect.
    """

    global cloud_client

    # If client was not already made
    if not cloud_client:
        # Attempt a client connection
        cloud_client = client = MongoClient("mongodb+srv://admin:mongodb9143@cluster0.femb8.mongodb.net/group5db?retryWrites=true&w=majority")

        try:
            # Causes this thread to block until client has connected or not
            client.server_info()
            # Return client instance
            return client
        except Exception as e:
            # Raise exception if client cannot connect
            raise e

    # Client instance already created
    else:
        return cloud_client


def close_client():
    """
    Closes the MongoDB client.

    Formally disconnected the client. The client instance can be retrieved
    via open_client(). Issuing commands through it will automatically reopen it.
    :return: None
    :raise: An Exception if the client was never created or opened.
    """
    if cloud_client:
        cloud_client.close()
    else:
        raise Exception('no existing or open client to close')


def log_event(event: dict):
    """
    Writes the given event to the MongoDB server.

    Saves the provided event as a document under a collection named with
    the event's date in ISO-8601 format. This collection is stored under a
    database within MongoDB with the name of _DATABASE_NAME.

    :param event: The dictionary containing data to write.
    :return: a MongoDB document object ID for the inserted event record
    :raise: An Exception if the client fails to log the event
    """

    # Assume timestamp is right now if unspecified
    if 'timestamp' not in event:
        event['timestamp'] = datetime.datetime.utcnow()
    if isinstance(event['timestamp'], str):
        event['timestamp'] = datetime.datetime.fromisoformat(
            event['timestamp'])

    # Get handle on collection for the day
    date = str(event['timestamp'].date())
    cloud_collection_handle = get_collection(cloud_db_name, cloud_collection)

    try:
        # Insert the event as a document in the collection; return its ID
        # print("Successfully inserted to both local and cloud DB")
        return cloud_collection_handle.insert_one(event).inserted_id
    except Exception as e:
        print(e)
        print("Failed to upload to cloud DB")
        return cloud_collection_handle.insert_one(event).inserted_id


def log_processes(processes: dict):
    """
    Writes the given event to the MongoDB server.

    Saves the provided event as a document under a collection named with
    the log's date in ISO-8601 format. This collection is stored under a
    database within MongoDB with the name of _DATABASE_NAME.

    :param processes: The dictionary containing data to write.
    :return: a MongoDB document object ID for the inserted event record
    :raise: An Exception if the client fails to log the event
    """

    # Stringify all PIDs
    for key in list(processes.keys()):
        if isinstance(key, int):
            processes[str(key)] = processes[key]
            del processes[key]

    # Assume timestamp is right now if unspecified
    if 'timestamp' not in processes:
        processes['timestamp'] = datetime.datetime.utcnow()
    if isinstance(processes['timestamp'], str):
        processes['timestamp'] = datetime.datetime.fromisoformat(
            processes['timestamp'])

    # Get handle on collection for the day
    date = str(processes['timestamp'].date())
    cloud_collection_handle = get_database(cloud_db_name)[cloud_collection]

    # Insert the event as a document in the collection; return its ID
    return cloud_collection_handle.insert_one(processes).inserted_id


def get_database(database: str):
    return open_client()[database]


def get_collection(database: str, collection: str):
    return open_client()[database][collection]


if __name__ == '__main__':
    import random

    start_server()
    open_client(timeout=3000)
    pid = random.randint(10000, 65000)
    hwnd = random.randint(100000000, 199999999)
    # print('Inserted new mouse event: {}'.format(
    #     log_event({
    #         'process_obj': {'pid': pid, 'name': 'UnnamedProcess64.exe',
    #                         'exe': '/path/to/exe/UnnamedProcess64.exe', 'username': 'Current User'},
    #         'window': {'hwnd': hwnd, 'title': 'Process Window Title'},
    #         'event': 'mouse'
    #     })
    # ))
    # print('Inserted window event: {}'.format(
    #     log_processes({
    #         str(pid): {
    #             'process_obj': {'pid': pid, 'name': 'UnnamedProcess64.exe',
    #                             'exe': '/path/to/exe/UnnamedProcess64.exe', 'username': 'Current User'},
    #             'windows': [{'hwnd': hwnd, 'title': 'Process Window Title'}]
    #         }
    #     })
    # ))
    close_client()
    input('Waiting for signal to close db server...')
    close_server()
else:
    print('Starting MongoDB server...')
    start_server()
    t = 90000
    print('Opening MongoDB client (Timeout = {} seconds)...'.format(t / 1000))
    open_client(timeout=t)
    print('Client connected: ', cloud_client)
