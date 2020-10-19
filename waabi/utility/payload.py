import os
import waabi
from waabi.utility.reader import Reader

class Payload(object):
    
    @staticmethod 
    def Extensions():
        return [
              ".xml",
              ".sql",
              ".ql",
              ".xlsx",
              ".xlsm",
              ".xls",
              ".doc",
              ".docx",
              ".svg",
              ".html",
              ".jpeg",
              ".pdf",
              ".gif",
              ".bmp",
              ".ico",
              ".tiff",
              ".png",
              ".txt",
              ".rtf",
              ".json"
          ]


    @staticmethod
    def Get(name):
        if name in Payload.GetNames():
            return Reader.ReadBytes(os.path.join(waabi.globals.payload_path,name))
        return False

    @staticmethod
    def GetPaths():
        results = []
        for fn in os.listdir(waabi.globals.payload_path):
            x,ext = os.path.splitext(fn)
            if ext in Payload.Extensions():
                results.append(os.path.join(waabi.globals.payload_path,fn))
        return results

    @staticmethod
    def GetNames():
        results = []
        for fp in Payload.GetPaths():
            results.append(os.path.basename(fp))
        return results
