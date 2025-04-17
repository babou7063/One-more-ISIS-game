import sys
import numpy as np
from PySide6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QSpinBox, QPushButton, QTextEdit
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from crypto.isis import ISISInstance, ISISOracle

class SimpleISISGame(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ISIS Game")
        main_layout = QHBoxLayout(self)

        # Left column -> param + histo
        left_layout = QVBoxLayout()
        self.n_spin = QSpinBox(); self.n_spin.setValue(2)
        self.m_spin = QSpinBox(); self.m_spin.setValue(4)
        self.q_spin = QSpinBox(); self.q_spin.setValue(97)
        self.k_spin = QSpinBox(); self.k_spin.setValue(5)

        for label, spin in [("n = Dimension of x", self.n_spin), ("m = Number of equations", self.m_spin), ("q = Modulo used", self.q_spin), ("k = Maximum number of requests", self.k_spin)]:
            left_layout.addWidget(QLabel(label))
            left_layout.addWidget(spin)

        left_layout.addWidget(QLabel("Historic"))
        self.output = QTextEdit(); self.output.setReadOnly(True)
        left_layout.addWidget(self.output)

        # Right column -> graph + buttons
        right_layout = QVBoxLayout()
        self.canvas = FigureCanvas(Figure(figsize=(3, 3)))
        self.ax = self.canvas.figure.subplots()
        right_layout.addWidget(self.canvas)

        self.gen_button = QPushButton("Generate an instance")
        self.query_button = QPushButton("Request to oracle")
        right_layout.addWidget(self.gen_button)
        right_layout.addWidget(self.query_button)

        right_layout.addWidget(QLabel("x (separated by ' , ')"))
        self.x_input = QTextEdit(); self.x_input.setFixedHeight(30)
        right_layout.addWidget(self.x_input)

        right_layout.addWidget(QLabel("t (separated by ' , ')"))
        self.t_input = QTextEdit(); self.t_input.setFixedHeight(30)
        right_layout.addWidget(self.t_input)

        self.verify_button = QPushButton("Check solution")
        right_layout.addWidget(self.verify_button)
        self.verify_button.clicked.connect(self.verify_solution)

        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

        self.instance = None
        self.oracle = None

        self.gen_button.clicked.connect(self.gen_instance)
        self.query_button.clicked.connect(self.query_oracle)

    def gen_instance(self):
        n = self.n_spin.value()
        m = self.m_spin.value()
        q = self.q_spin.value()
        k = self.k_spin.value()

        self.instance = ISISInstance(n, m, q)
        self.oracle = ISISOracle(self.instance.A, q, k)
        self.output.append("New instance generated.")

        if n == 2:
            self.ax.clear()
            a1, a2 = self.instance.A[:,0], self.instance.A[:,1]
            self.ax.quiver(0, 0, a1[0], a1[1], angles='xy', scale_units='xy', scale=1, color='r')
            self.ax.quiver(0, 0, a2[0], a2[1], angles='xy', scale_units='xy', scale=1, color='b')
            self.ax.set_xlim(-q//2, q//2)
            self.ax.set_ylim(-q//2, q//2)
            self.ax.set_aspect('equal')
            self.ax.grid(True)  # On affiche la grille
            self.canvas.draw()

    def query_oracle(self):
        if not self.oracle:
            self.output.append("Instance not initialized.")
            return
        try:
            t = self.oracle.query()
            self.output.append(f"Oracle output t = {t}")
        except Exception as e:
            self.output.append(str(e))

    def verify_solution(self):
        if not self.oracle:
            self.output.append("Instance not initialized.")
            return
        try:
            x = np.array([int(i) for i in self.x_input.toPlainText().split(',')])
            t = np.array([int(i) for i in self.t_input.toPlainText().split(',')])
            valid = self.oracle.verify(x, t)
            if valid:
                self.output.append("Valid solution.")
            else:
                self.output.append("Invalid solution.")
        except Exception as e:
            self.output.append(f"Error: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimpleISISGame()
    window.show()
    sys.exit(app.exec())
