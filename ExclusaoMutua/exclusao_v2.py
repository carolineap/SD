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
					
					if (message.mid[0] != str(self.pid)):
							
						flag = True
						for r in self.rlist:
							if message.rid == r.rid and r.isUsing == True:
								flag = False
								break
							elif message.rid == r.rid and r.requested == True:
								if int(str(r.message.time) + r.message.mid[0]) < int(str(message.time) + message.mid[0]):
									flag = False
									break

						if (flag == True):
							ack = Message(message.mid, myTime, None, True)
							print("Sending ACK to process {} uses resource R{}".format(message.mid[0], message.rid))
							self.sock.sendto(pickle.dumps(ack), (MCAST_GRP, MCAST_PORT + int(message.mid[0])))	
							myTime += 1

						if (flag == False):
							message_list.append(message)
							message_list.sort(key=lambda message: int(str(message.time) + message.mid[0]))					
						
						for x in range(len(message_list)):
							print('[{}][R{}]' .format(message_list[x].mid, message_list[x].rid)) 

					else:
						ack = Message(message.mid, myTime, None, True)
						print("Sending ACK to process {} uses resource R{}".format(message.mid[0], message.rid))
						self.sock.sendto(pickle.dumps(ack), (MCAST_GRP, MCAST_PORT + int(message.mid[0])))	
						myTime += 1

				else:		
					
					print("Received ACK of message %s" % message.mid)

					for r in self.rlist:
						if (r.requested == True and r.message.mid == message.mid):
							r.message.ack += 1
							if (r.message.ack == 3):
								r.isUsing = True
								r.requested = False
								myTime += 1

class Sender(threading.Thread):

	def __init__(self, pid, sock, rlist):

		threading.Thread.__init__(self)
		self.sock = sock
		self.pid = pid
		self.rlist = rlist

	def run(self):

		global cont
		global myTime

		time.sleep(random.randint(3, 5))
		cont = 0
		while(True):
			while(cont < 5): #enquanto ainda há recursos para serem utilizados
				myTime += 1
				message = Message(str(self.pid) + '/' + str(myTime), myTime, self.rlist[cont].rid, False)
				print("Asking for resource R" + str(message.rid) + " com o mid = " + str(message.mid))
				self.rlist[cont].askResource(message)
				for i in range(1, 4):
					sent = self.sock.sendto(pickle.dumps(message), (MCAST_GRP, MCAST_PORT + i))
				time.sleep(random.randrange(0, 3)) # esperar tempo aleatório antes de enviar a próxima mensagem
				cont += 1

class CriticalRegion(threading.Thread):

	def __init__(self, sock, rlist):

		threading.Thread.__init__(self)
		self.sock = sock
		self.rlist = rlist

	def run(self):
		global isUsing
		global myTime
		
		while True:
			for r in self.rlist:
				if r.isUsing == True:
					print("I am using R%s" % r.rid)
					time.sleep(random.randint(2, 5))
					print("Stop using R%s" % r.rid)
					r.isUsing = False
				for m in message_list:
					if (r.isUsing == False and m.rid == r.rid and r.requested == False):
						ack = Message(m.mid, myTime, None, True)
						print("Sending ACK to process {} uses resource R{}".format(m.mid[0], m.rid))
						self.sock.sendto(pickle.dumps(ack), (MCAST_GRP, MCAST_PORT + int(m.mid[0])))
						message_list.pop(message_list.index(m))
						myTime += 1
							
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

	def askResource(self, message):
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
	print(temp)

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
