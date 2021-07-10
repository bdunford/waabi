import copy
import json
import requests
import traceback
from waabi.utility import Html, To


class Replay(object):

    def __init__(self,options):
        self._opts = options

    def _opt(self,key):
        return self._opts.Get(key)


    def Parameters(self):
        return [
            "headers",
            "cookies", 
            "query",
            "path",
            "url",
            "body",
            "method",
        ]

    def Methods(self):
        return [
            "GET",
            "POST",
            "PUT",
            "DELETE",
            "OPTIONS",
            "TRACE",
            "CONNECT",
        ]
    
    def _remove_headers(self,req,headers):
        rm = []
        for ek in req["headers"].keys():
            for rk in headers:
                if rk.lower() == ek.lower():
                    rm.append(ek)
        for k in rm:
            del req["headers"][k]
        return req
        
    
    def _method_change(self,req,log,flip):
        f = log.method.upper()
        t = req["method"].upper()
        if t == f or t not in self.Methods():
            return req
        if flip:
            if t == "GET":
                if isinstance(req["body"],dict):
                    req["query"] = {} if not req["query"] else req["query"]
                    for k,v in req["body"].items():
                        req["query"][k] = v
                req["body"] = None
                req = self._remove_headers(req,["content-type","content-length"])
            if f == "GET" and t in ("POST","PUT"):
                if isinstance(req["query"],dict):
                    req["body"] = {} if not req["body"] else req["body"]
                    for k,v in req["query"].items():
                        req["body"][k] = v
                req["query"] = None
                req["headers"]["Content-Type"] = "application/x-www-form-urlencoded"
             
        return req
    
    def _pv_opts(self,pv_opts):
        find = False
        template = False
        if pv_opts:
            for o in pv_opts:
                if o:
                    if o.find("{0}") > -1:
                        template = o
                    else:
                        find = o
        return find,template

    def _prepare_value(self,source,value,find):
        if isinstance(source,list):
            if len(source) == 1: 
                value = value.replace("{base}",source[0])
                value = source[0].replace(find,value) if find else value
        else: 
            value = value.replace("{base}",source)
            value = source.replace(find,value) if find else value

        return value            

    def Result(self,result,proxies):
            req = result.response.request
            r = requests.request(
                req.method.lower(),
                req.url,
                headers=req.headers,
                data=req.body,
                allow_redirects=False,
                verify=False,
                proxies=proxies
            )        
            return r


    def Repeat(self,i,log,label,parameters,values,pv_opts,meta_opts,on_success,on_fail):
        pvl = []
        find,template = self._pv_opts(pv_opts)
        if isinstance(parameters,list):
            pvl = parameters
        else: 
            for v in values:
                x = Html.UrlEncode(v) if self._opt("encode_path") and parameters == "path" else v 
                x = x if not template else template.format(x)
                pvl.append(To.Dict(parameters,x))
        for pv in pvl:
            res,err = self.Request(log,pv,find)
            if not err:
                args = [res] + meta_opts[1:]
                flag,meta = meta_opts[0](*args)
                on_success(i,label,pv,res,flag,meta)
            else:
                on_fail(err)

    
    def Request(self,log,pv=None,find=False,flip=False,proxies=None):
        try: 
            x = copy.deepcopy(log)
            o = {
                "headers": x.request.HeaderNoCookies(),
                "cookies": x.request.cookies,
                "query": x.request.query,
                "path": x.path,
                "url": x.url[:8] + x.url[8:].split("?")[0].replace(log.path,""),
                "body": x.request.body,
                "method": x.method
            }
            if pv:
                v = o
                for parameter,value in pv.items():
                    if parameter == "query":
                        v["query"] = Html.QueryToStr(o["query"])
                    if parameter == "body":
                        v["body"] = x.request.content

                    pt = To.Array(parameter,".") 
                    for i in range(len(pt)): 
                        if pt[i] in v.keys():
                            if i == len(pt) - 1:
                                v[pt[i]] = self._prepare_value(v[pt[i]],value,find)
                            else:
                                if v[pt[i]] == None:
                                    v[pt[i]] = {}
                                v = v[pt[i]]
                        else: 
                            if i == 0 or i < len(pt) - 1:
                                raise(Exception("Bad parameter string {0}".format(parameter)))
                            else:
                                v[pt[i]] = ""
                                v[pt[i]] = self._prepare_value(v[pt[i]],value,find)
            o = self._method_change(o,log,flip)
            query = Html.SmartEncode(o["query"]) if self._opt("smart_encode") else o["query"]
            
            if isinstance(o["body"], str): 
                body = o["body"]
                json = None
            else: 
                ct = "default"
                for k in o["headers"].keys():
                    if k.lower() == "content-type":
                        ct = o["headers"][k]
                json = o["body"] if ct.find("json") > -1 else None
                body = None if json != None else o["body"]

            r = requests.request(
                o["method"].lower(),
                o["url"] + o["path"],
                headers=o["headers"],
                cookies=o["cookies"],
                params=query,
                data=body,
                json=json,
                allow_redirects=False,
                verify=False,
                proxies=proxies
            )        
            return r,False
        except:
            return False,traceback.format_exc()


