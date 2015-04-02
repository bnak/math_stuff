import random
import math
import pprint
from operator import attrgetter
import logging

'''Source: https://gist.githubusercontent.com/gbigwood/5304126/raw/fa64a8299e653bcbc5d056d9d49f2a16ec6a310f/queues-theory.py'''

logging.basicConfig(filename="queues-sim.log", level=logging.INFO, 
        filemode="w")

class Shop(object):

    def __init__(self, shopName, workStations):
        self.shopName = shopName
        #A matrix of stations. [[station], [station,station],[station]]
        self.stations = workStations

        self.total_number_of_customers = 0
        self.total_time_spent_waiting = 0
        self.total_time_spent_being_served = 0
        #set up workstation index. Shows where in the pipeline they are.
        index = 0
        for station in self.stations:
            for substation in station:
                substation.index = index
                substation.parentShop = self
            index += 1

    def addCustomer(self, customer, arrivalTime):
        logging.debug("Adding customer %d at %d",
                customer.customerID, arrivalTime)
        self.moveCustomerToNextStation(-1, customer, arrivalTime)
        pass

    def moveCustomerToNextStation(self, currentStationIndex,
            customer, currentTime):
        #If the next station is a list, add to one with the shortest line
        #If the next station is a node, add to the node itself.
        #IF the customer has finished being served, they can now leave.

        stationIndex = currentStationIndex + 1

        if (stationIndex == len(self.stations)):
            #customer has finished being served by the shop, they can leave
            customer.exitTime = currentTime
            self.total_number_of_customers += 1
            self.total_time_spent_waiting += customer.getWaitingTime()
            self.total_time_spent_being_served += customer.getServiceTime()
            logging.debug("Customer %d exiting shop %s at time %d", 
                    customer.customerID, self.shopName, currentTime)
        else:
            #Find which of the potential stations to use:
            nextStation = min(self.stations[stationIndex])#smallest queue
            logging.debug("Customer %d moving to station %s at time %d",
                    customer.customerID, nextStation.description, currentTime)
            nextStation.addCustomer(customer, currentTime)

    def tickOfTime(self, currentTickNumber):
        for station in self.stations:
            for subStation in station:
                #make each station see if it is finished with any customers
                subStation.tickOfTime(currentTickNumber)

    def areCustomersInStore(self):
        for station in self.stations:
            for substation in station:
                if substation.areCustomersAtStation():
                    return True
        return False

    def getMeanAverageWaitingTime(self):
        if (self.total_number_of_customers == 0):
            return 1
        return (float(self.total_time_spent_waiting) /
                float(self.total_number_of_customers))

    def getMeanAverageServiceTime(self):
        if (self.total_number_of_customers == 0):
            return 1
        return (float(self.total_time_spent_being_served) /
                float(self.total_number_of_customers))

    def getAllQueueStrings(self):
        stationQueues = "%s" %self.shopName
        for station in self.stations:
            for subStation in station:
                stationQueues += subStation.getQueueStrings()
        return stationQueues

    def getStats(self):
        return """
    ShopName: %s
    Mean Average Waiting Time: %f
    Mean Average Service Time: %f
    Proportion of Time Wasted: %f
    Customers Served: %d""" % (self.shopName,
            self.getMeanAverageWaitingTime(),
            self.getMeanAverageServiceTime(),
            self.getMeanAverageWaitingTime() / (
                self.getMeanAverageWaitingTime() +
                self.getMeanAverageServiceTime()),
            self.total_number_of_customers
            )

