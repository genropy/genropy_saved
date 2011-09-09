from suds.client import Client
hello_client = Client('http://127.0.0.1:8087/soap/soap/?wsdl')
result = hello_client.service.test("Pippo", "Pluto")
print result
