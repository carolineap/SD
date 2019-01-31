import sys
import json
import requests

URL_CB = 'https://sd-cloud-broker.herokuapp.com'
#URL_CB = 'http://localhost:5000'

using_vm = []

class Resource:

	def __init__(self, hd, ram, cpu):
		self.hd = hd
		self.ram = ram
		self.cpu = cpu

def main():

	global using_vm
	
	print("Menu de opções:\n0 - Imprimir recursos sendo utilizados\n1 - Busca por recursos\n2 - Liberar recurso")
	print("Insira uma das opções: ")

	while True:
		
		opcao = int(input())
		
		if opcao == 0:
			
			print("Recursos utilizados: [ID/PROVEDOR]")	
			print(using_vm)

		elif opcao == 1:

			print("Buscar por nova máquina virtual")     

			qtd = int(input("Insira a quantidade de recursos desejados: "))

			resources = []

			while qtd:
				
				cpu = int(input("Insira a quantidade de vCPUs desejada: "))
				ram = int(input("Insira a quantidade de memória RAM desejada: "))
				hd = int(input("Insira a quantidade de memória de disco (HD) desejada: "))
				
				qtd -= 1
				resources.append(Resource(hd, ram, cpu))

			r = requests.post(URL_CB + '/clientRequest', data=json.dumps(resources, default=lambda o: o.__dict__))

			if r.text != 'Fail':
				
				content = json.loads(r.text)
				
				pid = content['provider_id']

				resp = input("Encontrado provedor " + str(pid) + " que fornece os recursos com valor total de R$ " + str(content['preco_total']) + ". Deseja utilizar [S/N]? ")

				if resp == 'S' or resp == 's':
				
					print("Requisitando pelas máquinas:")
					print(content['vm_list'])

					r = requests.post("http://localhost:" + str(8000 + int(pid)), data=json.dumps({'type': 'request', 'vm_list': content['vm_list'], 'provider_id': int(pid)}))

					print(r.status_code)

					if r.status_code == 200:
						print("Utilizando recursos do provedor " + str(content['provider_id']))
						for vm in content['vm_list']:
							using_vm.append(str(vm) + "/" + str(content['provider_id']))
					else:
						print("Erro na requisição ao provedor!")
			else:
				print("Não há recurso que satisfaça esses requisitos!\n")
				

		elif opcao == 2:
			
			vm_id = input("Insira [ID/PROVEDOR] da VM que deseja liberar:\n")

			if vm_id not in using_vm:
				print("Esse recurso não está sendo utilizado\n")
			else:
				r = requests.post("http://localhost:" + str(8000 + int(content['provider_id'])), data=json.dumps({'type': 'free', 'vm_id': int(vm_id.split('/')[0]), 'provider_id': int(vm_id.split('/')[1])}))
				
				if r.status_code == 200:
					print("Recurso liberado!")
					using_vm.pop(using_vm.index(vm_id))
				else:
					print("Erro na liberação do recurso!")
		else:
			print("Opção inválida!")            



if __name__ == "__main__": main()