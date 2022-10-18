from wsgiref.util import setup_testing_defaults
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

    #ui stuff, you can skip over this
    def __init__(self):
        super().__init__()
        self.player_skip = [False, False]
        
        self.button = QtWidgets.QPushButton("Start game!")
        self.helpButton = QtWidgets.QPushButton("View Instructions")
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

        self.p1Pic = QtWidgets.QLabel(self)
        self.p2Pic = QtWidgets.QLabel(self)
        
        self.p1Health = QtWidgets.QLabel(alignment=QtCore.Qt.AlignCenter, objectName="p1Health")
        self.p2Health = QtWidgets.QLabel(alignment=QtCore.Qt.AlignCenter, objectName="p2Health")
        self.moveText = QtWidgets.QLabel(alignment=QtCore.Qt.AlignLeft)
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
        self.layout.addWidget(self.moveText)
        self.layout.addLayout(self.playerBox)
        self.layout.addWidget(self.button)
        self.layout.addWidget(self.helpButton)
        self.layout.addLayout(self.hbox)
        

        #player health boxes
        self.playerBox.addLayout(self.p1Box)
        self.playerBox.addLayout(self.p2Box)
    
        self.p1Box.addWidget(self.p1Pic)
        self.p2Box.addWidget(self.p2Pic)
        self.p1Box.addWidget(self.p1Health)
        self.p2Box.addWidget(self.p2Health)
        self.p1Health.show()
        self.p2Health.show()

        self.helpButton.clicked.connect(self.showInstructions)
        self.button.clicked.connect(self.startGame)
    
    @QtCore.Slot()
    def startGame(self):
        self.text.setAlignment(QtCore.Qt.AlignCenter)
        self.moveText.hide()
        self.helpButton.hide()
        self.text.setText("Player 1, select your type")
        self.hbox.addWidget(self.typeButton1) 
        self.hbox.addWidget(self.typeButton2)
        self.button.hide()
        self.typeButton1.clicked.connect(lambda: self.setPlayerType("Dr. Davis", 0))
        self.typeButton2.clicked.connect(lambda: self.setPlayerType("Pikachu", 0))

    def showInstructions(self):
        self.text.setText("""
        Instructions:
        At the start of the game, each player will choose their respective pokemon.
        Each pokemon has different health, attack, and defense.
        Each player will have a turn to choose a move.
        All moves have some sort of quantum concept applied during their executions.
        Each set of two moves has a separate quantum circuit.
        Once two moves have passed, the results of the moves will be shown.
        After every set of two moves, the order of who goes first will be switched.
        Once any player’s health goes below 0, the game will end.
        """)
        self.text.setAlignment(QtCore.Qt.AlignLeft)
        self.moveText.setText("""
        Move Descriptions:
        50% - Move has a 50% chance of hitting for standard damage
            Uses Hadamard gate
        25%- Move has a 25% chance of hitting for significant damage
            Uses unitary that puts qubit into a state that has 25% chance of measuring 1
        Reflect - Depending on the user’s pokemon defense, the user has a chance to “reflect” the opponent’s damage back to them
            Uses controlled swap
            Be careful, this could have unintended consequences!
        Nullify - Depending on the user’s pokemon defense, the user has a chance to nullify the opponent’s move
            Uses controlled swap and finds the inverse unitary of the opponent’s respective move’s unitary
        Breakout Room Banishment - Depending on the user’s pokemon attack, has a chance of forcing the opponent to skip their next move
        Infinite Randomness - Puts hadamards on every qubit
            Creates a secondary quantum circuit that creates a random base damage by applying hadamards on every qubit
            Measures all qubits to find bitstring
            Uses bitstring’s value to assign base damage

        """)

        self.helpButton.hide()
        self.button.setText("Start Game")

    # primary quantum function 
    # returns [first player, second player]
    # calculates damage or applies effect on players based on their moves
    def dmg_cnts(self, measure_results, first_player):
        self.player_skip = [False, False]
        bases = [0, 0]
        multipliers = [0,0]
        multipliers[0] = types[self.type_list[0]]["attack"]
        multipliers[1] = types[self.type_list[1]]["attack"]
        final_dmg = [0, 0]

        #determine multipliers based on move used
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
            #bases are standard, grab them from the move history map
            bases[0] = move_history_map[self.move_history[-1]]
            bases[1] = move_history_map[self.move_history[-2]]
        
        #calculate final damage
        final_dmg[0] = measure_results[0] * bases[0] * multipliers[0]
        final_dmg[1] = measure_results[1] * bases[1] * multipliers[1]
        return final_dmg
    
    def setPlayerType(self, specifiedType, player):
        self.type_list[player] = specifiedType
        if player < 1: # first player
            if specifiedType == "Pikachu":
                p1Image = QtGui.QPixmap("pikachu.png",).scaledToHeight(250)
                self.p1Pic.setPixmap(p1Image)
            elif specifiedType == "Dr. Davis":
                p1Image = QtGui.QPixmap("dr_davis.png").scaledToHeight(250)
                self.p1Pic.setPixmap(p1Image)
            self.p1Pic.setAlignment(QtCore.Qt.AlignCenter)
            self.text.setText("Player 2, select your type")
            self.typeButton1.clicked.disconnect()
            self.typeButton2.clicked.disconnect()
            self.typeButton1.clicked.connect(lambda: self.setPlayerType("Dr. Davis", 1))
            self.typeButton2.clicked.connect(lambda: self.setPlayerType("Pikachu", 1))
        else: # second player 
            if specifiedType == "Pikachu":
                p2Image = QtGui.QPixmap("pikachu.png").scaledToHeight(250)
                self.p2Pic.setPixmap(p2Image)
            elif specifiedType == "Dr. Davis":
                p2Image = QtGui.QPixmap("dr_davis.png").scaledToHeight(250)
                self.p2Pic.setPixmap(p2Image)
            self.p2Pic.setAlignment(QtCore.Qt.AlignCenter)
            self.text.setText("Game has started!")
            self.typeButton1.setParent(None)
            self.typeButton2.setParent(None)
            self.setupBattle("initial")


    def makeMove(self, move):
        #skipped if breakout room banishment was successful
        self.callMove(move)
        if self.move_count % 2 == 0:
            #show results since moves are called in sets of 2
            self.setupBattle("show results")
        elif self.player_skip[self.player] == True:
            self.setupBattle("skip")
        else:
            self.setupBattle("default")
        
    
    def callMove(self, move):
        if move == '50%':
            fiftyPercentAtk(self.qc, self.player)
        elif move == 'reflect':
            reflect(self.qc, types[self.type_list[self.player]]["defense"], self.player)
        elif move == '25%':
            twentyFivePercentAtk(self.qc, self.player)
        elif move == 'nullify':
            inverse_prob = 0

            #infinite randomness cannot be nullified
            if self.move_history[-1] != 'infinite randomness':
                if self.move_history[-1] == '50%':
                    inverse_prob = 0.5
                elif self.move_history[-1] == '25%':
                    inverse_prob = 0.25
                elif self.move_history[-1] == 'breakout_room_banishment':
                    inverse_prob =  types[self.type_list[1 - self.player]]["attack"] / 5
            nullify(self.qc, types[self.type_list[self.player]]["defense"], self.player, inverse_prob)
        elif move == 'breakout room banishment':
            breakout_room_banishment(self.qc, types[self.type_list[self.player]]["attack"] / 5, self.player)
        elif move == 'infinite randomness':
            val = infinite_randomness(self.qc)
            move_history_map['infinite randomness'] = val
        self.move_history.append(move)
        self.move_count += 1      
        if (self.move_count % 2 == 1):
            self.player = 1 - self.player
            self.reflectButton.show()
  


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
            self.text.setText(f"Player 1 received {dmgs[0]} damage\nPlayer 2 received {dmgs[1]} damage")

            self.button.show()
            self.button.setText("Continue")
            self.button.clicked.disconnect()

            self.health_list[0] -= dmgs[0]
            self.health_list[1] -= dmgs[1]

            self.p1Health.setText(str(self.health_list[0]))
            self.p2Health.setText(str(self.health_list[1]))

            #one or both players died
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
            
            #create a new quantum circuit for next set of moves
            self.qc = QuantumCircuit(3,2)

        #certain moves cant be used by certain types
        if (self.type_list[self.player] == "Pikachu"):
            self.breakout_room_banishment_button.hide()
        if (self.type_list[self.player] == "Dr. Davis"):
            self.infinite_randomness_button.hide()
        if (self.move_count % 2 == 0):
            self.reflectButton.hide()
            #check if next player should be skipped
            if self.player_skip[self.player] == True:
                self.button.clicked.connect(lambda: self.setupBattle("skipped from show results"))
            else:
                self.button.clicked.connect(lambda: self.setupBattle("default"))
    
    def showSkip(self, origin):
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
