import sys
import os
import json
import xml.etree.ElementTree as ET

class Reader(object):

    @staticmethod
    def List(filepath):
        with open(filepath,'r') as r:
            return r.read().strip("\n").split("\n")

    @staticmethod
    def Read(filepath):
        with open(filepath,'r') as r:
            return r.read()

    @staticmethod
    def ReadBytes(filepath):
        with open(filepath,'rb') as r:
            return r.read()

    @staticmethod
    def Json(filepath):
        with open(filepath,'r') as r:
            return json.loads(r.read())

    @staticmethod
    def Xml(filepath):
        xdoc = ET.parse(filepath)
        return xdoc.getroot()

    @staticmethod
    def Substitute(content, target, value):
        content = content.replace(target,value)
        return content



