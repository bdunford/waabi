import re
from waabi.utility.finder import Finder 
import json

class Printer(object):
    @staticmethod
    def HR():
        print("-" * 95)

    @staticmethod
    def Print(mixed):
        if mixed:
            if isinstance(mixed, (list,tuple)):
                for r in mixed:
                    print(r)
                return
            if isinstance(mixed,dict):
                for k in reversed(list(mixed.keys())):
                    if isinstance(mixed[k], (list, tuple)):
                        print("%s: " % k)
                        for v in mixed[k]:
                            print(v)
                    else:
                        print("{0}: {1}".format(k, mixed[k]))
                return
            print(mixed)

    @staticmethod
    def PrintWebResponse(r, content=True):
        Printer.HR()
        Printer.Print({"stats" : r.status_code})
        Printer.Print({"url" : r.url})
        Printer.Print("-----------Headers------------")
        Printer.Print(dict(r.headers))
        if content:
            Printer.Print("-----------Content------------")
            print(r.text)
        Printer.HR()
    
    @staticmethod
    def PrintWebSummary(r, plus=True, append=False):
        pl = "[+]" if plus else "[-]" 
        cl = len(r.text)
        ct = r.headers["content-type"].split(";")[0] if "content-type" in r.headers else "None"
        ap = append if append else r.url

        Printer.Cols([
            (pl,4,False),
            (r.status_code,4,False),
            (cl,8,False),
            (ct,15,False),
            (int(r.elapsed.microseconds / 1000),7,False),
            (ap,82,False),
        ])

    @staticmethod
    def Cols(vals,prnt=True):
        s = ""
        for v in vals:
            x = str(v[0])[:v[1]-1]
            if v[2]:
                x = x.rjust(v[1]) + " "
            else:
                x = x.ljust(v[1]) + " "
            if len(v) == 4:
                x = Printer.Highlighter(x,v[3])
            s += x

        if not prnt:
            return s
        else:
            print(s)
    

    @staticmethod
    def Highlighter(val,color="green",newline=False):
        colors = {
            "red": "\033[0;31m{}\033[m",
            "green" : "\033[0;32m{}\033[m",
            "yellow": "\033[0;33m{}\033[m",
            "blue": "\033[0;34m{}\033[m",
            "orange": "\33[38;5;202m{}\33[m"
        }
        
        if color not in colors.keys():
            return val

        if newline: 
            eps = colors[color].split("{}")
            val = val.replace("\n",eps[1] + "\n" + eps[0])
        
        return colors[color].format(val)
        

    @staticmethod
    def Highlight(val,ptrn,color="green",prnt=True):
        mc = 0
        lines = []
        try:
            rexp = re.compile(ptrn,re.MULTILINE|re.DOTALL|re.IGNORECASE)
            matches = rexp.findall(val)
            if len(matches) > 0: 
                lines = Finder.LineNumbers(val,matches)
                for m in set(matches):
                    val = val.replace(m,Printer.Highlighter(m,color,True))
                mc = len(matches)
        except:
            raise(Exception("Regex pattern error check highlight pattern"))
        if prnt:
            print(val)
            return mc,lines
        else:
            return mc,list(map(lambda x: str(x),lines)),val

    @staticmethod
    def PrintBody(content,highlight=False,skip=0,take=0,printer=print):
        if not content:
            printer("")
            return False,False

        if isinstance(content,(dict,list)):
            content = json.dumps(content,indent=2)
        content = content.replace("\r\n","\n")
        hc = 0
        lines = False
        if highlight:
            hc,lines,content = Printer.Highlight(content,highlight,"green",False)
        
        lined = []
        i = 1

        for l in content.replace("\r\n","\n").split("\n"):
            lined.append((i,l))
            i += 1
         
        take = len(lined) if take <= 0 and skip == 0 else abs(int(take)) + 1
        skip = 0 if skip <= 0 else abs(int(skip))
        skip = skip -1 if skip > 0 else skip
        results = "\n".join(map(lambda x: "\033[0;90m{0}\033[m {1}".format(str(x[0]).rjust(len(str(i))),x[1]),lined[skip:skip+take]))
        printer(results)
        return hc,lines
        
        


        


