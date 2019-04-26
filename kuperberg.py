from numpy import array
from fractions import gcd
import math
import random

class DoubleDict:
	#This is a class representing a function
	#b:B->J
	#but where we also want a function j:J->2^B
	#that returns the pre-image of an element of J
	#Thus the b function takes a "j" as input and returns a "b"
	#The j function takes a "b" ant returns a "j"
	def __init__(self):
		self.b_function={}
		self.j_function={}

	def add_b_key(self,key,item):
		#When adding a new key to the b-function
		#it must also update the j-function
		self.__new_b_key(key,item)
		self.__new_j_key(item,key)

	def add_j_key(self,key,item):
		self.__new_j_key(key,item)
		self.__new_b_key(item,key)

	def __new_j_key(self,key,item):
		if key in self.j_function:
			self.j_function[key].append(item)
		else:
			self.j_function[key]=[item]

	def __new_b_key(self,key,item):
		self.b_function[key]=item

	def get_b_of_j(self,key):
		return self.b_function[key]

	def get_j_of_b(self,key):
		return self.j_function[key]

	def length(self):
		return len(self.b_function)

	def check_b_key(self,key):
		return key in self.b_function

	def check_j_key(self,key):
		return key in self.j_function

	@classmethod
	def reverse_dict(self_class,input_dict):
		#Constructs a reverse dictionary out of a regular
		#dictionary
		new_dict=self_class()
		for key in input_dict:
			new_dict.add_b_key(key,input_dict[key])
		return new_dict


