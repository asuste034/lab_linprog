from scipy.optimize import linprog

c = [-0.5, -0.83, -1.57]

A = [
    [1.57, 1.33, 1.38],
    [1.29, 2, 1.6]
]

b = [1.2, -1.38]

A_ = [
    [-2, -0.57, 0]
]
b_ = [-4]

# bounds = [(-float("inf"), float("inf")) for _ in range(3)]
res = linprog(c, A_ub=A, b_ub=b, A_eq=A_, b_eq=b_, method='highs')

print(res)