from Quantum import fiftyPercentAtk, measure, nullify, reflect, twentyFivePercentAtk, breakout_room_banishment, infinite_randomness
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, Aer, execute
import numpy as np
import matplotlib.pyplot as plt
from qiskit.visualization import plot_histogram
from qiskit.quantum_info import Statevector
import sys
import random
from PySide6 import QtCore, QtWidgets, QtGui 
import time

move_history_map = { 
    "50%": 10,
    "25%": 20,
    "breakout room banishment": 0,
    "garbage": 0
}

def dmg_cnts(measure_results, move_history, first_player, type_list, player_skip):
    # returns [first player, second player]
    #print(measure_results)
    bases = [0, 0]
    multipliers = [0,0]
    multipliers[first_player] = types[type_list[first_player]]["attack"]
    multipliers[(1 + first_player) % 2] = types[type_list[1 - first_player]]["attack"]
    final_dmg = [0, 0]
    if move_history[-1] == "reflect":
        multipliers[0], multipliers[1] = multipliers[1], multipliers[0]
        bases[0] = move_history_map[move_history[-2]] # base damage done to first player = their own move
    elif move_history[-1] == "nullify":
        bases[1] = move_history_map[move_history[-2]]
    elif "breakout room banishment" in move_history[-2:]:
        if move_history[-1] == "breakout room banishment": # first player getting banished 
            if measure_results[0] == 1:
                player_skip[first_player] = True
        if move_history[-2] == "breakout room banishment": # second player getting banished
            if measure_results[1] == 1:
                player_skip[1 - first_player] = True
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
        self.player_skip = [False, False]
        
        self.button = QtWidgets.QPushButton("Start game!")
        self.text = QtWidgets.QLabel("Welcome to Quantum Pokemon!",
                                     alignment=QtCore.Qt.AlignCenter)

        self.layout = QtWidgets.QVBoxLayout(self)
        
        self.hbox = QtWidgets.QHBoxLayout(self)
        self.hbox.setObjectName("hbox")

        self.playerBox = QtWidgets.QHBoxLayout(self, objectName="playerBox")
        self.p1Box = QtWidgets.QVBoxLayout(self, objectName="p1Box")
        self.p2Box = QtWidgets.QVBoxLayout(self, objectName="p2Box")

        self.typeButton1 = QtWidgets.QPushButton("Dr. Davis", objectName="type1Button")
        self.typeButton2 = QtWidgets.QPushButton("Pikachu", objectName="type2Button")

        self.type_list = ["", ""]
        self.health_list = []
        self.player = random.randint(0, 1)
        self.qc = QuantumCircuit(3, 2)
        self.move_history = []
        self.move_count = 0

        self.p1Health = QtWidgets.QLabel(alignment=QtCore.Qt.AlignCenter, objectName="p1Health")
        self.p2Health = QtWidgets.QLabel(alignment=QtCore.Qt.AlignCenter, objectName="p2Health")

        #parent of everything
        self.layout.addWidget(self.text)
        self.layout.addLayout(self.playerBox)
        self.layout.addWidget(self.button)
        self.layout.addLayout(self.hbox)


        #player health boxes
        self.playerBox.addLayout(self.p1Box)
        self.playerBox.addLayout(self.p2Box)


        self.button.clicked.connect(self.startGame)
    
    @QtCore.Slot()
    def startGame(self):
        print("started game")
        self.text.setText("Player 1, select your type")
        self.hbox.addWidget(self.typeButton1) 
        self.hbox.addWidget(self.typeButton2)
        self.button.setParent(None)
        self.typeButton1.clicked.connect(lambda: self.setPlayerType("Dr. Davis", 0))
        self.typeButton2.clicked.connect(lambda: self.setPlayerType("Pikachu", 0))
    
    def setPlayerType(self, type, player):
        self.type_list[player] = type
        if player < 1:
            self.text.setText("Player 2, select your type")
            self.typeButton1.clicked.connect(lambda: self.setPlayerType("Dr. Davis", 1))
            self.typeButton2.clicked.connect(lambda: self.setPlayerType("Pikachu", 1))
        else:
            self.text.setText("Game has started!")
            self.typeButton1.setParent(None)
            self.typeButton2.setParent(None)
            self.setupBattle()
            #how to find children --
            # for child in self.hbox.findChildren(QtWidgets.QPushButton):
            #     print(f"rawr, {child}")
            # for i in range(self.layout.count()):
            #     print("rawr" + str(self.layout.itemAt(i)))

    def addMoveButtons(self):
        self.twentyFiveButton = QtWidgets.QPushButton("25%")
        self.fiftyButton = QtWidgets.QPushButton("50%")
        self.reflectButton = QtWidgets.QPushButton("reflect")
        self.nullifyButton = QtWidgets.QPushButton("nullify")
        self.infinite_randomness_button = QtWidgets.QPushButton("infinite randomness")
        self.breakout_room_banishment_button = QtWidgets.QPushButton("breakout room banishment")

        
        self.twentyFiveButton.clicked.connect(lambda: self.makeMove("25%"))
        self.fiftyButton.clicked.connect(lambda: self.makeMove("50%"))
        self.reflectButton.clicked.connect(lambda: self.makeMove("reflect"))
        self.nullifyButton.clicked.connect(lambda: self.makeMove("nullify"))
        self.infinite_randomness_button.clicked.connect(lambda: self.makeMove("infinite randomness"))
        self.breakout_room_banishment_button.clicked.connect(lambda: self.makeMove("breakout room banishment"))

        
        self.hbox.addWidget(self.twentyFiveButton)
        self.hbox.addWidget(self.fiftyButton)
        self.hbox.addWidget(self.reflectButton)
        self.hbox.addWidget(self.nullifyButton)
        self.hbox.addWidget(self.infinite_randomness_button)
        self.hbox.addWidget(self.breakout_room_banishment_button)

    def setupBattle(self):
        self.health_list = [types[self.type_list[0]]["health"], types[self.type_list[1]]["health"]]
        self.p1Health.setText(str(self.health_list[0]))
        self.p1Box.addWidget(self.p1Health)
        self.p2Health.setText(str(self.health_list[1]))
        self.p2Box.addWidget(self.p2Health)

        self.addMoveButtons()

        self.playerBox.addLayout(self.p1Box)
        self.playerBox.addLayout(self.p2Box)

        

    #def beginBattle(self):


    


app = QtWidgets.QApplication([])
widget = MyWidget()
widget.resize(800, 600)
widget.show()
sys.exit(app.exec())
