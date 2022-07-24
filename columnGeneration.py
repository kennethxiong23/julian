"""
Description: This program uses the concept column generation
to solve the capacitated vehicle routing prolbem. In essence, solves the problem
with a subset off all the data points and then adds more and more until it reaches
a solution that applies to every route. For problems where the possible routes
might not even be ennumerable, it can still solve it.
Name: Kenneth
Date: July 16, 2022
"""
from scipy.optimize import linprog, milp, LinearConstraint
import random
from itertools import combinations
import argparse
import numpy as np

#arguement parsing
ap = argparse.ArgumentParser()
ap.add_argument("-n", "--number_of_custs", type=int)
ap.add_argument("-c", "--capacity", type=int)
ap.add_argument("-dm", "--demand_max", type=int)
args = ap.parse_args()

if args.number_of_custs == None:
    args.number_of_custs = 5
if args.capacity == None:
    args.capacity = 10
if args.demand_max == None:
    args.demand_max = 3

def findDistance(x, y):
    """
    Purpose: find the L1 distance between two points
    Parameters: x(list), the starting point, y(list), the end points
    Return Val: The distance(int)
    """
    xDist = abs(x[0] - y[0])
    yDist = abs(x[1] - y[1])
    return xDist + yDist

def getTotalDistance(path):
    """
    Purpose: finds total distance between an ordered set of points
    Parameters: the set of points(list of lists)
    Return Val: The distance(int)
    """
    distance = 0
    for i in range(len(path)-1): # goes through and adds up the individual distance between points
        distance += findDistance(path[i][0], path[i+1][0])
    return distance

def findRoutes(depot, custList, capacity):
    """
    Purpose: Uses column generation to find the least cost path of routes
    Parameters: The depot(list), list of customers, and capacity of each truck
    Return Val: a list with the least cost set of routes
    """
    restrictedRoutes = []
    objCoef = []
    #add coefficient for obj function
    for cust in custList:
        restrictedRoutes.append([depot, cust, depot])
        objCoef.append(-1)
    while True:
        #adds to coefficient of c_l for eahc route, not in obj func, so 0
        for route in restrictedRoutes:
            if len(objCoef) < len(custList) + len(restrictedRoutes):
                objCoef.append(0)
        #coefficient for constraint vars
        constrCoefList = []
        routeNum = 0
        for route in restrictedRoutes:
            constrCoef = []
            for cust in custList:
                if cust in route:
                    constrCoef.append(-1) #aul *piu
                else:
                    constrCoef.append(0)
            filler = [0] * len(restrictedRoutes) #filler for setting the cost coefficient
            filler[routeNum] = 1
            constrCoef += filler
            constrCoefList.append(constrCoef)
            routeNum += 1
            
        #adds coef for setting the value of c_l
        for i in range(len(restrictedRoutes)):
            constrCoef = [0] * len(restrictedRoutes) 
            constrCoef[i] = 1
            filler = [0] * len(custList)
            constrCoef = filler + constrCoef
            constrCoefList.append(constrCoef)
        constrUB = [np.inf] * len(restrictedRoutes)#constraint upper bounds
        constrLB = [0] * len(restrictedRoutes)#constraint lower bounds
        for route in restrictedRoutes: #calculates the cost of each route
            cost = getTotalDistance(route)
            constrUB.append(cost) #sets both the upper and lower bound to cost
            constrLB.append(cost) #makes the cost constant
        constraints = (constrCoefList, constrLB, constrUB)
        integrality = [0]*  len(objCoef) #restrict the sol to be integer
        res = milp(c=objCoef, constraints=constraints, integrality=integrality)
        piList = res["x"][0:len(restrictedRoutes)]
        # routeCostList = rex["x"][len(restrictedRoutes):]
        possibleCustLists = []
        route = [depot]
        endCust = depot
        routeCapacity = capacity
        print(res)
        #tries to create the path that violtes the contraint the most
        while True:
            #calculates resulting value for each partial path
            totalPi = 0
            for cust in route[1:-1]:
                index = custList.index(cust)
                totalPi += piList[index]
            #generates every possible cust to visit next, includes resulting const val
            for i in range(len(custList)):
                if custList[i] not in route:
                    deltaCust = findDistance(endCust[0], custList[i][0]) - (totalPi + piList[i])
                    possibleCustLists.append([custList[i], deltaCust])
            possibleCustLists.sort(key=getDemmand)
            #find worse possible point
            minCust = None
            for cust in possibleCustLists:
                if minCust == None or minCust[1] > cust[1]:
                    minCust = cust
                if minCust[0][1] > routeCapacity:
                    minCust = None
            #if all exceed capacity route is finished
            if minCust != None:
                routeCapacity -= minCust[0][1]
                route.append(minCust[0])
            else:
                #if the most egrigous route meets the constraint optimal sol is found
                cost = getTotalDistance(route)
                totalPi = 0
                for cust in route[1:-1]:
                    index = custList.index(cust)
                    totalPi += piList[index]
                if cost - totalPi == 0:
                    break
                route.append(depot)
                restrictedRoutes.append(route)
                break
            endCust = route[-1]
        #if the most egrigous route meets the constraint optimal sol is found
        cost = getTotalDistance(route)
        totalPi = 0
        for cust in route[1:-1]:
            index = custList.index(cust)
            totalPi += piList[index]
        print(cost - totalPi)
        if cost - totalPi == 0:
            break
        
    c = res["x"][len(cust):]
    A = [] # array of a_ul values for each path
    for cust in custList: #assembles a_ul value by row
        row = []
        for route in restrictedRoutes:
            if cust in route:
                row.append(1) #vals are stored as -1 to invert the defaul inequality
            else:
                row.append(0)
        A.append(row)
    b_l = [1] * len(A)
    b_u = [np.inf] * len(A)
    constraints = (A, b_l, b_u)
    integrality = np.ones_like(c)
    res = milp(c =c, constraints = constraints, integrality = integrality)
    #acutally putting together optimal routes
    routes = []
    for i in range(len(res["x"])):
        if res["x"][i] == 1:
            routes.append(restrictedRoutes[i])
    return (res["fun"], routes)

        
        
