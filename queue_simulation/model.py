import math
import operator
import random
import simpy

class Server(object): 
	'''A server object in queuing simulation, in this case a cashier'''

	def __init__(self):
		self.arrivalRate = 0.0
		self.serviceRate = 0.0
		self.line = []
		self.lineCount = len(self.line)


class Customer(object):
	""""A customer object in queuing simulation"""
	def __init__(self):
		self.arrivalTime = 0.0
		self.itemCount = random.randint(0,50)
		self.waitingTime =0.0

def generateCustomers(number):
	customerList = [Customer() for i in range(number)]
	return customerList

def generateCashiers(serverNum): 
	cashierList = [Server() for i in range(serverNum)]
	return cashierList

def procedureB(customerList): 
	cashierList = generateCashiers(5)

	
	for item in customerList: 
		cashierList = sorted(cashierList, key = operator.attrgetter('lineCount'))


	procedureStatistics = "Placeholder"
	print procedureStatistics
	return cashierList	

def main(): 

	customerList = generateCustomers(15)
	
	for i in range (len(customerList)): 
		print customerList[i].itemCount
	cashierList = procedureB(customerList)
	print cashierList
	print "ran"

if __name__ == '__main__':
	main()