import base64
import urllib.parse



class KV(object):
    def __init__(self,k,v):
        self.k = k
        self.v = v


class Request(object):

    def __init__(self,raw):
        self.raw = raw
        self.header = Parser.HeaderFromRaw(raw)
        self.cookies = Parser.CookiesFromHeader(self.header["Cookie"]) if "Cookie" in self.header.keys() else {}
        #self.header
        #self.cookies
        #self.body string

class Response(object):

    def __init__(self,raw):
        self.raw = raw
        self.header = Parser.HeaderFromRaw(raw)
        self.cookies = Parser.CookiesFromHeader(self.header["Set-Cookie"]) if "Set-Cookie" in self.header.keys() else {}

        #self.body


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
        self.request = Request(Parser.Get(item,"request"))
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
        header_parts = raw.split("\r\n\r\n")[0].split("\r\n")[1:]
        header = {}
        for r in header_parts:
            header[r.split(":")[0]] = r.split(":")[1].strip()

    @staticmethod
    def HeaderFromRaw(raw):
        header_parts = raw.split("\r\n\r\n")[0].split("\r\n")[1:]
        header = {}
        for r in header_parts:

            parts = r.split(":")
            k = parts[0]
            v = ":".join(parts[1:])

            if k == "Set-Cookie":
                if k in header.keys():
                    header[k].append(v.strip())
                else:
                    header[k] = [v.strip()]
            else :
                header[k] = v.strip()
        return header


    def BodyFromRaw(raw,t):
        parts = raw.split("\r\n\r\n")
        if t == "raw":
            return raw
        if t == "form":
            return raw
        if t == "multi":
            return raw
        if t == "json":
            return raw


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
