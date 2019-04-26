from kuperberg import HiddenShiftProblem
from kuperberg import PhaseState
import math


test_problem=HiddenShiftProblem(math.pow(2,40),[1,3,7],3)
low_height_state=test_problem.sample_of_height(2)
print('Queries:',test_problem.query_count)
low_height_state.display()
balanced_state=low_height_state.balance()
if balanced_state:	
	balanced_state.display()
	print(balanced_state.measure())
print('Unbalanced:')

