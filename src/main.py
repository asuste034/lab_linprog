from typing import Literal
from scipy.optimize import linprog, OptimizeResult
import numpy as np

# РЕФЕРЕНСЫ
# https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linprog.html
# https://proglib.io/p/lineynoe-programmirovanie-praktika-resheniya-zadach-optimizacii-na-python-2020-11-26

"""
f = -4x_1 -> max

	2x_1 + x_2 >= 1
	x_1 - 2x_2 <= 3
	x_1 - x_2 >= 1
"""
"""
obj = [4, 0]
lhs_ineq = [[-2, -1],[1, -2],[-1, 1]]
rhs_ineq = [-1, 3, -1]
bnd = [(0, float("inf")), (0, float("inf"))]
optim = linprog(c=obj, A_ub=lhs_ineq, b_ub=rhs_ineq, bounds=bnd)
print(optim)"""

strive_to = ["min", "max"]
method_optim = [
    "highs",
    "highs-ds",
    "highs-ipm",
    "interior-point",
    "revised simplex",
    "simplex",
]


class Optimizer(object):
    def __init__(
        self,
        objects: np.ndarray,
        objects_strive: Literal["min", "max"],
        lhs_ineq: np.ndarray | None = None,
        rhs_ineq: np.ndarray | None = None,
        lhs_eq: np.ndarray | None = None,
        rhs_eq: np.ndarray | None = None,
        bounds: list = [(0, float("inf")), (0, float("inf"))],
        method: Literal[
            "highs",
            "highs-ds",
            "highs-ipm",
            "interior-point",
            "revised simplex",
            "simplex",
        ] = "highs",
    ) -> None:
        self.count = 0
        self.objects = objects  # Вектор неизвестных
        self.objects_strive = objects_strive  # Вектор стремится к -> [min, max]
        self.lhs_ineq = lhs_ineq  # Левая сторона неравенств
        self.rhs_ineq = rhs_ineq  # Правая сторона неравенств
        self.lhs_eq = lhs_eq  # Левая сторона равенств
        self.rhs_eq = rhs_eq  # Правая сторона равенств
        self.method = method
        self.bounds = bounds
        self.last_result = None
        # if len(self.lhs_ineq) != len(self.lhs_ineq):
        #     raise Exception('Неверно сформированна матрица!')

    def __str__(self) -> str:
        letter_obj = [f"a{i}" for i in range(len(self.objects))]
        obj = [
            f'{"+" if (val>=0) else ''}{val}*a{i}' for i, val in enumerate(self.objects)
        ]
        str_func = (
            f"* f({','.join(letter_obj)}) = {''.join(obj)} -> {self.objects_strive}"
        )
        limit_func = []
        for i in range(len(self.lhs_ineq)):
            t = " ".join(
                [
                    f'{"+" if (val>=0) else ''}{val}*a{a}'
                    for a, val in enumerate(self.lhs_ineq[i])
                ]
            )
            t += f" <= {self.rhs_ineq[i]}"
            limit_func.append(t)
        for i in range(len(self.lhs_eq)):
            t = " ".join(
                [
                    f'{"+" if (val>=0) else ''}{val}*a{a}'
                    for a, val in enumerate(self.lhs_eq[i])
                ]
            )
            t += f" = {self.rhs_eq[i]}"
            limit_func.append(t)
        return str_func + "\nОграничение:\n" + "\n".join(limit_func) + "\n"

    def __len__(self) -> int:
        return len(self.objects)

    def __del__(self) -> None:
        del self  # bye bye!

    def solve(self) -> OptimizeResult:
        # obj возвращает значения стремящиеся к min, чтоб сделать максимум надо домножить все на -1
        obj = [(i * -1 if self.objects_strive == "max" else i) for i in self.objects]
        result = linprog(
            c=obj,
            A_ub=(self.lhs_ineq if self.lhs_ineq is not None else None),
            b_ub=(self.rhs_ineq if self.rhs_ineq is not None else None),
            A_eq=(self.lhs_eq if self.lhs_eq is not None else None),
            b_eq=(self.rhs_eq if self.rhs_eq is not None else None),
            bounds=self.bounds,
            method=self.method,
        )
        print(result)
        if not result.success:
            raise OptimizerException(result.message)
        self.count += 1
        self.last_result = result
        return result


class OptimizerException(Exception):
    def __init__(self, value) -> None:
        self.value = value
        self.message = f"linprog вернул ошибку!: {value}"
        super().__init__(self.message)


if __name__ == "__main__":
    test = Optimizer(
        [-0.17, 1, -1.33],
        "min",
        # [[-3.33, -0.88, -0.38],
        #  [1.22, 4.5, -1.33]],
        # [-0.4, -9],
        # [[-2, -0.43, -2.75]], [-5],
        lhs_eq=[[0, 0, -1]],
        rhs_eq=[1],
    )
    print(test.solve())
