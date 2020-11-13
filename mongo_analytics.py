import heapq
from datetime import datetime, timedelta
from pprint import pprint

from icons_helper import find_icon_from_path
from ApplicationTimeLog import ApplicationTimeLog
from DefaultDict import DefaultDict
from mongo_client import get_collection
from mongo_server import close_server


def read_events(start: datetime, end: datetime):
    """
    Obtains all events logged in MongoDB between the start and end time given, inclusive.
    :param start: a datetime instance in UTC time
    :param end: a datetime instance in UTC time
    :return: a List of MongoDB event documents
    """

    # Base case: no valid range given
    if end <= start:
        return []

    # Base case: start date is after current time
    if start >= datetime.utcnow():
        return []

    events = []
    # Get events for start date, where time needs to be considered
    events += get_collection("group5db", str(start.date())
                             ).find({'timestamp': {'$gte': start}})
    # Get events for all intermediate dates
    start += timedelta(days=1)
    while start.date() < end.date():
        # print(start.date())
        events += get_collection("group5db",
                                 str(start.date())).find({})
        start += timedelta(days=1)
    # Get events for end date, where time needs to be considered
    events += get_collection("group5db",
                             str(start.date())).find({'timestamp': {'$lte': end}})

    return events


def read_processes(start: datetime, end: datetime):
    """
    Obtains all process snapshots logged in MongoDB between the start and end time given, inclusive.
    :param start: a datetime instance in UTC time
    :param end: a datetime instance in UTC time
    :return: a List of MongoDB process logs
    """

    # Base case: no valid range given
    if end <= start:
        return []

    # Base case: start date is after current time
    if start >= datetime.utcnow():
        return []

    processes = []
    # Get processes for start date, where time needs to be considered
    processes += get_collection("group5db",
                                str(start.date())).find({'timestamp': {'$gte': start}})
    # Get processes for all intermediate dates
    start += timedelta(days=1)
    while start.date() < end.date():
        # print(start.date())
        processes += get_collection("group5db",
                                    str(start.date())).find({})
        start += timedelta(days=1)
    # Get processes for end date, where time needs to be considered
    processes += get_collection("group5db",
                                str(start.date())).find({'timestamp': {'$lte': end}})

    return processes


def bpt_diagram_info(start: datetime, end: datetime, active_buf: int, idle_buf: int, think_buf: int):
    """
    Post-processes the information from business_process_info to provide the information that
    will appear in generated graphviz swim lane diagrams.
    :param start: timestamp indicating the earliest event to include from MongoDB
    :param end: timestamp indicating the latest event to include from MongoDB
    :param active_buf: grace time (seconds) given between events for a process to be considered active time
    :param idle_buf: grace time (seconds) given between events for a process to be considered idle time
    :param think_buf: grace time (seconds) given between events for a process to be considered thinking time
    :return: a dict of the processes in a schedule with their corresponding information
    """

    intervals = business_process_info(
        start, end, active_buf, idle_buf, think_buf)
    # generate "activities" list
    activities = []
    for process in intervals.as_dict().keys():
        activities += [(time, process)
                       for time in intervals[process].open_times]

    # create schedule
    schedule = schedule_activities(activities)
    # convert each list to an equivalent dict
    schedule_dict = {}
    for row_num in range(len(schedule)):
        row = schedule_dict[f'list{row_num + 1}'] = []
        # information to provide for each scheduled process
        for activity in schedule[row_num]:
            row.append({
                'name': activity[1],
                'start': activity[0][0],
                'finish': activity[0][1],
                'idle_time': intervals[activity[1]].total_idle_time(start, end),
                'mouse_time': intervals[activity[1]].total_mouse_time(start, end),
                'kb_time': intervals[activity[1]].total_kb_time(start, end),
                'duration': activity[0][1] - activity[0][0],
                "icon": intervals[activity[1]].icon
            })

    return schedule_dict


def react_ui_info(start: datetime, end: datetime, active_buf: int, idle_buf: int, think_buf: int):
    """
    Post-processes the information from business_process_info to provide the information that
    will appear in the ReactJS UI.
    :param start: timestamp indicating the earliest event to include from MongoDB
    :param end: timestamp indicating the latest event to include from MongoDB
    :param active_buf: grace time (seconds) given between events for a process to be considered active time
    :param idle_buf: grace time (seconds) given between events for a process to be considered idle time
    :param think_buf: grace time (seconds) given between events for a process to be considered thinking time
    :return: a dict with each process name and its associated information to display
    """

    intervals = business_process_info(
        start, end, active_buf, idle_buf, think_buf)
    # compile results of analysis into simple time totals and percentages
    totals = {
        process: {
            "mouse_usage": round(intervals[process].total_mouse_time(start, end).total_seconds() / 60),
            "keyboard_usage": round(intervals[process].total_kb_time(start, end).total_seconds() / 60),
            "idle": round(intervals[process].total_idle_time(start, end).total_seconds() / 60),
            "thinking": round(intervals[process].total_thinking_time(start, end).total_seconds() / 60),
            "open": round(intervals[process].total_open_time(start, end).total_seconds() / 60),
            "icon": intervals[process].icon
        }
        for process in intervals.as_dict().keys()
    }
    return totals


