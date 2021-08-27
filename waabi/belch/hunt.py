import re
import inspect
import json
from waabi.utility.printer import Printer
from waabi.utility.to import To

class Hunt(object):
    
    def __init__(self,logs,category=None):
        self.logs = logs
        self.results = {}
        cats = {f[0].replace("for_",""):f[1] for f in inspect.getmembers(self,predicate=inspect.ismethod) if f[0].find("for_") > -1}
        if category in cats.keys(): 
            self.results[category.capitalize()] = cats[category]()
        else: 
            for k,v in cats.items():
                self.results[k.capitalize()] = v()


    def _reflect_calc_score(self,params):
        score = 0
        if not params: 
            return 0,None
        ret = []
        for k,v in params.items(): 
            if isinstance(v,list):
                vals = []
                for x in v: 
                    score = score if len(x) < score else len(x)
                    vals.append(x) 
                ret.append("{0}: {1}".format(k,",".join(vals)))
            else:
                ret.append("{0}: {1}".format(k,v))
        return score,ret
        
    
   
    def _reflect_result(self,logId,method,url,qMatches,bMatches):
        qscore, q = self._reflect_calc_score(qMatches)
        bscore, b = self._reflect_calc_score(bMatches)
        ret = {"score":bscore if bscore > qscore else qscore, "sig": method+url}
        ret["value"] = "{0}  {1} {2}\n".format(logId,method,url)
        if q: 
            ret["value"] += "Query Params --> {0}\n".format(" | ".join(q))
        if b: 
            ret["value"] += "Post Params  --> {0}\n".format(" | ".join(b))
        return ret

       

    def _reflect_find(self,body,params):
        ret = {}
        if not params or not body: 
            return None
        for key,val in params.items():
            vals = val if isinstance(val,list) else [val]
            for v in vals:
               if body.find(str(v)) > -1:
                    if key in ret.keys():
                        if isinstance(ret[key],list):
                            ret[key].append(str(val))
                        else:
                            ret[key] = [ret[key],str(val)]
                    else: 
                        ret[key] = str(val)
        return ret
    

    def _ifind(self,haystack,needle): 
        if haystack.lower().find(needle.lower()) > -1: 
            return True
        return False

    def _injections_result(self,logid,method,url,headers,qm,bm):
        
        ret={"id":logid,"sig":method+url}
        ret["value"] = "{0}  {1} {2}\n".format(logid,method,url)
        
        qm = qm if qm else {}
        bm = bm if bm else {}
        
        for k in set(list(qm.keys()) + list(bm.keys())): 
            ret["value"] += "{0}: {1}\n".format(k,headers[k])
            if k in qm.keys(): 
                ret["value"] += "  Query Params --> {0}\n".format(" | ".join(map(lambda x: "{0}={1}".format(x[0],x[1]),qm[k])))
            if k in bm.keys(): 
                ret["value"] += "  Post Params --> {0}\n".format(" | ".join(map(lambda x: "{0}={1}".format(x[0],x[1]),bm[k])))
        return ret


    def _injections_find(self,headers,params): 
        l = 3
        ret = {}
        if not params: 
            return None
        for hk,hv in headers.items(): 
            hv = " ".join(hv) if isinstance(hv,list) else hv
            matches = []
            for pn,pv in params.items(): 
                found = False
                pv = pv if isinstance(pv,list) else [pv]
                for v in pv: 
                    if len(pn) > l: 
                        if self._ifind(hk,pn):
                            found = True
                        if self._ifind(hv,pn):
                            found = True
                    if len(v) > l: 
                        if self._ifind(hk,v):
                            found = True
                        if self._ifind(hv,v):
                            found = True
                if found: 
                    matches.append((pn," ".join(pv)))
            if len(matches) > 0: 
                ret[hk] = matches
        if len(ret.keys()) > 0: 
            return ret
        return None
        
    def _header_find(self,header,headers): 
        for k,v in headers.items(): 
            if header.lower() == k.lower():
                return "{0}: {1}".format(header,v)
        return False

    def for_reflected(self):
        ret = []
        for log in self.logs.Search([],{"mime":"HTML"}):
            if int(log[1].length) > 0:
                body = log[1].response.body 
                body = To.SafeDecode(body)
                body = body if not isinstance(body,(list,dict,tuple)) else json.dumps(body)
                qm = self._reflect_find(body,log[1].request.query)
                bm = self._reflect_find(body,log[1].request.body) if isinstance(log[1].request.body,dict) else None 
            if qm or bm: 
                url = "{0}://{1}{2}".format(log[1].protocol,log[1].host,log[1].path)
                ret.append(self._reflect_result(log[0],log[1].method,url,qm,bm))
        final = []
        for r in sorted(ret, key = lambda i: -i["score"]):
            if r["sig"] not in map(lambda m: m["sig"],final):
                final.append(r)
            else: 
                for i in range(len(final)):
                    if r["sig"] == final[i]["sig"] and r["score"] > final[i]["score"]:
                        final[i] = r
        return map(lambda m: m["value"],final)

                   
    def for_headers(self): 
        ret = []
        x = ["Server","X-Powered-By","Content-Type","Transfer-Encoding","Access-Control-Allow-Origin"]

        for l in self.logs.Search(): 
            for h in x: 
                reqh = self._header_find(h,l[1].request.header)
                if reqh and reqh not in ret:
                    ret.append(reqh)
                resh = self._header_find(h,l[1].response.header)
                if resh and resh not in ret:
                    ret.append(resh)
        return list(sorted(ret))
    
    def for_inputs(self):
        patterns = {
            "url": re.compile("(http|https)\:\/\/"),
            "file": re.compile("\.(php|pdf|exe|txt|asp|aspx|json|do|pl|html|js|csv|htm|jsp|css|ashx|dhtml|cgi|cfm|action|rb|shtml|xml)"),
            "code": re.compile("[\{\}\$\;\=\|\:]+"),
            "path": re.compile("[\/\\\\]+")
        }

        ret = []
        tpl = "{0} {1} {2}\n{3}\n"
        
        for log in self.logs.Search():
            params = {}
            if log[1].request.query: 
                params["Query"] = To.SingleDemension(log[1].request.query)
            if log[1].request.body:
                sd = To.SingleDemension(log[1].request.body)
                if sd: 
                    params["Body"] = sd
            finds = {}
            for param,values in params.items(): 
                for f,v in values.items(): 
                    for t,p in patterns.items():
                        if p.search(v.lower()):
                            if param in finds.keys(): 
                                finds[param][f] = (t,v)
                            else: 
                                finds[param] = {f:(t,v)}
                            break
            
                   
            if len(finds.keys()) > 0: 
                meta = []
                for p,find in finds.items():
                    label = p + ":"
                    for f,v in find.items():
                        meta.append(Printer.Cols([
                            (label,7,False),
                            (f,25,False),
                            (v[0].upper(),5,False),
                            (v[1],80,False),
                        ],False))
                        label = ""
                ret.append(
                    tpl.format(
                        log[0],
                        log[1].method,
                        log[1].request.uri,
                        "\n".join(meta)
                    )
                )


        return ret
        
    def for_injections(self): 
        ret = []
        for log in self.logs.Search():
            #filter
            headers = log[1].response.header
            qm = self._injections_find(headers,log[1].request.query)
            bm = self._injections_find(headers,log[1].request.body) if isinstance(log[1].request.body,dict) else None 
            if qm or bm: 
                url = "{0}://{1}{2}".format(log[1].protocol,log[1].host,log[1].path)
                ret.append(self._injections_result(log[0],log[1].method,url,headers,qm,bm))
        final = []
        for r in sorted(ret, key = lambda i: -i["id"]):
            if r["sig"] not in map(lambda m: m["sig"],final):
                final.append(r)
        return map(lambda m: m["value"],final)



