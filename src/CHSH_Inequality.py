 # General
import numpy as np

# Qiskit imports
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.quantum_info import SparsePauliOp
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

# Qiskit Runtime imports
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit_ibm_runtime import EstimatorV2 as Estimator

# Plotting routines
import matplotlib.pyplot as plt
import matplotlib.ticker as tck

# Mike comment: the items above are items I need to import for any of the code below to run without error

# To run on hardware, select the backend with the fewest number of jobs in the queue
service = QiskitRuntimeService() # Mike comment: create a new instance of the QiskitRuntimeService class called 'service'

# Mike comment: the least_busy() method under QiskikRuntimeService() looks for a real quantum machine to use for the simulation. This program needs 127 qubits to run properly. 'name' is one of its properties.
backend = service.least_busy(
    operational=True, simulator=False, min_num_qubits=127
)
print(backend.name)

# Create a parameterized CHSH circuit
# Mike comment: rotation angle Theta to change the state of a qubit
theta = Parameter("$\\theta$")

chsh_circuit = QuantumCircuit(2) # Mike comment: set up a circuit with 2 qubits
chsh_circuit.h(0) # Mike comment: 1st qubit, always |0>
chsh_circuit.cx(0, 1) # Mike comment: entagles the 2 qubits
chsh_circuit.ry(theta, 0) # Mike comment: ry = rotate around the y-axis...by angle theta per the arguments
chsh_circuit.draw(output="mpl", idle_wires=False, style="iqp") # Mike comment: draws a diagram of the chsh circuit

number_of_phases = 21 # Mike comment: phases of theta
phases = np.linspace(0, 2 * np.pi, number_of_phases)
# Phases need to be expressed as list of lists in order to work
individual_phases = [[ph] for ph in phases]

# <CHSH1> = <AB> - <Ab> + <aB> + <ab> -> <ZZ> - <ZX> + <XZ> + <XX>
# Mike comment: does this become the blue curve in my diagram?
observable1 = SparsePauliOp.from_list(
    [("ZZ", 1), ("ZX", -1), ("XZ", 1), ("XX", 1)]
)

# <CHSH2> = <AB> + <Ab> - <aB> + <ab> -> <ZZ> + <ZX> - <XZ> + <XX>
# Mike comment: does this become the orange curve in my diagram?
observable2 = SparsePauliOp.from_list(
    [("ZZ", 1), ("ZX", 1), ("XZ", -1), ("XX", 1)]
)

# Mike comment: set the target for the chart
target = backend.target
pm = generate_preset_pass_manager(target=target, optimization_level=3)

# Mike comment: configure the drawing for the circuit results
chsh_isa_circuit = pm.run(chsh_circuit)
chsh_isa_circuit.draw(output="mpl", idle_wires=False, style="iqp")

isa_observable1 = observable1.apply_layout(layout=chsh_isa_circuit.layout)
isa_observable2 = observable2.apply_layout(layout=chsh_isa_circuit.layout)

# To run on a local simulator:
# Use the StatevectorEstimator from qiskit.primitives instead.

estimator = Estimator(mode=backend)

pub = (
    chsh_isa_circuit,  # ISA circuit -- Mike comment - ISA = Instruction Set Architecture
    [[isa_observable1], [isa_observable2]],  # ISA Observables
    individual_phases,  # Parameter values
)

job_result = estimator.run(pubs=[pub]).result() # Mike comment: sets the result of the estimator run on the local simulator

chsh1_est = job_result[0].data.evs[0] # Mike comment: average measurement outcome for chsh1 for all 21 theta values
chsh2_est = job_result[0].data.evs[1] # Mike comment: average measurement outcome for chsh2 for all 21 theta values

fig, ax = plt.subplots(figsize=(10, 6)) # Mike comment: chart dimensions, including those below...

# results from hardware
ax.plot(phases / np.pi, chsh1_est, "o-", label="CHSH1", zorder=3)
ax.plot(phases / np.pi, chsh2_est, "o-", label="CHSH2", zorder=3)

# classical bound +-2
ax.axhline(y=2, color="0.9", linestyle="--")
ax.axhline(y=-2, color="0.9", linestyle="--")

# quantum bound, +-2√2
ax.axhline(y=np.sqrt(2) * 2, color="0.9", linestyle="-.")
ax.axhline(y=-np.sqrt(2) * 2, color="0.9", linestyle="-.")
ax.fill_between(phases / np.pi, 2, 2 * np.sqrt(2), color="0.6", alpha=0.7)
ax.fill_between(phases / np.pi, -2, -2 * np.sqrt(2), color="0.6", alpha=0.7)

# set x tick labels to the unit of pi
ax.xaxis.set_major_formatter(tck.FormatStrFormatter("%g $\\pi$"))
ax.xaxis.set_major_locator(tck.MultipleLocator(base=0.5))

# set labels, and legend
plt.xlabel("Theta")
plt.ylabel("CHSH witness")
plt.legend()
plt.show()

# Mike comments: end the chart show