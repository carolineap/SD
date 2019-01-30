from flask import Flask, jsonify, request
import json
from pymongo import MongoClient
import os

RESOURCES = []

app = Flask(__name__)

class VirtualMachine:

	def __init__(self, isFree, provider_id, vm_id, hd, ram, cpu, preco):
		self.isFree = isFree
		self.provider_id = provider_id
		self.vm_id = vm_id
		self.hd = hd
		self.ram = ram
		self.cpu = cpu
		self.preco = float(preco)

@app.route('/')
def cloudBroker():
	return jsonify({"message": "Cloud Broker 2018!"})

@app.route('/providerAdd', methods=["POST"])
def providerAdd():
	
	if (request.method == 'POST'):
		try:
			content = request.get_json(force=True)
			newVM = VirtualMachine(content['isFree'], content['provider_id'], content['vm_id'], content['hd'], content['ram'], content['cpu'], content['preco'])
			RESOURCES.append(newVM)
			RESOURCES.sort(key=lambda newVM: newVM.preco)
		except:
			return 'Fail'

	return 'Success'

@app.route('/providerUpdate', methods=["POST"])
def providerUpdate():
	
	if (request.method == 'POST'):
		try:
			flag = False
			content = request.get_json(force=True)
			for r in RESOURCES:
				if r.provider_id == content['provider_id'] and r.vm_id == content['vm_id']:
					RESOURCES.pop(RESOURCES.index(r))
					flag = True
			if (flag == False):
				return 'This machine does not exist in cloud broker'
			updateVM = VirtualMachine(content['isFree'], content['provider_id'], content['vm_id'], content['hd'], content['ram'], content['cpu'], content['preco'])
			RESOURCES.append(updateVM)
			RESOURCES.sort(key=lambda updateVM: updateVM.preco)
		except:
			return 'Fail'

	return 'Success'

@app.route('/clientRequest', methods=["POST"])	
def clientRequest():
	
	if (request.method == 'POST'):
		try:
			content = request.get_json(force=True)
			hd = content['hd']
			ram = content['ram']
			cpu = content['cpu']

			for vm in RESOURCES:
				if vm.hd >= hd and vm.ram >= ram and vm.cpu and vm.isFree == 1:
					return json.dumps({'provider_id': vm.provider_id, 'vm_id': vm.vm_id})
		except:
			return 'Fail'

	return 'Successs'


if __name__ == "__main__":
	port = int(os.environ.get("PORT", 5000))
	app.run(host='0.0.0.0', port=port)