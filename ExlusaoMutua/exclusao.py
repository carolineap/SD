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

random.seed()
myTime = 0
cont = 0

class Receiver(threading.Thread):
	global myTime
	def __init__(self, pid, sock, rlist):
		
		threading.Thread.__init__(self)

		self.sock = sock
		self.pid = pid
		self.rlist = rlist
		
	def run(self):
		global myTime
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

					

					for i in range(len(ack_buffer)):
						if ack_buffer[i].mid == message.mid:
							message.ack += 1
							ack_buffer.pop(i)

					
					if (message.mid[0] != str(self.pid)):
							
						flag = False
						for r in rlist:
							if message.rid == r.rid and r.isUsing == False and r.requested == True:
								if int(str(r.message.time) + r.message.mid[0]) > int(str(message.time) + message.mid[0]):
									flag = True
									ack = Message(message.mid, myTime, None, True)
									print("Sending OK to message {}".format(message.mid))
									self.sock.sendto(pickle.dumps(ack), (MCAST_GRP, MCAST_PORT + int(message.mid[0])))
									break

						if (flag == False):
							flag = True
							ack = Message(message.mid, myTime, None, True)
							print("Sending OK to message {}".format(message.mid))
							self.sock.sendto(pickle.dumps(ack), (MCAST_GRP, MCAST_PORT + int(message.mid[0])))	

						if (flag == False):
							message_list.append(message)
							message_list.sort(key=lambda message: int(str(message.time) + message.mid[0]))					
						
						for x in range(len(message_list)):
							print('[{}][R{}]' .format(message_list[x].mid, message_list[x].rid)) 

				else:		
					print("Received ACK from message %s" % message.mid)
					flag = False

					for x in range(len(message_list)):
						if ((message_list[x].mid == message.mid)):
							flag = True	
							message_list[x].ack += 1
							if (message_list[x].ack == 2):
								isUsing.append(message_list[x].rid)
								rlist.pop(rlist.index(message_list[x].rid))
								break		

					if (flag == False):
						ack_buffer.append(message)
										

class Sender(threading.Thread):

	def __init__(self, pid, sock, rlist):

		threading.Thread.__init__(self)
		self.sock = sock
		self.pid = pid
		self.rlist = rlist

	def run(self):

		global cont
		global myTime
		# esperar 7s antes de enviar a mensagem, senão não da tempo de abrir os 3 processos
		time.sleep(random.randint(3, 5))
		cont = 0
		while(True):
			while(cont < 5): #enquanto ainda há recursos para serem utilizados
				myTime += 1
				message = Message(str(self.pid) + '/' + str(myTime), myTime, self.rlist[cont].rid, False)
				print("Asking for resource R" + str(message.rid) + " com o mid = " + str(message.mid))
				for i in range(1, 4):
					sent = self.sock.sendto(pickle.dumps(message), (MCAST_GRP, MCAST_PORT + i))
				self.rlist[cont].askResource(message)
				time.sleep(random.randrange(0, 3)) # esperar tempo aleatório antes de enviar a próxima mensagem
				cont += 1



class CriticalRegion(threading.Thread):

	def __init__(self, sock, rlist):

		threading.Thread.__init__(self)
		self.sock = sock
		self.rlist = rlist

	def run(self):
		global isUsing

		while True:

			for r in self.rlist:
				if r.isUsing == True:
					time.sleep(1)
					r.isUsing = False
					for m in message_list:
						if (m.rid == r.rid):
							ack = Message(m.mid, myTime, None, True)
							print("Sending OK to message {}".format(message.mid))
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


class Resource:

	def __init__(self, rid):
		self.message = None
		self.rid = rid
		self.isUsing = False
		self.requested = False

	def askResource(message):
		self.message = message
		self.requested = True


def main():
	global myTime
	
	pid = int(sys.argv[1])

	ttl = 1
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, ttl)
	sock.bind((MCAST_GRP, MCAST_PORT + pid))

	rlist = []
	temp = random.sample(range(6), 5)
	for r in temp:
		rlist.append(Resource(r))

	receiver = Receiver(pid, sock, rlist)
	sender = Sender(pid, sock, rlist)
	critical = CriticalRegion(sock, rlist)

	myTime = pid + 1 # tempo do processo 
	print("I am process {} and my initial time is {}" .format(pid, myTime))

	receiver.start()
	sender.start()
	critical.start()

if __name__ == "__main__": main()
