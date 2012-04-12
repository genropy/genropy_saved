from suds.client import Client
hello_client = Client('http://127.0.0.1:8086/test15/soap/provisioning/?wsdl')
l=[]
for i in range(10):
	l.append(dict(
		name = 'N%i'%i,
    	type = 'T%i'%i,
    	key = 'K%i'%i,
    	password = 'P%i'%i,
    	nullable = 'Nu%i'%i,
    	values = 'V%i'%i)
	)
result = hello_client.service.create(l)
print result
