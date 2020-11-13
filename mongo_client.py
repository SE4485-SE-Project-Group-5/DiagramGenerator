import datetime
import pymongo
from mongo_server import start_server, close_server

_client_connection = None


def open_client(timeout=30000):
    """
    Creates a MongoDB client connected to a MongoDB server.

    :param port: The port number of the intended MongoDB server. Defaults to 27017.
    :param timeout: The maximum amount of time before terminating connection attempts. Default to 30,000ms.
    :return: The MongoDB client object instance.
    :raise: An Exception if the client cannot connect.
    """

    global _client_connection

    # If client was not already made
    if not _client_connection:
        # Attempt a client connection
        _client_connection = client = pymongo.MongoClient(
            "mongodb+srv://admin:mongodb9143@cluster0.femb8.mongodb.net/group5db?retryWrites=true&w=majority")

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
        return _client_connection


def close_client():
    """
    Closes the MongoDB client.

    Formally disconnected the client. The client instance can be retrieved
    via open_client(). Issuing commands through it will automatically reopen it.
    :return: None
    :raise: An Exception if the client was never created or opened.
    """
    if _client_connection:
        _client_connection.close()
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
    collection_handle = get_collection("group5db", date)

    # Insert the event as a document in the collection; return its ID
    return collection_handle.insert_one(event).inserted_id


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
    collection_handle = get_database("group5db")[date]

    # Insert the event as a document in the collection; return its ID
    return collection_handle.insert_one(processes).inserted_id


def get_database(database: str):
    return open_client()["group5db"]


def get_collection(database: str, collection: str):
    return open_client()["group5db"]["00:0c:29:de:a0:0d"]


if __name__ == '__main__':
    import random

    start_server()
    open_client(timeout=3000)
    pid = random.randint(10000, 65000)
    hwnd = random.randint(100000000, 199999999)
    print('Inserted new mouse event: {}'.format(
        log_event({
            'process_obj': {'pid': pid, 'name': 'UnnamedProcess64.exe',
                            'exe': '/path/to/exe/UnnamedProcess64.exe', 'username': 'Current User'},
            'window': {'hwnd': hwnd, 'title': 'Process Window Title'},
            'event': 'mouse'
        })
    ))
    print('Inserted window event: {}'.format(
        log_processes({
            str(pid): {
                'process_obj': {'pid': pid, 'name': 'UnnamedProcess64.exe',
                                'exe': '/path/to/exe/UnnamedProcess64.exe', 'username': 'Current User'},
                'windows': [{'hwnd': hwnd, 'title': 'Process Window Title'}]
            }
        })
    ))
    close_client()
    input('Waiting for signal to close db server...')
    close_server()
else:
    print('Starting MongoDB server...')
    start_server()
    t = 90000
    print('Opening MongoDB client (Timeout = {} seconds)...'.format(t / 1000))
    open_client(timeout=t)
    print('Client connected.')
