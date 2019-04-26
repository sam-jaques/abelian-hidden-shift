# Quantum Abelian Hidden Shift Algorithm Simulator

This simulates Kuperberg's algorithm from [Another subexponential-time quantum algorithm for the dihedral hidden subgroup problem
](https://arxiv.org/abs/1112.3333). The main quantum step involves only a fourier sample, and this is easy to simulate with knowledge
of the hidden shift. 

This simulator currently only simulates cyclic groups with order equal to a power of 2, though many methods would work 
with other smooth orders. The next step for this is to support any order of group using an approximate collimation technique.

## Use


### Prerequisites

Python 2.7.

### Importing

Following the example of kuperbergtest.py, import as follows:

```
from kuperberg import HiddenShiftProblem
from kuperberg import PhaseState
```

### Full Simulation

First, instantiate a hidden shift problem:
```
test_problem=HiddenShiftProblem(group_order,[phi_1,phi_2,phi_3],secret_shift)
```
Here the group order is group_order, the array [phi_1,phi_2,phi_3] represents the endomorphisms
phi (see Section 3.2 of Kuperberg's paper), which must be coprime to the group order.

To run the full recursive algorithm, call:
```
low_height_state=test_problem.sample_of_height(2)
```
This samples states and collimates them until it reaches the input height (in this case, 2).
It outputs a phase state, as an object of the class `PhaseState`.

### States

The `PhaseState` class represents individual states.

One can print out the main features of the state:
```
low_height_state.display()
```
The height of a state in this program is equal to 2^h for the height h used in Kuperberg's paper.

One can try to "balance" the state:
```
balanced_state=low_height_state.balance()
```
This returns a state with an injective b-function, or returns "false" if the simulated measurement fails.

If it has length 2, a state can also be measured in the +,- basis:
```
balanced_state.measure()
```
which returns 1 or 0.

### Collimating

The other main function is 
```
collimate(phase_state_array,M)
```
which performs the collimation subroutine. Here the phase_state_array is an array of `PhaseState` objects,
from the same `HiddenShiftProblem`. It can be array of size 1. 

The M is slightly different than what Kuperberg defines m to be. In his paper, collimation reduces 
a state of "height" 2^h to 2^m. This routine reduces a state of height h to h/M. Hence, M must 
divide the heights of all the input states. 

## Other Notes

Since the original paper did not explicitly optimize the choice of M, the reduction at each step,
I chose to set M to be the square root of the remaining height. This roughly matches the original
parameterization but is unlikely to be optimal.

To change this parameterization, you need to provide three things:
 * an array of height targets to recursively hit
 * a dictionary that maps height targets to the value of M to use at that height
 * a dictionary that maps height targets to length targets

These should be constructed in the `build_params` method of `HiddenShiftProblem`. 

Please let me know if you improve this.

## Authors

* **Samuel Jaques**

## License

Copyright 2019 Samuel Jaques

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
