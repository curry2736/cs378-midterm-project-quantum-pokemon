from Quantum import fiftyPercentAtk, measure, nullify, reflect, twentyFivePercentAtk
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, Aer, execute
import numpy as np
import matplotlib.pyplot as plt
from qiskit.visualization import plot_histogram
from qiskit.quantum_info import Statevector
import sys
import random
from PySide6 import QtCore, QtWidgets, QtGui 

move_history_map = { 
    "50%": 10,
    "25%": 20
}

def dmg_cnts(measure_results, move_history, first_player, type_list):
    bases = [0, 0]
    multipliers = []
    multipliers.append(types[type_list[first_player]]["attack"])
    multipliers.append(types[type_list[1 - first_player]]["attack"])
    final_dmg = [0, 0]
    if move_history[-1] == "reflect":
        multipliers[0], multipliers[1] = multipliers[1], multipliers[0]
        bases[0] = move_history_map[move_history[-2]]
    elif move_history[-1] == "nullify":
        bases[1] = move_history_map[move_history[-2]]
    else:
        bases[0] = move_history_map[move_history[-1]]
        bases[1] = move_history_map[move_history[-2]]
    final_dmg[0] = measure_results[0] * bases[0] * multipliers[0]
    final_dmg[1] = measure_results[1] * bases[1] * multipliers[1]
    return final_dmg

aux = 2
atk = 1
defense = 0
move_count = 0
moves = {'a': 10, 'b': 15, 'c': 20, 'd': 25}
quantum_moves = ['25%', '50%', 'reflect', 'nullify']

# lightning strike: high chance other player gets hit, low chance you get hit 

# breakout room banishment: forces you to skip a turn

types = {
    "Pikachu": {
        "health": 50,
        "attack": 0.9,
        "defense": 0.33
    },
    "Dr. Davis":  {
        "health": 40,
        "attack": 1.125,
        "defense": 0.2
    }
}

#start game


