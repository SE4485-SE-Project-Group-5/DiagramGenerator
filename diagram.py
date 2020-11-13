import datetime
import os
import platform
import sys
from graphviz import Digraph
import pandas
import json
from config import BUNDLE_DIR
from datetime import datetime, timedelta, date, time
import bson.json_util
from pymongo import MongoClient


client = MongoClient("mongodb+srv://admin:mongodb9143@cluster0.femb8.mongodb.net/group5db?retryWrites=true&w=majority")
db = client['group5db']
collection = db['00:0c:29:de:a0:0d']
cursor = collection.find()
mongo_docs = list(cursor)
mongo_docs = mongo_docs[:1]
docs = pandas.DataFrame(columns=[])

for num, doc in enumerate(mongo_docs):
    doc["_id"] = str(doc["_id"])
    doc_id = doc["_id"]
    series_obj = pandas.Series(doc, name=doc_id)
    docs = docs.append(series_obj)
    docs.to_json("test_export_json.json")


def generateDiagram(app_info):
    directory = None
    homepath = None

    directory = os.path.abspath(os.path.join(BUNDLE_DIR, 'static'))
    homepath = os.path.abspath(os.path.join(BUNDLE_DIR, 'static', 'icons'))
    g = Digraph('G', filename='test_export_json', directory=directory)
    g.attr(rankdir='TB', size='8,5')
    fontname = "Helvetica"

    # NOTE: the subgraph name needs to begin with 'cluster' (all lowercase)
    #       so that Graphviz recognizes it as a special cluster subgraph

    # username = user_info["username"]
    # mac_addy = user_info["mac_address"]
    # ip_addy = user_info["ip_address"]
    mac_addy = collection.name
    date = str(datetime.today().date())

    with g.subgraph(name='cluster_0', graph_attr={'bgcolor': 'lightcyan4', 'penwidth': '3', 'pencolor': 'navy'}) as c:
        c.attr(color='grey11', fontname=fontname, fontcolor='white')
        c.attr('node', shape='box', style='filled',
               color="gold", fontname=fontname, margin=".15")

        edges = []

        for list in app_info:
            for app in app_info[list]:
                # print(app["name"])
                # print("===")

                # TODO: convert from UTC to local time dynamically instead of hard-coding an offset
                dummyStart = app["start"] - timedelta(hours=5)
                startTime = dummyStart.strftime("%I:%M %p")

                # TODO: convert from UTC to local time dynamically instead of hard-coding an offset
                dummyFinish = app["finish"] - timedelta(hours=5)
                finishTime = dummyFinish.strftime("%I:%M %p")

                # Obtains the duration in hours, minutes and seconds format
                dummyDuration = app["duration"]
                total = dummyDuration.seconds
                hours, remainder = divmod(total, 3600)
                minutes, seconds = divmod(remainder, 60)

                # This piece of code would obtain just microseconds if needed/wanted
                # total2=dummyDuration.microseconds
                # hours, remainder = divmod(total, 3600000000)
                # minutes, rem = divmod(remainder, 60000000)
                # seconds, microseconds = divmod(rem, 1000000)

                # If, else if statmenets that will print out values that aren't 0 time
                if hours == 0:
                    if minutes == 0:
                        finalDuration = ('%s secs' % (seconds))
                    else:
                        finalDuration = ('%s mins %s secs' %
                                         (minutes, seconds))
                elif minutes == 0 and hours != 0:
                    finalDuration = f'{hours} hrs {seconds} secs'
                else:
                    finalDuration = f'{hours} hrs {minutes} mins {seconds} secs 0 msecs'

                iconpath = app["icon"]

                if iconpath and iconpath.strip():
                    path = homepath + "\\" + iconpath

                    # Creates the node displaying the app name, start time to end time, and duration
                    # along with the app's icon
                    c.node(str(app["start"]).replace(':', '') + app["name"], '''<<TABLE border="0">
                          <TR><TD fixedsize="true" width="55" height="50" bgcolor="transparent"><IMG SRC="''' + path + '''"/></TD>
                          <TD align="center" valign="middle">''' + app[
                        "name"] + '''<BR/><BR/>''' + startTime + ' - ' + finishTime + '''<BR/><BR/>Duration<BR/>''' + finalDuration + '''</TD></TR>
                          <TR><TD></TD></TR></TABLE>>''', width='5', height='1.5')
                else:
                    # Creates the node displaying the app name, start time to end time, and duration
                    # without the icon since it does not exist
                    c.node(str(app["start"]).replace(':', '') + app["name"], '''<<TABLE border="0">
                              <TR><TD fixedsize="true" width="55" height="50" bgcolor="transparent"></TD>
                              <TD align="center" valign="middle">''' + app[
                        "name"] + '''<BR/><BR/>''' + startTime + ' - ' + finishTime + '''<BR/><BR/>Duration<BR/>''' + finalDuration + '''</TD></TR>
                              <TR><TD></TD></TR></TABLE>>''', width='5', height='1.5')

            # print(len(app_info[list]))
            for i in range(len(app_info[list]) - 1):
                edges.append((str(app_info[list][i]["start"]).replace(':', '') + app_info[list][i]["name"],
                              str(app_info[list][i + 1]["start"]).replace(':', '') + app_info[list][i + 1]["name"]))

        # Changes the color of the arrows to red
        c.edge_attr.update(color='red')
        c.edges(edges)

        c.attr(label="User= " + '''username''' + " | MAC= " +
               mac_addy + " | IP= " + '''ip_addy''' + " | " + date)

    g.view()
