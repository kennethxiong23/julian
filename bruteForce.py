"""
    Description:
                This program attempts to find the least cost path starting from the depot and
                ending at u, while visiting every customer inside the set q. It attempts to solve this problem
                using brute force
    Name: Kenneth Xiong
    Date 05/29/22
"""
from itertools import permutations



def bruteForce(depot,q ,u):
    """
    Purpose: Finds the least cost path starting at the depot and ending at u
    Parameters: Depot(list), q(list of lists), end point u(list)
    Return Val: path(list of lists)
    """
    paths = permutations(q)
    minPath = []
    minDist = None
    for path in paths:
        distance = findDistance(depot, path[0])
        for i  in range(0, len(path) -2) :
            distance += findDistance(path[i], path[i+1])
        if minPath == None:
            minDist = distance
            minPath = path
        elif minDist > distance:
            minDist = distance
            minPath = [path]
        elif minDist == distance:
            minPath.append(path)

    return minPath



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
    depot = [0,0] #x,y coordinate is represented by a list
    customers = [[3,2], [3,5], [7,8], [1,3]]

    end = [1,1] #should be apart of customers, ommited for testing
    path = bruteForce(depot, customers, end)
main()
