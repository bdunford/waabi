import json
import sys
import os

class Writer(object):

    @staticmethod
    def Append(filepath, content, add_new_line=True):
        o = 'ab' if isinstance(content,bytes) else 'a'
        Writer.EnsureFilePath(filepath)
        with open(filepath,o) as w:
            w.write(content + '\n')
            w.close()

    @staticmethod
    def Replace(filepath, content): 
        o = 'wb' if isinstance(content,bytes) else 'w'
        Writer.EnsureFilePath(filepath)
        with open(filepath,o) as w:
            w.write(content)
            w.close()

    @staticmethod
    def Json(filepath, content):
        Writer.EnsureFilePath(filepath)
        j = json.dumps(content,indent=2)
        with open(filepath,'w') as w:
            w.write(j)
            w.close()

    @staticmethod
    def EnsureFilePath(filepath):
        if not os.path.exists(os.path.dirname(filepath)):
            os.makedirs(os.path.dirname(filepath))

    @staticmethod
    def SafeEncode(text):
        return text.encode('ascii', 'ignore').decode('ascii')
