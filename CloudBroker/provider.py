import sys
import json
import requests

vm_id = 0

URL_CB = 'http://localhost:5000/'


class Resource:

	def __init__(self, provider_id, vm_id, hd, ram, cpu, preco):
		self.provider_id = provider_id
		self.vm_id = vm_id
		self.hd = hd
		self.ram = ram
		self.cpu = cpu
		self.preco = preco

def main():

	global vm_id

	provider_id = int(sys.argv[1])

	while True:

		op = int(input("Digite a opção desejada: \n"))

		if op == 1:
			
			print("Adicionar nova máquina virtual\n")			
			# cpu = int(input("Insira a quantidade de vCPUs desejada: "))
			# ram = int(input("Insira a quantidade de memória RAM desejada: "))
			# hd = int(input("Insira a quantidade de memória de disco (HD) desejada: "))
			# preco = float(input("Insira o preço: "))

			cpu = ram = hd = preco = 1

			vm = Resource(provider_id, vm_id, hd, ram, cpu, preco)
			
			#print(json.dumps(vm, default=lambda o: o.__dict__))
			#try:
			headers = {'Content-Type':'application/json'}
			r = requests.get(URL_CB + 'add', data=json.dumps(vm, default=lambda o: o.__dict__))
			#except:
			#print("OH MY GOD")

			vm_id += 1

		elif op == 2:
			print("Deletar uma máquina virtual\n")		
			id = input("Insira o id da máquina virtual que deseja deletar\n")	
		elif op == 3:
			pass
		elif op == 4:
			pass

if __name__ == "__main__": main()