#callback that returns demmand of a cust
def getDemmand(e):
    return e[1]

def main():
    #location is a tuple. Each cust is a list of with location and demmand
    depot = ((0,0), 0, "San Diego")
    capacity = 2
    customersList = [((0,1), 1, "Upper West Side"), ((0,1), 1, "Midtown"), ((0,1), 1, "Park Slope")]
    # customersList = [] #list of lists

    #generates a random route with random demand for each cust
    # num  = 1
    # while len(customersList) < args.number_of_custs:
    #     point = (random.randrange(-30,30), random.randrange(-30,30))
    #     demand = random.randrange(1, args.demand_max)
    #     if point not in customersList:
    #         customersList.append((point, demand, "cust %s" %num))
    #     num += 1

   
    routes = findRoutes(depot, customersList, capacity)
    # print(routes)
    print("-----------NY Example-----------")
    print("Customers: %15s %15s %15s %15s" %(depot[2], customersList[0][2], customersList[1][2], customersList[2][2]))
    print("Location: %15s %15s %15s %15s" %(depot[0], customersList[0][0], customersList[1][0], customersList[2][0]))
    print("Demand: %15s %15s %15s %15s" %(depot[1], customersList[0][1], customersList[1][1], customersList[2][1]))
    print("\nTruck Capacity %s" %capacity)
    print("Total Cost: %s" %round(routes[0]))
    print("# of Routes: %s" %len(routes[1]))
    routeString = "routes:"
    routeList = []
    for route in routes[1]:
        routeString += "\nDepot --> "
        for cust in route:
            routeString += "%s --> "
            routeList.append(cust[2])
        routeString += "Depot\n"
    print(routeString %tuple(routeList))



    depot = ((0,0), 0, "San Diego")
    capacity = args.capacity
    customersList = [((0,1), 1, "Upper West Side"), ((0,1), 1, "Midtown"), ((0,1), 1, "Park Slope")]
    customersList = [] #list of lists

    # generates a random route with random demand for each cust
    num  = 1
    while len(customersList) < args.number_of_custs:
        point = (random.randrange(-30,30), random.randrange(-30,30))
        demand = random.randrange(1, args.demand_max)
        if point not in customersList:
            customersList.append((point, demand, "cust %s" %num))
        num += 1
    print("-----------Random Example-----------")
    colors = ["green", "orange", "yellow", "purple", "grey", "lime", "brown"]
    customerString = "Customers: %15s"
    locationString = "Location: %15s"
    demmandString = "Demand: %15s"
    demmandList = [depot[1]]
    locationList = [depot[0]]
    customerList = [depot[2]]
    for cust in customersList:
        customerString += "%15s "
        demmandString += "%15s "
        locationString += "%15s "
        demmandList.append(cust[1])
        customerList.append(cust[2])
        locationList.append(cust[0])
    print(customerString %tuple(customerList))
    print(locationString %tuple(locationList))
    print(demmandString %tuple(demmandList))
    print("\nTruck Capacity %s" %capacity)
    print(routes)

    routes = findRoutes(depot, customersList, capacity)

    assert routes == newRoutes
    print("Total Cost: %s" %round(routes[0]))
    routeString = "routes:"
    routeList = []
    i = 0
    for route in routes:
        routeString += "\n%s: Depot --> "
        routeList.append(colors[i])
        for cust in route:
            routeString += "%s --> "
            routeList.append(cust[2])
        routeString += "Depot\n"
        i += 1
    print(routeString %tuple(routeList))


main()