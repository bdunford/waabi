
import sys
import os

class Writer(object):

    @staticmethod
    def Append(filepath, content, add_new_line=True):

        Writer.EnsureFilePath(filepath)
        with open(filepath,'a') as w:
            w.write(content + '\n')
            w.close()

    @staticmethod
    def Replace(filepath, content):

        Writer.EnsureFilePath(filepath)
        with open(filepath,'w') as w:
            w.write(content)
            w.close()

    @staticmethod
    def EnsureFilePath(filepath):
        if not os.path.exists(os.path.dirname(filepath)):
            os.makedirs(os.path.dirname(filepath))

    @staticmethod
    def SafeEncode(text):
        return text.encode('ascii', 'ignore').decode('ascii')
