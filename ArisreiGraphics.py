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
        self.player = 0
        self.qc = QuantumCircuit(3, 2)
        self.move_history = []
        self.move_count = 0

        self.p1Health = QtWidgets.QLabel(alignment=QtCore.Qt.AlignCenter, objectName="p1Health")
        self.p2Health = QtWidgets.QLabel(alignment=QtCore.Qt.AlignCenter, objectName="p2Health")

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

        #parent of everything
        self.layout.addWidget(self.text)
        self.layout.addLayout(self.playerBox)
        self.layout.addWidget(self.button)
        self.layout.addLayout(self.hbox)
        

        #player health boxes
        self.playerBox.addLayout(self.p1Box)
        self.playerBox.addLayout(self.p2Box)
    
        self.p1Box.addWidget(self.p1Health)
        self.p2Box.addWidget(self.p2Health)
        self.p1Health.hide()
        self.p2Health.show()

        self.button.clicked.connect(self.startGame)
    
    @QtCore.Slot()
    def startGame(self):
        print("started game")
        self.text.setText("Player 1, select your type")
        self.hbox.addWidget(self.typeButton1) 
        self.hbox.addWidget(self.typeButton2)
        self.button.hide()
        self.typeButton1.clicked.connect(lambda: self.setPlayerType("Dr. Davis", 0))
        self.typeButton2.clicked.connect(lambda: self.setPlayerType("Pikachu", 0))

    def dmg_cnts(self, measure_results, first_player):
        # returns [first player, second player]
        #print(measure_results)
        self.player_skip = [False, False]
        bases = [0, 0]
        multipliers = [0,0]
        multipliers[0] = types[self.type_list[0]]["attack"]
        multipliers[1] = types[self.type_list[1]]["attack"]
        final_dmg = [0, 0]
        if self.move_history[-1] == "reflect":
            multipliers[0], multipliers[1] = multipliers[1], multipliers[0]
            bases[0] = move_history_map[self.move_history[-2]] # base damage done to first player = their own move
        elif self.move_history[-1] == "nullify":
            bases[1] = move_history_map[self.move_history[-2]]
        elif "breakout room banishment" in self.move_history[-2:]:
            if self.move_history[-1] == "breakout room banishment": # first player getting banished 
                if measure_results[first_player] == 1:
                    print(f"banishing player {1 + first_player}")
                    self.player_skip[first_player] = True
            if self.move_history[-2] == "breakout room banishment": # second player getting banished
                if measure_results[1 - first_player] == 1:
                    print(f"banishing player {2 - first_player}")
                    self.player_skip[1 - first_player] = True
        else:
            bases[0] = move_history_map[self.move_history[-1]]
            bases[1] = move_history_map[self.move_history[-2]]
        
        final_dmg[0] = measure_results[0] * bases[0] * multipliers[0]
        final_dmg[1] = measure_results[1] * bases[1] * multipliers[1]
        print(f"dmg cnts - {self.player_skip}")
        return final_dmg
    
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
            self.setupBattle("initial")


    def makeMove(self, move):
        #skipped if breakout room banishment was successful
        self.callMove(move)
        if self.move_count % 2 == 0:
            self.setupBattle("show results")
        elif self.player_skip[self.player] == True:
            self.setupBattle("skip")
        else:
            self.setupBattle("default")
        
    
    def callMove(self, move):
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
        self.move_count += 1      
        if (self.move_count % 2 == 1):
            self.player = 1 - self.player
  


    def addMoveButtons(self):
        print("adding move buttons")     
        if self.move_count == 0:
            self.hbox.addWidget(self.twentyFiveButton)
            self.hbox.addWidget(self.fiftyButton)
            self.hbox.addWidget(self.reflectButton)
            self.hbox.addWidget(self.nullifyButton)
            self.hbox.addWidget(self.infinite_randomness_button)
            self.hbox.addWidget(self.breakout_room_banishment_button)
        
        else:
            print("showing buttons")
            for i in range(self.hbox.count()):
                self.hbox.itemAt(i).widget().show()


    def setHealthText(self):

        self.p1Health.show()
        self.p2Health.show()

        self.p1Health.setText(str(self.health_list[0]))
        self.p2Health.setText(str(self.health_list[1]))

    def setupBattle(self, situation):
        if situation == "initial":
            self.text.setText(f"Player {1 + self.player}, it is your turn")
            self.health_list = [types[self.type_list[0]]["health"], types[self.type_list[1]]["health"]]
            self.setHealthText()

            self.addMoveButtons()

            self.playerBox.addLayout(self.p1Box)
            self.playerBox.addLayout(self.p2Box)
        elif situation == "default": # setting up a new move
            print("running default")
            self.button.hide()
            self.text.setText(f"Player {self.player + 1}, it is your turn")
            self.text.show()
            self.setHealthText()

            self.addMoveButtons()
            #if self.
            #self.playerBox.addLayout(self.p1Box)
            #self.playerBox.addLayout(self.p2Box)

        elif situation == "skip":
            self.showSkip("move screen")
        elif situation == "skipped from show results":
            self.showSkip("show results")
        elif situation == "skipped from skip screen":
            self.showSkip("skip screen")
        elif situation == "show results":
            for i in range(self.hbox.count()):
                self.hbox.itemAt(i).widget().hide()
            results = measure(self.qc, self.move_history)
            first_player = 1 - ((self.move_count // 2) % 2)
            dmgs = self.dmg_cnts(results, first_player)
            print(f"show results - {self.player_skip}")
            self.text.setText(f"Player 1 received {dmgs[0]} damage\nPlayer 2 received {dmgs[1]} damage")

            self.button.show()
            self.button.setText("Continue")
            self.button.clicked.disconnect()

            self.health_list[0] -= dmgs[0]
            self.health_list[1] -= dmgs[1]

            self.p1Health.setText(str(self.health_list[0]))
            self.p2Health.setText(str(self.health_list[1]))
            if self.health_list[0] <= 0 or self.health_list[1] <= 0:
                for i in range(self.hbox.count()):
                    self.hbox.itemAt(i).widget().hide()
                for i in range(self.layout.count()):
                    if self.layout.itemAt(i) != None and self.layout.itemAt(i).widget() != None:
                        self.layout.itemAt(i).widget().hide()   

                self.text.show()
                if self.health_list[0] <= 0 and self.health_list[1] <= 0:
                    self.text.setText(f"You both died!")
                elif self.health_list[0] <= 0:
                    self.text.setText(f"Player 1 died!")
                else:
                    self.text.setText(f"Player 2 died!")

                return
          
            self.qc = QuantumCircuit(3,2)

            #if self.move_count % 4 == 0: # keeps the game fair
                #self.player = 1 - self.player
            
            #check if next player should be skipped
            if self.player_skip[self.player] == True:
                self.button.clicked.connect(lambda: self.setupBattle("skipped from show results"))
            else:
                self.button.clicked.connect(lambda: self.setupBattle("default"))
    
    def showSkip(self, origin):
        #how to find children --
        # for child in self.hbox.findChildren(QtWidgets.QPushButton):
        #     print(f"rawr, {child}")
        # for i in range(self.layout.count()):
        #     print("rawr" + str(self.layout.itemAt(i)))

        #self.player_skip[self.player] = False
        self.move_count += 1
        self.move_history.append("garbage")

        self.text.show()
        self.text.setText(f"Player {1 + self.player}, your turn was skipped")

        # remove everything from layout
        self.button.clicked.disconnect()
        if origin == "show results": # first player was skipped, skipping the first player
            # set button to go to make move
            if self.player_skip[1 - self.player]:
                self.button.clicked.connect(lambda: self.setupBattle("skipped from skip screen"))
            else:
                self.button.clicked.connect(lambda: self.setupBattle("default"))

            self.button.setText("Continue to next move")
            
        if origin == "skip screen": # both players were skipped, skipping the second player
            # set button to go to show results
            self.button.clicked.connect(lambda: self.setupBattle("show results"))
            self.button.setText("Continue to results")

        if origin == "move screen": # only the second player was skipped, skipping the second player
            # set button to remove the buttons and go to show results 
            for i in range(self.layout.count()):
                if self.layout.itemAt(i) != None and self.layout.itemAt(i).widget() != None:
                    self.layout.itemAt(i).widget().hide()

            for i in range(self.hbox.count()):
                self.hbox.itemAt(i).widget().hide()
            
            self.text.show()
            self.text.setText(f"Player {self.player + 1} was skipped")
            self.button.show()
            self.button.setText("Continue to results")
            self.button.clicked.connect(lambda: self.setupBattle("show results"))
        if (self.move_count % 2 == 1):
            self.player = 1 - self.player


    


app = QtWidgets.QApplication([])
widget = MyWidget()
widget.resize(800, 600)
widget.show()
sys.exit(app.exec())
