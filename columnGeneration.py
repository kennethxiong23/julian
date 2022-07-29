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
from itertools import permutations
import argparse
import numpy as np
from time import time

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

def getLastElement(L):
    """
    Purpose: returns the last element in a list
    Parameters: the list
    return Val: the last item in the list
    """
    return L[-1]

def findRoutes(depot, custList, capacity):
    """
    Purpose: Uses column generation to find the least cost path of routes
    Parameters: The depot(list), list of customers, and capacity of each truck
    Return Val: a list with the least cost set of routes
    """
    #preprocessing to find Q for pricing
    Q = []
    possiblePairs = permutations(custList, 2)
    for cust in custList:   # u,v,d pairs where u is the depot
        Q.append([depot, cust, capacity])
    for cust in custList:   # u,v,d pairs where v is the depot
        d = capacity - cust[1]
        for i in range(0, d + 1):
            Q.append([cust, depot, i])
    for pair in possiblePairs:  #u,v,d pairs for every cust pair
        d = capacity - pair[0][1] #total capacity - demand of first cust
        for i in range(0, d + 1):
            Q.append([pair[0], pair[1], i])
    restrictedRoutes = []
    objCoef = []
    #add coefficient for obj function
    for cust in custList:
        restrictedRoutes.append([depot, cust, depot])
    flag = 0
    bool = True
    prevCost = None
    prevAdded = None
    while bool:
        #adds to coefficient of c_l for each route, not in obj func, so 0
        objCoef = [-1] * len(custList)
        #coefficient for constraint vars
        constrCoefList = []
        for route in restrictedRoutes:
            constrCoef = []
            for cust in custList:
                if cust in route:
                    constrCoef.append(1) #aul *piu
                else:
                    constrCoef.append(0)
            constrCoefList.append(constrCoef)
        #sets c_l to be the bound of each constraint
        constrUB = []#constraint upper bounds
        constrLB = []#constraint lower bounds
        for route in restrictedRoutes: #calculates the cost of each route
            cost = getTotalDistance(route)
            constrUB.append(cost) #sets both the upper to cost
            constrLB.append(-np.inf)
        constraints = (constrCoefList, constrLB, constrUB)
        integrality = [0]*  len(objCoef) #restrict the sol to be integer
        res = milp(c=objCoef, constraints=constraints, integrality=integrality)
        piList = res["x"][0:len(restrictedRoutes)]
        #pricing to find lowest reduced cost route
        objCoef = []
        constraints = []
        constrUB = []
        constrLB = []
        for u,v,d in Q:
            #calculates the reduced cost for each pair
            if v != depot:  #if v is the depot don't need to get pi
                piV = piList[custList.index(v)]     #indexing of piList matches that of custList
                reducedCost = findDistance(u[0],v[0]) - piV
            else:
                reducedCost = findDistance(u[0],v[0])
            objCoef.append(reducedCost)
        depotConstCoef = [] #constraint from equation 13b, must start at depot
        #must equal one
        constrLB.append(1)
        constrUB.append(1)
        #adds only points starting at the depot with full capacity
        for u,v,d in Q:
            if u == depot and d == capacity:
                depotConstCoef.append(1)
            else:
                depotConstCoef.append(0)
        constraints.append(depotConstCoef)
        for cust in custList:  #constr from 13c, must vist each cust at most once
            numConstCoef = []
            for u,v,d in Q:     #for loop to check all u in uvd, cust can only be u once
                if cust == u:
                    numConstCoef.append(1)
                else:
                    numConstCoef.append(0)
            constraints.append(numConstCoef)
            constrLB.append(0) #can be between 0 or 1
            constrUB.append(1)
        for cust in custList:   #constr from 13d, must service a visted customer
            #get all uvd with cust set to be v
            for i in range(0, capacity  + 1):
                demConstCoef = []
                for u,v,d in Q:
                    if d == i and v == cust:
                        demConstCoef.append(1)
                    elif d == i - u[1] and u == cust:   #get all uvd where u is the cust
                        demConstCoef.append(-1)
                    else:
                        demConstCoef.append(0)
                constraints.append(demConstCoef)
                #must equal 0
                constrLB.append(0)
                constrUB.append(0)
        integrality = [3] * len(objCoef)    #enfore integer solution
        res = milp(c=objCoef, constraints=[constraints, constrLB, constrUB], bounds = (0,1), integrality=integrality)
        uvdList = []
        route = []
        for i in range(0, len(res["x"])):   #find which uvd in q corresponds to the one and zero
            if res["x"][i] == 1 or  res["x"][i] > 0.5:
                uvdList.append(Q[i])
        uvdList.sort(reverse=True, key=getLastElement) #sort from highest to lowest demand
        for uvd in uvdList:     #assemble the route
            route.append(uvd[0])
        #iteration termination when cost is 0 or cost is very small and no longer chaning
        if round(res["fun"], 10) == 0:
            print("optimal set has been found after %s iterations" %flag)
            break
        if prevCost = res["fun"] and prevAdded == route:
            if res["fun"] < 0:
                print("optimal set has been found after %s iterations" %flag)
                break
        prevCost = res["fun"]
        prevAdded = route
        route.append(depot)
        restrictedRoutes.append(route)

        print("added %s with cost %s to restrictedRoutes" %(route, res["fun"]))
        print("iteration %s" %flag)
        flag += 1
    #calculates route with restricted set
    objCoef = []
    constraints = []
    constrLB = []
    constrUB = []
    for route in restrictedRoutes:
        cost = getTotalDistance(route)
        objCoef.append(cost)
    for cust in custList: #assembles a_ul value by row
        row = []
        for route in restrictedRoutes:
            if cust in route:
                row.append(1) #vals are stored as -1 to invert the defaul inequality
            else:
                row.append(0)
        constraints.append(row)
    constrLB =[1] * len(constraints)
    constrUB = [1] * len(constraints)
    integrality = [1] * len(objCoef)
    res = milp(c=objCoef, constraints=[constraints, constrLB, constrUB], integrality=integrality)
    #calculate the rotes
    allRoutes = []
    for i in range(0,len(res["x"])):
        if res["x"][i] == 1:
            allRoutes.append(restrictedRoutes[i])

    return (allRoutes, res["fun"])



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
    print("Total Cost: %s" %round(routes[1]))
    print("# of Routes: %s" %len(routes[0]))
    routeString = "routes:"
    routeList = []
    for route in routes[0]:
        routeString += "\n"
        for cust in route:
            routeString += "%s --> "
            routeList.append(cust[2])
        routeString += "\n"
    print(routeString %tuple(routeList))



    depot = ((0,0), 0, "San Diego")
    capacity = args.capacity
    customersList = [((0,1.05), 1, "Upper West Side"), ((0,0.96), 1, "Midtown"), ((0,1), 1.3, "Park Slope")]
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
    t0 = time()
    routes = findRoutes(depot, customersList, capacity)
    t1 = time()
    print(t1-t0)
    print("Total Cost: %s" %round(routes[1]))
    routeString = "routes:"
    routeList = []
    i = 0
    for route in routes[0]:
        routeString += "\n%s: "
        routeList.append(colors[i])
        for cust in route:
            routeString += "%s --> "
            routeList.append(cust[2])
        routeString += "\n"
        i += 1
    print(routeString %tuple(routeList))


main()
