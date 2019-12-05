# Test files introduction (python)
The next files are full examples of authentication, authorisation and access to MRD througth PEP.
- Test.py: Sends a GET request with type=http://example.org/vehicle/Vehicle.
- TestPOST.py: Sends a POST request of "urn:ngsi-ld:Vehicle:99" entity.
- TestGET.py: Sends a GET request of "urn:ngsi-ld:Vehicle:99" entity.
- TestPATCH.py: Sends a PATCH request to "urn:ngsi-ld:Vehicle:99" entity.
- TestDELETE.py: Sends a DELETE request to "urn:ngsi-ld:Vehicle:99" entity.

# Launch test files
To launch test files you can execute the next command:

```sh
python3 <file.py>
```