import waabi
import json
import os
from waabi.utility.writer import Writer

class WaabiProxyLogger(object):

    @staticmethod
    def Log(message):
        print("-" * 100)
        j = json.dumps(message,indent=4)
        print(j)
        Writer.Append(os.path.join(waabi.globals.data_path,"proxy.dat"),j+",")
    
    
    
    
