import sys
import json
import requests

URL_Dest = 'http://localhost:5000/cliente'
def main():


    while True:
        print("Menu de opções:\n0 - Sair do programa\n1 - Busca por recursos\n2 - Liberar recurso")
        print("Insira uma das opções: ")
        opcao = int(input())
        if opcao == 0:
            return
        elif opcao == 1:
            #pegar os recursos
            print("--------Consulta--------")
            vCPUs = int (input("Insira a quantidade de vCPUs desejada: "))
            ram = int (input("Insira a quantidade de memória RAM desejada: "))
            hd = int (input("Insira a quantidade de memória de disco (HD) desejada: "))

            #coisar para json
            recurso = {"vCPUs": vCPUs, "RAM": ram, "HD": hd}
            resoucer = {"operation": "request", "resourcer" : recurso}
            jsonRequest = {"request": json.dumps(resoucer)}
            #enviar para o cloud broker
            request = requests.get(URL_Dest, params=jsonRequest)
            #pegar a resposta
            resposta = request.json()
            print("resposta")
            #utilizar o recurso

        elif opcao == 2:
            #verificar se está usando algum recurso
                break;
            #request para json para parar de usar o recurso

        else:
            print("Opção inválida!")            



if __name__ == "__main__": main()