from requests_html import HTML
import re
import difflib


class Html(object):


    @staticmethod
    def FindExecJs(res,code,attributes,tryRender=True):
        
        if len(res.text) > 0:
            hl = HTML(html=res.text)
            attributes = attributes if isinstance(attributes,list) else [attributes] 

            if tryRender:
                try:
                    hl.render(timeout=0.5)
                except Exception as ex:
                    pass

            
            expr = re.compile("(^|\"\;\s*|\'\;\s*|\=\s*|\+\s*|\(\s*|\{\s*)" + re.escape(code))
            scripts = ["script: " + el.text for el in filter(lambda x: expr.search(x.text) != None,hl.find("script"))]

                
            attrs = []
            
            
            for a in attributes: 
                prfxs = ["javascript:"]
                if a[0:2] == "on":
                    prfxs.append("")
                if a == "src":
                    prfxs.append("data:text/javascript,")
                for pfx in prfxs:                    
                    attrs += ["attr: " + el.attrs[a] for el in hl.find("[{0}^='{1}']".format(a,pfx + code))]
       
            ret = {
                "type": "match",
                "matches": list(set(scripts)) + list(set(attrs)), 
                "count": len(scripts) + len(attrs),
                "rendered": hl.html
            }
        
            return ((len(scripts) + len(attrs) > 0 ),ret)
        else:
            return (False,{"matches":[],"count":0,"rendered":""})

        
    

    @staticmethod
    def Reflected(res,value,tryRender=True):
        if len(res.text) > 0:
            hl = HTML(html=res.text)
            if tryRender:
                try:
                    hl.render(timeout=0.5)
                except Exception as ex:
                    pass
            
            matches = re.findall(".{1,15}" + re.escape(value) + ".{1,15}",hl.html, re.DOTALL)
        
            ret = {
                "type": "match",
                "count": len(matches),
                "matches": list(set(matches)),
                "rendered": hl.html
            }

            return (( len(matches) > 0),ret)
        else:
            return (False,{"type":"match","matches":[],"count":0,"rendered":""})


         
    
    @staticmethod
    def UrlEncode(val):
        for enc in [("?","%3f"),("=","%3d"),("&","%26"),("/","%2f")]:
            val = val.replace(enc[0],enc[1])
        return val

    @staticmethod
    def SmartEncode(query): 
        ret = []
        if query:
            if isinstance(query,str):
                return query
            for k,v in query.items():
                if isinstance(v,list):
                    for x in v:
                        ret.append("{0}={1}".format(k,Html.UrlEncode(x)))
                else:
                    ret.append("{0}={1}".format(k,Html.UrlEncode(v)))
            if len(ret) > 0:
                return "&".join(ret)
        
        return None

    @staticmethod
    def GetMime(res):
        m = {
            "html": "HTML",
            "json": "JSON",
            "css": "STYLE",
            "script": "SCRIPT",
            "font": "FONT",
            "xml": "XML",
            "pdf": "PDF",
            "image": "IMAGE",
            "vdn": "DOC",
            "octet": "BINARY",
            "csv": "CSV",
            "java-archive": "JAR",
            "xip": "ZIP",
            "plain": "TEXT"
        }

        if res.headers and "content-type" in res.headers.keys():
            ct = res.headers["content-type"]
            for k,v in m.items():
                if ct.find(k) > -1:
                    return v
        return "TEXT"

    @staticmethod
    def Compare(res,orig):
        olines = orig.text.splitlines(keepends=True)
        rlines = res.text.splitlines(keepends=True)
        ret = {
            "type": "compare",
            "status": orig.status_code != res.status_code,
            "length": len(orig.text) != len(res.text),
            "lines": len(olines) != len(rlines),
            "content": orig.text != res.text,
            "time": abs(int(orig.elapsed.microseconds / 1000) - int(res.elapsed.microseconds / 1000)) > 700,
            "headers": Html.dictCompare(orig.headers,res.headers),
            "cookies": Html.dictCompare(orig.cookies,res.cookies),
            "diff": list(difflib.Differ().compare(olines,rlines)),
            "count": 0
        }
        i = 0
        for v in ret.values():
            if v:
                i += 1 
        ret["count"] = i - 2
        flag = False
        if not ret["status"] and (ret["content"] or len(ret["headers"]) + len(ret["cookies"])):
            flag = True
        return flag,ret
        


        return ret
    
    @staticmethod
    def dictCompare(dicta,dictb):
        results = []
        for k,v in dicta.items():
            try:
                if k not in dictb.keys() or v != dictb[k]:
                    results.append(k)
            except:
                pass

        for k,v in dictb.items():
            try:
                if k not in dicta.keys() or v != dicta[k]:
                    results.append(k)
            except: 
                pass
        return list(set(results))