class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.hello = ["Hallo Welt", "Hei maailma", "Hola Mundo", "Привет мир"]

        self.button = QtWidgets.QPushButton("Start game!")
        self.text = QtWidgets.QLabel("Welcome to Quantum Pokemon!",
                                     alignment=QtCore.Qt.AlignCenter)

        self.layout = QtWidgets.QVBoxLayout(self)
        #self.input = QtWidgets.QLineEdit(self, alignment=QtCore.Qt.AlignCenter)
        
        self.hbox = QtWidgets.QHBoxLayout(self)
        self.playerBox = QtWidgets.QHBoxLayout(self)
        self.p1Box = QtWidgets.QVBoxLayout(self)
        self.p2Box = QtWidgets.QVBoxLayout(self)


        self.typeButton1 = QtWidgets.QPushButton("Dr. Davis")
        self.typeButton2 = QtWidgets.QPushButton("Pikachu")

        self.type_list = ["", ""]
        self.health_list = []
        self.player = random.randint(0, 1)
        self.qc = QuantumCircuit(3, 2)
        self.move_history = []
        self.move_count = 0

        self.p1Health = QtWidgets.QLabel(alignment=QtCore.Qt.AlignCenter)
        self.p2Health = QtWidgets.QLabel(alignment=QtCore.Qt.AlignCenter)


        self.layout.addWidget(self.text)
        self.layout.addLayout(self.playerBox)
        self.playerBox.addLayout(self.p1Box)
        self.playerBox.addLayout(self.p2Box)


       # self.layout.addWidget(self.input)
        self.layout.addWidget(self.button)
        self.layout.addLayout(self.hbox)


        self.button.clicked.connect(self.startGame)

    @QtCore.Slot()
    def startGame(self):
        self.text.setText("Player 1, select your type")
        self.hbox.addWidget(self.typeButton1) 
        self.hbox.addWidget(self.typeButton2)
        self.typeButton1.clicked.connect(lambda: self.setPlayerOneType("Dr. Davis"))
        self.typeButton2.clicked.connect(lambda: self.setPlayerOneType("Pikachu"))

        self.button.setParent(None)

    def setPlayerOneType(self, selected_type):
        self.type_list[0] = selected_type
        self.text.setText("Player 2, select your type")
        self.typeButton1.clicked.disconnect()
        self.typeButton2.clicked.disconnect()
        self.typeButton1.clicked.connect(lambda: self.setPlayerTwoType("Dr. Davis"))
        self.typeButton2.clicked.connect(lambda: self.setPlayerTwoType("Pikachu"))

    def setPlayerTwoType(self, selected_type):
        self.type_list[1] = selected_type

        self.text.setText(f"Player {self.player + 1} is up")
        self.health_list = [types[self.type_list[0]]["health"], types[self.type_list[1]]["health"]]

        self.p1Health.setText(str(self.health_list[0]))
        self.p1Box.addWidget(self.p1Health)
        self.p2Health.setText(str(self.health_list[1]))
        self.p2Box.addWidget(self.p2Health)

        self.typeButton1.setParent(None)
        self.typeButton2.setParent(None)
        self.initGameLoop()
    
    def initGameLoop(self):
        twentyFiveButton = QtWidgets.QPushButton("25%")
        fiftyButton = QtWidgets.QPushButton("50%")
        reflectButton = QtWidgets.QPushButton("reflect")
        nullifyButton = QtWidgets.QPushButton("nullify")

        twentyFiveButton.clicked.connect(lambda: self.makeMove("25%"))
        fiftyButton.clicked.connect(lambda: self.makeMove("50%"))
        reflectButton.clicked.connect(lambda: self.makeMove("reflect"))
        nullifyButton.clicked.connect(lambda: self.makeMove("nullify"))
        
        self.hbox.addWidget(twentyFiveButton)
        self.hbox.addWidget(fiftyButton)
        self.hbox.addWidget(reflectButton)
        self.hbox.addWidget(nullifyButton)

    def makeMove(self, move):
        if move == '50%':
            fiftyPercentAtk(self.qc, types[self.type_list[self.player]]["attack"], self.player)
        elif move == 'reflect':
            reflect(self.qc, types[self.type_list[self.player]]["defense"], self.player)
        elif move == '25%':
            twentyFivePercentAtk(self.qc, types[self.type_list[self.player]]["attack"], self.player)
        elif move == 'nullify':
            nullify(self.qc, types[self.type_list[self.player]]["defense"], self.player, self.move_history[-1])
        self.move_history.append(move)
        self.player = 1 - self.player
        self.move_count += 1
        

        if self.move_count > 0 and self.move_count % 2 == 0:
            results = measure(self.qc, self.move_history)
            first_player = 1 - ((self.move_count % 4) // 2)
            dmgs = dmg_cnts(results, self.move_history, first_player, self.type_list)
            print("Player " + str(first_player + 1) + " received " + str(dmgs[0]) + " damage")
            print("Player " + str((1 - first_player) + 1) + " received " + str(dmgs[1]) + " damage")
            self.health_list[first_player] -= dmgs[0]
            self.health_list[1 - first_player] -= dmgs[1]
            self.p1Health.setText(str(self.health_list[0]))
            self.p2Health.setText(str(self.health_list[1]))

            if self.health_list[0] <= 0 or self.health_list[1] <= 0:
                print("done lol")

            self.qc = QuantumCircuit(3,2)
        if self.move_count > 0 and self.move_count % 4 == 0: # keeps the game fair
            self.player = 1 - self.player
        self.text.setText(f"Player {self.player + 1} is up")

    





app = QtWidgets.QApplication([])
widget = MyWidget()
widget.resize(800, 600)
widget.show()
sys.exit(app.exec())



    
if (health_list[0] > 0) :
    print("Player 2 died, Player 1 won!")
elif (health_list[1] > 0):
    print("Player 1 died, Player 2 won!")
else: 
    print("You both died, you suck lol!")
