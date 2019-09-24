import re

patternGET=['^/v2/entities/[a-z,:,0-9]+']
patternPOST=['^/v2/entities$']
patternPATCH=['^/v2/entities/.*/attrs$']
patternDELETE=['^/v2/entities/.*$']

if __name__ == '__main__':

    patternRequestMethod = []
    method='GET'
    resource='/v2/entities/asd212:as/asdasd'

    if (method.upper()=='GET'.upper()):
        patternRequestMethod = patternGET
    elif (method.upper()=='POST'.upper()):
        patternRequestMethod = patternPOST
    elif (method.upper()=='PATCH'.upper()):
        patternRequestMethod = patternPATCH
    elif (method.upper()=='DELETE'.upper()):
        patternRequestMethod = patternDELETE

    if(len(patternRequestMethod)>0):

        test=False
        for m in range(len(patternRequestMethod)):
            print(re.match(patternRequestMethod[m],resource))
            if(re.match(patternRequestMethod[m],resource)):
                test=True
                print("Search successful.")
                break

        if(test==False):
            print("Search unsuccessful.")	

    else:
        print("Method is not supported.")