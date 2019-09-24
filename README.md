# Introduction

This project is a PEP-Proxy which is designed to supports different APIs. When PEP-Proxy receives a request, this component validates and handles the request before send it to the corresponding target (as to a Context Broker API).

This project contains:

- PEP-Proxy source files & folders.

    - PEP-Proxy.py: Run PEP-Proxy component.
    - config.cfg file: Contain the configuration of PEP-Proxy component.
    - UtilsPEP.py: Handle several requests receives by PEP-Proxy sending it to the corresponding API functionality.
    - API folder: Contain one file per specific API. Each one has the functionality to validate and cypher the request body.

- PEP-Proxy folder to ssl.

    - certs folder: Contains the certificates needed to ssl.

- PEP-Proxy files & folder to cypher.
    - conf_files folder: Contain key files.
    - cpabe_cipher.jar file: It is a Java application to cypher text with cp-abe.
    - cpabe_decipher.jar file: It is a Java application to decipher text with cp-abe.

- PEP-Proxy files to deploy.

    - Dockerfile file: Contain the actions and commands to create the Docker image needed to run de PEP-Proxy component.
    - requirements.txt: Contain the auxiliar python modules needed by the application. Dockerfile uses it.
    - build.sh file: To create the PEP-Proxy Docker image using Dockerfile.
    - docker-compose.yml file: To deploy PEP-Proxy container.

# Configuration config.cfg file

Before launching the PEP-Proxy, it's necessary to review the config.cfg file:

```sh
cd projectPath / PEP-Proxy
vi config.cfg
```

- Params to PEP-Proxy's endpoint.

    - pep_host: No change admittable (always 0.0.0.0)
    - pep_port: If change this param, it's necessary to review Dockerfile and docker-compose.yml files. By default 1027.

- Params to the target's endpoint.

    - target_host: Context Broker host.
    - target_port: Context Broker port.
    - allApiHeaders: Define the admittable headers to send to target API. If a header of the request receives by PEP-Proxy is not included in this param, the final API request will not consider it. This param store all the headers of each API supported by PEP-Proxy. It's necessary to define an element for each API supported. **IMPORTANT:** It's necessary to use lower case.
    - chunk_size: To read the response received after the API request. Default 1024

- Params to cipher attributes.

    - allSeparatorPathAttributeEncriptation: Specify the separator used by relativePathAttributeEncriptation param to build a relative path into the attributes. This relative path is necessary to determine if an attribute requires cypher or no. Use a pattern never used by attributes or keywords. This param store a separator of each API supported by PEP-Proxy. It's necessary to define an element for each API supported.
    - relativePathAttributeEncriptation: This parameter is a tridimensional array. To understand it, we are going to use the next examples:

        1. **ONLY ONE CONDITION** - In this case, the system searches into each the attribute first a key named "metadata", and after, into it, a key named "cpabe-policy". If it is successful, the attribute will cypher.
        
        - Example (NGSIv2): 
        ```
        relativePathAttributeEncriptation=[[["metadata/cpabe-policy",""]]]
        ```

        **NOTE:** If the second element of the array is defined, the system also will verify if the value is the same as the relative path value. If it is also successful, the attribute will cypher.
        
        - Example (NGSIv1), the analog of previous NGSIv2 example: 
        ```
        relativePathAttributeEncriptation=[[["metadatas/name","cpabe-policy"]]]
        ```
        
        2. **TWO CONDITIONS AND MORE (AND)** -  In this case, the second condition must also be satisfied. It is an "and" condition. If both conditions are successful, the attribute will cypher.

        - Example (NGSIv1): 
        ```
        relativePathAttributeEncriptation=[[["metadatas/name","cpabe-policy"],["metadatas/type","policy"]]]
        ```

        3. **TWO CONDITIONS AND MORE (OR)** - In this case, if one of the conditions is successful, the attribute will cypher. It is an "or" condition.

        - Example (NGSIv1):
        ```
        relativePathAttributeEncriptation=[[["metadatas/name","cpabe-policy"]],
                                  [["metadatas/name","other-policy"]]
                                 ]
        ```                                 
        **NOTE:** Mixed cases are supported.

        **IMPORTANT:** This param is case sensitive.

        **IMPORTANT:** Before update this param see "Proxy PEP - updating relativePathAttributeEncriptation param" section.

    - noEncryptedKeys: It is a list of first-level attribute keys that never will be cyphered. **IMPORTANT:** It's necessary to use lower case. Default ["id","type","@context"].

