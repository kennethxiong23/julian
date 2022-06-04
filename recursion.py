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
from  turtle import *

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
        minDist = None
        cust1 = []
        cust2 = []
        for startCust in q: #brute force combinations
            for cust in q:
                if cust != startCust:
                    distance = findDistance(depot, startCust) + findDistance(startCust, cust) + findDistance(cust, u)
                    if minDist == None: #first run edge case
                        minDist = distance
                        cust1 = startCust
                        cust2 = cust
                    elif distance < minDist: #compare for lowest value
                        distance = minDist
                        cust1 = startCust
                        cust2 = cust
        path = [cust1, cust2]
        print(path)
        return path

    else:
        startPath = getShortestPath(depot, u, q, 2)
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
            elif distance < minDist:
                minDist = distance
                minCust = cust
        minDist = None
        minPath = []
        for i in range(0,2):
            for i in range(len(path) + 1):
                possiblePath = path[0:i] + [minCust] + path[i:]
                # distance = getTotalDistance(depot, u, possiblePath)
                distance = getTotalDistance(possiblePath[0], possiblePath[-1], possiblePath)
                # print(num," my way dist: ", distance)
                if minDist == None:
                    minDist = distance
                    minPath = possiblePath
                elif distance < minDist:
                    minDist = distance
                    minPath = possiblePath

            index1 = path.index(startPath[0])
            index2 = path.index(startPath[1])
            path[index1] = startPath[1]
            path[index2] = startPath[0]

        # print(num," minDist ", minDist)
        print(num, "minPath", minPath)
        return minPath



        # for cust in q: #fix this too
        #     distance = findDistance(depot, path[0])
        #     for i in range(0, len(path)-2):
        #         distance += findDistance(path[i], path[i+1])
        #     distance += findDistance(path[-1], cust) + findDistance(cust, u)
        #     if minDist == None:
        #         minDist = distance
        #         minCust = cust
        #     elif distance < minDist:
        #         minDist = distance
        #         minCust = cust
        # path.append(minCust)

        return path

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
    print("brute force", minDist)
    return minPath


def main():
    depot = [0,0] #x,y coordinate is represented by a list
    # customers = [[3,22], [332,5], [3217,8], [21,3]]
    customers = []
    end = [10,10] #should be apart of customers, ommited for testing
    while len(customers) < 7:
        point= [random.randrange(-30,30), random.randrange(-30,30)]
        if point not in customers:
            customers.append(point)
    customers1 = customers
    customers2 = customers1

    time0 = time()
    bruteForcePath = bruteForce(depot,customers1, end)
    time1 = time()
    path = getShortestPath(depot, end, customers, len(customers))
    time2 = time()


    # print(distance)
    print(bruteForcePath)
    print(path)
    print(time1-time0, "bruteForce")
    print(time2-time1, "my way")

    print(path in bruteForcePath)
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
    points = path + [depot] + [end]
    print(points)
    start = getShortestPath(depot, end, path, 2)
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
