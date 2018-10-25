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
#rlist = random.sample(range(6),5)
rlist = [6, 5, 4]
rlist.extend(random.sample(range(3),3))
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
				
				if (message.isAck == False and message.isNack == False):
					print("Received message %s" % message.mid)

					
					if (message.mid[0] != str(self.pid)):
						

						message_list.append(message)
						message_list.sort(key=lambda message: int(str(message.time) + message.mid[0]))

						if message.rid not in isUsing : #se eu não estou usando
							flag = False
							for i in myResources:
								if i.rid == message.rid:
									flag = True
									if int(str(message.time) + message.mid[0]) > int(str(i.time) + i.mid[0]) :									
										nack = Message(message.mid, myTime, None, False, True)	
										print("My time is smaller, Sending Nack to mensagem {}".format(message.mid))
										self.sock.sendto(pickle.dumps(nack), (MCAST_GRP, MCAST_PORT + int(message.mid[0])))
									else :
										ack = Message(message.mid, myTime, None, True, False)
										print("My time is bigger, Sending OK to message {}".format(message.mid))
										self.sock.sendto(pickle.dumps(ack), (MCAST_GRP, MCAST_PORT + int(message.mid[0])))
										message_list.pop(message_list.index(message))
							if flag == False:
								ack = Message(message.mid, myTime, None, True, False)
								print("Sending OK to message {}".format(message.mid))
								self.sock.sendto(pickle.dumps(ack), (MCAST_GRP, MCAST_PORT + int(message.mid[0])))
								message_list.pop(message_list.index(message))
						else :	# se eu estou usando
							nack = Message(message.mid, myTime, None, False, True)
							print("I am using, Sending Nack {}".format(message.mid))
							self.sock.sendto(pickle.dumps(nack), (MCAST_GRP, MCAST_PORT + int(message.mid[0])))

						for x in range(len(message_list)):
							print('[{}][R{}]' .format(message_list[x].mid, message_list[x].rid)) 
					else:
						myResources.append(message)
						ack = Message(message.mid, myTime, None, True, False)
						print("Sending OK to my message {}".format(message.mid))
						self.sock.sendto(pickle.dumps(ack), (MCAST_GRP, MCAST_PORT + int(message.mid[0])))	

				elif message.isAck == True and message.isNack == False:		
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
		time.sleep(random.randint(4, 5))
		cont = 0
		while(True):
			while(cont < 6): #enquanto ainda há recursos para serem utilizados
				myTime += 1
				message = Message(str(self.pid) + '/' + str(myTime), myTime, rlist[cont], False, False)
				print("Asking for resource R" + str(message.rid) + " com o mid = " + str(message.mid))
				for i in range(1, 4):
					sent = self.sock.sendto(pickle.dumps(message), (MCAST_GRP, MCAST_PORT + i))
				time.sleep(random.randrange(0, 1)) # esperar tempo aleatório antes de enviar a próxima mensagem
				cont += 1



class CriticalRegion(threading.Thread):

	def __init__(self, sock):

		threading.Thread.__init__(self)
		self.sock = sock

	def run(self):
		global isUsing
		global message_list
		while True:
			while len(isUsing):
				print("I am using R%d" % isUsing[0])
				time.sleep(5)
				r = isUsing.pop(0)
				print("Stop using R%d" % r)
				for m in message_list:
					if (m.rid == r):
						ack = Message(m.mid, myTime, None, True, False)
						print("Sending OK to message {}".format(m.mid))
						self.sock.sendto(pickle.dumps(ack), (MCAST_GRP, MCAST_PORT + int(m.mid[0])))
						#message_list.pop(message_list.index(m))
				for m in message_list:
					if(m.rid == r):
						message_list.pop(message_list.index(m))
class Message:

	def __init__(self, mid, time2, rid, isAck, isNack):
		self.mid = mid
		self.time = time2
		self.rid = rid
		self.isAck = isAck
		self.ack = 0
		self.isNack = isNack

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