# Prerequisites

To run this project is neccessary to install the docker-compose tool.

https://docs.docker.com/compose/install/


# Installation / Execution.

After the review of config.cfg file, we are going to obtain then PEP-Proxy Docker image. To do this, you have to build a local one, thus:

```sh
cd projectPath / PEP-Proxy
./build.sh
```

The build.sh file contains docker build -t iotcrawler/pep-proxy ./ command.

Finally, to launch the connector image, we use the next command:

```sh
cd projectPath / PEP-Proxy
docker-compose up -d
```

# Monitoring.

- To test if the connector is running:

```sh
docker ps -as
```

The system must return that the status of the PEP-Proxy container is up.

- To show the PEP-Proxy container logs.

```sh
docker-compose logs pepproxy
```

# PEP-Proxy functionality.

When PEP-Proxy receives a request, PEP-Proxy first obtain its action or method to process it with the corresponding functionality. At the moment the actions/methods are supported by PEP-Proxy art.
* GET.
* POST.
* PATCH.
* DELETE.

After, PEP-Proxy recovers the request body, if it exists, and finally cypher it if it is necessary.

PEP-Proxy supports the NGSIv1, NGSIv2 and NGSILD APIs. If it may be necessary to support new APIs, see the "Proxy PEP - supporting new API" section.

PEP-Proxy supports cp-abe cipher method. If it may be necessary to support new cipher methods, see the "Proxy PEP - supporting new cypher" section.

Only NGSIv2 and NGSILD APIs support cp-abe cipher method. 

To increase supported API actions/methods or paths you must review PEP-Proxy files. It's not be a problem if you don't need use cipher methods. If it may be necessary to support new actions/methods or paths that use cipher, see the "Proxy PEP - supporting new actions/path with cypher" section.

# Proxy PEP - supporting new API.

To support new APIs, follow the next steps:

1. Add API to config.cfg file.
    - APIVersion: Define a value to the new API and include it also into the param comments.
    - allApiHeaders: Define a new element for the API with the possible headers.
    - allSeparatorPathAttributeEncriptation: Define a new element for the API with the value.
    - relativePathAttributeEncriptation: TODO
    - noEncryptedKeys: TODO

2. Add a new file into API folder named "Utils{APIVersion}.py" using for it another existing file (copy).

3. Update UtilsPEP.py to import the new file and add a new case in each if statement.

4. Update API/"Utils{APIVersion}.py" file to add the corresponding functionality for the API.

5. Review/update al coments included in previous 4 points and update the README.md file


# Proxy PEP - supporting new cypher.

To support new cypher, follow the next steps:

1. Add attribute cypher condition to relativePathAttributeEncriptation param (config.cfg file).

2. Update all files of API folder to support the cypher. Exactly you need to review the "cipherBodyAttributes" function and add a new else: if(condition): statement into the for. The condition must validate the corresponding condition established in relativePathAttributeEncriptation param. Finally, include into the if block the code to cypher.


# Proxy PEP - updating relativePathAttributeEncriptation param (config.cfg).

The conditions established in this param determinate if an attribute must be cyphered. The cypher process validates the same conditions before to cypher the attribute. For this reason, if we update relativePathAttributeEncriptation param we must update the code, exactly, the "cipherBodyAttributes" functions into the API folder files.


# Proxy PEP - supporting new actions/path with cypher.

To support it you must review:

1) Edit UtilsPEP.py file and update the encryptProcess function.
2) Edit the file into API folder corresponding with the API and update/review processBody function.

