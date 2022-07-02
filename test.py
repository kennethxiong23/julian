from scipy.optimize import linprog
def main():
    c = [2,2,2,2,2,2]
    A = [[-1,0,0,-1,-1,0],[0,-1,0,0,-1,-1],[0,0,-1,-1,0,-1]]
    b = [-1,-1,-1]
    x1_bounds = (0,1)
    x2_bounds = (0,1)
    x3_bounds = (0,1)
    x4_bounds = (0,1)
    x5_bounds = (0,1)
    x6_bounds = (0,1)
    res = linprog(c, A_ub=A, b_ub=b, bounds=[x1_bounds, x2_bounds, x3_bounds, x4_bounds, x5_bounds, x6_bounds], options={"tol": 1})
    print(res)
    c = [2,2,2,2,2,2]
    A = [[-1,0,0,-1,-1,0],[0,-1,0,0,-1,-1],[0,0,-1,-1,0,-1]]
    b = [-1,-1,-1]
    x1_bounds = (0,1)
    x2_bounds = (0,1)
    x3_bounds = (0,1)
    x4_bounds = (0,0)
    x5_bounds = (0,1)
    x6_bounds = (0,1)
    res = linprog(c, A_ub=A, b_ub=b, bounds=[x1_bounds, x2_bounds, x3_bounds, x4_bounds, x5_bounds, x6_bounds], options={"tol": 0.01})
    print(res)
    c = [2,2,2,2,2,2]
    A = [[-1,0,0,-1,-1,0],[0,-1,0,0,-1,-1],[0,0,-1,-1,0,-1]]
    b = [-1,-1,-1]
    x1_bounds = (0,1)
    x2_bounds = (0,1)
    x3_bounds = (0,1)
    x4_bounds = (0,0)
    x5_bounds = (0,0)
    x6_bounds = (0,1)
    res = linprog(c, A_ub=A, b_ub=b, bounds=[x1_bounds, x2_bounds, x3_bounds, x4_bounds, x5_bounds, x6_bounds], options={"tol": 0.01})
    print(res)
main()
