import requests


class Printer(object):
    @staticmethod
    def HR():
        print("-" * 95)

    @staticmethod
    def Print(mixed):
        if mixed:
            if isinstance(mixed, (list,tuple)):
                for r in mixed:
                    print(r)
                return
            if isinstance(mixed,dict):
                for k in reversed(list(mixed.keys())):
                    if isinstance(mixed[k], (list, tuple)):
                        print("%s: " % k)
                        for v in mixed[k]:
                            print(v)
                    else:
                        print("{0}: {1}".format(k, mixed[k]))
                return
            print(mixed)

    @staticmethod
    def PrintWebResponse(r, content=True):
        Printer.HR()
        Printer.Print({"stats" : r.status_code})
        Printer.Print({"url" : r.url})
        Printer.Print("-----------Headers------------")
        Printer.Print(dict(r.headers))
        if content:
            Printer.Print("-----------Content------------")
            print(r.text)
        Printer.HR()

    

def req(url, headers, cookies, data=False):
    if not data: 
        r = requests.get(
            url, 
            headers=headers, 
            cookies=cookies, 
            allow_redirects=False, 
            verify=False)
    else: 
        r = requests.post







URL

header = @@HEADER

cookies = @@COOKIES

data = @@DATA