class Customer(object):
    NUMBER_OF_CUSTOMERS = 0

    def __init__(self, arrivalTime):
        self.customerID = Customer.NUMBER_OF_CUSTOMERS
        Customer.NUMBER_OF_CUSTOMERS +=1

        #When they arrived at the shop
        self.arrivalTime = arrivalTime
        #When they left the shop
        self.exitTime = None
        #Time spent Waiting
        self.timeSpentWaiting = 0.0
        #Time spent Being Served
        self.timeSpentBeingServed = 0.0

    def increaseWaitingTime(self):
        self.timeSpentWaiting += 1.0

    def increaseServingTime(self):
        self.timeSpentBeingServed += 1.0

    def computeTimeInSystem(self):
        if (self.exitTime == None):
            return self.arrivalTime + \
                    self.timeSpentWaiting + \
                    self.timeSpentBeingServed
        return self.exitTime - self.arrivalTime

    def getWaitingTime(self):
        return self.timeSpentWaiting

    def __repr__(self):
        return "<Customer ID: " + str(self.customerID) + " arrivalTime " + \
                str(self.arrivalTime) + \
                " timespentWaiting: " + str(self.timeSpentWaiting) + \
                " timespentBeingServed: " + str(self.timeSpentBeingServed) + \
                " >"

    def getArrivalTime(self):
        return self.arrivalTime

    def getServiceTime(self):
        return self.timeSpentBeingServed

class WorkStation(object):

    NUMBER_OF_STATIONS = 0

    def __init__(self, serviceRate, description, 
            numberOfServers = 1, probabilityOfUse = 1.0 ):

        self.numberOfServers = numberOfServers
        self.index = None #where in its parents list of stations is it?
        self.stationID = WorkStation.NUMBER_OF_STATIONS
        WorkStation.NUMBER_OF_STATIONS += 1
        self.description = description #what does this station do?

        self.currentWaitingCustomers = []
        self.currentServedCustomers = [] #should equal number of servers
        self.releaseCurrentCustomerAt = []

        self.serviceRate = serviceRate
        self.probabilityOfUse = probabilityOfUse

    def areCustomersAtStation(self):
        if ((len(self.currentWaitingCustomers) > 0) or
                (len(self.currentServedCustomers) > 0)):
            return True
        return False

    def startServingCustomer(self, customer, currentTickNumber):
        assert len(self.currentServedCustomers) < self.numberOfServers
        self.currentServedCustomers.append(customer)
        serviceTime = round(math.ceil(random.expovariate(self.serviceRate)))
        releaseTime = currentTickNumber + serviceTime
        self.releaseCurrentCustomerAt.append(releaseTime)
        logging.debug("Station %s going to release Customer %s at time %d",
                self.description, customer.customerID, releaseTime)

    def __repr__(self):
        return self.description + str(self.index) + \
                " queue: "+ str(len(self.currentWaitingCustomers))

    def addCustomer(self, customer, currentTickNumber):
        if (random.random() > self.probabilityOfUse):
            logging.debug("Customer %d skipping station %s at time %d",
                    customer.customerID, self.description, currentTickNumber)
            self.parentShop.moveCustomerToNextStation(self.index, customer,
                    currentTickNumber)
            return
        if (len(self.currentServedCustomers) >= self.numberOfServers):
            logging.debug("Customer %d added to waiting line at " +
                    "station %s at time %d",
                    customer.customerID, self.description, currentTickNumber)
            self.currentWaitingCustomers.append(customer)
        else:
            self.startServingCustomer(customer, currentTickNumber)

    def __cmp__(self, other):
        return cmp(len(self.currentWaitingCustomers),
                len(other.currentWaitingCustomers))

    def tickOfTime(self, currentTickNumber):
        #If they are done, move to next station
        toRemove = [ (releaseTime, self.currentServedCustomers[index]) for
                index, releaseTime in enumerate(self.releaseCurrentCustomerAt)
                if (releaseTime == currentTickNumber)]
        for releaseTime, customer in toRemove:
            self.releaseCurrentCustomerAt.remove(releaseTime)
            self.currentServedCustomers.remove(customer)
            logging.debug("Customer %d released by station %s at time %d",
                    customer.customerID,
                    self.description,
                    currentTickNumber)
            self.parentShop.moveCustomerToNextStation(self.index, customer,
                    currentTickNumber)

        #increaseServiceTime for customers still being served
        for customer in self.currentServedCustomers:
            customer.increaseServingTime()

        #Those in line have waited, increase time waited
        for customer in self.currentWaitingCustomers:
            customer.increaseWaitingTime()

        #Fill up available servers:
        freeServers = self.numberOfServers - len(self.currentServedCustomers)
        logging.debug("freeServer ID: %d desc: %s freeServers: %d",
                self.stationID, self.description, freeServers)
        while ((freeServers > 0) and (len(self.currentWaitingCustomers) > 0) ):
            nextInLine = self.currentWaitingCustomers.pop(0)
            self.startServingCustomer(nextInLine, currentTickNumber)
            freeServers -= 1

    def getQueueStrings(self):
        return "\nStation %s\nWaiting: %d\nServing: %d" % (self.description,
                len(self.currentWaitingCustomers),
                len(self.currentServedCustomers))

