# ChatGPT walking me through creating my first (in a long time) python program...

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

# create a quantum circuit with 2 qubits and 2 classical bits
qc = QuantumCircuit(2,2)
 
# put the first qubit into soooperposition
qc.h(0)

# entangle qubit 0 with qubit 1
qc.cx(0,1)

# measure both qubits
qc.measure([0,1], [0,1])

# run the circuit on a simulator
sim = AerSimulator()
result = sim.run(qc, shots = 1000).result()

# print results
counts = result.get_counts()
print(counts)
