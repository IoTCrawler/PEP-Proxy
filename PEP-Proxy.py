from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl
import http.client
import logging
import sys
import json
import configparser
import UtilsPEP
from subprocess import Popen, PIPE
import html

#import numpy as np


#  "ProxyPrivKey": "certs/server-priv-rsa.pem",
#  "ProxyPubKey": "certs/server-pub-rsa.pem",
#  "ProxyCert": "certs/server-public-cert.crt",

#Obtain configuracion from config.cfg file.
cfg = configparser.ConfigParser()  
cfg.read(["./config.cfg"])  
pep_host = cfg.get("GENERAL", "pep_host")
pep_port = int(cfg.get("GENERAL", "pep_port"))

APIVersion = cfg.get("GENERAL", "APIVersion")

allApiHeaders=json.loads(cfg.get("GENERAL", "allApiHeaders"))

#Obtain API headers
for m in range(len(allApiHeaders)):
    if(allApiHeaders[m][0].upper()==APIVersion.upper()):
        apiHeaders = allApiHeaders[m][1]
        break

target_protocol = cfg.get("GENERAL", "target_protocol")
chunk_size=int(cfg.get("GENERAL", "chunk_size"))

allSeparatorPathAttributeEncriptation=json.loads(cfg.get("GENERAL", "allSeparatorPathAttributeEncriptation"))

#Obtain API separator
for m in range(len(allSeparatorPathAttributeEncriptation)):
    if(allSeparatorPathAttributeEncriptation[m][0].upper()==APIVersion.upper()):
        sPAE = allSeparatorPathAttributeEncriptation[m][1]
        break

rPAE=json.loads(cfg.get("GENERAL", "relativePathAttributeEncriptation"))
noEncryptedKeys = json.loads(cfg.get("GENERAL", "noEncryptedKeys"))

#PDTE_JUAN: Quit and pass target_host, target_port to config.cfg.
target_host = ""
target_port = 0

if (APIVersion.upper() == "NGSIv1".upper() or APIVersion.upper() == "NGSIv2".upper()):
    #target_host = "155.54.95.242"
    target_host = "155.54.99.118"
    target_port = 1026
else:
    target_host = "155.54.95.248"
    target_port = 9090

def CBConnection(method, uri,headers,body = None):

    try:

        #logging.info("")
        #logging.info("")
        #logging.info(" ********* CBConnection ********* ")

        uri = UtilsPEP.obtainValidUri(APIVersion,uri)

        #logging.info("CBConnection: Sending the Rquest")

        # send some data
        
        if(target_protocol.upper() == "http".upper() or target_protocol.upper() == "https".upper()):

            state = True

            if (body != None):
                
                state = False

                #logging.info("Original body request: ")
                #logging.info(str(body))
                
                body, state = UtilsPEP.encryptProcess(APIVersion,method,uri,body,sPAE,rPAE,noEncryptedKeys)
                #body = html.escape(body)
                
                #logging.info("Body request AFTER encryption process: ")
                #logging.info(str(body))

            if (state):

                logging.info("BROKER REQUEST:\n" + 
                "\t\tMethod: " + method + "\n" + 
                "\t\tURI: " + uri + "\n" + 
                "\t\tHeaders: " + str(headers) + "\n" + 
                "\t\tBody: " + str(body))

                if(target_protocol.upper() == "http".upper()):
                    conn = http.client.HTTPConnection(target_host, target_port)
                else:                    
                    gcontext = ssl.SSLContext()
                    conn = http.client.HTTPSConnection(target_host,target_port,
                                                context=gcontext)

                conn.request(method, uri, body, headers)

                response = conn.getresponse()

                #logging.info("CBConnection - RESPONSE")
                logging.info("BROKER RESPONSE CODE: "      + str(response.code))
                #logging.info("Headers: ")
                #logging.info(response.headers)
            else:
                return -1
        
        #logging.info(" ********* CBConnection - END ********* ")

        return response

    except:

        return -1

def getstatusoutput(command):
    process = Popen(command, stdout=PIPE,stderr=PIPE)
    out, err = process.communicate()

    #print("out")
    #print(out)
    #print("err")
    #print(err)

    return (process.returncode, out)

def obtainRequestHeaders(RequestHeaders):

    headers = dict()

    content_length = 0

    try:
        # We get the headers
        
        #logging.info (" ********* HEADERS BEFORE obtainRequestHeaders ********* ")
        #logging.info (RequestHeaders)
        
        for key in RequestHeaders:
            #logging.info("Procesando: " + str(key) + ":" + str(RequestHeaders[key]))

            value_index=-1

            try:
                #To find only admittable headers from request previously configured in config.cfg file.
                value_index = apiHeaders.index(key.lower())

            except:
                value_index = -1

            #If the header key was found, it will be considered after.
            if (value_index > -1 ):

                #logging.info("Incluido: " + str(key) + ":" + str(RequestHeaders[key]))

                headers[key] = RequestHeaders[key]

            if(key.upper()=="Content-Length".upper()):
                content_length = int(RequestHeaders[key])

    except Exception as e:
        logging.info(e)

        headers["Error"] = str(e)

    #logging.info (" ********* HEADERS AFTER obtainRequestHeaders ********* ")
    #logging.info (headers)

    return headers, content_length