'''
#Chipotle example
chipotleStations = [
        [WorkStation(serviceRate = 1/5.0,
            description="burrito/bowl/tacos")],
        [WorkStation(serviceRate = 1/7.0,
            description="rice+meat")],
        [WorkStation(serviceRate = 1/12.0,
            description="salsa+salad")],
        [WorkStation(serviceRate = 1/9.0,
            description="wrapping+pricing")],
        [WorkStation(serviceRate = 1.0/10.0,
            description="paying")],
        ]

#Subway:
subwayStations = [
        [WorkStation(serviceRate = 1/8.0,
            description="What kind of bread? + slice")],
        [WorkStation(serviceRate = 1/17.0,
            description="Meat + cheese")],
        [WorkStation(serviceRate = 1/32.0,
            probabilityOfUse = 0.8, description="Toaster",
            numberOfServers=1.0)],
        [WorkStation(serviceRate = 1/17.0,
            description="Salad + dressing")],
        [WorkStation(serviceRate = 1/15.0,
            description="Paying + wrapping")],
        ]
subwayStationsb = [
        [WorkStation(serviceRate = 1/8.0,
            description="What kind of bread? + slice")],
        [WorkStation(serviceRate = 1/17.0,
            description="Meat + cheese")],
        [WorkStation(serviceRate = 1/32.0,
            probabilityOfUse = 0.8, description="Toaster",
            numberOfServers=2.0)],
        [WorkStation(serviceRate = 1/17.0,
            description="Salad + dressing")],
        [WorkStation(serviceRate = 1/15.0,
            description="Paying + wrapping")],
        ]
subwayStationsc = [
        [WorkStation(serviceRate = 1/8.0,
            description="What kind of bread? + slice")],
        [WorkStation(serviceRate = 1/17.0,
            description="Meat + cheese")],
        [WorkStation(serviceRate = 1/32.0,
            probabilityOfUse = 0.8, description="Toaster",
            numberOfServers=100.0)],
        [WorkStation(serviceRate = 1/17.0,
            description="Salad + dressing")],
        [WorkStation(serviceRate = 1/15.0,
            description="Paying + wrapping")],
        ]

#Starbucks
starbucksStations = [
        [WorkStation(serviceRate = 1/22.0,
            numberOfServers = 1.0, description="order + Paying ")],
        [WorkStation(serviceRate = 1/92.0,
            numberOfServers = 3.0, description="making coffee")],
        ]

#McDonalds
mcDonaldsStations = [
        [
            WorkStation(serviceRate = 1/42.0 , description = "order and pay"),
            WorkStation(serviceRate = 1/42.0 , description = "order and pay"),
            WorkStation(serviceRate = 1/42.0 , description = "order and pay"),
            WorkStation(serviceRate = 1/42.0 , description = "order and pay"),
            WorkStation(serviceRate = 1/42.0 , description = "order and pay"),
            ],
        [WorkStation( serviceRate = 1/102.0,
            numberOfServers = 5.0, description="food is made")],
        ]

#Chopt
choptStations = [
        [WorkStation(serviceRate = 1/4.0,
            numberOfServers = 1.0, description="Wait for placement")],
        [
            WorkStation(serviceRate = 1/32.0,
                numberOfServers = 1.0, description = "collect ingredients"),
            WorkStation(serviceRate = 1/32.0,
                numberOfServers = 1.0, description = "collect ingredients"),
            WorkStation(serviceRate = 1/32.0,
                numberOfServers = 1.0, description = "collect ingredients"),
            WorkStation(serviceRate = 1/32.0,
                numberOfServers = 1.0, description = "collect ingredients"),
            ],
        [
            WorkStation(serviceRate = 1/47.0,
                numberOfServers = 1.0, description="Chop ingredients"),
            WorkStation(serviceRate = 1/47.0,
                numberOfServers = 1.0, description="Chop ingredients"),
            WorkStation(serviceRate = 1/47.0,
                numberOfServers = 1.0, description="Chop ingredients"),
            WorkStation(serviceRate = 1/47.0,
                numberOfServers = 1.0, description="Chop ingredients"),
            WorkStation(serviceRate = 1/47.0,
                numberOfServers = 1.0, description="Chop ingredients"),
            WorkStation(serviceRate = 1/47.0,
                numberOfServers = 1.0, description="Chop ingredients"),
            ],
        [WorkStation(serviceRate = 1/17.0,
            numberOfServers = 3.0, description="paying + wrapping")],
        ]

SHOPS = [
        Shop("Chipotle", chipotleStations),
        Shop("Subway", subwayStations),
        Shop("Subway: two toasters", subwayStationsb),
        Shop("Subway: 100 toasters", subwayStationsc),
        Shop("Starbucks", starbucksStations),
        Shop("McDonalds", mcDonaldsStations),
        Shop("Chopt", choptStations)
        ]
'''
#Simulate customers and when they arrive.
AVERAGE_ARRIVAL_RATE = 1.0/5.0
NUMBER_OF_CUSTOMERS_TO_SIMULATE = 10000
ABORT_SIMULATION_TIME = 500000
MAX_ACCEPTABLE_QUEUE_LENGTH = 360

