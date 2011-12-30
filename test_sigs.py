import hmac, hashlib, base64

client_token = 'befb2a67a08949960608a14b3d838485'
client_secret = 'KOpo73I4Cl0QUY7qssY1/nj1TVnz5GEwGoro2iVz'
#client_token = 'abc'
#client_secret = 'xyz'

signature = hmac.new(
    digestmod=hashlib.sha256,
    key=client_secret,
    msg="abc",
).digest()

print signature
print base64.b64encode(signature)