def validationToken(headers,method,uri,body = None):

    validation = False

    outTypeProcessed = ""

    #print("uri: " + uri)

    try:

        for key in headers:

            if(key=="x-auth-token"):

                headersStr = json.dumps(headers)

                if (body == None):
                    bodyStr = "{}"
                else:
                    bodyStr = body.decode('utf8').replace("'", '"').replace("\t", "").replace("\n", "")
                    #bodyStr = body.decode('utf8').replace("'", '"')
                
                #print(type(str(method)))
                #print(type(str(uri)))
                #print(type(headersStr))
                #print(type(bodyStr))
                #print(type(str(headers[key])))

                #Validating token
                codeType, outType = getstatusoutput(["java","-jar","CapabilityEvaluator.jar",
                str(method),
                str(uri),
                headersStr, # "{}", #headers
                bodyStr,
                str(headers[key])])

                #print("outType: " + str(outType))

                outTypeProcessed = outType.decode('utf8').replace("'", '"').replace("CODE: ","").replace("\n", "")
                #outTypeProcessed = outType.decode('utf8').replace("'", '"').replace("CODE: ","")

                #print("outTypeProcessed: " + outTypeProcessed)

                if (outTypeProcessed=="AUTHORIZED"):
                    validation = True

                break


    except Exception as e:
        logging.info(e)

        headers["Error"] = str(e)

    logging.info ("Capability token validation - Result: " + str(validation) + " - Code: " + str(outTypeProcessed))

    return validation

def obtainResponseHeaders(ResponseHeaders):

    #logging.info (" ********* HEADERS BEFORE obtainResponseHeaders ********* ")
    #logging.info (ResponseHeaders)


    headers = dict()

    target_chunkedResponse = False

    try:
        for key in ResponseHeaders:
            #logging.info(str(key) + ":" + str(ResponseHeaders[key]))

            if(key.upper()=="Transfer-Encoding".upper() and ResponseHeaders[key].upper()=="chunked".upper()):
                target_chunkedResponse = True

            if(key.upper()!="Date".upper() and key.upper()!="Server".upper()):
                headers[key] = ResponseHeaders[key]
                
    except Exception as e:

        headers["Error"] = str(e)

    #logging.info (" ********* HEADERS AFTER obtainResponseHeaders ********* ")
    #logging.info (headers)

    return  headers, target_chunkedResponse

