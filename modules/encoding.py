import json


from modules import aes

def encodeEncrypted(data, key):
    data = json.dumps(data)
    data, iv = aes.Encrypt(data, key)
    dataToReturn = []
    dataToReturn.append(data)
    dataToReturn.append(iv)
    dataToReturn = json.dumps(dataToReturn)
    dataToReturn = dataToReturn.encode('utf-8')
    return dataToReturn

def encode(data):
    data = json.dumps(data) #Json dump message
    data = data.encode('utf-8') #Encode message in utf-8
    return(data) 
def decode(data):
    try:
        data = data.decode('utf-8') #Decode utf-8 data
        data = data.strip()
        data = json.loads(data) #Load from json
        return(data)
    except json.decoder.JSONDecodeError:
        print("json error")
        print(data)