**IMPORTANT:** If request body hasn't the same format as (processCypher example comments), you need build new functions because you can't use processCypher functionality.

# PEP-Proxy and CP-ABE cipher method:

At the moment, NGSIv2 and NGSILD APIs support cp-abe cipher method. 

Example CPABE cipher:
```
java -jar cpabe_cipher.jar "att1 att2 2of2" "hola"

```

We are going to see and example of each supported API to explain this:

* NGSIv2.

    - Defaul config.cfg configuration.
        
        ```
        ...
        APIVersion=NGSIv2
        ...
        relativePathAttributeEncriptation=[[["metadata/encrypt_cpabe/type","policy"]]]
        noEncryptedKeys=["id","type","@context"]
        ```


    - Format to detect an attribute must be cyphered.
        ```
        "attrName": {
            "value": attrValue,
            "type": attrType,
            "metadata": {
            "encrypt_cpabe":{
                "type":"policy",
                "value":policyValue
            }
            }
        }
        ```

    - How cypher an attribute with an example. 
        - Before cypher process.

            ```
            "temperature": {
                "type": "Float",
                "value": 23,
                "metadata": {
                "encrypt_cpabe":{
                    "type":"policy",
                    "value":"att1 att2 2of2"
                }
                }
            }
            ```

        - After cypher process. 
        
            1. temperature["type"]: "cyphertext".
            2. temperature["value"]: java -jar cpabe_cipher.jar "att1 att2 2of2" "23"
            3. temperature["metadata"]["encrypt_cpabe"]["value"]: java -jar cpabe_cipher.jar "att1 att2 2of2" "Float"


            ```
            "temperature": {
                "type": "cyphertext",
                "value": "eyJ2YTAvZ3NWMHV2SktLUi9UeFk4Mk13PT0iOiJBQUFBZ0NxK2MycjhMUjMzM1d4SEZwdWVlWGQ5dDdURUdZUXJLUVJuWUFvR2dDQ2NyU09oeXlDdzN0M2kydXo1QlhFcmFWK0Q2T3V0NHFqVVdRcnhabC9pRy94U1VjMldQN3lCSm0weHdPNzk4Y3VjTkJhUGZxeWd1bXlreFJRN254ZWRpaGxPUGphTE85cXZKVzJRRGhYMTdXVXZqT2IxZ0VRRjJ3WGNNMDdlZnhBY0FBQUFnSW80b3hhNEs1WVdGOVk4emQ5Wkg1ZmVUY25JR1l0QmphKysvUnZZVG96ZmFSVHFlQlBMbDdvZVlneGJtd3VpWjVabEZ6WXlkWEdkWkRtb0xjdDIvT1NkSFhiK0hoZzVJMW1pc1Z5UkdaRVlIc3FtcXhLVVlBVmg3aUlvS3lhcXBKYVB3MVR4QWdXMkYwdHBxbWYwSEx5L0dzU3hrU1VuQWFvVmhzRUY2ckRHQUFBQUFnQUFBQUlBQUFBQkFBQUFBQUFBQUFSaGRIUXhBQUFBZ0tZc280aHkxcDhsRlArNGNXUEVrTFRRUERVblhHZVR4OTB5VkhtSmZtQTRoWlJaWlJwZXIzNzYyOUU4Zy8zVkFLZTI3TmxkOTAzdGIyOGp3cXg5SCtDaDJibmNEQTh2T3JEYnlzaEJVcEVJVHZvZGIxa1pFSjdJOE5rUWxUZ1c3c1BIRjhPVTUvVjVyTDRrMXdVQSttSVhHbXhQUFpQQW5KMnVDckpXSFB0eEFBQUFnRGhRVGQ4ZlA0SnJCdldvS1dBc1BXUWZsUVNPZlNYQmZWS2RrR1dNeVlONkFnby9BK1VPT1dIb29lSnFuZDVtMC94bDNGYTdtSGVqWEw1SnlRM0hXbWxzQVV4dlZyczBrT1ZwR2NDSGd3WGF4ODNVOU9qaVFjdTVoamJmVjRGak84Yy9nWlV4U0xKNTBOUzF1U2dzeFZFaXhTcFYxWkRhZkNNZXBwY3lWelVGQUFBQUFRQUFBQUFBQUFBRVlYUjBNZ0FBQUlCOTlJQ1Z5eWFrSldTaW9TN0VHMHpNUTZ0QzlUYll1c0FjMlIxT0VGQktyeUtHZWNicUNyRnRUKzhENXpEeE0zV3dYMlV2TE5qOTB5Zk9qZzFGakljRE1yUlllcU4xS2pQU3RBZEhpeFFHMEdNaEcyYVZwbjgvYzJpUUhqS1JuR0h4ZXFTaCtKUjZSOGVmWXhaOHhNay8rMDdpSDhRVWdkbnRwalNGTE13TURBQUFBSUFCVHUyU1NGLzI2VWxuSzRnbGE3SEZwdUFkQ0UzS0VQSmtBRCs0SjQwbWlXK2hCT2xGazdUQ2pnSDhGVHY3Vkl2WHlNMFgvRE9pc3J5cVN2UFhXZ3hGRHVNZTVVaWdCN29xQkdtcG9pdFlQZmhLQkRyeWN1SGVwYm4xZXhaRjlnb2M3cTQ2REdtOUVHUlIzcWZSYmFKcGlLK2ZEazNUekRsUEFXK21FOWpGZnc9PSJ9",
                "metadata": {
                    "encrypt_cpabe": {
                        "type": "policy",
                        "value": "eyJPWjNBWC9HRU8yTGtZZ0NBU0EvM3lRPT0iOiJBQUFBZ0lVbTRLRlpDakNZSWpmL2kySVpDdUx2WENkdkhxcG1lNGpPeHQwRFlmSnB0cGl4SWRaTGJ5Q2ozQzdtZjl0Z2FERm92TnJmcmFYSzhOeThDWUVCbzh0NHBXT3R6N0R4ZUZkd2RpSkVkTGdOdkxEbzhKMDhRZ3JMM1lxSEcySUJuQjhDNU11eDdiZzEwTkhJU3R6WCtIaHFGV0dNb25xVHpZTThnakU5R3R3ZEFBQUFnSVk0NGo3ZHZaNkFOSWhJTGdMelZ2bE5iQ3FSbk9PVlJhR2tVdmlEVlA0cVNDeWE5V1ZBbEhsbm1XSmgwbm5hUndUODFvQndiRUR1SkNpbko4NDBnajJDQm5vSktwK3U2NjF4MjVEL0c3TzNPN0Q3UkRTS1FmTjRhTWVOOWc3a1k0NmFCY3pNd29kZnY2b2FmOS9SOXkrWjZSa3IzNzFVK2dhSUFSMVFaUVBTQUFBQUFnQUFBQUlBQUFBQkFBQUFBQUFBQUFSaGRIUXhBQUFBZ0J4QjFjWktWSURzRFZqOExmRnEwazNMcXVXcS9IV1daWFBDK1d3UE04cjRGemtMNVNNVWhFTWROZ1AwQm5FTnhCcllvbHlBMnVmWG9EbGJHK3RxL0J3Q05lNUpSWkQybTVGaDd6aFhONTNrT3pyUXpLaERTR1BNZXp3bDhNZENOcmtyU1FxUmxkdFJlVkFpNXVoN0tMK3VkTUxaUmJEeHQzUjFTNmQrRnRaNkFBQUFnQjU2YXRQclU3SjV6WVJoNUYvVWNPSkg4TDJUcExndnhCa1IxTmlhVUo4ajBjVTBGQ09EaVEvYlo4VzFMbldKck5TMEFPL3pHN0c1RjlJM1c2YktQYWhRYWRwbGFyTkcxZmgzMTVmeDRlZTZaRitxUTBQd0l2cUM5K2VrQTRPN3JNR2Fyb2NHaHQxNXdEUUI4QmkzSHRXZ2k2SERhd2NLUmhQQ004S1dZeW16QUFBQUFRQUFBQUFBQUFBRVlYUjBNZ0FBQUlBL05kOXgwQVNCbXBOTk8yaFZITkdrV3hLWU9YN2dkT3l6T0xNY1lBRXUweUZFTUgrbldqSTVFQWZQT0F1bjNLWDhOVERQMG9ua2tuYytGakFudHRraUkrYXlkUURncWRkMFR0TnFyV29MNjlSVEhLV3kya0RTR1JvajJmVmIxcDYrcUVaYzliWXRsVGdaaXY2eVpaZXJhTGxVNURtNlN1YzVaczZkR0dzNnJnQUFBSUJiR2Zrc1ZyTE0vZHBzWkJIZXJ3VFhZd1RwdG1FdE16bzIzZ2tGYXcrczNoejJiN2E1TGg5UWlMaGpLSDVOUUY4ZWZVdTdMbDJBdmdNOGd2YmhWWmluWDRYdlVrbk5LSXpnbFdpZ2lKZEJVUWp0NjJ3Z3poVDluOVlXcnhGd0tydHRvUXJCakZvQXNhZlMwV2dDZzJrYTltc0psbVlXNW9HRU9DV1ZHb09POUE9PSJ9"
                    }
                }
            }
            ```

