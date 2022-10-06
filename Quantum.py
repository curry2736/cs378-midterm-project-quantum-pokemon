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
    base = 20
    atk = current_player
    defense = 1 - current_player
    qc.h(defense)
    # qc.measure(defense, 0)
    # counts = execute(qc, backend = Aer.get_backend('qasm_simulator'), shots=1).result().get_counts(qc)
    # if '01' in counts:
    #     return newAtk
    # return 0

def reflect(qc, probability, current_player):
    defense = current_player
    atk = 1 - current_player
    createUnitary(qc, probability, aux)
    qc.ccx(aux, defense, atk)
    qc.ch(aux, defense)

def measure(qc):
    qc.measure(range(2), range(2))
    counts = execute(qc, backend = Aer.get_backend('qasm_simulator'), shots=1).result().get_counts(qc)
    result = list(counts.keys())[0]
    qc.draw('mpl', filename='circuit.png')
    print(result)
    #returning [p1, p2]
    return [int(result[1]), int(result[0])]


#probability is probability that targetted qubit is affected
def createUnitary(qc, probability, qubit):
    qc.u(2 * np.arcsin(probability ** 0.5),0,0,qubit)


if __name__ == "__main__":
    qc = QuantumCircuit(3,2)
    fiftyPercentAtk(qc, 0.5)
    reflect(qc,0.1)
    qc.draw('mpl', filename='circuit.png')

# qc.h(defense)
# fiftyPercentAtk(1.15)
# reflect()
# qc.measure([atk[0], defense[0]], cbits)
# qc.draw('mpl', filename='circuit.png')

# counts = execute(qc, backend = Aer.get_backend('qasm_simulator'), shots=1).result().get_counts(qc)
# print(counts)
# plot_histogram(counts, filename='histogram.png')