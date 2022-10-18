from venv import create
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, Aer, execute
import numpy as np
import matplotlib.pyplot as plt
from qiskit.visualization import plot_histogram
from qiskit.quantum_info import Statevector

aux = 2
#atk = 1
#defense = 0

def infinite_randomness(qc):
    
    # whether the move "lands" is random
    qc.h([0,1,2])

    #find a random base dmg count
    auxCirc = QuantumCircuit(3,3)
    # sets up random damage values
    auxCirc.h([0,1,2])
    auxCirc.measure([0,1,2], [0,1,2])
    auxCirc.draw('mpl', filename='infinite-random-aux.png')
    counts = execute(auxCirc, backend = Aer.get_backend('qasm_simulator'), shots=1).result().get_counts(auxCirc)
    result = list(counts.keys())[0]
    random_base = 50 * (int(result, 2) / 8)
    print(random_base)
    return random_base

def fiftyPercentAtk(qc, current_player):
    atk = current_player
    defense = 1 - current_player
    qc.h(defense)

def twentyFivePercentAtk(qc, current_player):
    defense = 1 - current_player
    createUnitary(qc, 0.25, defense)

def reflect(qc, probability, current_player):
    defense = current_player
    atk = 1 - current_player
    createUnitary(qc, probability, aux)

    #reflects the attack by swapping attacking and defending qubits
    qc.cswap(aux, atk, defense)

def nullify(qc, probability, current_player, inverse_prob):
    #nullifies by creating a unitary that is the inverse of the unitary that the
    #attacker applied
    createUnitary(qc, probability, aux)
    createUnitaryInverseControlled(qc, inverse_prob, aux, current_player)


def breakout_room_banishment(qc, probability, current_player):
    createUnitary(qc, probability, 1 - current_player)
    


def measure(qc, move_history):
    qc.measure(range(2), range(2))
    counts = execute(qc, backend = Aer.get_backend('qasm_simulator'), shots=1).result().get_counts(qc)
    result = list(counts.keys())[0]
    #qc.draw('mpl', filename='circuit.png')

    #returning [p1, p2]
    return [int(result[1]), int(result[0])]


#probability is probability that targetted qubit is affected
def createUnitary(qc, probability, qubit):
    qc.u(2 * np.arcsin(probability ** 0.5),0,0,qubit)
def createUnitaryInverseControlled(qc, probability, control, target):
    qc.cu(2 * np.arcsin(probability ** 0.5),np.pi,np.pi,0,control, target)


if __name__ == "__main__":
    
    # qc = QuantumCircuit(3, 3)
    # infinite_randomness(qc)
    # qc.draw('mpl', filename='infinite-rando.png')

    qc = QuantumCircuit(3,3)
    twentyFivePercentAtk(qc, 0)
    fiftyPercentAtk(qc, 1)  
    qc.measure([0, 1], [0, 1])

    qc.draw('mpl', filename='two-attacks.png')

    
    qc = QuantumCircuit(3,3)
    twentyFivePercentAtk(qc, 1)
    qc.barrier()
    reflect(qc, 0.3, 0)
    qc.draw('mpl', filename='reflect-25-30.png')


    qc = QuantumCircuit(3,3)
    fiftyPercentAtk(qc, 0)
    qc.barrier()

    nullify(qc, 1, 1, .5)
    
    qc.draw('mpl', filename='nullify-fifty.png')
