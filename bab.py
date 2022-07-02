"""
Description: This programs finds the least cost set of routes that visits each customer in a set of
                    customersList once. The demmand of each one of these routes must not excede the capcaity
                    of the trucks visiting the customersList.
Name: Kenneth
Date: 6/29/22
"""
from scipy.optimize import linprog
import random
from itertools import combinations
import argparse
from  turtle import *

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

def getShorterPath(depot, q, u, capacity):
    allFeasibleRoutes = []
    q = tuple(q) #keys need to be immutable
    distanceList = {}
    for i in range(1, len(q) + 1):
        paths = combinations(q, i)
        # keep track of the path that has the lowest distance
        minDist = None
        minKey = None
        #check every combination
        for path in paths:
            # path = tuple(sorted(path))
            for k in range(len(path)):
                end = path[k]
                partialPath = path[0:k] + path[k + 1:]
                #Keep track of leaast cost path
                optimizer = None
                minDistance = None
                #find possible ways to the end point
                for y in path:
                    if len(path) == 1:
                        minDistance = findDistance(depot[0], path[0][0])
                        end = path[0]
                        optimizer = path[0]
                    if y != end:
                        if len(path) == 2: #base case of only two points
                            distance = findDistance(depot[0], partialPath[0][0]) + findDistance(partialPath[0][0], end[0])
                            optimizer = y
                            minDistance = distance
                        else:
                            # previousPath = tuple(list(partialPath).remove(y)
                            distance = distanceList[(partialPath, y)][0] + findDistance(y[0], end[0])
                            # keep track of min optimizer
                            if optimizer == None:
                                optimizer = y
                                minDistance = distance
                            elif distance < minDistance:
                                optimizer = y
                                minDistance = distance
                            #keep track of the least cost path for the end
                            if minDist == None:
                                minDist = distance
                                minKey = (path, end)
                            elif distance < minDist:
                                minDist = distance
                                minKey = (path, end)
                # print(minDistance,optimizer)
                d_0 = capacity     #checks feasibilty of the path
                for cust in path:
                    d_0 -= cust[1]
                if d_0 >= 0:
                    ALREADY_IN = False
                    for route in allFeasibleRoutes: #checks for repeat routes, just w/ different optimizers
                        if path == route[0]:
                            ALREADY_IN = True
                    if ALREADY_IN == False:
                        allFeasibleRoutes.append((path, end))
                    else:
                        ALREADY_IN = False
                distanceList[(path, end)] = (minDistance, optimizer)
    #this section is for the final path, adds u to possible points
    # print(distanceList)
    minDist = None
    optimizer = None
    # partialPath = tuple(q)
    #adds u to the tuple
    # q = list(sorted(q))
    q = list(q)
    q.append(u)
    q = tuple(q)
    for y in partialPath: #same code as above
        distance = distanceList[(partialPath, y)][0] + findDistance(y[0], u[0])
        if optimizer == None:
            optimizer = y
            minDistance = distance
        elif distance < minDistance:
            optimizer = y
            minDistance = distance
        # print(minDistance, "hey")
    minKey = (q, u)
    distanceList[minKey] = (distance, optimizer)

    d_0 = capacity    #checks feasibilty of the path
    for cust in path:
        d_0 -= cust[1]
    if d_0 >= 0:
            ALREADY_IN = False
            for route in allFeasibleRoutes: #checks for repeat routes, just w/ different optimizers
                if path == route[0]:
                    ALREADY_IN = True
            if ALREADY_IN == False:
                allFeasibleRoutes.append((path, end))
            else:
                ALREADY_IN = False
    distanceList[(path, end)] = (minDistance, optimizer)

    return (distanceList, allFeasibleRoutes)

def findDistance(x, y):
    """
    Purpose: find the L1 distance between two points
    Parameters: x(list), the starting point, y(list), the end points
    Return Val: The distance(int)
    """
    xDist = abs(x[0] - y[0])
    yDist = abs(x[1] - y[1])
    return xDist + yDist
