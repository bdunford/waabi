import requests
import waabi
from waabi.utility import Printer
from waabi.utility import WordList
from waabi.utility import Payload
from waabi.utility import Reader
from waabi.utility import ReqObj
from waabi.utility import Html
import time

def req(o,proxy=False,smartEncode=False): 
    
    proxies = None if not proxy else o.Proxies()
    query = o.query if not smartEncode else Html.SmartEncode(o.query)
    json = o.body if "Content-Type" in o.header.keys() and o.header["Content-Type"].find("json") > -1 else None
    body = None if json != None else o.body    

    r = requests.request(
        o.method.lower(),
        o.url,
        headers=o.header,
        cookies=o.cookies,
        params=query,
        data=body,
        json=json,
        allow_redirects=False,
        verify=False,
        proxies=proxies
    )
    return r


o = @@REQOBJ

#payload Example
#o.data = Payload.Get("graphql-introspection.ql")

r = req(o)
Printer.PrintWebResponse(r)


#for w in WordList.Get("fuzz"):
#    time.sleep(1)
#    o.query["id"] = w
#    r = req(o,False,True)
#    Printer.PrintWebSummary(r,True,w)
    
#for w in WordList.Get("xss"):
#    time.sleep(1)
#    o.query["id"] = w
#    r = req(o,False,True)
#    x = Html.FindExecJs(r,"console.log(742)",["onpointermove","onerror"])
#    Printer.PrintWebSummary(r,x[0],w)
    



