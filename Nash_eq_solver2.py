
""" Finds a Nash equilibrium of a finite strategic form game of complete information.
A strategy of player i is represented as an array where the number of elements equals
the number of actions of this player; each element is the probability
of the corresponding action. 
A strategy profile is an array of strategies. """

from openopt import SNLE
import numpy as np
import time
start_time = time.time()

#these are the payoffs from the game table; 
#each column in the game table is a list of payoff tuples; 
#the game table is then a list of these columns
payoffs = np.array([[[0,0],[1,3]],[[3,1],[1,1]]])
#for games with 3 or more players:
## 3 players: an array with two player games as its components,
##the first one corresponds to the first action of P3 etc.
## n players: an array of 'n-1 player games', the k-th corresponds to the k-th action of player n
##example for 3 players with P1 having 3 actions, P2 and P3 having 2 actions
#payoffs = np.array([[[[0,0,0],[1,3,0],[1,1,1]],[[3,1,0],[1,1,0],[1,1,1]]],[[[0,0,0],[1,3,0],[1,1,1]],[[3,1,0],[1,1,0],[1,1,1]]]] ) 

dim = payoffs.shape

n = payoffs.ndim-1#number of players
no_a = [] #will contain number of actions available for each player
#as the first number is number of actions of last player etc., we eventually turn the list around
for i in dim[:-1]:
    no_a.append(i)
no_a = no_a[::-1]
    
#gets numpy array of likelihoods of action profiles (from players 0..i-1) and strategy of player i, 
#returns likelihoods of action profiles for players up to i
def help(probmatrix, strati):
    new = np.array([probmatrix*prob for prob in strati])
    return new

#returns the expected payoff of player i from playing ai if others play mixed strategies stratmini
def EUi(stratmini,ai,i):
    j = n-1#the next few lines define a list of slice object to extract i's payoffs when he plays ai from the payoff matrix; 
    #recall that the first index denotes the action of the last player in payoffs!
    obj = ()
    while j>i:
        obj = obj + (slice(0,None,1),)
        j = j-1
    obj = obj + (slice(ai,ai+1,1),)
    j = j-1
    while j>=0:
        obj = obj + (slice(0,None ,1),)
        j = j-1
    obj = obj + (slice(i,i+1,1),)
    payoffi = payoffs[obj]
    temp = np.array([1.])#constructs probability matrix, giving probabilities of action profiles of other players
    for stratj in stratmini:
        temp = help(temp,stratj)
    return np.dot(temp.flatten(),payoffi.flatten())
    

#This function takes a mixed strategy profile as argument.
#The output is the Delta described above but it returns the Delta for all players as a flat(!)  numpy array.
def Delta(strat):
    i = 0
    out = []
    while i < n:
        stratmini = strat[0:i] + strat[i+1:len(strat)]
        uimax = -1000.0#assumes that all payoffs are above -1000.0
        uilist = []
        for action in range (no_a[i]):
            uact = EUi(stratmini,action,i)
            uilist.append(uact)
            uimax = max(uimax,uact)
        deltai = [item - uimax for item in uilist]
        out.append(deltai)
        i+=1
    return np.array([item for sublist in out for item in sublist])


no_a_np = np.array(no_a)
total_no_a = no_a_np.sum()

lb = [0.0]*total_no_a#lower bound to ensure that all probabilities are above 0
ub = [1.0]*total_no_a#upper bound ensures that all probs are below 1

Aeq = []#constraints that ensure that both the  mixed strategies fo each player sum to 1
beq = [1.]*n#dito
x0 = []
actagg = [0]

for i in range(n):
    no_a_i = no_a[i]
    Aeq.append([0.]*actagg[i] + [1.]*no_a_i + [0.]*(total_no_a-actagg[i]-no_a_i))
    x0 = x0 + [1.0/no_a_i]*no_a_i
    actagg.append(actagg[i]+no_a_i)

#multiplies the vectors strat and Delta(strat); this product has to be 0 in equilibrium
def product(x):
    strat = []
    for i in range(n):
        strat.append(x[actagg[i]:actagg[i+1]])
    return np.dot(x,Delta(strat))

p = SNLE(product,x0,lb=lb,ub=ub,Aeq=Aeq,beq=beq)
p.iprint = -1
r = p.solve('nssolve')

if r.stopcase==1:
    print 'there is an equilibrium in which '
    for i in range(n):
        out = [round(item,3) for item in r.xf[actagg[i]:actagg[i+1]]]
        print 'player',i,'uses the mixed strategy',out
else:
    print 'Error: solver cannot find an equilibrium'

print("--- %s seconds ---" % (time.time() - start_time))