class HiddenShiftProblem:
	#This class represents an instance of a hidden
	#shift problem
	def __init__(
		self,
		group_size,
		shifts,#an array of integers representing the endomorphisms
		secret #the secret value s
		):
		"""Construct"""
		self.group_size=int(group_size)
		for phi in shifts:
			if gcd(group_size,phi)!=1:
				raise ValueError('Shifts are not endomorphisms')
		self.shifts=shifts 
		self.secret=secret
		self.states={}#A dictionary of arrays of states, represetning
					#which states are in quantum memory
					#They are indexed by height; self.states[h] contains
					#states of height at most h
		self.state_lengths={}#A dictionary of the product of lengths
						#in each array of states
		self.length_targets={}#Target lengths for states of a given height
		self.m_array={} #m-values used for collimation, indexed by height
		self.height_targets=[] #The different heights that will be used
						#This ends up lumping different heights together
						#but it prevents a "fragmenting" of heights
		self.final_height=2 #The target height of the final state
		self.query_count=0 #Number of queries (i.e., phase state samples)

	def get_shifts(self):
		return self.shifts

	def sample_state(self):
		#Randomly samples a new state for the problem
		self.query_count+=1
		return PhaseState.sample(self)

	def sample_nontrivial_state(self):
		#Randomly samples new states until the height is non-zer0
		new_state=self.sample_state()
		while new_state.height==0:
			new_state=self.sample_state()
		return new_state

	def m_function(self,h):
		#Returns the value of m used for collimation
		#Ideally the m value should already be in the array
		if h in self.m_array:
			return self.m_array[h]
		else:
			#This function guesses an optimal m as the square
			#root of the remaining height
			#However: There is an off-by-one error: the m
			#produced here should really be assigned to h*m, not h
			#But this is an okay approximation
			if self.group_size/h<=1:
				self.m_array[h]=1
				return 1
			m=max(int(math.sqrt(self.group_size/h)),2)
			while m>0:
				if (self.group_size/h)%m==0:
					self.m_array[h]=m
					return m
				m=m-1

	def build_params(self):
		#Sets the parameters of m, height targets, length targets, etc.
		self.height_targets=[2]
		h=2
		i=0
		self.states[h]=[]
		self.state_lengths[h]=1
		self.m_array[h]=1
		self.length_targets[h]=2
		while h<self.group_size:
			#Best guess for m: the value that will reduce the remaining
			#height by a square root
			m=self.get_m(math.sqrt(self.group_size/h),self.group_size/h)
			#We want to use this value of m for the next h
			h=h*m
			self.height_targets.append(h)
			i=i+1
			self.m_array[h]=m
			#Sets length targets so that the expected length is the right value
			self.length_targets[h]=math.sqrt(self.length_targets[self.height_targets[i-1]]*m)
			self.states[h]=[]
			self.state_lengths[h]=1
		#These are nice to see
		print 'Height targets:',self.height_targets	
		print'Length targets:',self.length_targets
		print 'Reduction targets:',self.m_array

	def get_m(self,target_m,h):
		#Given a target value for m
		#This finds the next permissible value,
		#since m must divide the height for the algorithm to work
		m=max(int(target_m),2)
		while m>0:
			if h%m==0:
				return m
			m=m-1

	def get_safe_m(self,h,input_length):
		#This picks a "safe" value of m for collimating
		#This is a value where it will approximately reach the
		#length target
		#However, there is an "off-by-one" error here
		#in which length target it picks
		#Thus, the algorithm (currently) does not use this
		m=self.get_m(input_length/self.length_targets[h],h)
		if (h/m)<2:
			m=h/2
		return m

	def set_m_function(self,m_function):
		#Currently unused
		self.m_array=m_function

	def state_insert(self,new_state):
		#Inserts a new state that has been created
		if new_state.height==0:
			#Ignores bad states
			return 
		if new_state.height<=8*math.sqrt(self.group_size):
			#This shows some progress without getting bogged down
			print 'Height:',new_state.height,'Length:',new_state.length
		#We need to find with array to insert into
		#This picks which pre-selected height is best
		for i in range(0,len(self.height_targets)):
			if self.height_targets[i]>=new_state.height:
				h=self.height_targets[i]
				break
		#Adds to array and increases the length count
		self.states[h].append(new_state)
		self.state_lengths[h]=self.state_lengths[h]*new_state.length
		#This lines forgets everything and returns the final state
		#if it fits the target height
		#Otherwise, the recursion can accumulate a "collimation debt"
		#and spends a long time collimating before finally returning
		if new_state.height<=self.final_height:
			return
		#Since a new state was added, it checks to see if there are enough
		#states to collimate, based on the expected length of the 
		#collimated state exceeding the target length
		if self.state_lengths[h]>=self.m_function(h)*self.length_targets[self.height_targets[max(i-1,0)]]:
			self.collimate_array(h)


	def collimate_array(self,h):
		#Collimates an array at a given height
		betterState=collimate(self.states[h],self.m_function(h))
		#Clears the previous array
		self.states[h]=[]
		self.state_lengths[h]=1
		self.state_insert(betterState)

	def sample_of_length(self,length_target):
		#Samples enough initial states to reach a specific length target
		finalState=self.sample_nontrivial_state()
		while finalState.length<length_target:
			finalState=mix_states(finalState,self.sample_nontrivial_state())
		return finalState

	def sample_of_height(self,height_target):
		#Repeatedly samples and collimates until it produces a state of the given
		#height
		self.final_height=height_target
		self.build_params()
		#It needs somewhere to put the finished state
		if not (height_target in self.states):
			self.states[height_target]=[]
		while not self.states[height_target]:
			self.state_insert(self.sample_of_length(self.length_targets[self.group_size]))
		return self.states[height_target][0]


	# 	#This follows Kuperberg's original description
	# 	#Currently it does not work with the class as written
	# def sampleOfHeight(self,height_target,r,length_target):
	# 	if height_target>=self.group_size:
	# 		finalState=self.sample_nontrivial_state()
	# 		while finalState.length<length_target:
	# 			finalState=mix_states(finalState,self.sample_nontrivial_state())
	# 	else:
	# 		height=0
	# 		while height==0:
	# 			state_array=[]
	# 			for i in range(0,r):
	# 				state_array.append(self.sampleOfHeight(height_target*self.m_function(height_target),r,length_target))
	# 				if state_array[i].height<=height_target and state_array[i].length>=length_target:
	# 					return state_array[i]
	# 			finalState=collimate(state_array,self.m_function(height_target))
	# 			height=finalState.height
	# 	return finalState



