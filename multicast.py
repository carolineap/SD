import sys
import socket
import struct
import threading
import time
import random
import pickle

MCAST_GRP = '224.0.0.1'
MCAST_PORT = 2048

msg_list = ["SOCORRO", "BATATA", "PAO", "DOGGO"]
message_list = []
random.seed()
myTime = 0
class Receiver(threading.Thread):
	global myTime
	def __init__(self, pid, time):
		
		threading.Thread.__init__(self)

		ttl = 1
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, ttl)
		sock.bind((MCAST_GRP, MCAST_PORT))
		self.sock = sock
		self.pid = pid
		#self.time = time

	def run(self):
		global myTime
		while(True):
			try: 
				data, addr = self.sock.recvfrom(1024)
				message = pickle.loads(data)
				#self.time += 1
				myTime = max(myTime, message.time) #+ 1
			except:
				print("Waiting for new message...")
			else:
				if (message.isAck == False):
					print("Received message %s" % message.mid)
					message_list.append(message)
					#print(message.mid[2:])
					message_list.sort(key=lambda message: message.time)
					for x in range(len(message_list)):
						print('[%s]' % message_list[x].mid)
					#self.time = max(self.time, message.time) + 1
					
					myTime += 1
					ack = Message(message.mid, myTime, None, True)
					
					print("Sending ACK {} to message {}".format(message.time, message.mid))
					self.sock.sendto(pickle.dumps(ack), (MCAST_GRP, MCAST_PORT))
					
					#time.sleep(1)
				else:
				#	self.time = max(self.time, ack_message.time) + 1
					print("Received ACK from message %s" % message.mid)
					for x in range(len(message_list)):
						if ((message_list[x].mid == message.mid)):
							message_list[x].ack += 1
							if ((message_list[x].ack == 3) and (x == 0)):
								print("Received {} ACK(s)! Removing message {} from queue!" .format(self.pid, message_list[x].mid))
								message_list.pop(0)
								break	

class Sender(threading.Thread):

	def __init__(self, pid, time):

		threading.Thread.__init__(self)

		ttl = 1
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, ttl)
		sock.bind((MCAST_GRP, MCAST_PORT))
		self.sock = sock
		#self.time = time
		self.pid = pid
		message_list = []

	def run(self):
		global msg_id 
		global myTime
		time.sleep(7)
		while(True):
			myTime += 1
			message = Message(str(self.pid) + '/' + str(myTime), myTime, msg_list[random.randint(0, 3)], False)
			time.sleep(3)
			print("Sending message %s" % message.mid)
			
			sent = self.sock.sendto(pickle.dumps(message), (MCAST_GRP, MCAST_PORT))
			

			#try:
			#	data, server = self.sock.recvfrom(512)
			#	ack_message = pickle.loads(data)
			#except socket.timeout:
			#	print('Timed out, no more responses')
			#	break
			#else:
				
class Message:

	def __init__(self, mid, time, data, isAck):
		self.mid = mid
		self.time = time
		self.data = data
		self.isAck = isAck
		self.ack = 0

def main():
	global myTime
	pid = int(sys.argv[1])

	receiver = Receiver(pid, time)
	sender = Sender(pid, time)
	myTime = pid + 1
	print("I am process {} and my initial time is {}" .format(pid, myTime))

	receiver.start()
	sender.start()

	receiver.join()
	sender.join()

if __name__ == "__main__": main()