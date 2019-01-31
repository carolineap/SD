from flask import Flask, jsonify, request
import json
from pymongo import MongoClient
import os

providers = [ [], [], [], []]

app = Flask(__name__)

class VirtualMachine:

	def __init__(self, isFree, provider_id, vm_id, hd, ram, cpu, preco):
		self.isFree = isFree
		self.provider_id = provider_id
		self.vm_id = vm_id
		self.hd = hd
		self.ram = ram
		self.cpu = cpu
		self.preco = preco

@app.route('/')
def cloudBroker():
	return jsonify({"message": "Cloud Broker 2018!"})

@app.route('/providerAdd', methods=["POST"])
def providerAdd():
	
	if (request.method == 'POST'):
		try:
			content = request.get_json(force=True)
			pid = content['provider_id'] - 1
			newVM = VirtualMachine(content['isFree'], content['provider_id'], content['vm_id'], content['hd'], content['ram'], content['cpu'], content['preco'])
			providers[pid].append(newVM)
			providers[pid].sort(key=lambda updateVM: newVM.preco)
		except:
			return 'Fail'

	return 'Success'

@app.route('/providerUpdate', methods=["POST"])
def providerUpdate():
	
	if (request.method == 'POST'):
		try:
			content = request.get_json(force=True)
			pid = content['provider_id'] - 1
			for r in providers[pid]:
				if r.vm_id == content['vm_id']:
					providers[pid].pop(providers[pid].index(r))
			updateVM = VirtualMachine(content['isFree'], content['provider_id'], content['vm_id'], content['hd'], content['ram'], content['cpu'], content['preco'])
			providers[pid].append(updateVM)		
			providers[pid].sort(key=lambda updateVM: updateVM.preco)	
		except:
			return 'Fail'

	return 'Success'

@app.route('/clientRequest', methods=["POST"])	
def clientRequest():
	
	if (request.method == 'POST'):

		content = request.get_json(force=True)

		minPrice = -1
		provider_id = -1
		vm_list = []


		for provider in providers: #para cada provedor

			total = 0
			i = 0
			aux = []

			for resource in content: #para cada recurso desejado

				cpu = resource['cpu']
				ram = resource['ram']
				hd = resource['hd']

				for vm in provider: #vejo preço pra aquele provedor

					if vm.cpu >= cpu and vm.ram >= ram  and vm.hd >= hd and vm.isFree == 1 and vm.vm_id not in aux:
						total += vm.preco
						aux.append(vm.vm_id)
						break

			if total > 0 and (minPrice == -1 or minPrice > total):
				minPrice = total
				provider_id = providers.index(provider)+1
				vm_list = aux

		if minPrice > -1:
			return json.dumps({'provider_id': provider_id, 'vm_list': vm_list, 'preco_total': minPrice})


	return 'Fail'


if __name__ == "__main__":
	port = int(os.environ.get("PORT", 5000))
	app.run(host='0.0.0.0', port=port)