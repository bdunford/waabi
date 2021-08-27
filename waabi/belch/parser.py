import base64
import urllib.parse
import json
import re
from waabi.utility.to import To
from waabi.utility.jwty import Jwty

class KV(object):
    def __init__(self,k,v):
        self.k = k
        self.v = v


class Request(object):

    def __init__(self,raw,url):
        
        self.raw = raw
        header, body, line = Parser.HttpSplit(raw)
        self.line = line
        self.uri = url.split("?")[0]
        self.header = Parser.HeaderFromSplit(header)
        self.cookies = Parser.CookiesFromHeader(self.header["Cookie"]) if "Cookie" in self.header.keys() else None
        self.query = None if len(url.split("?")) == 1 else urllib.parse.parse_qs(url.split("?")[1])
        self.body = Parser.BodyFromSplit(body,self.header)
        self.content = body

    def HeaderNoCookies(self):
        d =  {}
        for k,v in self.header.items():
            if k.lower() != "cookie":
                d[k] = v
        return d


class Response(object):

    def __init__(self,raw):
        self.raw = raw
        header, body, line = Parser.HttpSplit(raw)
        
        self.line = line
        self.header = Parser.HeaderFromSplit(header)
        self.cookies = Parser.CookiesFromHeader(self.header["Set-Cookie"]) if "Set-Cookie" in self.header.keys() else {}
        self.body = Parser.BodyFromSplit(body,self.header) 

class Log(object):

    def __init__(self,item):
        self.method = Parser.Get(item,"method")
        self.ip = Parser.Get(item,"host","ip")
        self.host = Parser.Get(item,"host")
        self.port = Parser.Get(item,"port")
        self.protocol = Parser.Get(item,"protocol")
        self.url = Parser.Get(item,"url")
        fpp = Parser.Get(item,"path").split("?")
        self.path = fpp[0]
        self.query = fpp[1] if len(fpp) > 1 else None
        self.status = Parser.Get(item,"status")
        self.length = Parser.Get(item,"responselength")
        self.mime = Parser.Get(item,"mimetype")
        self.extension = Parser.Get(item,"extension")
        self.request = Request(Parser.Get(item,"request"),self.url)
        self.response = Response(Parser.Get(item,"response"))

class Parser(object):

    @staticmethod
    def ParseBurpLog(burp_el):
        results = []
        for item_el in burp_el:
            results.append(Log(item_el))
        return results


    @staticmethod
    def Get(item_el,name,attr=False):
        el = item_el.find(name)
        if el != None:
            if attr:
                return el.get(attr)
            if el.text != None:
                if el.get("base64") == "true":
                    return base64.b64decode(el.text)
                else:
                    return el.text
        return ""


    @staticmethod
    def HeaderFromSplit(header_parts):
        header={}
        for r in header_parts:
            parts = r.decode().split(":") if isinstance(r,bytes) else r.split(":")
            k = parts[0]
            v = ":".join(parts[1:])
            if k == "Set-Cookie":
                if k in header.keys():
                    header[k].append(v.strip())
                else:
                    header[k] = [v.strip()]
            else:
                header[k] = v.strip()
        return header

    @staticmethod
    def BodyFromSplit(body,header):
        ct = "default"
        for k in header.keys():
            if k.lower() == "content-type":
                ct = header[k]
        if body != None:
            try:
                if len(body) == 0:
                    return None
                if ct.lower().find("application/json") > -1:
                    return json.loads(body)
                if ct.lower().find("application/x-www-form-urlencoded") > -1:
                    parsed = urllib.parse.parse_qs(body)
                    if parsed:
                        return parsed
                return body
            except Exception as e:
                #TODO: total error and print and include in load results
                #raise(e)
                return body
        return None


    @staticmethod
    def HttpSplit(raw):
        if raw =="":
            return "","",""
        try:
        
            cr = "\r\n" 
            n =  "\n"

            if isinstance(raw,bytes):
                cr = cr.encode()
                n  = n.encode()

            parts = raw.split(cr * 2)
            if  len(parts) > 2:
                parts = [parts[0],(cr * 2).join(parts[1:])]
            if len(parts) < 2:
                parts = raw.split(n * 2)
            if len(parts) > 2:
                parts = [parts[0],(n * 2).join(parts[1:])]


            header_parts = list(map(lambda x: str(x,'utf-8') if isinstance(x,bytes) else x,parts[0].split(cr)))

            if len(header_parts) < 2:
                header_parts = parts[0].split(n)
        
            first_line = header_parts[0]
            header_parts = header_parts[1:]

            body = None
        
            if len(parts[1]) > 1:
                try: 
                    body = str(parts[1],'utf-8') if isinstance(parts[1],bytes) else parts[1]
                except:
                    body = parts[1]
        
            return (header_parts,body,first_line)
        except Exception as e:
            print(raw)
            raise e

    @staticmethod
    def CookiesFromHeader(header_cookie):
        cookies = {}
        if isinstance(header_cookie, list):
            for c in header_cookie:
                crumbs = Parser.CookiesRows(c)
                cookie = {}
                cookie["value"] = Parser.CookieKV(crumbs[0]).v
                for x in crumbs[1:]:
                    cookie[Parser.CookieKV(x).k] = Parser.CookieKV(x).v
                cookies[Parser.CookieKV(crumbs[0]).k] = cookie
        else:
            for c in Parser.CookiesRows(header_cookie):
                cookies[Parser.CookieKV(c).k] = Parser.CookieKV(c).v
        return cookies

    @staticmethod
    def CookiesRows(c):
        return c.split(";")

    @staticmethod
    def CookieKV(c):
        parts = c.split("=")
        k = c.split("=")[0].strip()
        if len(parts) > 1:
            v = "=".join(c.split("=")[1:]).strip()
        else:
            v = ""
        return KV(k,v)
    
    @staticmethod
    def FindJWTs(raw): 
        ret = []    
        ptrn = "[A-Za-z0-9\+\/]{10,}\=*\.[A-Za-z0-9\+\/]{25,}\=*\.[A-Za-z0-9\+\/\=\_\-]*"  
        if isinstance(raw,bytes):
            ptrn = ptrn.encode()

        results = re.findall(ptrn,raw)
        for r in set(results):
            try: 
                if isinstance(r,bytes): 
                    ret.append(Jwty(r.decode()))
                else: 
                    ret.append(Jwty(r))
            except Exception as ex: 
                raise ex
                pass
        return ret if len(ret) > 0 else None
        
                   
                    

        

         
