import waabi
import json
import os
from waabi.utility.writer import Writer

class WaabiProxyLogger(object):

    @staticmethod

    def Request(uid,req):
        waabi.globals.requests[uid] = {"req":req,"chunk":None}

    def Response(uid,chunk):
        waabi.globals.requests[uid]["chunk"] = chunk

    def Log(uid):
        x = waabi.globals.requests.pop(uid)
        print("-" * 100)
        j = json.dumps(x["req"],indent=4)
        print(j)
        print(x["chunk"])
        Writer.Append(os.path.join(waabi.globals.data_path,"proxy.dat"),j+",")
