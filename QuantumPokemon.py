from Quantum import fiftyPercentAtk, measure, nullify, reflect, twentyFivePercentAtk
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, Aer, execute
import numpy as np
import matplotlib.pyplot as plt
import PyQt6
from qiskit.visualization import plot_histogram
from qiskit.quantum_info import Statevector



move_history_map = { 
    "50%": 10,
    "25%": 20
}

def dmg_cnts(measure_results, move_history, first_player):
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

print("Welcome to Quantum Pokemon!")
type_list = [input("Player 1, select your type: "), input("Player 2, select your type: ")]
print("-------------------------------------------------------------")
health_list = [types[type_list[0]]["health"], types[type_list[1]]["health"]]
#attack_list = [types[type_list[0]]["attack"], types[type_list[1]]["attack"]]
#defense_list = [types[type_list[0]]["defense"], types[type_list[1]]["defense"]]
player = 0

qc = QuantumCircuit(3, 2)
move_history = []
while health_list[0] > 0 and health_list[1] > 0:
    if move_count > 0 and move_count % 2 == 0:
        results = measure(qc, move_history)
        first_player = 1 - ((move_count % 4) // 2)
        dmgs = dmg_cnts(results, move_history, first_player)
        print("Player " + str(first_player + 1) + " received " + str(dmgs[0]) + " damage")
        print("Player " + str((1 - first_player) + 1) + " received " + str(dmgs[1]) + " damage")
        health_list[first_player] -= dmgs[0]
        health_list[1 - first_player] -= dmgs[1]

        if health_list[0] <= 0 or health_list[1] <= 0:
            break

        qc = QuantumCircuit(3,2)
    if move_count > 0 and move_count % 4 == 0: # keeps the game fair
        player = 1 - player
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
        if move == '50%':
            fiftyPercentAtk(qc, types[type_list[player]]["attack"], player)
        elif move == 'reflect':
            reflect(qc, types[type_list[player]]["defense"], player)
        elif move == '25%':
            twentyFivePercentAtk(qc, types[type_list[player]]["attack"], player)
        elif move == 'nullify':
            nullify(qc, types[type_list[player]]["defense"], player, move_history[-1])
        move_history.append(move)
    else:
        print("Your move did " + str(moves[move]) + " damage")
        health_list[player - 1] -= moves[move]
        print("The other player's health is now " + str(health_list[player - 1]))
        print("-------------------------------------------------------------")

    player = 1 - player
    move_count += 1
    
if (health_list[0] > 0) :
    print("Player 2 died, Player 1 won!")
elif (health_list[1] > 0):
    print("Player 1 died, Player 2 won!")
else: 
    print("You both died, you suck lol!")
