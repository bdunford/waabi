import json
from waabi.utility.printer import Printer
from waabi.utility.html import Html

class Display(object):
    
    def __init__(self,width=120):
        self.width = width
        pass
    
    def _displayOptions(self,opt1,opt2,opt3):
        opts = [x for x in [opt1,opt2,opt3] if x is not False and x is not None]
        highlight = None
        skip = False
        take = False
        for o in opts:
            if str(o).isdigit():
                if skip is False:
                    skip = int(o)
                else:
                    take = int(o)
            else:
                highlight = o
        return highlight,int(skip),int(take)
   
    def P(self,content,sep=False):
        print("{0}{1}{0}".format("\n" if sep else "",content))
       
    
    def Format(self,tpl,sep=False,*vals):
        tpl = "\n" + tpl + "\n" if sep else tpl
        self.P(tpl.format(*vals))

    def HR(self):
        self.P("-" * 120)

    def Pair(self,title,value,col=True,sep=False):
        self.P("{0}{1}{2} {3}{0}".format("\n" if sep else "",title,":" if col else "",value))

    def BR(self,cnt=1):
        for i in range(cnt):
            self.P("")
    
    def List(self,items,sep=True):
        self.BR()
        for item in items:
            self.P(item)
        self.BR()

    def Dict(self,d, indent=""): 
        for k,v in d.items(): 
            self.P("{0}{1}: {2}".format(indent,k,v))

    def Json(self,mixed):
        self.P(json.dumps(mixed,indent=2))

    def Header(self,title):
        self.BR()
        self.P(title)
        self.HR()
 
   
    def ResultHeader(self):
        self.BR()
        Printer.Cols([
            ("id",5,False),
            ("flag",5,False),
            ("log",5,False),
            ("status",7,False),
            ("length",8,False),
            ("mime",7,False), 
            ("time",7,False),
            ("cnt",4,False),
            ("type",7,False),
            ("parameter",25,False),
            ("value",35,False)  
        ])
        self.HR()



    def Result(self,result,detail=False,full=False,opt1=None,opt2=None,opt3=None):
        highlight,skip,take = self._displayOptions(opt1,opt2,opt3)
        res = result.response
        req = result.response.request
        meta = result.meta

        if not detail:
            Printer.Cols([
                (result.result_id,5,False),
                ("[+]" if result.flag else "[-]",5,False,"green" if result.flag else None),
                (result.log_id,5,False),
                (res.status_code,7,False),
                (len(res.text),8,False),
                (Html.GetMime(res),7,False),
                (int(res.elapsed.microseconds / 1000),7,False),
                (result.meta["count"] if result.meta else "",4,False),
                (result.type,7,False),
                (result.parameter,25,False),
                (result.value,35,False)  
            ])
        else:
           
            self.HR()
            self.Pair(req.method.upper(),req.url,False)
            self.Dict(req.headers)
            self.BR(2)
            if req.body:
                #TODO: correct json display
                self.P(req.body) 
            self.HR()
            self.Pair(res.status_code,res.reason,False)
            self.Dict(res.headers)
            self.BR(2)
            if full:
                body = res.text
                if result.meta and "rendered" in result.meta.keys():
                    body = result.meta["rendered"]
                if result.meta and "diff" in result.meta.keys():
                    body = "".join(result.meta["diff"])
                matches,lines = Printer.PrintBody(body,highlight,skip,take)
                if highlight:
                    self.BR()
                    self.Pair("Highlights",matches)
                    self.Pair("Lines",", ".join(lines))
                self.BR()

            self.HR()
            if result.pv:
                for p,v in result.pv.items():
                    self.Pair("Parameter",p)
                    self.Pair("Word",v)
                    self.BR()
            if meta:
                if meta["type"] == "match":
                    self.Pair("Matches",meta["count"])
                    for m in meta["matches"]:
                        self.Pair("   ",m,False)
                if meta["type"] == "compare":
                    diffs = []
                    for k,v in meta.items(): 
                        if isinstance(v,bool) and v == True: 
                            diffs.append(k)

                    self.Pair("Differences",meta["count"])
                    
                    self.P(", ".join(diffs))
                    self.BR()
                    if meta["headers"]:
                          self.Pair("Headers",", ".join(meta["headers"]))                         
                    if meta["cookies"]:
                          self.Pair("Cookies",", ".join(meta["cookies"]))
                self.BR() 
        
    def Log(self,record,detail=False,full=False,opt1=None,opt2=None,opt3=None):
        highlight,skip,take = self._displayOptions(opt1,opt2,opt3)
        ix = record[0]
        x = record[1]
        ct = ""
        cl = ""

        for k,v in x.request.header.items():
            if k.lower() == "content-type":
                ct = v.split(";")[0]
            if k.lower() == "content-length":
                cl = v
        self.HR()
        Printer.Cols([
            (ix,6,False),
            (x.method,7,False),
            (ct,34,False),
            (cl,8,False),
            ("Response: ",10,False),
            (x.status,4,False),
            (x.mime,7,False), 
            (x.length,8,False),
            (x.ip,15,False),     
            
        ])
        self.P(x.url)
        
        if detail: 
            self.HR()
            self.P(x.request.line)
            self.Dict(x.request.HeaderNoCookies())
            if x.request.cookies:
                self.P("Cookie:")
                self.Dict(x.request.cookies,"    ")
            self.BR(2)
            if x.request.body: 
                self.P(x.request.body) 
            self.HR()

            self.P(x.response.line) 
            self.Dict(x.response.header)
            self.BR(2)
            if full: 
                matches,lines = Printer.PrintBody(x.response.body,highlight,skip,take)
                if highlight:
                    self.BR()
                    self.Pair("Highlights",matches)
                    self.Pair("Lines",", ".join(lines))
                self.BR()

    def JWT(self,record,jwts,canary,issuer,private_key_file,kid):
        if record: 
            self.Log(record)
        else: 
            jwts = [jwts]
        self.BR()
        self.P("JWT(s):")
        if jwts: 
            for jwt in jwts:
                self.HR()
                self.Header("HEADER: ALGORITHM & TOKEN TYPE")
                self.Json(jwt.header)
                self.Header("PAYLOAD: DATA")
                self.Json(jwt.payload)
                self.Header("SIGNATURE: BASE64")
                self.P(jwt.signature)
                self.Header("ENCODED: ORIGIONAL")
                self.P(jwt.encoded)
                self.Header("ENCODED: NONE ALGORITHM")
                self.P(jwt.AsAlgNone())
                self.Header("ENCODED: HS256 ALGORITHM")
                self.P(jwt.AsAlgHS256())
                self.Header("ENCODED: WITH CANARY")
                self.P(jwt.WithCanaryIss(canary))
                self.Header("ENCODED: WITH MOCK OAUTH")
                self.P(jwt.WithMockOauth(issuer,private_key_file,kid))
                if len(jwt.errors) > 0:
                    self.Header("ERRORS: TOKEN PARSING ERRORS")
                    self.P(jwt.errors)

        else: 
           self.P("No JWT's found for this Log...",True)
        self.BR()

    def Success(self,message):
        self.P(Printer.Highlighter(message,"green"))    

    def Error(self,message):
        self.P(Printer.Highlighter(message,"red"))    

    def Warring(self,mesage):
        self.P(Printer.Highlighter(message,"yellow"))    

    def Intro(self,source,log_cnt,prnt=False):

        x = "\n".join([
            Printer.Highlighter(("<" * 55) + " belch CLI " + (">" * 55),"orange"),
            "Source: {0}".format(source),
            "Records: {0}".format(log_cnt),
            ""
        ])
        
        if not prnt:
            return x
        else:
            self.P(x)




    def GetPrompt(self):
       return Printer.Highlighter("b3l(h> ","orange")
       

