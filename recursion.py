"""
    Description:
                This program attempts to find the least cost path starting from the depot and
                ending at u, while visiting every customer inside the set q. It attempt this problem
                recursively instead of using brute force.
    Name: Kenneth Xiong
    Date 05/29/22
"""
from time import time
import random
from itertools import permutations
from itertools import combinations
from  turtle import *
import sys

def findDistance(x, y):
    """
    Purpose: find the L1 distance between two points
    Parameters: x(list), the starting point, y(list), the end points
    Return Val: The distance(int)
    """
    xDist = abs(x[0] - y[0])
    yDist = abs(x[1] - y[1])
    return xDist + yDist

def getShortestPath(depot, u, q, num):
    """
    Purpose: Returns the least cost path from the depot to u while visiting all inside of q.
    Parameters: depot(list), the end location, u(list), all the customers, q(dict), num(int) of places
    Return Val: A dictionary of the shortest path.
    """

    if num == 2: #base case
        minPath = []
        minDist = None
        paths = list(permutations(q, 2))
        for path in paths:
            path = list(path)
            distance = getTotalDistance(depot,u, path)
            if minDist == None:
                minDist = distance
                minPath = path
            elif distance < minDist:
                minDist = distance
                minPath = path

        print(minPath)
        return minPath

    else:
        path = getShortestPath(depot, u, q, num - 1)

        for cust in path: #remove already chosen path from the list
            if cust in q:
                q.remove(cust)
        #min from y to u
        minCust = []
        minDist = None
        for cust in q:
            distance = findDistance(cust, u)
            if minDist == None:
                minDist = distance
                minCust = cust
            elif distance > minDist:
                minDist = distance
                minCust = cust
        minDist = None
        minPath = []
        for i in range(0,2):
            for i in range(len(path) + 1):
                possiblePath = path[0:i] + [minCust] + path[i:]
                # distance = getTotalDistance(depot, u, possiblePath)
                distance = getTotalDistance(depot, possiblePath[-1], possiblePath)
                print(num," my way dist: ", distance)
                if minDist == None:
                    minDist = distance
                    minPath = possiblePath
                elif distance < minDist:
                    minDist = distance
                    minPath = possiblePath

            # index1 = path.index(startPath[0])
            # index2 = path.index(startPath[1])
            # path[index1] = startPath[1]
            # path[index2] = startPath[0]

        print(num," minDist ", minDist)
        print(num, "minPath", minPath)
        return minPath

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
            path = tuple(sorted(path))
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
                            distance = findDistance(depot, partialPath[0]) + findDistance(partialPath[0], end)
                            distances[(path, end)] = (distance, y)
                            optimizer = y
                            minDistance = distance
                        else:
                            # previousPath = tuple(list(partialPath).remove(y)
                            distance = distances[(partialPath, y)][0] + findDistance(y, end)
                            # print((partialPath, y), distances[(partialPath, y)][0], findDistance(y, end), end, distance, optimizer , minDistance)
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
    partialPath = tuple(sorted(q))
    #adds u to the tuple
    q = list(sorted(q))
    q.append(u)
    q = tuple(q)
    for y in partialPath: #same code as above
        distance = distances[(partialPath, y)][0] + findDistance(y, u)
        if optimizer == None:
            optimizer = y
            minDistance = distance
        elif distance < minDistance:
            optimizer = y
            minDistance = distance
        # print(minDistance, "hey")
    minKey = (q, u)
    distances[minKey] = (distance, optimizer)
    # print(minKey)
    # print(distances)
    #goes through the dictionary to assemble the final path
    minPath = []
    for i in range(len(q)-1):
        cust = distances[minKey][1]
        minPath.insert(0, cust)
        newPath = list(minKey[0])
        newPath.remove(minKey[1])
        newPath = tuple(newPath)
        minKey = (newPath, cust)

    return minPath

def getTotalDistance(depot, end, path):
    distance = 0 #add edge cases
    for i in range(len(path)-1) :

        distance += findDistance(path[i], path[i+1])

    distance += findDistance(depot,path[0])
    distance += findDistance(path[-1],end)
    return distance

def bruteForce(depot,q ,u):
    """
    Purpose: Finds the least cost path starting at the depot and ending at u
    Parameters: Depot(list), q(list of lists), end point u(list)
    Return Val: path(list of lists)
    """
    # print(q, "paths")
    paths = list(permutations(q))
    # print(paths, "permuted")
    minPath = []
    minDist = None
    for path in paths:
        path = list(path)
        distance = findDistance(depot, path[0])
        for i  in range(0, len(path) -1) :
            distance += findDistance(path[i], path[i+1])
        distance += findDistance(path[-1], u)
        if minDist == None:
            minDist = distance
            minPath = [path]
        elif distance < minDist:
            minDist = distance
            minPath = [list(path)]
        elif minDist == distance:
            minPath.append(list(path))
        distance = None
    print(minDist)
    return minPath

num = int(sys.argv[1])
def main():
    depot = (0,0) #x,y coordinate is represented by a list
    # customers = [(-30, -21), (2, 18), (5, 12), (16, 1), (13, 0)]
    customers =[]
    random.shuffle(customers)
    print(customers)
    end = (10,10) #should be apart of customers, ommited for testing

    print(num)
    while len(customers) < num:
        point= (random.randrange(-30,30), random.randrange(-30,30))
        if point not in customers:
            customers.append(point)
    customers1 = customers
    customers2 = customers1

    time0 = time()
    bruteForcePath = bruteForce(depot,customers1, end)
    time1 = time()
    # path = getShortestPath(depot, end, customers, len(customers))

    path = getShorterPath(depot, customers1, end)
    time2 = time()
    print(getTotalDistance(depot, end, path), "shorts")
    print(path)
    # print(getTotalDistance(depot, end, bruteForcePath[0]), "long")

    # print(distance)
    print(bruteForcePath)
    print(time0, time1)
    print(time1-time0, "bruteForce")
    print(time2-time1, "my way")

    assert path in bruteForcePath
    scale = 15
    colors = ["green", "orange", "yellow", "purple", "grey", "lime", "brown"]
    bruteForceTurtle = Turtle()
    bruteForceTurtle.pensize(15)
    for i in range(len(bruteForcePath)):
        for cust in bruteForcePath[i]:
            bruteForceTurtle.goto(cust[0] * scale, cust[1] * scale)
        bruteForceTurtle.goto(end[0] * scale,end[1] * scale)
        bruteForceTurtle.color(colors[i])
        bruteForceTurtle.pensize(15 - i*2)
        bruteForceTurtle.penup()
        bruteForceTurtle.goto(0,0)
        bruteForceTurtle.pendown()
    myTurtle = Turtle()
    myTurtle.color('red')
    myTurtle.pensize(10)
    for cust in path:
        myTurtle.goto(cust[0] * scale, cust[1] * scale)
    myTurtle.goto(end[0] * scale,end[1] * scale)

    setup = Turtle()
    setup.speed(100)
    setup.color("blue")
    setup.pensize(15)
    points = list(path) + [depot] + [end]
    print(points)
    start = getShortestPath(depot, end, path, 2)
    print(start)
    for point in points:
        if point in start:
            setup.color("yellow")
        setup.penup()
        setup.goto(point[0] * scale, point[1] * scale)
        setup.pendown()
        setup.forward(1)
        setup.color("blue")



    exitonclick()










main()
