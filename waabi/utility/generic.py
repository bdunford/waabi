


class ReqObj(object):

    def __init__(self,url,method,header,cookies,query,body):
        self.url = url
        self.method = method
        self.header = header
        self.cookies = cookies
        self.query = query
        self.body = body

    def Proxies(self): 
        return {
            "http" : "http://127.0.0.1:8080",
            "https" : "https://127.0.0.1:8080"
        } 
    
