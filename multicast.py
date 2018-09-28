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
msg_id = 0

class Receiver(threading.Thread):

	def __init__(self, pid, n):
		
		threading.Thread.__init__(self)

		ttl = 1
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, ttl)
		sock.bind((MCAST_GRP, MCAST_PORT))
		self.sock = sock

		self.num_ack = n
		self.message_list = []
	
		self.pid = pid
		self.time = random.randint(1, 10)



	def run(self):
		
		while(True):
			try: 
				data, addr = self.sock.recvfrom(1024)
				message = pickle.loads(data)
			except:
				print("Waiting for new message...")
			else:
				self.time = self.time + 1
				if (message.data != "ACK"):
			#		print("Receive message from %s! Sending ACK!" % addr)
					self.message_list.append(message)
					self.message_list.sort(key = lambda message: message.mid)
					for x in range(len(self.message_list)):
						print(self.message_list[x].data, self.message_list[x].mid, self.message_list[x].time)
				
					self.time = max(self.time, message.time) + 1
					ack = Message(message.mid, self.time, "ACK")
					print("Enviei ACK")
					self.sock.sendto(pickle.dumps(ack), (MCAST_GRP, MCAST_PORT))
					self.time = self.time + 1

			

class Sender(threading.Thread):

	def __init__(self, pid):

		threading.Thread.__init__(self)

		ttl = 1
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, ttl)
		sock.bind((MCAST_GRP, MCAST_PORT))
		self.sock = sock
		self.time = random.randint(1, 10)
		self.pid = pid
		

	def run(self):
		global msg_id 

		while(True):
			m = input("Digite sua mensagem: ");
			msg_id += 1
			message = Message(msg_id, self.time, m)
		#	message = Message(msg_id, self.time, msg_list[random.randint(0, 3)])
			print("Sending message with id %d" % msg_id)
			sent = self.sock.sendto(pickle.dumps(message), (MCAST_GRP, MCAST_PORT))
			self.time += 1
		
			try:
				data, server = self.sock.recvfrom(100)
			except socket.timeout:
				print('Timed out, no more responses')
				break
			else:
				ack_message = pickle.loads(data)
				self.time = self.time + 1
				print('Recebi ACK da mensagem %s' % ack_message.mid)
				ack_message.ack += 1
				print("ACK", ack_message.ack)
			

class Message:

	def __init__(self, mid, time, data):
		self.mid = mid
		self.time = time
		self.data = data
		self.ack = 0

def main():

	prc_id = random.randint(1, 2000)
	n_process = sys.argv[1:]

	receiver = Receiver(prc_id, n_process)
	sender = Sender(prc_id)

	receiver.start()
	sender.start()

	receiver.join()
	sender.join()

if __name__ == "__main__": main()