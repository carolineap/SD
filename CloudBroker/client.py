import sys
import json
import requests

URL_CB = 'http://localhost:5000/'

using_vm = []



def main():

    global using_vm

    while True:
        print("Menu de opções:\n0 - Sair do programa\n1 - Busca por recursos\n2 - Liberar recurso")
        print("Insira uma das opções: ")
        opcao = int(input())
        if opcao == 0:
            return
        elif opcao == 1:

            headers = {'Content-Type':'application/json'}
            r = requests.get(URL_CB + 'client', data=json.dumps({'key': 'value'}, default=lambda o: o.__dict__))

            # #pegar os recursos
            # print("--------Consulta--------")
            # vCPUs = int (input("Insira a quantidade de vCPUs desejada: "))
            # ram = int (input("Insira a quantidade de memória RAM desejada: "))
            # hd = int (input("Insira a quantidade de memória de disco (HD) desejada: "))

            # #coisar para json
            # recurso = {"vCPUs": vCPUs, "RAM": ram, "HD": hd}
            # resoucer = {"operation": "request", "resourcer" : recurso}
            # jsonRequest = {"request": json.dumps(resoucer)}
            # #enviar para o cloud broker
            # request = requests.get(URL_Dest, params=jsonRequest)
            # #pegar a resposta
            # resposta = request.json()
            # print("resposta")
            # #utilizar o recurso

        elif opcao == 2:
            
            vm_id = input("Insira o id da vm que deseja liberar:\n")

            if vm_id not in using_vm:
                print("Esse recurso não está sendo utilizado")
            else:
                r = requests.get(URL_CB + 'clientFree', data=json.dumps({'vm_id': vm_id}))
                using_vm.pop(vm_id)

        else:
            print("Opção inválida!")            



if __name__ == "__main__": main()