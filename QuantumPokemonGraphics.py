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
        self.player_skip = [False, False]

        try:
            self.button.clicked.disconnect()
        except RuntimeError:
            pass
        

        self.button.setText("Keep Going")
        self.button.clicked.connect(self.putHboxBack)
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

    def callMove(self, move):
        print("callMove")
        if move == '50%':
            fiftyPercentAtk(self.qc, types[self.type_list[self.player]]["attack"], self.player)
        elif move == 'reflect':
            reflect(self.qc, types[self.type_list[self.player]]["defense"], self.player)
        elif move == '25%':
            twentyFivePercentAtk(self.qc, types[self.type_list[self.player]]["attack"], self.player)
        elif move == 'nullify':
            inverse_prob = 0

            #infinite randomness cannot be nullified
            if self.move_history[-1] != 'infinite randomness':
                if self.move_history[-1] == '50%':
                    inverse_prob = 0.5
                elif self.move_history[-1] == '25%':
                    inverse_prob = 0.25
                elif self.move_history[-1] == 'breakout_room_banishment':
                    inverse_prob =  types[self.type_list[1 - self.player]]["attack"] / 10
            nullify(self.qc, types[self.type_list[self.player]]["defense"], self.player, inverse_prob)
        elif move == 'breakout room banishment':
            breakout_room_banishment(self.qc, types[self.type_list[self.player]]["attack"] / 10, self.player)
        elif move == 'infinite randomness':
            infinite_randomness(self.qc, move_history_map)
        self.move_history.append(move)
        self.player = 1 - self.player
        self.move_count += 1        

    def makeMove(self, move):
        print("makeMove")
        #skipped if breakout room banishment was successful

        self.callMove(move)

        if self.move_count % 2 == 1:
            if (move != "garbage"):
                self.text.setText(f"Player {self.player + 1} is up")
            if self.player_skip[self.player] == True:
                self.setPlayerSkipped()
        
        if self.move_count > 0 and self.move_count % 2 == 0:
            self.showResults()

    def setPlayerSkipped(self):
        print("Player " + str(1 + self.player) +", your turn was skipped!")
        self.removeAllButtons()
        try:
            self.button.clicked.disconnect()
        except RuntimeError:
            pass
        self.button.clicked.connect(self.continueSkipped)
        self.layout.addWidget(self.button)
        self.text.setText("Player " + str(1 + self.player) +", your turn was skipped!")
        self.player_skip[self.player] = False
        

    def showResults(self):
        print("Show results")
        self.player_skip = [False, False]
        results = measure(self.qc, self.move_history)
        first_player = 1 - ((self.move_count % 4) // 2)
        dmgs = dmg_cnts(results, self.move_history, first_player, self.type_list, self.player_skip)
        
        self.removeAllButtons()
        
        self.text.setText(f"Player {first_player + 1} received {dmgs[0]} damage\nPlayer {(1 - first_player) + 1} received {dmgs[1]} damage")
        try:
            self.button.clicked.disconnect()
        except RuntimeError:
            pass
        self.button.clicked.connect(self.putHboxBack)
        self.button.setText("Back to the game")
        self.layout.addWidget(self.button)
        
        self.health_list[first_player] -= dmgs[0]
        self.health_list[1 - first_player] -= dmgs[1]
        self.p1Health.setText(str(self.health_list[0]))
        self.p2Health.setText(str(self.health_list[1]))



        if self.health_list[0] <= 0 or self.health_list[1] <= 0:
            print("done lol")
        self.qc = QuantumCircuit(3,2)

        if self.move_count % 4 == 0: # keeps the game fair
            self.player = 1 - self.player
            
    def putHboxBack(self):
        print("putHboxBack")
        self.button.setParent(None)
        if self.player_skip[self.player] == True:
            self.setPlayerSkipped()
        else:
            self.text.setText(f"Player {self.player + 1} is up")
            self.putButtonsIn()

    
    def continueSkipped(self):
        print("continueSkipped")
        try:
            self.button.clicked.disconnect()
        except RuntimeError:
            pass
        moves_before = self.move_count

        self.makeMove("garbage")
        if (moves_before % 2 == 0):
            #self.putButtonsIn()
            self.button.setText("Next player's turn")
            self.button.clicked.connect(self.putHboxBack)
        else:
            #self.button.setParent(None)
            self.button.setText("Show results")
            self.button.clicked.connect(self.showResults)


    def removeAllButtons(self):
        print("removeallButtons")
        self.twentyFiveButton.setParent(None)
        self.fiftyButton.setParent(None)
        self.reflectButton.setParent(None)
        self.nullifyButton.setParent(None)
        self.infinite_randomness_button.setParent(None)
        self.breakout_room_banishment_button.setParent(None)
        self.p1Health.setParent(None)
        self.p2Health.setParent(None)
    
    def putButtonsIn(self):
        print("putButtonsIn")
        self.hbox.addWidget(self.twentyFiveButton)
        self.hbox.addWidget(self.fiftyButton)
        self.hbox.addWidget(self.reflectButton)
        self.hbox.addWidget(self.nullifyButton)
        self.hbox.addWidget(self.infinite_randomness_button)
        self.hbox.addWidget(self.breakout_room_banishment_button)
        self.p1Box.addWidget(self.p1Health)
        self.p2Box.addWidget(self.p2Health)
    





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
