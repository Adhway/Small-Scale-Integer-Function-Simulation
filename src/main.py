# This program will execute the other programs (can be changed according to the working)
from input_validate import get_inputs
from classical_order import find_classical_order

N, a = get_inputs()
classical_order= find_classical_order(a,N)