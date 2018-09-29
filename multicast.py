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

class Receiver(threading.Thread):

	def __init__(self, pid, time):
		
		threading.Thread.__init__(self)

		ttl = 1
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, ttl)
		sock.bind((MCAST_GRP, MCAST_PORT))
		self.sock = sock
	#	self.message_list = []
		self.pid = pid
		self.time = time

	def run(self):
		
		while(True):
			try: 
				data, addr = self.sock.recvfrom(1024)
				message = pickle.loads(data)
				self.time += 1
			except:
				print("Waiting for new message...")
			else:
				if (message.isAck == False):
				#	self.message_list.append(message)
					self.time = max(self.time, message.time) + 1
					print("Send ACK to message {}".format(message.mid))
					ack = Message(message.mid, self.time, None, True)
					self.sock.sendto(pickle.dumps(ack), (MCAST_GRP, MCAST_PORT))
					self.time += 1
					time.sleep(1)

class Sender(threading.Thread):

	def __init__(self, pid, time):

		threading.Thread.__init__(self)

		ttl = 1
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, ttl)
		sock.bind((MCAST_GRP, MCAST_PORT))
		self.sock = sock
		self.time = time
		self.pid = pid
		self.message_list = []

	def run(self):
		global msg_id 

		while(True):

			message = Message(str(self.pid) + str(self.time), self.time, msg_list[random.randint(0, 3)], False)
			self.message_list.append(message)
			time.sleep(5)
			sent = self.sock.sendto(pickle.dumps(message), (MCAST_GRP, MCAST_PORT))
			self.time += 1

			try:
				data, server = self.sock.recvfrom(512)
				ack_message = pickle.loads(data)
			except socket.timeout:
				print('Timed out, no more responses')
				break
			else:
				for x in range(len(self.message_list)):
					print('[%s]' % self.message_list[x].mid)
				if (ack_message.isAck == True):
					for x in range(len(self.message_list)):
						if ((self.message_list[x].mid == ack_message.mid)):
							self.message_list[x].ack += 1
							if ((self.message_list[x].ack == 2) and (x == 0)):
								self.message_list.pop(0)
								print("Receive three ACKs! Removing message %s from queue!" % self.message_list[x].mid)
								break 

class Message:

	def __init__(self, mid, time, data, isAck):
		self.mid = mid
		self.time = time
		self.data = data
		self.isAck = isAck
		self.ack = 0

def main():

	pid = int(sys.argv[1])
	time = random.randint(1, 10)
	
	receiver = Receiver(pid, time)
	sender = Sender(pid, time)

	print("I am process {} and my initial time is {}" .format(pid, time))

	receiver.start()
	sender.start()

	receiver.join()
	sender.join()

if __name__ == "__main__": main()