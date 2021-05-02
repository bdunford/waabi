
import os
import re
import sys
import time
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
        parsed  = self._parse_lines(
            "http[s]*\:\/\/[^\s\*]+",
            self._multi_line_input("Enter Target Scope:"),
        )
        
        working = []
        consolidated = [] 
        project = {
            "proxy":{
                "http_history_display_filter":{
                    "by_request_type": {"show_only_in_scope_items":True}
                }
            },
            "target":{
                "scope":{"exclude":[],"include":[]},
                "filter":{"by_request_type":{"show_only_in_scope_items":True}}
            }
        }
        scope = []

        for r in parsed: 
            u = urlparse(r)
            pp = u.path.split("/")
            
            if pp[-1].find(".") > -1: 
                pp[-1] = ""
            working.append("https://{0}{1}".format(u.netloc,"/".join(pp)).rstrip("/"))


        for w in sorted(set(working),key=len):
            found = False
            for c in consolidated: 
                if w.find(c) == 0: 
                    found = True
            if not found:
                consolidated.append(w)
        
        for x in consolidated: 
            u = urlparse(x)
            scope.append("https://{0}{1}".format(u.netloc,u.path))
            scope.append("http://{0}{1}".format(u.netloc,u.path))
            project["target"]["scope"]["include"].append(
                {
                    "enabled":"true",
                    "protocol":"any",
                    "host":u.netloc,
                    "file":u.path
                }
            )
        Writer.Replace(self.scope,"\n".join(scope))
        Writer.Json(self.project,project)
        Writer.Replace(self.orig,"\n".join(parsed))
        


        


    def _multi_line_input(self,prompt):
        print(prompt)
        lines = []
        while True:
            line = input()
            if len(line) == 0:
                return lines
            else: 
                lines.append(line)
            
    def _parse_lines(self,ptrn,lines):
        ret = []
        for l in lines:
            m = re.findall("http[s]*\:\/\/[^\s\*]+",l) 
            if len(m) > 0:
                ret.append(m[0])
        return list(sorted(set(ret)))
       
        






            
           
            
        
        


