import sys
import numpy as np
from PySide6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QSpinBox, QPushButton, QTextEdit, QGroupBox, QFormLayout, QLineEdit
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from crypto.isis import ISISInstance, ISISOracle

class SimpleISISGame(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ISIS Game")
        main_layout = QHBoxLayout(self)

        # Left Panel -> Parameters and History 
        left_panel = QVBoxLayout()

        # Parameters
        param_box = QGroupBox("Parameters")
        param_layout = QFormLayout()
        param_layout.setHorizontalSpacing(40) 
        
        self.n_spin = QSpinBox()
        self.n_spin.setValue(2)
        self.m_spin = QSpinBox()
        self.m_spin.setValue(4)
        self.q_spin = QSpinBox()
        self.q_spin.setValue(97)
        self.k_spin = QSpinBox()
        self.k_spin.setValue(5)
        
        for spin in [self.n_spin, self.m_spin, self.q_spin, self.k_spin]:
            spin.setFixedWidth(80)

        param_layout.addRow(QLabel("<b>n</b> : dimension of x"), self.n_spin)
        param_layout.addRow(QLabel("<b>m</b> : number of equations           "), self.m_spin)
        param_layout.addRow(QLabel("<b>q</b> : modulo used"), self.q_spin)
        param_layout.addRow(QLabel("<b>k</b> : max requests"), self.k_spin)

        self.gen_button = QPushButton("Generate Instance")
        param_layout.addRow(self.gen_button)
        
        self.query_button = QPushButton("Request to Oracle")
        param_layout.addRow(self.query_button)

        self.requests_left_label = QLabel("Requests left: 0")
        param_layout.addRow(self.requests_left_label)

        param_box.setLayout(param_layout)

        # History
        histo_box = QGroupBox("History")
        histo_layout = QVBoxLayout()

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        histo_layout.addWidget(self.output)

        histo_box.setLayout(histo_layout)

        left_panel.addWidget(param_box)
        left_panel.addWidget(histo_box, stretch=1)
        
        # Right Panel -> Game + Goal
        right_panel = QVBoxLayout()
        
        # Goal
        goal_box = QGroupBox("Goal")
        goal_layout = QVBoxLayout()
        self.goal_label = QLabel("Find <b>x, t </b>such that <b>A·x ≡ t mod q</b>")
        goal_layout.addWidget(self.goal_label)
        goal_box.setLayout(goal_layout)
        
        # Game
        game_box = QGroupBox("Game")
        game_layout = QVBoxLayout()

        self.x_input = QLineEdit()
        self.x_input.setFixedHeight(25)
        self.t_input = QLineEdit()
        self.t_input.setFixedHeight(25)
        self.x_input.setPlaceholderText("ex: 1,2")
        self.t_input.setPlaceholderText("ex: 12,34,56,78")
        
        self.dimension_x = QLabel("Input <b>x</b> with dimension: -")
        self.dimension_t = QLabel("Input <b>t</b> with dimension: -")

        game_layout.addWidget(self.dimension_x)
        game_layout.addWidget(self.x_input)
        game_layout.addWidget(self.dimension_t)
        game_layout.addWidget(self.t_input)

        self.verify_button = QPushButton("Check Solution")
        game_layout.addWidget(self.verify_button)

        # Grid
        self.canvas = FigureCanvas(Figure(figsize=(4, 4)))
        self.ax = self.canvas.figure.subplots()
        game_layout.addWidget(self.canvas)

        game_box.setLayout(game_layout)
        
        right_panel.addWidget(goal_box)
        right_panel.addWidget(game_box)

        #  Assemble the two sections 
        main_layout.addLayout(left_panel)
        main_layout.addLayout(right_panel)

        self.instance = None
        self.oracle = None

        self.gen_button.clicked.connect(self.gen_instance)
        self.query_button.clicked.connect(self.query_oracle)
        self.verify_button.clicked.connect(self.verify_solution)

    def gen_instance(self):
        n = self.n_spin.value()
        m = self.m_spin.value()
        q = self.q_spin.value()
        k = self.k_spin.value()

        self.instance = ISISInstance(n, m, q)
        self.oracle = ISISOracle(self.instance.A, q, k)
        self.output.append("New instance generated.")
        self.update_requests_left()
        
        self.dimension_x.setText(f"Input <b>x</b> with dimension: {n}")
        self.dimension_t.setText(f"Input <b>t</b> with dimension: {m}")

        if n == 2:
            self.ax.clear() # Clear the plot
            a1 = self.instance.A[:, 0] # First col of A
            a2 = self.instance.A[:, 1] # Second col of A

            u = np.linspace(-5, 5, 11) 
            v = np.linspace(-5, 5, 11)
            for i in u:
                for j in v:
                    point = i * a1 + j * a2 # Linear combination of a1 and a2
                    if -q//2 <= point[0] <= q//2 and -q//2 <= point[1] <= q//2:  # Filter the points we want to plot
                        self.ax.plot(point[0], point[1], 'ko', markersize=2)

            # Draw base vectors from 0,0
            self.ax.quiver(0, 0, a1[0], a1[1], angles='xy', scale_units='xy', scale=1, color='r')
            self.ax.quiver(0, 0, a2[0], a2[1], angles='xy', scale_units='xy', scale=1, color='b')

            # Set limits and draw
            self.ax.set_xlim(-q//2, q//2)
            self.ax.set_ylim(-q//2, q//2)
            self.ax.set_aspect('equal')
            self.ax.axhline(0, color='black', linewidth=0.1)
            self.ax.axvline(0, color='black', linewidth=0.1)

            # Just for aesthetics
            for spine in self.ax.spines.values():
                spine.set_linewidth(0.5)
                spine.set_color('gray')

            self.ax.grid(False)
            self.canvas.draw()

    def query_oracle(self):
        if not self.oracle:
            self.output.append("Instance not initialized.")
            return
        try:
            t = self.oracle.query()
            self.output.append(f"Oracle output t = {t}")
            self.update_requests_left()
        except Exception as e:
            self.output.append(str(e))

    def verify_solution(self):
        if not self.oracle:
            self.output.append("Instance not initialized.")
            return
        try:
            # Convert user input from string to int -> ex: '1,2' -> [1,2]
            x = np.array([int(i) for i in self.x_input.text().split(',')])
            t = np.array([int(i) for i in self.t_input.text().split(',')])
            
            # Check if the solution is valid
            valid = self.oracle.verify(x, t)
            if valid:
                self.output.append("Valid solution.")
            else:
                self.output.append("Invalid solution.")

            # Draw t if n = 2 and m = 2
            if self.instance and self.instance.n == 2 and self.instance.m == 2:
                try:
                    self.ax.plot(t[0], t[1], marker='x', color='green', markersize=8)
                    self.canvas.draw()
                except Exception as e:
                    self.output.append(f"Error while plotting t: {e}")
                    
        except Exception as e:
            self.output.append(f"Error: {e}")
            
    def update_requests_left(self):
        if self.oracle:
            remaining = self.oracle.k - self.oracle.count
            self.requests_left_label.setText(f"Requests left: {remaining}")
            
            # Disable the button
            self.query_button.setEnabled(remaining > 0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimpleISISGame()
    window.show()
    sys.exit(app.exec())
    