* NGSILD.

TODO
Tomar como referencia las indicaciones para NGSIv2....


# PEP-Proxy and CP-ABE decipher method:

Example CPABE decipher:
```
java -jar cpabe_decipher.jar "eyJWRTVwRkp6aktVUmp5dGZpS0U2eWZ3PT0iOiJBQUFBZ0FINjJFRUNzUVdyenNTWTNqeXViM1JRQzdwZHBpQnlMN2JEWXhEMkNnUEJYUEVZb3R5dTM5ZUxQSUlzTUxFZ1RhWFYxWFd1Qk40bFRPYndsY2lUWFhZbG1DdXh0Z2hYTFl1Vy9LdkFjTUNZR2Ywb2xGdnNjNjBlei9PZ0lFMlIxeU0vVWx2RVNVWFozMUhwOUJJWXZxNWYza3JLTjZKNnVncjdaaEFSdllwMEFBQUFnSDNKY2JWYXBxQnF1TXJqYU1admx0MHQxcUVITXgyUkdaejNMdCtQdWJnTHNaVmptQ3V4K2g2Vld4b1NwdVNJYmovZmtWMi91R1ZaUGlyalphVGdLOEFDaTdQeDBlSkx5Sy8zYmVLeUtBV3Y1ZGdNZzJhUWUxeWh4bHVLSmEwblBwTTEvVHIzZlBPSGk3SVJqeFJVTjJvN2hlQVFTQnB5UHRkMjVPWGY5TVczQUFBQUFnQUFBQUlBQUFBQkFBQUFBQUFBQUFSaGRIUXhBQUFBZ0V0MW5VTnQ1OXJodlpHTGRIZDVkMnArdmxTNldPUjhHeFNBUmgydTJMUXhzV2JraHJzZU40c2R6ZmVvOWZKMTk4SHJQWHZ3L3hPSnBBQitKWEl1UTlObEQ0eWJ5VjU5NnJleUlibXVWeFBxdzNlZ01KeUtOREdNZVNtd0ZhN09CN0RrcmVCYzIvd1MwV0JEdTdVSzFSOGlSeDM4WnZxMGJHMzgvTG1NVDJ3bUFBQUFnQ3BoT1NWQjgySHpLdTlnblB6ZmpnZmxQb293T2pJVzR4SmYwNGhlaVZLc01VSUowYzBvWkUxQk5tb3E1OWJORjJEak9Ncm50OTlXbWVvYlhyV3Q1S2Rid1ZMTmhIOStOQS9oa0JreTZZUUs0TitCeEtyVW9SRjc2NG5HQkVST1EyUWVwaXpVS3BwTTZYVmh0ZXVHUExyVVJldGNmc0QzODZWVWFqZkxVMVYrQUFBQUFRQUFBQUFBQUFBRVlYUjBNZ0FBQUlDQVROYldTM2hFK2ZtRVpDeTIwZS9RVEdPK3JTVVNTYktaSStyZ3g0cUNMOXBGMmM2RElVQlJWYjB6MkJhMUNEbE1FcENHQ0hMRkhuMnJVVFZCZEZTNWs4aUl3bGJ0NGVLdStOYnAyVXZJRnJrb00rQ3BVempZZDBZWUh1OGNWYUMwVncvQ29UZnFjcEhuWGRHU0taeGUrNG5WcmVXNHBUa3gwTTdkNWNyNE9RQUFBSUIwUitiR2Nrd3RleEpqdVliVVk5RkVGQkRIcHlRMWRlVEdPSEtLZll5c05xelBxR0xKekJGZEM4WVBrY3kxSThvNkt4VTgzczVXN1dCbmtxTStiZUJSVGtncnE1dWdqTmZxcDRFRWJFQldZZGpUS2lITlZIZFNTUXhrVWgxWllwY3UzVkhHT2YwVkVHYjR3Zm5vSVZnUGVVQUdjQnhvTktnNUNOVnlrNGJpWFE9PSJ9"
```

