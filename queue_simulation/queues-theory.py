import math
import operator


'''Source: https://gist.githubusercontent.com/gbigwood/5304126/raw/fa64a8299e653bcbc5d056d9d49f2a16ec6a310f/queues-theory.py'''

class WorkStation(object):
    """Represents a single station in a restaurants system"""

    def __init__(self, arrivalRate = 0.0, serviceRate = 0.0, 
            numberOfServers = 1.0):
        """
        Construct a workstation with parameters provided or defaults
        """
        self.arrivalRate = float(arrivalRate)
        self.serviceRate = float(serviceRate)
        self.numberOfServers = float(numberOfServers)

        #Compute the utilisation
        self.utilisation = self.computeUtilisation()
        pass

    def findIValue(self, i):
        i = float(i)
        singleNodeUtilisation = (self.numberOfServers *
                (self.arrivalRate * self.serviceRate))
        return ((singleNodeUtilisation ** i) / math.factorial(i))

    def possionRatioFunction(self):
        #This could be more efficient if using one loop. Left as is for clarity
        numerator = sum(self.findIValue(i)
                for i in xrange(int(self.numberOfServers) - 1))
        demonimator = sum(self.findIValue(i)
                for i in xrange(int(self.numberOfServers)))
        self.poissonRatio = numerator/demonimator
        return self.poissonRatio

    def computeProbabilityOfMultipleServersBeingBusy(self):
        self.possionRatioFunction()
        self.probabilityOfMultipleServersBeingBusy  = \
                ((1- self.poissonRatio) /
                (1 - (self.utilisation * self.poissonRatio)))
        return self.probabilityOfMultipleServersBeingBusy

    def computeUtilisation(self):
        assert self.numberOfServers >= 1, "No servers"
        self.utilisation = (self.arrivalRate /
                (self.serviceRate*self.numberOfServers))
        if (self.arrivalRate >= self.serviceRate):
            self.utilisation = 1.0
        assert ((self.utilisation >= 0) and (self.utilisation <= 1))
        return self.utilisation

    def computeNumberOfCustomersWaitingToBeServed(self):
        if (self.numberOfServers == 1.0):
            self.customersWaitingToBeServed = (((self.utilisation)**2) / 
                    (1 - self.utilisation))
        else:
            self.customersWaitingToBeServed = (
                    ((self.utilisation) / (1 - self.utilisation)) * 
                    self.computeProbabilityOfMultipleServersBeingBusy())
        return self.customersWaitingToBeServed

    def computeTimeWaiting(self):
        """
        Units in seconds or arrivals per second
        """
        if (self.numberOfServers == 1.0):
            self.timeWaiting = ((1.0/ (self.serviceRate - self.arrivalRate)) -
                    (1.0 / self.serviceRate))
        else:#multiple servers
            self.timeWaiting = (
                    (self.computeProbabilityOfMultipleServersBeingBusy() *
                        (1/self.serviceRate)) /
                    (self.numberOfServers * (1.0 - self.utilisation)))
        return self.timeWaiting

    def computeTimeInSystem(self):
        """
        Units in seconds or arrivals per second
        """
        if (self.numberOfServers == 1.0):
            self.timeInSystem = (1.0 / (self.serviceRate - self.arrivalRate))
        else:
            self.timeInSystem = self.computeTimeWaiting()+(1/self.serviceRate)
        return self.timeInSystem

    def computeProbabilityOfNJobsInTheSystem(self, N):
        self.NJobsInTheSystem = (1 - self.utilisation) * (self.utilisation ** N)
        return self.NJobsInTheSystem

