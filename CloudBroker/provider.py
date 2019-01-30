from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
from pymongo import MongoClient
import sys
import json
import requests

provider_id = 0
URL_CB = 'https://sd-cloud-broker.herokuapp.com/'
#URL_CB = 'http://localhost:5000/'
vms = None

class Resource:

	def __init__(self, isFree, provider_id, vm_id, hd, ram, cpu, preco):
		self.isFree = isFree
		self.provider_id = provider_id
		self.vm_id = vm_id
		self.hd = hd
		self.ram = ram
		self.cpu = cpu
		self.preco = preco

class myHandler(BaseHTTPRequestHandler):

	def do_POST(self):
		
		content_length = int(self.headers['Content-Length']) 
		post_data = self.rfile.read(content_length)
		post_data = json.loads(post_data)

		if (post_data['type'] == 'request'):

			for v in post_data['vm_list']:

				result = vms.find_one({"vm_id": v, "provider_id": post_data["provider_id"]})
			
				if result['isFree'] == 1:
					vm = Resource(0, provider_id, result['vm_id'], result['hd'], result['ram'], result['cpu'], result['preco'])
					r = requests.post(URL_CB + 'providerUpdate', data=json.dumps(vm, default=lambda o: o.__dict__))
					print(r.text)
					vms.update_one({"vm_id": result['vm_id'], "provider_id": result['provider_id']}, {"$set": {"isFree":0}})
				else:
					self.send_response(204)					
				
			self.send_response(200)
			
		elif (post_data['type'] == 'free'):

			result = vms.find_one({"vm_id": post_data['vm_id'], "provider_id": post_data["provider_id"]})
			
			if result and result['isFree'] == 0:
				vm = Resource(1, provider_id, result['vm_id'], result['hd'], result['ram'], result['cpu'], result['preco'])
				r = requests.post(URL_CB + 'providerUpdate', data=json.dumps(vm, default=lambda o: o.__dict__))
				print(r.text)
				vms.update_one({"vm_id": result['vm_id']},{"$set": {"isFree": 1}})
				self.send_response(200)
			else:
				self.send_response(204)		
		else:
			self.send_response(202)
	
		
		self.send_header('Content-type', 'application/json')
		self.end_headers()
			

def main():

	global provider_id
	global vms

	provider_id = int(sys.argv[1])

	client = MongoClient('localhost', 27017)
	db = client['resources-db']
	coll_name = 'coll' + str(provider_id)
	vms = db[coll_name]

	if vms.count() != 0:    #Check if collection named 'posts' is empty
		vms.drop()    

	with open(coll_name + '.json') as f:
		data = json.load(f)

	vms.insert(data)
	
	result = vms.find()
	for i in range(result.count()):
		vm = Resource(result[i]['isFree'], provider_id, result[i]['vm_id'], result[i]['hd'], result[i]['ram'], result[i]['cpu'], result[i]['preco'])
		r = requests.post(URL_CB + 'providerAdd', data=json.dumps(vm, default=lambda o: o.__dict__))
		print("VM" + str(result[i]['vm_id']) + ": " + r.text)

	PORT_NUMBER = 8000 + provider_id

	try:
		server = HTTPServer(('', PORT_NUMBER), myHandler)
		print('Started httpserver on port ' + str(PORT_NUMBER))
		server.serve_forever()
	except: 
		print("error, shutting down the web server")
		server.socket.close()


if __name__ == "__main__": main()