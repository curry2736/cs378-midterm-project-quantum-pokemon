from Quantum import fiftyPercentAtk, measure, reflect
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, Aer, execute
import numpy as np
import matplotlib.pyplot as plt
from qiskit.visualization import plot_histogram
from qiskit.quantum_info import Statevector


aux = 2
atk = 1
defense = 0
move_count = 0
moves = {'a': 10, 'b': 15, 'c': 20, 'd': 25}
quantum_moves = ['f', 'r']
move_map = {'f': fiftyPercentAtk, 'r': reflect}

types = {
    "1": {
        "health": 50,
        "attack": 0.9,
        "defense": 1
    },
    "2":  {
        "health": 40,
        "attack": 1.125,
        "defense": 1
    }
}

#start game

type_list = [input("Player 1, select your type: "), input("Player 2, select your type: ")]
print("-------------------------------------------------------------")
health_list = [types[type_list[0]]["health"], types[type_list[1]]["health"]]
#attack_list = [types[type_list[0]]["attack"], types[type_list[1]]["attack"]]
#defense_list = [types[type_list[0]]["defense"], types[type_list[1]]["defense"]]
player = 0

qc = QuantumCircuit(3, 2)
while health_list[0] > 0 and health_list[1] > 0:
    if move_count > 0 and move_count % 2 == 0:
        base = 20
        results = measure(qc)

        #attack_list should be the other player's attack
        p1_dmg = results[0] * base * types[type_list[1]]["attack"]
        p2_dmg = results[1] * base * types[type_list[0]]["attack"]
        print("Player 1 received " + str(p1_dmg) + " damage")
        print("Player 2 received " + str(p2_dmg) + " damage")
        health_list[0] -= p1_dmg
        health_list[1] -= p2_dmg

            
        qc = QuantumCircuit(3,2)
    #select moves
    print("Your health is " + str(health_list[player]))
    print("Your moves are " + str(list(moves.keys())))
    print("Your quantum moves are " + str(quantum_moves))
    move = input("Player " + str(player + 1) + ", enter the letter for your move: ")

    while move not in moves and move not in quantum_moves:
        print("That was not a valid move\n")
        print("Your moves are " + str(moves))
        print("Your quantum moves are " + str(quantum_moves))
        move = input("Player " + str(player + 1) +  ", enter the letter for your move: ")
    
    if move in quantum_moves:
        if move == 'f':
            fiftyPercentAtk(qc, types[type_list[player]]["attack"], player)
        elif move == 'r':
            reflect(qc, types[type_list[player]]["defense"], player)
    else:
        print("Your move did " + str(moves[move]) + " damage")
        health_list[player - 1] -= moves[move]
        print("The other player's health is now " + str(health_list[player - 1]))
        print("-------------------------------------------------------------")

    player = 1 - player
    move_count += 1