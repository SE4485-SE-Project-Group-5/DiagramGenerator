from datetime import timedelta


class ApplicationTimeLog:

    def __init__(self, active: int, idle: int, thinking: int):
        self.active_times = []  # During what times is this an active process
        self.idle_times = []  # During what times is this an idle process
        self.thinking_times = []  # During what times is this a thinking process
        self.open_times = []  # During what times is this process open at all
        self.mouse_times = []  # During what times is there mouse activity
        self.kb_times = []  # During what times is there keyboard activity
        self.timeouts = {'active': active, 'idle': idle, 'thinking': thinking}

        self.final_stats = {}
        self.icon = None

    def update_event(self, event, timestamp):
        """
        Updates interval times for keyboard and mouse usage.
        :param event: The event type indicator string
        :param timestamp: The timestamp this event occurred at
        :return: None
        """

        # TODO: make this activity timeout a parameter somewhere
        timeout = timedelta(seconds=5)

        # Is this a keyboard event?
        if event.startswith('KEYBOARD'):
            # if no kb events have been logged
            if len(self.kb_times) == 0:
                self.kb_times.append([timestamp, timestamp])
            # otherwise, check if last interval should be extended
            elif timestamp - self.kb_times[-1][1] <= timeout:
                self.kb_times[-1][1] = timestamp
            # otherwise, start a new interval
            else:
                self.kb_times.append([timestamp, timestamp])
        # This is a mouse event
        elif event.startswith('MOUSE'):
            # same logic as keyboard events
            if len(self.mouse_times) == 0:
                self.mouse_times.append([timestamp, timestamp])
            elif timestamp - self.mouse_times[-1][1] <= timeout:
                self.mouse_times[-1][1] = timestamp
            else:
                self.mouse_times.append([timestamp, timestamp])
        else:
            print(f'Invalid event type received: {event}')

    def update_active(self, timestamp):
        """
        Updates interval times for active/idle/thinking time spans.
        :param timestamp: The timestamp that this process was active at
        :return: None
        """

        # This application is being opened for the first time or has been closed already
        if len(self.open_times) == 0 or self.open_times[-1][1] is not None:
            self.open_times.append([timestamp, None])

        # If no active times are logged, start a new interval
        if len(self.active_times) == 0:
            self.active_times.append([timestamp, timestamp])
            return

        # Get the last interval
        last_interval = self.active_times[-1]
        # Determine if the last time this was active was within active timeout window
        if timestamp - last_interval[1] <= timedelta(seconds=self.timeouts['active']):
            # If so, extend the last interval recorded
            self.active_times[-1][1] = timestamp
            return
        else:
            # It's active now, so create a new active window
            self.active_times.append([timestamp, timestamp])

        # Check if within idle timeout window
        if timestamp - last_interval[1] <= timedelta(seconds=self.timeouts['idle']):
            # If so, create an interval originating from the last active time to now
            self.idle_times.append([self.active_times[-1][1], timestamp])
        # Check if within thinking timeout window
        elif timestamp - last_interval[1] <= timedelta(seconds=self.timeouts['thinking']):
            # If so, create an interval originating from the last active time to now
            self.thinking_times.append([self.active_times[-1][1], timestamp])
        # If it's been even longer, do something
        else:
            pass

    def update_is_open(self, timestamp):
        """
        Updates interval times for when this process is open.
        :param timestamp: The timestamp that this process was active at
        :return: None
        """

        # If this app hasn't been open before
        if len(self.open_times) == 0:
            self.open_times.append([timestamp, None])
            return

        # If this app has been closed already
        if self.open_times[-1][1] is not None:
            self.open_times.append([timestamp, None])
            return

        # If it's still open, do nothing

        # TODO: what if you query over multiple days? app could be open all night
        # # If it has been more than thinking time since last open, assume it was closed the last time it was active
        # if self.open_times[-1][0] + timedelta(seconds=self.timeouts['thinking']) < timestamp:
        #     # Close the open time
        #     self.open_times[-1][1] = self.active_times[-1][1]
        #     # Start new interval
        #     self.open_times.append([timestamp, None])

    def update_is_closed(self, timestamp):
        """
        Updates interval times for when this process is closed.
        :param timestamp: The timestamp that this process is closed at
        :return: None
        """

        # If this app hasn't been open before, do nothing
        if len(self.open_times) == 0:
            return

        # If this app is already open
        if self.open_times[-1][1] is None:
            self.open_times[-1][1] = timestamp

    def finalize(self):
        """
        Closes remaining intervals where an end time was not properly closed.
        :return: None
        """

        # Close cases where arrays are empty
        if len(self.active_times) == 0:
            self.active_times.append(
                [self.open_times[-1][0], self.open_times[-1][0]])
        if len(self.idle_times) == 0:
            self.idle_times.append(
                [self.open_times[-1][0], self.open_times[-1][0]])
        if len(self.thinking_times) == 0:
            self.thinking_times.append(
                [self.open_times[-1][0], self.open_times[-1][0]])

        # Terminate open status if necessary
        if self.open_times[-1][1] is None:
            self.open_times[-1][1] = max(self.active_times[-1][1],
                                         self.idle_times[-1][1], self.thinking_times[-1][1])

        # Calculate total amounts of time among categories by summing intervals
        # self.final_stats['active_time'] = sum([t2 - t1 for t1, t2 in self.active_times], timedelta()).total_seconds()
        # self.final_stats['idle_time'] = sum([t2 - t1 for t1, t2 in self.idle_times], timedelta()).total_seconds()
        # self.final_stats['thinking_time'] = sum([t2 - t1 for t1, t2 in self.thinking_times],
        #                                         timedelta()).total_seconds()
        # self.final_stats['open_time'] = sum([t2 - t1 for t1, t2 in self.open_times], timedelta()).total_seconds()
        # return self.final_stats

    def total_open_time(self, start, end):
        """
        Sums all time intervals this process was open for.
        :param start: starting timestamp to include in sum
        :param end: ending timestamp to include in sum
        :return: a timedelta instance for the total time sum
        """

        # TODO: edge case of interval starting before start; ending after start
        # TODO: edge case of interval ending before end; ending after end
        return sum([interval[1] - interval[0] for interval in self.open_times
                    if interval[0] >= start and interval[1] <= end], timedelta())

    def total_thinking_time(self, start, end):
        """
        Sums all time intervals this process was categorized as thinking time for.
        :param start: starting timestamp to include in sum
        :param end: ending timestamp to include in sum
        :return: a timedelta instance for the total time sum
        """

        # TODO: edge case of interval starting before start; ending after start
        # TODO: edge case of interval ending before end; ending after end
        return sum([interval[1] - interval[0] for interval in self.thinking_times
                    if interval[0] >= start and interval[1] <= end], timedelta())

    def total_idle_time(self, start, end):
        """
        Sums all time intervals this process was categorized as idle time for.
        :param start: starting timestamp to include in sum
        :param end: ending timestamp to include in sum
        :return: a timedelta instance for the total time sum
        """

        # TODO: edge case of interval starting before start; ending after start
        # TODO: edge case of interval ending before end; ending after end
        return sum([interval[1] - interval[0] for interval in self.idle_times
                    if interval[0] >= start and interval[1] <= end], timedelta())

    def total_mouse_time(self, start, end):
        """
        Sums all time intervals this process had active mouse time for.
        :param start: starting timestamp to include in sum
        :param end: ending timestamp to include in sum
        :return: a timedelta instance for the total time sum
        """

        # TODO: edge case of interval starting before start; ending after start
        # TODO: edge case of interval ending before end; ending after end
        return sum([interval[1] - interval[0] for interval in self.mouse_times
                    if interval[0] >= start and interval[1] <= end], timedelta())

    def total_kb_time(self, start, end):
        """
        Sums all time intervals this process had active keyboard time for.
        :param start: starting timestamp to include in sum
        :param end: ending timestamp to include in sum
        :return: a timedelta instance for the total time sum
        """

        # TODO: edge case of interval starting before start; ending after start
        # TODO: edge case of interval ending before end; ending after end
        return sum([interval[1] - interval[0] for interval in self.kb_times
                    if interval[0] >= start and interval[1] <= end], timedelta())
