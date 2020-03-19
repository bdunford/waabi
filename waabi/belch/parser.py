import base64
import urllib.parse
import json



class KV(object):
    def __init__(self,k,v):
        self.k = k
        self.v = v


class Request(object):

    def __init__(self,raw,url):
        self.uri = url.split("?")[0]
        self.header = Parser.HeaderFromRaw(raw)
        self.cookies = Parser.CookiesFromHeader(self.header["Cookie"]) if "Cookie" in self.header.keys() else None
        self.query = None if len(url.split("?")) == 1 else urllib.parse.parse_qs(url.split("?")[1])
        self.body = Parser.BodyFromRaw(raw,self.header)

    def HeaderNoCookies(self):
        d =  {}
        for k,v in self.header.items():
            if k != "Cookie":
                d[k] = v
        return d


class Response(object):

    def __init__(self,raw):
        self.raw = raw
        self.header = Parser.HeaderFromRaw(raw)
        self.cookies = Parser.CookiesFromHeader(self.header["Set-Cookie"]) if "Set-Cookie" in self.header.keys() else {}
        self.body = Parser.BodyFromRaw(raw,self.header)



class Log(object):

    def __init__(self,item):
        self.method = Parser.Get(item,"method")
        self.ip = Parser.Get(item,"host","ip")
        self.host = Parser.Get(item,"host")
        self.port = Parser.Get(item,"port")
        self.protocol = Parser.Get(item,"protocol")
        self.url = Parser.Get(item,"url")
        self.path = Parser.Get(item,"path")
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
                    return str(base64.b64decode(el.text),'utf-8')
                else:
                    return el.text
        return ""


    @staticmethod
    def HeaderFromRaw(raw):
        header_parts, x = Parser.HttpSplit(raw)
        header={}
        for r in header_parts:
            parts = r.split(":")
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
    def BodyFromRaw(raw,header):
        ct = header["Content-Type"] if "Content-Type" in header.keys() else "default"
        x, body = Parser.HttpSplit(raw)
        if body != None:
            try:
                if len(body) == 0:
                    return None
                if ct.find("application/json") > -1:
                    return json.loads(body)
                if ct.find("application/x-www-form-urlencoded") > -1:
                    return urllib.parse.parse_qs(body)
                return body
            except Exception as e:
                return body
        return None


    @staticmethod
    def HttpSplit(raw):
        parts = raw.split("\r\n\r\n")
        if  len(parts) > 2:
            parts = [parts[0],"\r\n\r\n".join(parts[1:])]
        if len(parts) < 2:
            parts = raw.split("\n\n")
        if len(parts) > 2:
            parts = [parts[0],"\n\n".join(parts[1:])]

        header_parts = parts[0].split("\r\n")[1:]
        if len(header_parts) < 2:
            header_parts = parts[0].split("\n")[1:]

        return (header_parts,parts[1] if len(parts) > 1 else None)

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
            v = urllib.parse.unquote(c.split("=")[1].strip())
        else:
            v = True
        return KV(k,v)
