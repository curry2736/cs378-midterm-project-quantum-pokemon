from venv import create
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, Aer, execute
import numpy as np
import matplotlib.pyplot as plt
from qiskit.visualization import plot_histogram
from qiskit.quantum_info import Statevector

aux = 2
#atk = 1
#defense = 0

def fiftyPercentAtk(qc, multiplier, current_player):
    atk = current_player
    defense = 1 - current_player
    qc.h(defense)

def twentyFivePercentAtk(qc, multiplier, current_player):
    defense = 1 - current_player
    createUnitary(qc, 0.25, defense)

def reflect(qc, probability, current_player):
    defense = current_player
    atk = 1 - current_player
    createUnitary(qc, probability, aux)
    qc.cswap(aux, atk, defense)

def nullify(qc, probability, current_player, move_to_nullify):
    if move_to_nullify == '50%':
        createUnitary(qc, probability, aux)
        qc.ch(aux, current_player)
    elif move_to_nullify == '25%':
        createUnitary(qc, probability, aux)
        createUnitaryInverseControlled(qc, 0.25, aux, current_player)


def measure(qc, move_history):
    p1_move = move_history[-2]
    p2_move = move_history[-1]
    qc.measure(range(2), range(2))
    counts = execute(qc, backend = Aer.get_backend('qasm_simulator'), shots=1).result().get_counts(qc)
    result = list(counts.keys())[0]
    qc.draw('mpl', filename='circuit.png')
    #print(result)
    #returning [p1, p2]
    return [int(result[1]), int(result[0])]


#probability is probability that targetted qubit is affected
def createUnitary(qc, probability, qubit):
    qc.u(2 * np.arcsin(probability ** 0.5),0,0,qubit)
def createUnitaryInverseControlled(qc, probability, control, target):
    qc.cu(2 * np.arcsin(probability ** 0.5),np.pi,np.pi,0,control, target)


if __name__ == "__main__":

    qc = QuantumCircuit(3,3)
    fiftyPercentAtk(qc, 1, 0)
    nullify(qc, 1, 1, "50%")

    qc.measure([0,1], [0,1])
    qc.draw('mpl', filename='circuit.png')

    counts = execute(qc, backend = Aer.get_backend('qasm_simulator'), shots=1024).result().get_counts(qc)
    print(counts)
    plot_histogram(counts, filename='histogram.png')