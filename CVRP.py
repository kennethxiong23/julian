"""
    Description: This program contains 3 functions. One of the functions calculates the aul, auvdl and
                        cost of a given path. Another one calculates the path and cost of said path. The last
                        one finds the least cost path given all the auvdl's. All three of these functions also
                        validate the feasbilty of the paths
    Name: Kenneth Xiong
    Date: 06/14/22
"""
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


def calculateRoute(auvdl, depot, capacity):
    """
    Purpose: Calculates the route, the cost, and feasibility of a route given a list of the route's auvdl
    values.
    Parameters: a list of all auvdl values that are one, the depot[list]
    Return Val: a list with the ordered route and the cost of the route or -1 if route is not feasible
    """
    auvdl.sort(reverse = True, key = getLastElement) #sorts d val from largest to smallest for route construction
    route = []
    aul = []
    for uvd in auvdl: #builds the route from the auvdl
        if uvd[2] < 0: #checks if demmand ever exceeds capacity
            return -1
        if capacity != uvd[2]: #make ssure d lines up
            return -1
        if uvd[0] == uvd[1]: #can't start and end at same place
            return -1
        if uvd[0] in aul: #can't start from the same place multiple times
            return -1
        if uvd != depot:
            if auvdl[len(route) - 1][1] != uvd[0]: #makes sure the previous end and current start are the same
                return -1
        route.append(uvd[0]) #adds the u term to the route
        if uvd == auvdl[-1]: #adds the v term of the last auvdl term
            route.append(uvd[1])
        capacity -= uvd[1][1]
        aul.append(uvd[0])
    if validateRoute(route, depot) == False: #makes sure route meets equations (5, 6, 7)
        return -1
    else:
        cost = getTotalDistance(route) #equation 4
    return [route, cost]

def optimizeRoute(aul, depot, capacity):
    """
    Purpose: Calculates the least cost feasible route given a set of aul values
    Parameters: a list of aul values that are one and the depot(list)
    Return Val: If there is no feasible path, -1, otherwise a list with two elements: the route and auvdl's
    """
    #function returns routes in sorted order from shortest to longest
    possibleRoutesLists = getShorterPath(depot, aul, depot) #gets paths of the shortest possible routes
    for route in possibleRoutesLists: #checks each one for feasibility
        route = route[0]
        route = [depot] + route + [depot] # change format to meet the getRouteInfo()
        routeInfo = getRouteInfo(route, depot, capacity)
        return routeInfo[1:] #returns everything besides the aul val
    return -1

def getRouteInfo(route, depot, capacity):
    """
    Purpose: Calculates the Auvdl, Aul and cost of a given path. It also checks whether or not the path
    is feasible.
    Parameters: the route to evaluate(list of lists), the depot of the route(list),
    the capacity of the vehicle(int)
    Return Val: If the path is not feasible, -1, otherwise a tuple with three elements: a list with all aul's
    that are one, a list with all auvdl's equal to one, and the cost(int).
    """
    if validateRoute(route, depot) == False:
        return -1
    aul = []
    auvdl = []
    for i in range(len(route) - 1): #iterates through all cust's
        cust = route[i]
        capacity -= cust[1]
        if capacity < 0: # must be more capacity than demand
            return -1
        if cust != depot: # depot is not included in the set of custs
            aul.append(cust)
        auvdl.append([cust, route[i + 1], capacity])
    cost = getTotalDistance(route) #equation 4
    return [aul, auvdl, cost]

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

def validateRoute(route, depot):
    """
    Purpose: Checks if the route does not repeat customers and starts and ends at the depot.
    Parameters: the route to evaluate(list of lists), the depot of the route(list)
    Return Val: True if the route meets all the conditions listed, false otherwise.
    """
    checker = []
    for cust in route[1:-1]: #checks if a customer has already occured in the route(equation 7)
        if cust in checker:
            return False
        checker.append(cust)
    #makes sure that the first and last place is the depot (equation 5 + 6)
    if route[0] != route[-1] or route[0] != depot or route[-1] != depot:
        return False
    return True

def getShorterPath(depot, q, u):
    q = tuple(q) #keys need to be immutable
    distances = {}
    for i in range(2, len(q) + 1):
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
                    if y != end:
                        if len(path) == 2: #base case of only two points
                            distance = findDistance(depot[0], partialPath[0][0]) + findDistance(partialPath[0][0], end[0])
                            distances[(path, end)] = (distance, y)
                            optimizer = y
                            minDistance = distance
                        else:
                            # previousPath = tuple(list(partialPath).remove(y)
                            distance = distances[(partialPath, y)][0] + findDistance(y[0], end[0])
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
                distances[(path, end)] = (minDistance, optimizer)
    #this section is for the final path, adds u to possible points
    # print(distances)
    minDist = None
    optimizer = None
    # partialPath = tuple(q)
    #adds u to the tuple
    # q = list(sorted(q))
    q = list(q)
    q.append(u)
    q = tuple(q)
    possiblePathList = []
    for y in partialPath: #same code as above
        distance = distances[(partialPath, y)][0] + findDistance(y[0], u[0])
        key = (q, u, y)
        distances[key] = (distance, y)
        path = []
        for i in range(len(q)-1):
            cust = distances[key][1]
            path.insert(0, cust)
            newPath = list(key[0])
            newPath.remove(key[1])
            newPath = tuple(newPath)
            key = (newPath, cust)
        possiblePathList.append([path, distance])
    possiblePathList.sort(key = getLastElement)

    return possiblePathList