def loggingPEPRequest(req):
    logging.info("")
    #logging.info (" ********* PEP-REQUEST ********* ")
    #logging.info(req.address_string())
    #logging.info(req.date_time_string())
    #logging.info(req.path)
    #logging.info(req.protocol_version)
    #logging.info(req.raw_requestline)
    logging.info(" ******* PEP-REQUEST : " + req.address_string() + " - " + str(req.raw_requestline) + " ******* ")  

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_HandleError(self,method):
        message = UtilsPEP.obtainErrorResponseBody(APIVersion,method)
        code = UtilsPEP.obtainErrorResponseCode(APIVersion,method)
        self.send_response(code)

        errorHeaders,chunkedResponse = UtilsPEP.obtainErrorResponseHeaders(APIVersion,method,message)
        for key in errorHeaders:
            self.send_header(key, errorHeaders[key])
        self.end_headers() 
        data = json.dumps(message).encode()
        if(chunkedResponse):
            self.wfile.write(b"%X\r\n%s\r\n" % (len(data), data))
        else:
            self.wfile.write(data)

        self.close_connection

    def do_GET(self):

        target_chunkedResponse=False

        try:
            loggingPEPRequest(self)

            headers,content_length = obtainRequestHeaders(self.headers)

            try:
                #To find only admittable headers from request previously configured in config.cfg file.
                value_index = apiHeaders.index("Error")
            except:
                value_index = -1

            testSupported = UtilsPEP.validateNotSupportedMethodPath(APIVersion,"GET",self.path)

            if (value_index != -1 or testSupported == False ):
                logging.info("Error: " + str(headers["Error"]))
                SimpleHTTPRequestHandler.do_HandleError(self,"GET")

            else:

                validation = validationToken(headers,"GET",self.path)

                if (validation == False):
                    logging.info("Error: " + str(headers["Error"]))
                    SimpleHTTPRequestHandler.do_HandleError(self,"GET")

                else:
                
                    # We are sending this to the CB
                    result = CBConnection("GET", self.path, headers, None)

                    errorCBConnection = False
                    try:
                        if(result==-1):
                            errorCBConnection = True
                    except:
                        errorCBConnection = False

                    if(errorCBConnection):
                        SimpleHTTPRequestHandler.do_HandleError(self,"GET")

                    else:

                        # We send back the response to the client
                        self.send_response(result.code)

                        headersResponse, target_chunkedResponse = obtainResponseHeaders(result.headers)

                        #logging.info(" ******* Sending Headers back to client ******* ")
                        for key in headersResponse:
                            self.send_header(key, headersResponse[key])

                        self.end_headers()

                        #logging.info("Sending the Body back to client")

                        # Link to resolve Transfer-Encoding chunked cases
                        # https://docs.amazonaws.cn/en_us/polly/latest/dg/example-Python-server-code.html

                        while True:
                            data = result.read(chunk_size)
                    
                            if data is None or len(data) == 0:
                                break

                            if (target_chunkedResponse):
                                self.wfile.write(b"%X\r\n%s\r\n" % (len(data), data))
                            else:
                                self.wfile.write(data)

                        if (target_chunkedResponse):
                            self.wfile.flush()

                    self.close_connection

        except Exception as e:
            logging.info(str(e))

            SimpleHTTPRequestHandler.do_HandleError(self,"GET")

    def do_POST(self):
        target_chunkedResponse=False

        try:

            loggingPEPRequest(self)

            headers,content_length = obtainRequestHeaders(self.headers)

            try:
                #To find only admittable headers from request previously configured in config.cfg file.
                value_index = apiHeaders.index("Error")
            except:
                value_index = -1

            testSupported = UtilsPEP.validateNotSupportedMethodPath(APIVersion,"POST",self.path)

            if (value_index != -1 or testSupported == False):
                logging.info("Error: " + str(headers["Error"]))
                SimpleHTTPRequestHandler.do_HandleError(self,"POST")
                    
            else:

                #logging.info (" ********* OBTAIN BODY ********* ")
                # We get the body
                if (content_length>0):
                    #logging.info ("-------- self.rfile.read(content_length) -------")
                    post_body   = self.rfile.read(content_length)
                else:
                    #logging.info ("-------- Lanzo self.rfile.read() -------")
                    post_body   = self.rfile.read()

                #logging.info(post_body)

                validation = validationToken(headers,"POST",self.path,post_body)

                if (validation == False):
                    logging.info("Error: " + str(headers["Error"]))
                    SimpleHTTPRequestHandler.do_HandleError(self,"POST")

                else:

                    # We are sending this to the CB
                    result = CBConnection("POST", self.path,headers, post_body)

                    errorCBConnection = False
                    try:
                        if(result==-1):
                            errorCBConnection = True
                    except:
                        errorCBConnection = False

                    if(errorCBConnection):
                        SimpleHTTPRequestHandler.do_HandleError(self,"POST")

                    else:

                        # We send back the response to the client
                        self.send_response(result.code)

                        headersResponse, target_chunkedResponse = obtainResponseHeaders(result.headers)

                        #logging.info(" ******* Sending Headers back to client ******* ")
                        for key in headersResponse:
                            self.send_header(key, headersResponse[key])

                        self.end_headers()

                        #logging.info("Sending the Body back to client")

                        # Link to resolve Transfer-Encoding chunked cases
                        # https://docs.amazonaws.cn/en_us/polly/latest/dg/example-Python-server-code.html

                        while True:
                            data = result.read(chunk_size)
                    
                            if data is None or len(data) == 0:
                                break

                            if (target_chunkedResponse):
                                self.wfile.write(b"%X\r\n%s\r\n" % (len(data), data))
                            else:
                                self.wfile.write(data)
            
                        if (target_chunkedResponse):
                            self.wfile.flush()

                    self.close_connection

        except Exception as e:
            logging.info(str(e))
            
            SimpleHTTPRequestHandler.do_HandleError(self,"POST")

    def do_DELETE(self):
        target_chunkedResponse=False

        try:
            
            loggingPEPRequest(self)

            headers,content_length = obtainRequestHeaders(self.headers)

            try:
                #To find only admittable headers from request previously configured in config.cfg file.
                value_index = apiHeaders.index("Error")
            except:
                value_index = -1

            testSupported = UtilsPEP.validateNotSupportedMethodPath(APIVersion,"DELETE",self.path)

            if (value_index != -1 or testSupported == False):
                logging.info("Error: " + str(headers["Error"]))
                SimpleHTTPRequestHandler.do_HandleError(self,"DELETE")

            else:

                validation = validationToken(headers,"DELETE",self.path)

                if (validation == False):
                    logging.info("Error: " + str(headers["Error"]))
                    SimpleHTTPRequestHandler.do_HandleError(self,"DELETE")

                else:
                
                    # We are sending this to the CB
                    result = CBConnection("DELETE", self.path, headers, None)

                    errorCBConnection = False
                    try:
                        if(result==-1):
                            errorCBConnection = True
                    except:
                        errorCBConnection = False

                    if(errorCBConnection):
                        SimpleHTTPRequestHandler.do_HandleError(self,"DELETE")
                    else:        
                        # We send back the response to the client
                        self.send_response(result.code)

                        headersResponse, target_chunkedResponse = obtainResponseHeaders(result.headers)

                        #logging.info(" ******* Sending Headers back to client ******* ")
                        for key in headersResponse:
                            self.send_header(key, headersResponse[key])

                        self.end_headers()

                        #logging.info("Sending the Body back to client")

                        # Link to resolve Transfer-Encoding chunked cases
                        # https://docs.amazonaws.cn/en_us/polly/latest/dg/example-Python-server-code.html

                        while True:
                            data = result.read(chunk_size)
                    
                            if data is None or len(data) == 0:
                                break

                            if (target_chunkedResponse):
                                self.wfile.write(b"%X\r\n%s\r\n" % (len(data), data))
                            else:
                                self.wfile.write(data)
                
                        if (target_chunkedResponse):
                            self.wfile.flush()

                    self.close_connection

        except Exception as e:
            logging.info(str(e))

            SimpleHTTPRequestHandler.do_HandleError(self,"DELETE")

    def do_PATCH(self):
        target_chunkedResponse=False

        try:

            loggingPEPRequest(self)

            headers,content_length = obtainRequestHeaders(self.headers)

            try:
                #To find only admittable headers from request previously configured in config.cfg file.
                value_index = apiHeaders.index("Error")
            except:
                value_index = -1

            testSupported = UtilsPEP.validateNotSupportedMethodPath(APIVersion,"PATCH",self.path)

            if (value_index != -1 or testSupported == False):
                logging.info("Error: " + str(headers["Error"]))
                SimpleHTTPRequestHandler.do_HandleError(self,"PATCH")

            else:

                #logging.info (" ********* OBTAIN BODY ********* ")
                # We get the body
                if (content_length>0):
                    #logging.info ("-------- self.rfile.read(content_length) -------")
                    patch_body   = self.rfile.read(content_length)
                else:
                    #logging.info ("-------- Lanzo self.rfile.read() -------")
                    patch_body   = self.rfile.read()

                #logging.info(patch_body)

                validation = validationToken(headers,"PATCH",self.path,patch_body)

                if (validation == False):
                    logging.info("Error: " + str(headers["Error"]))
                    SimpleHTTPRequestHandler.do_HandleError(self,"PATCH")

                else:
                    # We are sending this to the CB
                    result = CBConnection("PATCH", self.path,headers, patch_body)

                    errorCBConnection = False
                    try:
                        if(result==-1):
                            errorCBConnection = True
                    except:
                        errorCBConnection = False

                    if(errorCBConnection):
                        SimpleHTTPRequestHandler.do_HandleError(self,"PATCH")

                    else:        
                        # We send back the response to the client
                        self.send_response(result.code)

                        headersResponse, target_chunkedResponse = obtainResponseHeaders(result.headers)

                        #logging.info(" ******* Sending Headers back to client ******* ")
                        for key in headersResponse:
                            self.send_header(key, headersResponse[key])

                        self.end_headers()

                        logging.info("Sending the Body back to client")

                        # Link to resolve Transfer-Encoding chunked cases
                        # https://docs.amazonaws.cn/en_us/polly/latest/dg/example-Python-server-code.html

                        while True:
                            data = result.read(chunk_size)
                    
                            if data is None or len(data) == 0:
                                break

                            if (target_chunkedResponse):
                                self.wfile.write(b"%X\r\n%s\r\n" % (len(data), data))
                            else:
                                self.wfile.write(data)
                
                        if (target_chunkedResponse):
                            self.wfile.flush()

                    self.close_connection

        except Exception as e:
            logging.info(str(e))
            SimpleHTTPRequestHandler.do_HandleError(self,"PATCH")

    #Actually not suppported
    def do_PUT(self):
        SimpleHTTPRequestHandler.do_HandleError(self,"PUT")

logPath="./"
fileName="out"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
    handlers=[
        logging.FileHandler("{0}/{1}.log".format(logPath, fileName)),
        logging.StreamHandler(sys.stdout)
    ])

httpd = HTTPServer( (pep_host, pep_port), SimpleHTTPRequestHandler )

httpd.socket = ssl.wrap_socket (httpd.socket,
        keyfile="certs/server-priv-rsa.pem",
        certfile='certs/server-public-cert.pem',
        server_side = True)

httpd.serve_forever()