#Caroline Aparecida 726506
#Isabela Sayuri Matsumoto 726539
import sys
import socket
import threading
import time
import random
import pickle

MCAST_GRP = '224.0.0.1'
MCAST_PORT = 2048

msg_list = ["kurose", "tanenbaum", "ross", "bcc", "network", "mainframe", "arcabouço"]
message_list = []
random.seed()
myTime = 0
cont = 0

class Receiver(threading.Thread):
	global myTime
	def __init__(self, pid):
		
		threading.Thread.__init__(self)

		ttl = 1
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, ttl)
		sock.bind((MCAST_GRP, MCAST_PORT))
		self.sock = sock
		self.pid = pid
		
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
						#	exit(1)

					message_list.append(message)
					message_list.sort(key=lambda message: int(str(message.time) + message.mid[0]))

					for x in range(len(message_list)):
						print('[%s]' % message_list[x].mid)

					
					ack = Message(message.mid, myTime, None, True)
					
					print("Sending ACK to message {}".format(message.mid))
					self.sock.sendto(pickle.dumps(ack), (MCAST_GRP, MCAST_PORT))
					myTime += 1
				
				else:
					print("Received ACK from message %s" % message.mid)
					flag = False
					for x in range(len(message_list)):
						if ((message_list[x].mid == message.mid)):
							message_list[x].ack += 1
							flag = True		
					while (message_list and message_list[0].ack == 3):
						print("Received {} ACK(s)! Removing message {} from queue!" .format(3, message_list[0].mid))
						message_list.pop(0)
				
					if (flag == False):
						#exit(1)
						ack_buffer.append(message)
										

class Sender(threading.Thread):

	def __init__(self, pid):

		threading.Thread.__init__(self)

		ttl = 1
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, ttl)
		sock.bind((MCAST_GRP, MCAST_PORT))
		self.sock = sock
		self.pid = pid

	def run(self):
		global cont
		global myTime
		# esperar 7s antes de enviar a mensagem, senão não da tempo de abrir os 3 processos
		time.sleep(7)
		while(True):
			
			while(cont < 40): #envia apenas 20 mensagens
				myTime += 1
				message = Message(str(self.pid) + '/' + str(myTime), myTime, msg_list[random.randint(0, 3)], False)
				print("Sending message " + message.data + " com o mid = " + str(message.mid))
				sent = self.sock.sendto(pickle.dumps(message), (MCAST_GRP, MCAST_PORT))
				cont += 1
				time.sleep(random.randrange(0, 2)) # esperar tempo aleatório antes de enviar a próxima mensagem
			#	time.sleep(0.0001)
				
class Message:

	def __init__(self, mid, time2, data, isAck):
		self.mid = mid
		self.time = time2
		self.data = data
		self.isAck = isAck
		self.ack = 0

def main():
	global myTime
	pid = int(sys.argv[1])

	receiver = Receiver(pid)
	sender = Sender(pid)
	myTime = pid + 1 # tempo do processo 
	print("I am process {} and my initial time is {}" .format(pid, myTime))

	receiver.start()
	sender.start()

	#receiver.join()
	#sender.join()

if __name__ == "__main__": main()