def getLastElement(L):
    """
    Purpose: returns the last element in a list
    Parameters: the list
    return Val: the last item in the list
    """
    return L[-1]

if __name__ == "__main__":
    #location is a tuple. Each cust is a list of with location and demmand
    depot = ((0,0), 0)
    capacity = args.capacity
    customers = [] #list of lists

    #generates a random route with random demand for each cust
    while len(customers) < args.number_of_custs:
        point = (random.randrange(-30,30), random.randrange(-30,30))
        demand = random.randrange(1, args.demand_max)
        if point not in customers:
            customers.append((point, demand))
    route = [depot] + customers + [depot]

    print("----------Starting Route----------")
    pointsStr = "%6s" %"Points:"
    demandStr = "%s" %'Demand:'
    points = []
    demmand = []
    for cust in route:
        pointsStr += "%15s"
        points.append(str(cust[0]))
        demandStr += "%15s"
        demmand.append(str(cust[1]))
    print(pointsStr %tuple(points))
    print(demandStr %tuple(demmand))

    print("----------getRouteInfo()------------")
    print("input:\nroute-%s\ndepot-%s\ncapacity-%s" %(route, depot, capacity))
    routeInfo = getRouteInfo(route,depot,capacity)
    if routeInfo != -1:
        print('\nOutput:\nAul-%s\nAuvdl-%s\ncost-%s' %(routeInfo[0], routeInfo[1], routeInfo[2]))
    else:
        print("\nOutput: -1\nRoute is not feasible")

    #check distances not lining up
    auvdl = [[((0, 0), 0), ((-20, 26), 2), 10], [((-20, 26), 1), ((-2, 16), 1), 8], [((-2, 16), 1), ((-29, -4), 2), 7],
    [((-29, -4), 2), ((10, -9), 2), 5], [((10, -9), 2), ((-3, -22), 1), 3], [((-3, -22), 1), ((0, 0), 0), 2]]
    assert calculateRoute(auvdl, depot, capacity) == -1

    #check going to self
    auvdl = [[((0, 0), 0), ((-20, 26), 2), 10], [((-20, 26), 2), ((-20, 26), 2), 8], [((-2, 16), 1), ((-29, -4), 2), 7],
    [((-29, -4), 2), ((10, -9), 2), 5], [((10, -9), 2), ((-3, -22), 1), 3], [((-3, -22), 1), ((0, 0), 0), 2]]
    assert calculateRoute(auvdl, depot, capacity) == -1

    #check starting from same place twice
    auvdl = [[((0, 0), 0), ((-20, 26), 2), 10], [((-20, 26), 2), ((-2, 16), 1), 8], [((-20, 26), 2), ((-29, -4), 2), 6],
    [((-29, -4), 2), ((10, -9), 2), 5], [((10, -9), 2), ((-3, -22), 1), 3], [((-3, -22), 1), ((0, 0), 0), 2]]
    assert calculateRoute(auvdl, depot, capacity) == -1

    #check not end and starting in the same place
    auvdl = [[((0, 0), 0), ((-20, 26), 2), 10], [((-20, 26), 2), ((-2, 16), 1), 8], [((-2, 85), 1), ((-29, -4), 2), 7],
    [((-29, -4), 2), ((10, -9), 2), 5], [((10, -9), 2), ((-3, -22), 1), 3], [((-3, -22), 1), ((0, 0), 0), 2]]
    assert calculateRoute(auvdl, depot, capacity) == -1

    print("----------calculateRoute()------------")
    if routeInfo == -1:
        print("getRouteInfo() did not return a valid route")
    else:
        print("input:\nauvdl-%s\ndepot-%s" %(routeInfo[1], depot))
        reformedRoute = calculateRoute(routeInfo[1], depot, capacity)
        assert reformedRoute[0] == route
        assert reformedRoute[1] == routeInfo[2]
        if reformedRoute != -1:
            print('\nOutput:\nroute-%s\ncost-%s' %(reformedRoute[0], reformedRoute[1]))

    print("----------optimizeRoute()------------")
    if routeInfo == -1:
        print("getRouteInfo() did not return a valid route")
    else:
        print("input:\nal-%s\ndepot-%s\ncapacity-%s" %(routeInfo[0], depot, capacity))
        optimizedRoute = optimizeRoute(routeInfo[0], depot, capacity)
        if optimizedRoute != -1:
            print('\nOutput:\nroute-%s\ncost-%s' %(optimizedRoute[0], optimizedRoute[1]))

    # test = getRouteInfo(route, depot, capacity)
    # print(test)
    # print(route)
    # test1 = calculateRoute(test[1], depot)
    # assert route == test1[0]
    #
    # test2 = optimizeRoute(test[0], depot, capacity)
    # print(test2)