class PhaseState:
	#This is the class for a state
	#It mostly houses the (classically known)
	# "b-function" which makes j to the phase associated with j
	#Here, the phases are represented as integers
	#b_function.BofJ(j) gives the integer b associated with a state j
	#such that the phase is exp(2pi i b/N)
	def __init__(self,
		hidden_shift_problem,
		b_function):#
		self.base_problem=hidden_shift_problem
		self.b_function=b_function #It expects a b_function where b(0)=0
						#i.e., it's projected
						#This must also be a DoubleDict
		#Computes length and height
		#For a a phase integer b, the height is N/gcd(N,b)
		#The height of a phase state is the maximum height
		# of all phase integers in it
		self.length=b_function.length()
		self.height=0
		for i in range(1,self.length):
			#If this fails it means the phase state is badly formatted
			self.height=gcd(self.height,self.b_function.get_b_of_j(i))
		if self.height!=0:
			self.height=int(hidden_shift_problem.group_size/gcd(hidden_shift_problem.group_size,self.height))

	@classmethod
	def sample(stateClass,hidden_shift_problem):
		#Produces a random state according to the sampling process
		base_problem=hidden_shift_problem
		fourier_measurement=random.randint(0,base_problem.group_size-1)
		b_function=DoubleDict()
		height=base_problem.group_size;
		i=0;
		for phi in base_problem.get_shifts():
			#These should be projective
			#So it sets the first coordinate to 0
			#And this gives it an offset for all the other values
			if i==0:
				base=phi*fourier_measurement % base_problem.group_size
				b_function.add_b_key(i,0)
			else:
				b_function.add_b_key(i,(phi*fourier_measurement - base) % base_problem.group_size)
			i=i+1
		length=b_function.length()
		return stateClass(base_problem,b_function)

	@classmethod
	def state_from_b(stateClass,hidden_shift_problem,b_dict):
		#Produces a state from the b function provided by b_dict
		#b_dict should be a regular dictionary
		j_function={}
		first_flag=True
		base=0
		#Projects the coordinates in the dictionary
		for j in b_dict:
			if first_flag:
				base=b_dict[j]
				b_dict[j]=0
				first_flag=False
			else:
				b_dict[j]=(b_dict[j]-base)%hidden_shift_problem.group_size
		b_function=DoubleDict.reverse_dict(b_dict)
		return stateClass(hidden_shift_problem,b_function)

	def check_all_mods(self,j_val,modulus):
		#Checks whether there is any j in the state such that
		#b(j)=j_val mod (modulus)

		#Kuperberg's method was to sort on the low-order bits
		#That's not obvious in python so this is an inefficent
		#method in the meantime

		#It checks which is quicker: check all moduli,
		#or check all j values

		if self.base_problem.group_size/modulus<len(self.b_function.j_function):
			#Checks all moduli by added modulus to j_val
			j_flag=False
			de_modded_j=j_val
			while de_modded_j < self.base_problem.group_size:
				if self.b_function.check_j_key(de_modded_j):
					return True
				de_modded_j=de_modded_j+modulus
			return False
		else:
			#Brute force check of all j values
			for j in self.b_function.j_function:
				if (j % modulus)==j_val:
					return True
			return False

	def get_all_mods(self,j_val,modulus):
		#Returns all values of j such that b(j)=j_val mod (modulus)

		#Kuperberg's method was to sort on the low-order bits
		#That's not obvious in python so this is an inefficent
		#method in the meantime

		#It checks which is quicker: check all moduli,
		#or check all j values
		new_b_array=[];
		if self.base_problem.group_size/modulus<len(self.b_function.j_function):
			de_modded_j=j_val
			while de_modded_j<self.base_problem.group_size:
				if self.b_function.check_j_key(de_modded_j):
					new_b_array=new_b_array+self.b_function.get_j_of_b(de_modded_j)
				de_modded_j=de_modded_j+modulus
		else:
			for j in self.b_function.j_function:
				if (j % modulus)==j_val:
					new_b_array=new_b_array+self.b_function.get_j_of_b(j)
		return new_b_array

	def balance(self):
		#Takes a state, and probabilistic returns a state where 
		#each distinct value of b(j) has an equal-sized preimage
		#(and thus, it sets the pre-image to size 1)
		#This ignores the quantum cost to re-order things
		new_b_function={}
		min_length=self.length
		i=0
		#The balanced state will have preimages equal to the size
		#of the smallest preimage of the current state, which this
		#loop finds
		for b in self.b_function.j_function:
			j=self.b_function.get_j_of_b(b)
			if len(j)<min_length:
				min_length=len(j)
			new_b_function[i]=b
			i+=1
		#Randomly selects a value to simulate measurement
		r=random.randint(0,self.length)
		if r<min_length*len(self.b_function.j_function):
			return PhaseState.state_from_b(self.base_problem,new_b_function)
		else:
			return False

	def measure(self):
		#Measures a length-2 state in the |+>, |-> basis
		if self.length>2:
			print('Cannot measure this state yet')
			return False
		angle=(2.0*math.pi)*float(self.base_problem.secret* self.b_function.get_b_of_j(1))/float(self.base_problem.group_size)
		prob_0=(math.pow(1+math.cos(angle),2)+math.pow(math.sin(angle),2))/2.0
		print(prob_0)
		r=random.uniform(0,1)
		if r<prob_0:
			return 0
		else:
			return 1

	def display(self):
		print 'State of height',self.height,'and length',self.length
		if self.length<=100: #arbitrary cutoff
			print 'B function:',self.b_function.b_function
		else:
			print  'Too long to display b-function'


