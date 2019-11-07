import http.client

import configparser
import json

import ssl

def get_chunk_size(resp):
    size_str = resp.read(2)
    if(size_str.decode('utf8').replace("'", '"')==""):
        return 0
    while size_str[-2:] != b"\r\n":
        size_str += resp.read(1)
    return int(size_str[:-2], 16)

def get_chunk_data(resp,chunk_size):
    data = resp.read(chunk_size)
    resp.read(2)
    return data

if __name__ == '__main__':

    gcontext = ssl.SSLContext()

    #Obtain configuracion from config.cfg file.
    cfg = configparser.ConfigParser()  
    cfg.read(["./config.cfg"])  
    
    keyrock_protocol = cfg.get("GENERAL", "keyrock_protocol")
    keyrock_host = cfg.get("GENERAL", "keyrock_host")
    keyrock_port = cfg.get("GENERAL", "keyrock_port")

    capman_protocol = cfg.get("GENERAL", "capman_protocol")
    capman_host = cfg.get("GENERAL", "capman_host")
    capman_port = cfg.get("GENERAL", "capman_port")

    policy_action = cfg.get("GENERAL", "policy_action")
    policy_device = cfg.get("GENERAL", "policy_device")
    policy_resource = cfg.get("GENERAL", "policy_resource")

    pep_protocol = cfg.get("GENERAL", "pep_protocol")
    pep_host = cfg.get("GENERAL", "pep_host")
    pep_port = cfg.get("GENERAL", "pep_port")

    headers = {"Content-Type":"application/json"}
    body = json.dumps({"name":"pedrog@um.es","password":"iotcrawler"}).encode()

    keyRockMethod="POST"
    keyRockUri="/v1/auth/tokens"
    
    print("******* Sending authentication request to KeyRock... *******")
    print("Method: " + keyRockMethod)
    print("URI: " + keyRockUri)
    print("Headers: " + str(headers))
    print("Body: " + str(body))

    if(keyrock_protocol.upper()=="http".upper() or keyrock_protocol.upper()=="https".upper()):
        
        if(keyrock_protocol.upper()=="http".upper()):
            conn = http.client.HTTPConnection(keyrock_host,keyrock_port)
        else:
            #conn = http.client.HTTPSConnection(keyrock_host,keyrock_port,
            #                                    key_file="./certs/idm-2018-key.pem",
            #                                    cert_file="./certs/idm-2018-cert.pem",
            #                                    context=gcontext)

            conn = http.client.HTTPSConnection(keyrock_host,keyrock_port,
                                                context=gcontext)

        conn.request(keyRockMethod, keyRockUri, body, headers)
        response = conn.getresponse()

        status = response.status
        reason = response.reason
        data = response.read()
        conn.close()

        if(status==201):
            #Example format: keyRockToken = "4aece71b-8c22-4012-9397-608da3f58c6c"
            keyRockToken = response.headers["X-Subject-Token"]

            print("\nAUTH SUCCESS: Authentication Keyrock Token obtained : " + keyRockToken)

            headers = {"Content-Type":"application/json"}
            body = json.dumps({"token":keyRockToken,"ac":policy_action,"de":policy_device,"re":policy_resource}).encode()

            capmanMethod="POST"
            capmanUri="/"

            print("\n******* Sending authorisation request to Capability Manager... *******")
            print("Method: " + capmanMethod)
            print("URI: " + capmanUri)
            print("Headers: " + str(headers))
            print("Body: " + str(body))

            if(capman_protocol.upper()=="http".upper()):
                conn = http.client.HTTPConnection(capman_host,capman_port)
            else:
                #conn = http.client.HTTPSConnection(capman_host,capman_port,
                #                                key_file="./certs/idm-2018-key.pem",
                #                                cert_file="./certs/idm-2018-cert.pem",
                #                                context=gcontext)
                conn = http.client.HTTPSConnection(capman_host,capman_port,
                                                context=gcontext)

            conn.request(capmanMethod, capmanUri, body, headers)
            response = conn.getresponse()

            status = response.status
            reason = response.reason
            data = response.read()
            conn.close()

            
            if(status==200):

                bodyJSON = json.loads(data.decode('utf8').replace("'", '"'))
                print("\nSUCCESS: Authorisation Granted --> Capability token obtained : " + str(bodyJSON))

                headers = {"Accept":"application/ld+json",
                           "x-auth-token":json.dumps(bodyJSON)}

                uri="/ngsi-ld/v1/entities/?type=http://example.org/vehicle/Vehicle"                          
                method="GET"                           
                
                print("\n******* Sending NGSI-LD query to MDR through PEP_PROXY... *******")
                print("Method: " + method)
                print("URI: " + uri)
                print("Headers: " + str(headers))

                if(pep_protocol.upper()=="http".upper()):
                    conn = http.client.HTTPConnection(pep_host,pep_port)
                else:
                    #conn = http.client.HTTPSConnection(pep_host,pep_port,
                    #                                key_file="./certs/idm-2018-key.pem",
                    #                                cert_file="./certs/idm-2018-cert.pem",
                    #                                context=gcontext)
                    conn = http.client.HTTPSConnection(pep_host,pep_port,
                                                    context=gcontext)
                conn.request(method, uri, None, headers)
                response = conn.getresponse()

                status = response.status
                reason = response.reason
                #data = response.read()
                headersPEPResponse = response.headers

                response.chunked = False
                respbody = ""
                while True:
                    chunk_size = get_chunk_size(response)
                    if (chunk_size == 0):
                        break
                    else:
                        chunk_data = get_chunk_data(response,chunk_size)
                        #print("Chunk Received: " + chunk_data.decode())
                        respbody += chunk_data.decode()

                conn.close()

                print("\nSUCCESS: NGSI-LD response:\n")
                print("* Code: " + str(status))
                print("* Message: " + str(reason))
                print("* Headers:\n" + str(headersPEPResponse))
                print("* Body:\n" + str(respbody))

            else:
                print("\nFAILURE Authorisation Error --> Capability Manager.")
                print(data)
        else:
            print("\nFAILURE: Authentication Error --> Key Rock")
            print(json.loads(data.decode('utf8').replace("'", '"')))
    else:
        print("Incorrect value for 'keyrock_protocol': " + keyrock_protocol)