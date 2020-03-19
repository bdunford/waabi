import requests
import waabi
from waabi.utility import Printer
from waabi.utility import WordList


def req(url, method, header, cookies, query, data): 
    
    json = data if "Content-Type" in header.keys() and header["Content-Type"].find("application/json") > -1 else None
    data = None if json != None else data    

    r = requests.request(method.lower(),url,headers=headers,cookies=cookies,params=query,data=data,json=json,allow_redirects=False,verify=False)
    return r

url = @@URL
method = @@METHOD

header = @@HEADER

cookies = @@COOKIES

query = @@QUERY

data = @@DATA



r = req(url, header, cookies, query, data)
Printer.PrintWebResponse(r)
