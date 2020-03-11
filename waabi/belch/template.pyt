import requests
import waabi
from waabi.utility import Printer


def req(url, headers, cookies, query, data=False):
    if not data:
        r = requests.get(
            url,
            headers=headers,
            cookies=cookies,
            params=query,
            allow_redirects=False,
            verify=False
        )
    else:
        r = requests.get(
          url,
          headers=headers,
          cookies=cookies,
          params=query,
          data=data,
          allow_redirects=False,
          verify=False
        )

url = @@URL

header = @@HEADER

cookies = @@COOKIES

query = @@QUERY

data = @@DATA



r = req(url, header, cookies, query, data)
Printer.PrintWebResponse(r)