def mix_states(first_state,second_state):
		#Returns the tensor product of two states
		#with a new state 
		#The b-function is simple to calculate for these states
		if (first_state.base_problem!=second_state.base_problem):
			raise ValueError('States do not share a group')
		b_function=DoubleDict()
		length=first_state.length*second_state.length
		for i in range(0,length):
			b_function.add_b_key(i,(first_state.b_function.get_b_of_j(i/second_state.length)+second_state.b_function.get_b_of_j(i % second_state.length)) % first_state.base_problem.group_size)
			i=i+1
		return PhaseState(first_state.base_problem,b_function)


def collimate(state_array,M):
	#Takes an array of states and performs the collimation process

#	print 'Collimating',len(state_array),'vectors from height',state_array[0].height,'to',state_array[0].height/M
	c=0
	max_height=0
	for state in state_array:
		max_height=max(max_height,state.height)
	#min_height is the minimum amount of "space" availale
	min_height=state_array[0].base_problem.group_size/max_height
	M=M*min_height
	#Simulate measuring a random value of c
	for state in state_array:	
		random_j=random.randint(0,state.length-1)
		c=(c+state.b_function.get_b_of_j(random_j)) % M
	b_function=DoubleDict()
	r=len(state_array)
	#b_array contains the guesses for values of b(j)
	#that will sum to c
	#b_array[r-1] is always set so that the sum of 
	#the values will be equal to c mod (M)
	b_array=[0]*r
	b_array[r-1]=c
	pi_function={}
	new_j=0
	i=0
	base_val=0
	firstFlag=True
	while i>=0:
		#Check whether the values in b_array are possible,
		#given the b functions in the states being collimated
		while i<r and state_array[i].check_all_mods(b_array[i],M):
			#This loop iterates up until it finds one that doesn't match
			if i==r-1:
				#If all checks pass, it constructs an array of possible j-values
				#The j-values are the product of individual values
				#Hence we want b_array to be a list of lists
				#Each element is a list of j-values j1,...,jr
				#such that b1(j1)+...+br(jr)=c (mod M)
				#These are built by appending all possible values of ji
				#such that bi(ji)=j_array[i], for each i
				#get_all_mods returns these values of ji
				j_array=state_array[0].get_all_mods(b_array[0],M)
				j_array_temp=[]
				for j in j_array:
					j_array_temp.append([j])
				j_array=j_array_temp
				for k in range(1,r):
					j_array_temp =[]; 
					new_j_array=state_array[k].get_all_mods(b_array[k],M)
					for j in j_array:
						for newj in new_j_array:
							jnew=list(j)
							jnew.append(newj)
							j_array_temp.append(jnew)
					j_array=j_array_temp
				#Once all these values are found, they define new b values
				#here b=b1(j1)+...+br(jr) (without the mod)
				for j_vec in j_array:
					b=0;
					for k in range(0,r):
						b=b+state_array[k].b_function.get_b_of_j(j_vec[k])
					#This "projects" onto the first coordinate
					if firstFlag:
						base_val=b
						b=0
						firstFlag=False
					else:
						b=(b-base_val)% state_array[0].base_problem.group_size
					#The pi function maps that tuple to j, which increases
					#sequentially
					pi_function[tuple(j_vec)]=b
					b_function.add_b_key(new_j,b)
					new_j+=1
			i+=1
		if i>=r-1:
			#if it breaks the first loop with i too large, it means it successfully 
			#added new values, so it should try a new value of b_array[r-2]
			i=r-2
		#increment the next value of j_array
		#(changing b_array[r-1] to maintain congruence with c)
		b_array[i]+=min_height
		b_array[r-1]=(b_array[r-1]-min_height) % M
		#If it exceeds the maximum possible value:
		while b_array[i]>= M:
			#loop back as much as necessary
			i-=1
			if i>=0: 
				b_array[i]+=min_height
				b_array[r-1]=(b_array[r-1]-min_height) % M
		#once it increments properly, clear the rest of the values to 0
		for k in range(i+1,r-1):
			b_array[r-1] = (b_array[r-1] - b_array[k] )% M
			b_array[k]=0
	if b_function.length()==0:
		#A collimation should never produce a length-0 state
		#So this checks for logic errors in the code
		print 'Collimation error'
	return PhaseState(state_array[0].base_problem,b_function)

	