#create customers arrival diffs:
CUSTOMERS = [round(random.expovariate(AVERAGE_ARRIVAL_RATE)) for tick in 
        xrange(NUMBER_OF_CUSTOMERS_TO_SIMULATE - 1)]

#Take the arrival rate values and add them to create arrival times:
for index, i in enumerate(CUSTOMERS):
    if (index == 0):
        CUSTOMERS[index] = 0
    else:
        CUSTOMERS[index] = CUSTOMERS[index-1] + i

CUSTOMERS.sort()

currentTick = 0

while True:
    #TODO refactor into several functions
    if ((currentTick  % 1000) == 0):
        logging.info("TickNumber %d ", currentTick)
        #print "TickNumber", currentTick
        for shop in SHOPS:
            logging.info("Shop Stats %s", shop.getStats())
            logging.debug(shop.getAllQueueStrings())

    if ((currentTick == ABORT_SIMULATION_TIME) or
            ((CUSTOMERS[0] < currentTick) and \
                    not(any(shop.areCustomersInStore() for shop in SHOPS)))):
        #simulation over, we have looped, there are no customers in any store
        break

    while (CUSTOMERS[0] == currentTick):
        arrivalTime = CUSTOMERS.pop(0)
        #Customer goes to the shops!
        for shop in SHOPS:
            #We try go to all the shops!
            if (shop.getMeanAverageWaitingTime() < MAX_ACCEPTABLE_QUEUE_LENGTH):
                newCustomer = Customer(arrivalTime)
                shop.addCustomer(newCustomer, currentTick)
            else:
                logging.info("Line too long at %s. AverageWaitingTime: %d " +
                        "current time %d ",
                        shop.shopName, shop.getMeanAverageWaitingTime(),
                        currentTick)
        CUSTOMERS.append(arrivalTime)

    for shop in SHOPS:
        shop.tickOfTime(currentTick)
    #no more of the same arrival time.
    currentTick += 1

print "Simulation over."
print "Ticks:", currentTick
print "Customers:,", NUMBER_OF_CUSTOMERS_TO_SIMULATE
print "Statistics:"
logging.info("Simulation over.\nTickNumber %d\nStatistics: ", currentTick)
for shop in SHOPS:
    print shop.getStats()
    logging.info("Shop Stats %s", shop.getStats())
    logging.info("-----")