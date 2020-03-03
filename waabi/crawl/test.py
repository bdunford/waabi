from requests_html import HTMLSession
session = HTMLSession()
from urllib3.exceptions import InsecureRequestWarning

r = session.get('https://my.caresource.com/')

#this will hit each link


#forms = r.html.find("form")
#do a regex parse for any urls too
#for f in forms:
#    print(f)
#    for i in f.find("input"):
#        for k,v in i.attrs.items():
#            print(k,v)
        
    #for attr in 
#start enumerating links

#for l in r.html.absolute_links:
#    print(l)
print(len(r.html.links))
r.html.render()
print(len(r.html.links))
