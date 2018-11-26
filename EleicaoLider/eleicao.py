#Caroline Aparecida de Paula Silva - 726506
#Isabela Sayuri Matsumoto - 726539
#Sistemas Distribuidos - Eleicao de Lider - P1

import sys
import socket
import threading
import time
import random
import pickle

MCAST_GRP = '127.0.0.1'
MCAST_PORT = 2048
SOURCE_NID = 0 

class Node:
	def __init__(self, nid, adj, capacity):
		self.nid = nid
		self.adj = adj
		self.capacity = capacity
		self.pred = None
		self.ack = 0
		self.maxCapacity = [capacity, nid]

class Message:

	def __init__(self, source, dest, mType, maxCapacity):
		self.source = source
		self.dest = dest
		self.type = mType
		self.capLeader = maxCapacity


class Receiver(threading.Thread):

	def __init__(self, socket, node):
		threading.Thread.__init__(self)
		self.node = node
		self.sock = socket
		
		
	def run(self):
		
		while(True):
			try: 
				data, addr = self.sock.recvfrom(1024)
				message = pickle.loads(data)
			except:
				print("Waiting for new message...")
			else:
				if (message.type == 'ELECTION'):
					if self.node.nid != SOURCE_NID and self.node.pred == None:
						self.node.pred = message.source
						print("My parent is node " + str(self.node.pred))
						for i in self.node.adj:
							if i != self.node.pred:
								message = Message(self.node.nid, i, 'ELECTION', None)
								sent = self.sock.sendto(pickle.dumps(message), (MCAST_GRP, MCAST_PORT + i))
					else:
						print("Receive a message from node " + str(message.source) + " but I already have a parent! Sendind ACK!")
						message = Message(self.node.nid, message.source, 'ACK', None)
						sent = self.sock.sendto(pickle.dumps(message), (MCAST_GRP, MCAST_PORT + message.source))
				elif (message.type == 'ACK'):
					print("Receive ACK from node " + str(message.source))
					if (message.capLeader != None and message.capLeader[0] > self.node.maxCapacity[0]):
						self.node.maxCapacity = message.capLeader
					self.node.ack += 1
				elif (message.type == 'BROADCAST'):
					print("Node " + str(message.capLeader[1]) + " with capacity " + str(message.capLeader[0]) + " has been elected the leader!")



class Sender(threading.Thread):

	def __init__(self, socket, node):
		threading.Thread.__init__(self)
		self.node = node
		self.sock = socket

	def run(self):
		if (self.node.nid == SOURCE_NID):
			input("Press Enter to continue...")
			print("Starting election...")
			for i in self.node.adj:
				message = Message(self.node.nid, i, 'ELECTION', None)
				sent = self.sock.sendto(pickle.dumps(message), (MCAST_GRP, MCAST_PORT + i))

		endElection = False
		while not endElection:
			if (self.node.nid == SOURCE_NID):
				if (self.node.ack == len(self.node.adj)):
					print("Sending broadcast message...")
					for i in range(10):
						message = Message(self.node.nid, message.source, 'BROADCAST', self.node.maxCapacity)
						sent = self.sock.sendto(pickle.dumps(message), (MCAST_GRP, MCAST_PORT + i))
					endElection = True
			elif (self.node.pred != None and self.node.ack == len(self.node.adj) - 1):
				print("Sending ACK to my parent, the max capacity I found is " + str(self.node.maxCapacity[0]))
				message = Message(self.node.nid, self.node.pred, 'ACK', self.node.maxCapacity)
				sent = self.sock.sendto(pickle.dumps(message), (MCAST_GRP, MCAST_PORT + self.node.pred))
				self.node.ack = 0

def main():

	nid = int(sys.argv[1])
	#capacity = int(sys.argv[2])

	ttl = 1
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, ttl)
	sock.bind((MCAST_GRP, MCAST_PORT + nid))

	adj = []

	#Topologia inventada
	# if nid == 0:
	# 	adj = [1, 2, 3]
	# elif nid == 1:
	# 	adj = [0, 2, 4]
	# elif nid == 2:
	# 	adj = [0, 1, 3, 4, 5, 6]
	# elif nid == 3:
	# 	adj = [0, 2, 6]
	# elif nid == 4:
	# 	adj = [1, 2, 5, 7]
	# elif nid == 5:
	# 	adj = [2, 4, 6, 7, 8, 9]
	# elif nid == 6:
	# 	adj = [2, 3, 5, 9]
	# elif nid == 7:
	# 	adj = [4, 5, 8]
	# elif nid == 8:
	# 	adj = [5, 7, 9]
	# elif nid == 9:
	# 	adj = [5, 6, 8]
	# else:
	# 	print("Invalid node number")
	# 	return

	#Topologia do slide:
	if nid == 0:
		adj = [1, 9]
		capacity = 4
	elif nid == 1:
		adj = [0, 2, 6]
		capacity = 2
	elif nid == 2:
		adj = [1, 3, 4]
		capacity = 3
	elif nid == 3:
		adj = [2, 4, 5]
		capacity = 2
	elif nid == 4:
		adj = [2, 3, 5, 6]
		capacity = 1
	elif nid == 5:
		adj = [3, 4, 8]
		capacity = 4
	elif nid == 6:
		adj = [1, 4, 7, 9]
		capacity = 2
	elif nid == 7:
		adj = [6, 8]
		capacity = 8
	elif nid == 8:
		adj = [5, 7]
		capacity = 5
	elif nid == 9:
		adj = [0, 6]
		capacity = 4
	else:
		print("Invalid node number")
		return

	# if nid == 0:
	# 	adj = [1, 2, 3]
	# elif nid == 1:
	# 	adj = [0, 2, 4]
	# elif nid == 2:
	# 	adj = [0, 1, 3, 4]
	# elif nid == 3:
	# 	adj = [0, 2]
	# elif nid == 4:
	# 	adj = [1, 2]
	# else:
	# 	print("Invalid node number")
	# 	return

	print("I am node " + str(nid))
	print(adj)
	print(capacity)

	node = Node(nid, adj, capacity)
	receiver = Receiver(sock, node)
	sender = Sender(sock, node)

	receiver.start()
	sender.start()

if __name__ == "__main__": main()


