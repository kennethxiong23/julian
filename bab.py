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

def main():
    #location is a tuple. Each cust is a list of with location and demmand
    depot = ((0,0), 0, "depot")
    capacity = args.capacity
    customersList = [((0,1), 1, "cust1"), ((0,1), 1, "cust2"), ((0,1), 1, "cust3")]
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
    print(allFeasibleRoutes)
    branchTree = []
    #calcualtes all the cost scalors for thetas
    costList = []
    branch = []
    for route in allFeasibleRoutes:
        cost = allRoutes[route][0] + findDistance(route[1][0], depot[0])
        costList.append(cost)
        branch.append((0,1))
    A = []
    for cust in customersList:
        row = []
        for route in allFeasibleRoutes:
            if cust in route[0]:
                row.append(-1)
            else:
                row.append(0)
        A.append(row)
    b = [-1] * len(customersList)
    print(A,b)
    res = linprog(costList, A_ub=A, b_ub=b, bounds=branch)
    print(res)
    branchTree.append((branch, res["fun"], res["x"]))
    zeroBranch = []
    oneBranch = []
    while True:
        print("i ran")
        minCost = None
        minIndex = None
        for i in range(len(branchTree)):
            if minCost == None or branchTree[i][1] < minCost:
                minCost = branchTree[i][1]
                minCost = i
        currentBranch = branchTree.pop(i)
        resVal = currentBranch[2]
        thetaVals = currentBranch[0]
        print()
        for i in range(len(resVal)):
            resVal[i] = round(resVal[i], 3)
        print(resVal)
        difference = 1
        ALL_INTS = True
        index = None
        for i in range(len(resVal)):
            if resVal[i] % 1 != 0:
                ALL_INTS = False
            if 0 < resVal[i] < 1:
                if index == None or resVal[i] % 0.5 < difference :
                    index = i
        if ALL_INTS == True:
            print('Done at first level')
            print(currentBranch)
            break
        for i in range(len(thetaVals)):
            if i == index:
                oneBranch = thetaVals[0:i] + [(1,1)] + thetaVals[i+1:]
                # print(oneBranch)
                oneBranchRes = linprog(costList, A_ub=A, b_ub=b, bounds=oneBranch)
                # print(oneBranchRes)
                zeroBranch = thetaVals[0:i] + [(0,0)] + thetaVals[i+1:]
                print(zeroBranch)
                zeroBranchRes = linprog(costList, A_ub=A, b_ub=b, bounds=zeroBranch)
                print(zeroBranchRes)
                branchTree.append([oneBranch, oneBranchRes["fun"], oneBranchRes['x']])
                branchTree.append([zeroBranch, zeroBranchRes["fun"], zeroBranchRes['x']])


main()