def printStatistics(nameOfRestaurant, listOfWorkStations):
    """Print statistics for a given shop and workStations"""
    #nameOfRestaurant = '{:<12}'.format(nameOfRestaurant)
    try:
        print nameOfRestaurant, "waiting time:",
        totalTimeWaiting = sum(station.computeTimeWaiting()
                for station in listOfWorkStations)
        print totalTimeWaiting
        print nameOfRestaurant, "total time in system:",
        totalTimeInSystem = sum(station.computeTimeInSystem()
                for station in listOfWorkStations)
        print totalTimeInSystem
        print nameOfRestaurant, "proportion of time wasted:",
        print (totalTimeWaiting) / (totalTimeInSystem)

        print nameOfRestaurant, "customers waiting to be served:",
        customersWaitingToBeServed = sum(
                station.computeNumberOfCustomersWaitingToBeServed()
                for station in listOfWorkStations)
        print customersWaitingToBeServed

        for N in [1, 5, 10]:
            print nameOfRestaurant, "probability of", '{:>4}'.format(N) ,"customers in system:",
            #Chance of them not blocking
            probs = [1.0 - station.computeProbabilityOfNJobsInTheSystem(N) for station in listOfWorkStations]
            #Demorgan's law
            print 1.0 - reduce(operator.mul, probs, 1)

    except Exception as e:
        print e
    finally:
        print "--------"

#In people per second:
ARRIVAL_RATE = 0.005

#A basic counter with one station and an infinite queue:
basicCounter = WorkStation(arrivalRate = 0.25, serviceRate = 0.5)
print "Basic queue waiting time:", basicCounter.computeTimeWaiting()
print "Basic queue time in system: ", basicCounter.computeTimeInSystem()
print "--------"





'''
#Chipotle example
chipotleStations = [
        WorkStation(arrivalRate = ARRIVAL_RATE,
            serviceRate = 1/5.0), # burrito/bowl/tacos
        WorkStation(arrivalRate = ARRIVAL_RATE,
            serviceRate = 1/8.0), # rice + meat
        WorkStation(arrivalRate = ARRIVAL_RATE,
            serviceRate = 1/12.0), # salsa + salad
        WorkStation(arrivalRate = ARRIVAL_RATE,
            serviceRate = 1/9.0), # wrapping + pricing
        WorkStation(arrivalRate = ARRIVAL_RATE,
            serviceRate = 1.0/10.0), # paying
        ]
printStatistics("Chipotle", chipotleStations)

#Subway:
probabilityOfUsingTheToaster = 0.8
subwayStations = [
        WorkStation(arrivalRate = ARRIVAL_RATE,
            serviceRate = 1/8.0), # What kind of bread? + slice
        WorkStation(arrivalRate = ARRIVAL_RATE,
            serviceRate = 1/17.0), # Meat + cheese
        WorkStation(arrivalRate = ARRIVAL_RATE * probabilityOfUsingTheToaster,
            serviceRate = 1/32.0), # Toaster with 
        WorkStation(arrivalRate = ARRIVAL_RATE,
            serviceRate = 1/17.0), # Salad + dressing
        WorkStation(arrivalRate = ARRIVAL_RATE,
            serviceRate = 1/15.0), # Paying + wrapping 
        ]
printStatistics("Subway", subwayStations)

#Starbucks
starbucksStations = [
        WorkStation(arrivalRate = ARRIVAL_RATE,
            serviceRate = 1/22.0, numberOfServers = 1.0), #order + Paying 
        WorkStation(arrivalRate = ARRIVAL_RATE,
            serviceRate = 1/92.0, numberOfServers = 3.0), #making coffee
        ]
printStatistics("Starbucks", starbucksStations)

#McDonalds
mcDonaldsStations = [
        WorkStation(arrivalRate = ARRIVAL_RATE,
            serviceRate = 1/42.0, numberOfServers = 5.0), #order + Paying 
        WorkStation(arrivalRate = ARRIVAL_RATE,
            serviceRate = 1/122.0, numberOfServers = 5.0), #food is made
        ]
printStatistics("McDonalds", mcDonaldsStations)

#Chopt
choptStations = [
        WorkStation(arrivalRate = ARRIVAL_RATE,
            serviceRate = 1/4.0, numberOfServers = 1.0), #Wait for placement
        WorkStation(arrivalRate = ARRIVAL_RATE/4,
            serviceRate = 1/32.0, numberOfServers = 1.0), #Collect ingredients
        WorkStation(arrivalRate = ARRIVAL_RATE/6,
            serviceRate = 1/47.0, numberOfServers = 1.0), #Chop ingredients
        WorkStation(arrivalRate = ARRIVAL_RATE,
            serviceRate = 1/17.0, numberOfServers = 3.0), #paying + wrapping
        ]
printStatistics("Chopt", choptStations)'''