def branchAndBound(customersList, allRoutes, allFeasibleRoutes, capacity, depot):
    """
    Purpose: Implementation of branch and bound algorithm
    Parameters: The list of customers, A dictionary with all routes, A list of all feasible routes, the
    capacity of each truck(int), and the depot
    Return Val: the standard return dict of scipy.linprog() just of the optimial integer lp
    """
    branchTree = []
    costList = [] #stores all the cost scalors for all thetas
    branch = [] #stores how many thetas ther are
    for route in allFeasibleRoutes: #goes through and find cost of each route, and adds a theta to branch
        cost = allRoutes[route][0] + findDistance(route[1][0], depot[0])
        costList.append(cost)
        branch.append((0,1))
    A = [] # array of a_ul values for each path
    for cust in customersList: #assembles a_ul value by row
        row = []
        for route in allFeasibleRoutes:
            if cust in route[0]:
                row.append(-1) #vals are stored as -1 to invert the defaul inequality
            else:
                row.append(0)
        A.append(row)
    b = [-1] * len(customersList) #restrics the objective function, array of a_ul * thetas < 1
    res = linprog(costList, A_ub=A, b_ub=b, bounds=branch) #first LP
    branchTree.append((branch, res["fun"], res["x"]))#adds branch to tree
    #initialize zero and one branch
    zeroBranch = []
    oneBranch = []
    n = 1 #interations of while loop
    while True:
        n += 1
        minCost = None
        minIndex = None
        for i in range(len(branchTree)): #finds the index of the lowest cost branch
            if minCost == None or branchTree[i][1] < minCost:
                minCost = branchTree[i][1]
                minCost = i
        currentBranch = branchTree.pop(i) #sets current branch to lowest cost branch
        resVal = currentBranch[2] #value of all theta's after solving the lp
        auls = currentBranch[0] #matrix of all the auls for the paths
        for i in range(len(resVal)): #rounds all the tiny float vals to three decimal places
            resVal[i] = round(resVal[i], 3)
        difference = 1
        ALL_INTS = True
        index = None
        #finds the index of the theta value closest to 0.5 to to branch on, also checks if all are integer
        for i in range(len(resVal)):
            if resVal[i] % 1 != 0:
                ALL_INTS = False
            if 0 < resVal[i] < 1:
                if index == None or resVal[i] % 0.5 < difference :
                    index = i
        #if all are integer that means that optimal integer solution has been reached
        if ALL_INTS == True:
            print("%s branches checked" %n)
            return currentBranch
        #creates the zero and one kids
        for i in range(len(auls)):
            if i == index:
                oneBranch = auls[0:i] + [(1,1)] + auls[i+1:]
                oneBranchRes = linprog(costList, A_ub=A, b_ub=b, bounds=oneBranch)
                zeroBranch = auls[0:i] + [(0,0)] + auls[i+1:]
                zeroBranchRes = linprog(costList, A_ub=A, b_ub=b, bounds=zeroBranch)
                branchTree.append([oneBranch, oneBranchRes["fun"], oneBranchRes['x']])
                branchTree.append([zeroBranch, zeroBranchRes["fun"], zeroBranchRes['x']])

def calculateRoutes(allRoutes, allFeasibleRoutes, solution):
    """
    Purpose: takes the output from the branch and bound finds the actual paths
    Parameters: A dictionary of all the routes, a list of all feasible routes, and the output from branchAndBound()
    Return Val: a list with the routes that constitute the solution.
    """
    routeKeys = []
    visitedRoutes = solution[2]
    for i in range(len(allFeasibleRoutes)):
        if visitedRoutes[i] == 1:
            routeKeys.append(allFeasibleRoutes[i])
    routesList = []
    for key in routeKeys:
        minPath = []
        for i in range(len(key[0])):
            u = key[1]
            y = allRoutes[key][1]
            minPath.insert(0, u)
            newPath = list(key[0])
            newPath.remove(u)
            newPath = tuple(newPath)
            key = (newPath, y)
        routesList.append(minPath)
    return routesList

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

    allRoutes, allFeasibleRoutes = getShorterPath(depot, customersList, depot, capacity)
    optimalSol = branchAndBound(customersList, allRoutes, allFeasibleRoutes, capacity, depot)
    routes = calculateRoutes(allRoutes, allFeasibleRoutes, optimalSol)
    print(routes)
    print("-----------NY Example-----------")
    print("Customers: %15s %15s %15s %15s" %(depot[2], customersList[0][2], customersList[1][2], customersList[2][2]))
    print("Location: %15s %15s %15s %15s" %(depot[0], customersList[0][0], customersList[1][0], customersList[2][0]))
    print("Demand: %15s %15s %15s %15s" %(depot[1], customersList[0][1], customersList[1][1], customersList[2][1]))
    print("\nTruck Capacity %s" %capacity)
    print("Total Cost: %s" %round(optimalSol[1],3))
    print("# of Routes: %s" %len(routes))
    routeString = "routes:"
    routeList = []
    for route in routes:
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
    allRoutes, allFeasibleRoutes = getShorterPath(depot, customersList, depot, capacity)
    optimalSol = branchAndBound(customersList, allRoutes, allFeasibleRoutes, capacity, depot)
    routes = calculateRoutes(allRoutes, allFeasibleRoutes, optimalSol)
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
    print("Total Cost: %s" %round(optimalSol[1],3))
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
    scale = 15
    for i in range(len(routes)):
        turtle = Turtle()
        turtle.speed(5)
        turtle.color(colors[i])
        turtle.pensize(15)
        for cust in routes[i]:
            turtle.goto(cust[0][0] * scale, cust[0][1] * scale)
        turtle.goto(0,0)
    turtle = Turtle()
    turtle.pensize(15)
    turtle.speed(1000)
    for cust in customersList:
                turtle.forward(1)
                turtle.penup()
                turtle.goto(cust[0][0] * scale, cust[0][1] * scale)
                turtle.pendown()
    turtle.forward(1)
    exitonclick()



main()
