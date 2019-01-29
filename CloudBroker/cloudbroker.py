from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
import json
from pymongo import MongoClient

app = Flask(__name__)

#app.config["MONGO_URI"] = "mongodb://localhost:27017/cloudbroker_db"

client = MongoClient('localhost', 27017)#host uri
banco = client['test-database']
VMS = banco['test-collection'] #Select the collection name


class VirtualMachine:

	def __init__(self, vm_id, hd, ram, cpu, preco):
		self.id = vm_id
		self.hd = hd
		self.ram = ram
		self.cpu = cpu
		self.preco = preco

@app.route('/add', methods=["GET", "POST"])
def addVM():
   	
	if (request.method == 'GET'):
		#try:
			 
		content = request.get_json(force=True)
		x = banco.VMS.insert_one(content)
		#print(x)

		#except:
		#	pass

	return 'OK'



@app.route('/client', methods=["GET", "POST"])	
def findMatch():
	
	if (request.method == 'GET'):

	#	try:
			
		mydoc = banco.VMS.find()
		




	return 'OK'




if __name__ == "__main__":
    app.run(host='localhost', port=5000)