def business_process_info(start: datetime, end: datetime, active_buf: int, idle_buf: int, think_buf: int):
    """
    Performs a query for all events collected in MongoDB between the indicated start and end
    times. Performs analysis and compiles events into a series of time intervals based on process name.
    :param start: timestamp indicating the earliest event to include from MongoDB
    :param end: timestamp indicating the latest event to include from MongoDB
    :param active_buf: grace time (seconds) given between events for a process to be considered active time
    :param idle_buf: grace time (seconds) given between events for a process to be considered idle time
    :param think_buf: grace time (seconds) given between events for a process to be considered thinking time
    :return: a DefaultDict pairing each process name to a ApplicationTimeLog tracking the process' time intervals
    """

    # Tells us what the active process/window is, sorted by timestamp
    user_events = sorted(read_events(start, end), key=lambda e: e['timestamp'])
    # Tells us what all processes/windows are, sorted by timestamp
    window_log = sorted(read_processes(start, end),
                        key=lambda e: e['timestamp'])
    # dict to keep track of information associated with each process
    intervals = DefaultDict(lambda: ApplicationTimeLog(
        active_buf, idle_buf, think_buf))

    # Iterate through events in order of timestamps
    user_event_index, window_log_index = 0, 0
    while user_event_index < len(user_events) and window_log_index < len(window_log):
        if user_events[user_event_index]['timestamp'] < window_log[window_log_index]['timestamp']:
            intervals[user_events[user_event_index]['process_obj']['name']].update_active(
                user_events[user_event_index]['timestamp'])
            intervals[user_events[user_event_index]['process_obj']['name']].update_event(
                user_events[user_event_index]['event_type'], user_events[user_event_index]['timestamp'])
            intervals[user_events[user_event_index]['process_obj']['name']].icon = find_icon_from_path(
                user_events[user_event_index]['process_obj']['exe'])
            user_event_index += 1
        else:
            # Convenience variables
            curr_log = window_log[window_log_index]
            pids = [key for key in curr_log.keys() if key not in [
                '_id', 'timestamp']]
            open_apps = [curr_log[pid]['process_obj']['name'] for pid in pids]

            # App is open. track it as such
            for app in open_apps:
                intervals[app].update_is_open(curr_log['timestamp'])

            # Update icons
            for pid in pids:
                app_name = curr_log[pid]['process_obj']['name']
                intervals[app_name].icon = find_icon_from_path(
                    curr_log[pid]['process_obj']['exe'])

            # Among all tracked apps, update closed apps
            for app in intervals.as_dict():
                if app not in open_apps:
                    intervals[app].update_is_closed(curr_log['timestamp'])

            window_log_index += 1

    # Iterate through remaining of user events
    while user_event_index < len(user_events):
        intervals[user_events[user_event_index]['process_obj']['name']].update_active(
            user_events[user_event_index]['timestamp'])
        intervals[user_events[user_event_index]['process_obj']['name']].update_event(
            user_events[user_event_index]['event_type'], user_events[user_event_index]['timestamp'])
        intervals[user_events[user_event_index]['process_obj']['name']].icon = find_icon_from_path(
            user_events[user_event_index]['process_obj']['exe'])
        user_event_index += 1

    # Iterate through remaining of window log events
    while window_log_index < len(window_log):
        # Convenience variables
        curr_log = window_log[window_log_index]
        pids = [key for key in curr_log.keys() if key not in [
            '_id', 'timestamp']]
        open_apps = [curr_log[pid]['process_obj']['name'] for pid in pids]

        # App is open. track it as such
        for app in open_apps:
            intervals[app].update_is_open(curr_log['timestamp'])

        # Update icons
        for pid in pids:
            app_name = curr_log[pid]['process_obj']['name']
            intervals[app_name].icon = find_icon_from_path(
                curr_log[pid]['process_obj']['exe'])

        # Among all tracked apps, update closed apps
        for app in intervals.as_dict():
            if app not in open_apps:
                intervals[app].update_is_closed(curr_log['timestamp'])

        window_log_index += 1

    # Close edge cases with trailing intervals and NoneTypes
    for process_name in intervals.as_dict().keys():
        intervals[process_name].finalize()

    return intervals


def schedule_activities(activities):
    """
    Implementation of the classic greedy activity scheduling algorithm, packing/scheduling
    the given activities in as few rooms, or lists, as required.
    :param activities: a list of tuples, where tuple[0] contains a tuple for start and finish
    timestamps in datetime format. tuple[1] contains the name of the process we are scheduling.
    :return: a list of lists describing a schedule with each process timed as compactly as
    possible without overlapping.
    """

    # Ignore activities under five seconds in duration
    activities = [activity for activity in activities
                  if activity[0][1] - activity[0][0] > timedelta(seconds=3)]

    # sort activities by start time
    act_start = sorted(activities, key=lambda a: (a[0][0], a[0][1]))
    # sort activities by finish time
    act_finish = sorted(activities, key=lambda a: (a[0][1], a[0][0]))
    # generate list IDs in a heap
    lists = []
    num_lists = 0
    heapq.heapify(lists)
    # array pointers
    start, finish = 0, 0
    # list assignment map
    assignment = {}
    # storage list
    schedule = []

    while finish < len(act_finish):
        # finishing time needs to be processed
        if start >= len(act_start) or act_start[start][0][0] >= act_finish[finish][0][1]:
            # put the list occupied by the process back into the available lists
            heapq.heappush(lists, assignment[act_finish[finish][1]])
            # increment finish activity pointer
            finish += 1
        else:
            # no available lists
            if len(lists) == 0:
                # add a list
                num_lists += 1
                # add the list to queue
                heapq.heappush(lists, num_lists - 1)
            # Assign the list
            chosen_list = heapq.heappop(lists)
            assignment[act_start[start][1]] = chosen_list
            # add new list to schedule
            if chosen_list == len(schedule):
                schedule.append([])
            # add new item to existing list to schedule
            schedule[chosen_list].append(act_start[start])
            # increment start activity pointer
            start += 1

    return schedule


if __name__ == '__main__':
    info = bpt_diagram_info(datetime.utcnow() - timedelta(hours=12),
                            datetime.utcnow() + timedelta(days=1),
                            5, 15, 60)
    pprint(info)
    close_server()
