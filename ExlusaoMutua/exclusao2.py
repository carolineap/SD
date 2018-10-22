#Caroline Aparecida 726506
#Isabela Sayuri Matsumoto 726539
import sys
import socket
import threading
import time
import random
import pickle

MCAST_GRP = '127.0.0.1'
MCAST_PORT = 2048
message_list = []
rlist = random.sample(range(6),5)
isUsing = []
myResources = []
random.seed()
myTime = 0


class Receiver(threading.Thread):
	global myTime
	def __init__(self, pid, sock):
		
		threading.Thread.__init__(self)

		self.sock = sock
		self.pid = pid
		
	def run(self):
		global myTime
		global myResources
		global isUsing
		ack_buffer = []
		while(True):
			try: 
				#time.sleep(random.randint(0, 3))
				data, addr = self.sock.recvfrom(1024)
				message = pickle.loads(data)
				myTime = max(myTime, message.time) + 1
				
			except:
				print("Waiting for new message...")
			else:
				
				if (message.isAck == False):
					print("Received message %s" % message.mid)

					
					if (message.mid[0] != str(self.pid)):
						

						message_list.append(message)
						message_list.sort(key=lambda message: int(str(message.time) + message.mid[0]))

						if message.rid not in isUsing :
							flag = False
							for i in myResources:
								if i.rid == message.rid:
									flag = True
									if int(str(message.time) + message.mid[0]) < int(str(i.time) + i.mid[0]) :
										ack = Message(message.mid, myTime, None, True)
										print("Chegou Primeiro Sending OK to message {}".format(message.mid))
										self.sock.sendto(pickle.dumps(ack), (MCAST_GRP, MCAST_PORT + int(message.mid[0])))
										message_list.pop(message_list.index(message))
									else :	
										print("Meu tempo é maior")	

							if flag == False:
								ack = Message(message.mid, myTime, None, True)
								print("Não quero usar e não pretendo Sending OK to message {}".format(message.mid))
								self.sock.sendto(pickle.dumps(ack), (MCAST_GRP, MCAST_PORT + int(message.mid[0])))
								message_list.pop(message_list.index(message))

						for x in range(len(message_list)):
							print('[{}][R{}]' .format(message_list[x].mid, message_list[x].rid)) 
					else:
						myResources.append(message)
						ack = Message(message.mid, myTime, None, True)
						print("Sending OK to my message {}".format(message.mid))
						self.sock.sendto(pickle.dumps(ack), (MCAST_GRP, MCAST_PORT + int(message.mid[0])))	

				else:		
					print("Received OK from message %s" % message.mid)
					flag = False

					for x in range(len(myResources)):
						if ((myResources[x].mid == message.mid)):
							flag = True	
							myResources[x].ack += 1
							if (myResources[x].ack == 3):
								isUsing.append(myResources[x].rid)
								myResources.pop(x)
								break		

class Sender(threading.Thread):

	def __init__(self, pid, sock):

		threading.Thread.__init__(self)
		self.sock = sock
		self.pid = pid
		self.rlist = rlist

	def run(self):
		global myTime
		# esperar 7s antes de enviar a mensagem, senão não da tempo de abrir os 3 processos
		time.sleep(random.randint(3, 5))
		cont = 0
		while(True):
			while(cont < 5): #enquanto ainda há recursos para serem utilizados
				myTime += 1
				message = Message(str(self.pid) + '/' + str(myTime), myTime, rlist[cont], False)
				print("Asking for resource R" + str(message.rid) + " com o mid = " + str(message.mid))
				for i in range(1, 4):
					sent = self.sock.sendto(pickle.dumps(message), (MCAST_GRP, MCAST_PORT + i))
				time.sleep(random.randrange(0, 2)) # esperar tempo aleatório antes de enviar a próxima mensagem
				cont += 1



class CriticalRegion(threading.Thread):

	def __init__(self, sock):

		threading.Thread.__init__(self)
		self.sock = sock

	def run(self):
		global isUsing

		while True:
			while isUsing:
				print("I am using R%d" % isUsing[0])
				time.sleep(5)
				r = isUsing.pop(0)
				for m in message_list:
					if (m.rid == r):
						ack = Message(m.mid, myTime, None, True)
						print("Sending OK to message {}".format(m.mid))
						self.sock.sendto(pickle.dumps(ack), (MCAST_GRP, MCAST_PORT + int(m.mid[0])))
						message_list.pop(message_list.index(m))
						break
				
class Message:

	def __init__(self, mid, time2, rid, isAck):
		self.mid = mid
		self.time = time2
		self.rid = rid
		self.isAck = isAck
		self.ack = 0

def main():
	global myTime
	
	pid = int(sys.argv[1])

	ttl = 1
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, ttl)
	sock.bind((MCAST_GRP, MCAST_PORT + pid))

	receiver = Receiver(pid, sock)
	sender = Sender(pid, sock)
	critical = CriticalRegion(sock)

	myTime = pid + 1 # tempo do processo 
	print("I am process {} and my initial time is {}" .format(pid, myTime))
	print(rlist)
	receiver.start()
	sender.start()
	critical.start()

if __name__ == "__main__": main()
