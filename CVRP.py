"""
    Description: This program contains 3 functions. One of the functions 
                calculates the aul, auvdl and cost given a path. Another one
                calculate the path and cost of said path. The last one finds
                the least cost path given all the auvdl's
    Name: Kenneth Xiong
    Date: 06/14/22
"""
import random
from recursion import *

def calculateRoute():

def optimizeRoute():

def getRouteInfo():

if __name__ == "__main__":
    #location is a tuple. Each cust is a list of with location and demmand
    depot = [(0,0), 0] 
    capacity = 10
    customers = [] #list of lists

    #generates a random route with random demand for each cust
    while len(customers) < 7: 
        point = (random.randrange(-30,30), random.randrange(-30,30))
        demand = random.randrange(1,3)
        if point not in customers:
            customers.append([point, demand])

    
