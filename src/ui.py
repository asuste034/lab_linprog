import sys
import numpy as np
from main import Optimizer
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QTableWidget,
    QLabel,
    QHBoxLayout,
    QComboBox,
)


class LPApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Линейное программирование")
        self.resize(900, 600)

        layout = QVBoxLayout()

        strive_layout = QHBoxLayout()
        self.strive_box = QComboBox()
        self.strive_box.addItems(["min", "max"])
        strive_layout.addWidget(QLabel("f(x) -> "))
        strive_layout.addWidget(self.strive_box)
        layout.addLayout(strive_layout)

        layout.addWidget(QLabel("Вектор коэф. функции"))
        self.obj_table = QTableWidget(1, 2)
        self.obj_table.verticalHeader().setVisible(False)
        self.obj_table.horizontalHeader().setVisible(False)
        self.obj_table.verticalHeader().setDefaultSectionSize(25)
        self.obj_table.setFixedHeight(
            self.obj_table.horizontalHeader().height() + 25 + 2
        )
        layout.addWidget(self.obj_table)

        layout.addWidget(QLabel("Ограничения"))
        self.con_table = QTableWidget(0, 4)  # последние 2 колонки: знак и RHS
        layout.addWidget(self.con_table)
        [self.add_row() for _ in range(1)]

        self.method_box = QComboBox()
        self.method_box.addItems(
            [
                "highs",
                "highs-ds",
                "highs-ipm",
                "interior-point",
                "revised simplex",
                "simplex",
            ]
        )
        layout.addWidget(self.method_box)

        btn_layout = QHBoxLayout()
        self.add_row_btn = QPushButton("Добавить ограничение")
        self.add_col_btn = QPushButton("Добавить переменную")
        self.solve_btn = QPushButton("РЕШИТЬ!")

        btn_layout.addWidget(self.add_row_btn)
        btn_layout.addWidget(self.add_col_btn)
        btn_layout.addWidget(self.solve_btn)

        layout.addLayout(btn_layout)

        self.result_label = QLabel("Результат: ", wordWrap=True)
        layout.addWidget(self.result_label)

        self.setLayout(layout)

        self.add_row_btn.clicked.connect(self.add_row)
        self.add_col_btn.clicked.connect(self.add_column)
        self.solve_btn.clicked.connect(self.solve)
        # self.con_table.verticalHeader().sectionClicked.connect(self.on_row_clicked)

    def update_sign_widgets(self):
        sign_column = self.con_table.columnCount() - 2

        for row in range(self.con_table.rowCount()):
            combo = QComboBox()
            combo.addItems(["<=", "=", ">="])
            self.con_table.setCellWidget(row, sign_column, combo)

    def add_row(self):
        row = self.con_table.rowCount()
        self.con_table.insertRow(row)
        self.update_sign_widgets()

    def add_column(self):
        col = self.con_table.columnCount() - 2
        self.con_table.insertColumn(col)
        self.obj_table.insertColumn(col)
        self.update_sign_widgets()

    def on_row_clicked(self, col):
        # не даём удалить знак и RHS
        if col < self.con_table.rowCount() - 2:
            self.con_table.removeRow(col)
            self.obj_table.removeRow(col)

            self.update_sign_widgets()

    def get_float(self, item):
        return float(item.text()) if item and item.text() else 0.0

    def solve(self):
        try:
            # === Целевая функция ===
            c = np.array(
                [
                    self.get_float(self.obj_table.item(0, j))
                    for j in range(self.obj_table.columnCount())
                ]
            )
            bounds = [(0, float("inf")) for _ in range(len(c))]
            strive = self.strive_box.currentText()
            method = self.method_box.currentText()

            # === Ограничения ===
            lhs_ineq = []
            rhs_ineq = []
            lhs_eq = []
            rhs_eq = []

            sign_column = self.con_table.columnCount() - 2
            rhs_column = self.con_table.columnCount() - 1

            for i in range(self.con_table.rowCount()):
                row = [
                    self.get_float(self.con_table.item(i, j))
                    for j in range(self.con_table.columnCount() - 2)
                ]

                widget = self.con_table.cellWidget(i, sign_column)
                sign = widget.currentText() if widget else "<="

                rhs = self.get_float(self.con_table.item(i, rhs_column))

                if sign == "<=":
                    lhs_ineq.append(row)
                    rhs_ineq.append(rhs)
                elif sign == "=":
                    lhs_eq.append(row)
                    rhs_eq.append(rhs)
                elif sign == ">=":
                    lhs_ineq.append([-x for x in row])
                    rhs_ineq.append(-rhs)

            lhs_ineq = np.array(lhs_ineq) if lhs_ineq else None
            rhs_ineq = np.array(rhs_ineq) if rhs_ineq else None
            lhs_eq = np.array(lhs_eq) if lhs_eq else None
            rhs_eq = np.array(rhs_eq) if rhs_eq else None

            opt = Optimizer(
                objects=c,
                objects_strive=strive,
                lhs_ineq=lhs_ineq,
                rhs_ineq=rhs_ineq,
                lhs_eq=lhs_eq,
                rhs_eq=rhs_eq,
                bounds=bounds,
                method=method,
            )
            res = opt.solve()
            print(res)
            self.result_label.setText(
                f"Решение: {res.x}\nЗначение: {res.fun*-1 if strive=='max' else res.fun}"
            )

        except Exception as e:
            self.result_label.setText(f"ОШИБКА: {e}")
            print(res)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LPApp()
    window.show()
    sys.exit(app.exec())
