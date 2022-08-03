import os
import re
import sys
import time
import json
import waabi
from urllib.parse import urlparse
from waabi.core import Base
from waabi.utility.reader import Reader
from waabi.utility.writer import Writer




class Target(Base):

    def Init(self):
        self.name = self.options.parameter
        self.working = os.getcwd()
        self.path = os.path.join(self.working,self.name)
        self.scope = os.path.join(self.path,"scope")
        self.project = os.path.join(self.path,"project.json")
        self.burp = os.path.join(self.path,"burp.xml")
        self.orig = os.path.join(self.path,"orig_scope")
        self.notes = os.path.join(self.path,"notes")
        self.writeup = os.path.join(self.path,"writeup") 

    @staticmethod
    def Help(): 
        return ("Creates a new target directory with scope and  notes","target [name]")

    def Run(self):
        hr = "-" * 80
        if os.path.isdir(self.path):
            print("\nTarget: {0} already exists...\n".format(self.name))
            sys.exit()
        print(hr)
        print("Creating Target: {0}".format(self.name))
        print("Path: {0}".format(self.path))
        os.mkdir(self.path)
        print(hr)
        self._accept_scope()
        Writer.Replace(self.notes,"\n")   
        self._add_writeup()
        print("Target Created: {0}".format(self.name))
        print("Path: {0}".format(self.path))
        print(hr)
        print("Starting belch CLI ...")
        self._change_working()
        self._start_belch() 
    
    def _add_writeup(self): 
        os.mkdir(self.writeup)
        Writer.Replace(os.path.join(self.writeup,"report.md"),("\n" * 5).join([
            "# NAME:","# DESCRIPTION:","# IMPACT","# RECOMMENDED FIX:",""
        ]))
        Writer.Replace(os.path.join(self.writeup,"payload"),"")
        Writer.Replace(os.path.join(self.writeup,"request"),"") 
        

    def _change_working(self):
        os.chdir(self.path)

    def _start_belch(self): 
        time.sleep(2) 
        Writer.Replace(self.burp,"<?xml version=\"1.0\"?>\n<items></items>")   
        waabi.belch.Cli().Start(self.burp,None)

    def _accept_scope(self):
        scope  = self._parse_scope(
            "http[s]*\:\/\/[^\s\*]+",
            self._multi_line_input("Enter Target Scope:"),
        )
        
        project = {
            "proxy":{
                "http_history_display_filter":{
                    "by_request_type": {"show_only_in_scope_items":True}
                },
                "match_replace_rules":[
                    {
                        "comment":"Add QWERTY Query String Exists",
                        "enabled":True,
                        "is_simple_match":False,
                        "rule_type":"request_first_line",
                        "string_match":"^(\\w+\\s[^\\s]+\\?[^\\s]+)(\\sHTTP.+)$",
                        "string_replace":"$1&qwerty=ytrewq$2"
                    },
                    {
                        "comment":"Add QWERTY No Query String",
                        "enabled":True,
                        "is_simple_match":False,
                        "rule_type":"request_first_line",
                        "string_match":"^(\\w+\\s[^\\?]+)(\\sHTTP.+)$",
                        "string_replace":"$1?qwerty=ytrewq$2"
                    },
                    {
                        "comment":"Add QWERTY Query (?) exists with no query",
                        "enabled":True,
                        "is_simple_match":False,
                        "rule_type":"request_first_line",
                        "string_match":"^(\\w+\\s[^\\s]+\\?)(\\sHTTP.+)$",
                        "string_replace":"$1qwerty=ytrewq$2"
                    },
                    {
                        "comment":"Add QWERTY Remove Doubled query",
                        "enabled":True,
                        "is_simple_match":False,
                        "rule_type":"request_first_line",
                        "string_match":"^(\\w+\\s[^\\s]+\\?[^\\s]*)qwerty\\=ytrewq\\&qwerty\\=ytrewq([^\\s]*\\sHTTP.+)$",
                        "string_replace":"$1qwerty=ytrewq$2"
                    },
                    {
                        "comment":"Emulate IE",
                        "enabled":False,
                        "is_simple_match":False,
                        "rule_type":"request_header",
                        "string_match":"^User-Agent.*$",
                        "string_replace":"User-Agent: Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0)"
                    },
                    {
                        "comment":"Emulate iOS",
                        "enabled":False,
                        "is_simple_match":False,
                        "rule_type":"request_header",
                        "string_match":"^User-Agent.*$",
                        "string_replace":"User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 5_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9B176 Safari/7534.48.3"
                    },
                    {
                        "comment":"Emulate Android",
                        "enabled":False,
                        "is_simple_match":False,
                        "rule_type":"request_header",
                        "string_match":"^User-Agent.*$",
                        "string_replace":"User-Agent: Mozilla/5.0 (Linux; U; Android 2.2; en-us; Droid Build/FRG22D) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1"
                    },
                    {
                        "comment":"Require non-cached response",
                        "enabled":False,
                        "is_simple_match":False,
                        "rule_type":"request_header",
                        "string_match":"^If-Modified-Since.*$"
                    },
                    {
                        "comment":"Require non-cached response",
                        "enabled":False,
                        "is_simple_match":False,
                        "rule_type":"request_header",
                        "string_match":"^If-None-Match.*$"
                    },
                    {
                        "comment":"Hide Referer header",
                        "enabled":False,
                        "is_simple_match":False,
                        "rule_type":"request_header",
                        "string_match":"^Referer.*$"
                    },
                    {
                        "comment":"Require non-compressed responses",
                        "enabled":False,
                        "is_simple_match":False,
                        "rule_type":"request_header",
                        "string_match":"^Accept-Encoding.*$"
                    },
                    {
                        "comment":"Ignore cookies",
                        "enabled":False,
                        "is_simple_match":False,
                        "rule_type":"response_header",
                        "string_match":"^Set-Cookie.*$"
                    },
                    {
                        "comment":"Rewrite Host header",
                        "enabled":False,
                        "is_simple_match":False,
                        "rule_type":"request_header",
                        "string_match":"^Host: foo.example.org$",
                        "string_replace":"Host: bar.example.org"
                    },
                    {
                        "comment":"Add spoofed CORS origin",
                        "enabled":False,
                        "is_simple_match":True,
                        "rule_type":"request_header",
                        "string_replace":"Origin: foo.example.org"
                    },
                    {
                        "comment":"Remove HSTS headers",
                        "enabled":False,
                        "is_simple_match":False,
                        "rule_type":"response_header",
                        "string_match":"^Strict\\-Transport\\-Security.*$"
                    },
                    {
                        "comment":"Disable browser XSS protection",
                        "enabled":False,
                        "is_simple_match":True,
                        "rule_type":"response_header",
                        "string_replace":"X-XSS-Protection: 0"
                    }
                ]
            },
            "target":{
                "scope":scope,
                "filter":{"by_request_type":{"show_only_in_scope_items":True}}
            }
        }


        urls = []
        for x in scope["include"]: 
            
            tpl = "{0}://{1}{2}"
            if x["host"].find(":443") + x["host"].find(":80") == -2:
                prot = x["prot"].lower() if x["protocol"] != "any" else "https"
                urls.append(tpl.format(prot,x["host"],x["path"] if "path" in x.keys() else "/"))
            
        Writer.Json(self.project,project)
        Writer.Replace(self.scope,"\n".join(urls))
        
    def _multi_line_input(self,prompt):
        print(prompt)
        lines = []
        while True:
            line = input()
            if len(line) == 0:
                return lines
            else: 
                lines.append(line)
            
    def _parse_scope(self,ptrn,lines):

        try:
            target = json.loads("\n".join(lines))
            if "scope" in target["target"].keys(): 
                return target["target"]["scope"]
        except Exception as e: 
            pass
            
        parsed = []
        for l in lines:
            m = re.findall("http[s]*\:\/\/[^\s\*]+",l) 
            if len(m) > 0:
                parsed.append(m[0])

        scope = {"exclude":[],"include":[]}

        for x in list(set(parsed)): 
            u = urlparse(x)
            scope["include"].append(
                {
                    "enabled":"true",
                    "protocol":"any",
                    "host":u.netloc,
                    "file":u.path
                }
            )
        return scope

       


        






            
           
            
        
        