If we decipher the previous example, only the policy value can't recovered from the original body.





# Resume and other considerations and limitations in PEP-Proxy.

- Supported APIs: NGSIv1, NGSIv2, NGSILD

- Cipher:
    - Supported cipher method: cp-abe
    - Supported APIs uses cipher method (cp-abe): NGSIv2, NGSILDv1
    - No supported cipher for "id", "type" or "@context" first-level keys.

- If update relativePathAttributeEncriptation param, PEP-Proxy code must be update, see "Proxy PEP - updating relativePathAttributeEncriptation param" section

- To cypher all entity attributes we can do it if defining one condition that all attributes satisfy, for example, all attributes include a key named "type" or "value", before do it see also "Proxy PEP - updating relativePathAttributeEncriptation param" section: 

    ```
    relativePathAttributeEncriptation=[[["type",""]]]
    ```

- No supported actions:
    - POST /v2/op/update (NGSIv2). Insecure process because it allows actions like DELETE, we haven't an explicit control about the real actions (APPEND_STRICT, UPDATE, DELETE, REPLACE).
    - PUT. Not necessary, no JSON body, cypher difficulty.

- PEP-Proxy errors or validations return a simulated fixed response from API. At the moment some headers are missed comparing with the original API response (Connection, Content-Length), because they create errors.

TODO





# TODO:

- (incluir en el resumen) ¿Qué pasa si queremos sobreescribir el dato encriptado con un valor y no viene el metadato de encriptación? ¿se podria hacer? ¿como se controlaría? ¿el metadato se puede borrar del CB?
    - NGSIv1 --> Hacer prueba e indicar que pasaría aunque actualmente no esté soportado.
    - NGSIv2 --> Hacer prueba e indicar que pasaría.
    - NGSILDv1 --> Hacer prueba e indicar que pasaría.

PDTE_JUAN: incluir algo al respecto de la validación.

Tener lo mismo que he hecho para "allApiHeaders" y "allSeparatorPathAttributeEncriptation", pero en este caso para los parámetros "relativePathAttributeEncriptation" y "noEncryptedKeys" -Revisar la aparición de los paŕamtros en todos lados para actualizar tambíen las anotaciones...

BUSCAR TODO y PDTE_JUAN por si hubiera algo anotado y que se hubiese pasado actualizar o contemplar....


# DOUBTS

* ¿Qué pasa si queremos buscar fintrando por attributo encriptado?
* ¿se tienen que encriptar los metadatos?









