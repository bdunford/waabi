import os
from waabi.utility.reader import Reader
from waabi.utility.writer import Writer
from waabi.utility.to import To




class Generate(object):
    
    @staticmethod
    def Header(record,fp):
        Writer.Json(fp,record.request.header)
        return "Header Written to: {0}".format(fp)

    @staticmethod
    def Code(logs,fp):
        mapped = []
        multi = False
        jpad = 4
        opad = 0
        tpl = "single"
    
        if not isinstance(logs,list): 
            logs = [logs]

        if len(logs) > 1:
            multi = True
            jpad = 8
            opad = 4
            tpl = "multiple"
    

        for log in logs:
            mapped.append(Generate.substitute_map(log,jpad))
        const_header = "None"
        const_cookies = "None"

        if multi: 
            if len(set(map(lambda x: x["@@HEADER"],mapped))) == 1:
                const_header = To.Code(logs[0].request.HeaderNoCookies())
                for m in mapped:
                   m["@@HEADER"] = "header"
                
            if len(set(map(lambda x: x["@@COOKIES"],mapped))) == 1:
                const_cookies =  To.Code(logs[0].request.cookies)
                for m in mapped:
                   m["@@COOKIES"] = "cookies"

        t = Reader.Read("{0}/{1}.pyt".format(os.path.dirname(__file__),tpl))
        req_objs = [Generate.gen_request_object(m,opad) for m in mapped]
        
        if multi: 
            t = Reader.Substitute(t,"@@HEADER",const_header)
            t = Reader.Substitute(t,"@@COOKIES",const_cookies)
            t = Reader.Substitute(t,"@@REQOBJS",",\n".join(req_objs))
        else: 
            t = Reader.Substitute(t,"@@REQOBJ",req_objs[0])
        
        Writer.Replace(fp,t)
        return "Python Script Written to: {0}".format(fp)
     
    @staticmethod
    def substitute_map(log,pad):
        return {
            "@@URL": To.Code(log.request.uri),
            "@@METHOD": To.Code(log.method),
            "@@HEADER": To.Code(log.request.HeaderNoCookies(),pad),
            "@@COOKIES": To.Code(log.request.cookies,pad),
            "@@QUERY": To.Code(log.request.query,pad),
            "@@BODY": To.Code(log.request.body,pad)
        }
        
    @staticmethod
    def gen_request_object(s_map,pad):
        lpad = " " * pad
        t = [
            "ReqObj(",
            "    url = @@URL,",
            "    method = @@METHOD,",
            "    header = @@HEADER,",
            "    cookies = @@COOKIES,",
            "    query = @@QUERY,",
            "    body = @@BODY",
            ")"
        ]
        
        tpl = "\n".join([lpad + l for l in t])

        for k,v in s_map.items():
            tpl = Reader.Substitute(tpl,k,v)
        return tpl

