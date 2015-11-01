
from numpy import *
from openopt import LP
from operator import add

##TO DO: funnily, the solver cannot solve games in which each player has a unique rationalizable action
## and returns an error there.
##This could be easily fixed by handing the game to the rationalizability solver in the "except" statement below.

#the game is read in
# format: first we keep the action of P2 fixed and vary P1's action
# hence, we write the columns of the game table as lists
# for 3 players: holding P3's action fixed we have a two player game as below;
#simply enter a list of these two player games (one for each action of P3);
#for more players: proceed as going from 2 to 3
game = [[(0,0),(1,5)],[(5,1),(4,4)]]
#example game with three actions per player
#game = [[(0,0),(1,1),(1,1)],[(1,1),(0,0),(1,1)],[(1,1),(1,1),(0,0)]] 
#example game with three players (see MSZ example 8.2)
#game = [[[(0,1,3),(1,1,1)],[(0,0,0),(1,0,0)]],[[(2,2,2),(2,2,0)],[(0,0,0),(2,2,2)]],[[(0,1,0),(1,1,1)],[(0,0,0),(1,0,3)]]]
##example game with only one rationalizable action per player (currently cannot be solved)
#game = [[(3,2),(1,1)],[(2,1),(1,3)]]
##matching pennies example: there is a unique correlated equilibrium
#game = [[(1,-1),(-1,1)],[(-1,1),(1,-1)]]

#determine the set of all payoff profiles and write them in one long list
Ulist = game #will become a list of all payoff profiles which is similar to as set of all action profiles
no_action = [] #a vector which contains the number of actions of each player

temp = 1
while type(Ulist[0])!=tuple:
    no_action.insert(0,len(Ulist)/temp)
    temp = temp*no_action[0]
    Ulist = [item for sublist in Ulist for item in sublist]
no_action.insert(0,len(Ulist)/temp)
#resulting format of Ulist:
#Ulist is list of payoff tuples (for 2 player games, we move column by column):
#-first tuple is when every player uses his first action
#-second tuple: P1 uses his second action, everyone else his first
#-third tuple: P1 uses his third action, everyone else his first etc.
#-...
#-..:P2 uses second action, everyone else uses first
#-...: P1 and P2 use second action; everyone else first action
#...

#construct a payoff list by player,
#Ulist_by_player contains one tuple for each player,
#the i-th tuple contains Pi's payoffs for each action profile (ordered as in Ulist)
Ulist_by_player = zip(*Ulist)


#creates a vector with one entry for every action profile (ordered as in Ulist)
#entry of the vector is "1." if player i uses action k in this action profile
#entry is "0." otherwise
#note: k=0 is the first action of a player, i=0 is first player
def aik_indicator(i,k):
    temp = 1
    j = 0
    while j < len(no_action):#j cycles through all players
        if j<i:
            temp = temp*no_action[j]
        elif j==i:
            x = [0.]*temp*k + [1.]*temp + [0.]*temp*(no_action[i]-k-1)
            temp = 1
        else:
            temp = temp*no_action[j]
        j+=1
    x = x*temp
    return x


#for i>0: in Ulist, several consecutive payoff profiles have the same action for player i
# this function calculates how many profiles where i plays ai are next to each other
#before a profile comes in which i plays another action ai'
#note i=0 is the first player
def blockwidth(i):
    if i == 0:
        return 1
    else:
        return prod(no_action[:i])

#construct ui(ap,a-i)-ui(ak,a-i)
# take i's payoff vector, generate a shifted payoff vector z
# such that the entry ui(ap,a-i) is at the same position in z as ui(ak,a-i) is in the original payoff vector
# note 1: i=0 is first player
# note 2: construction only makes sense at entries where a-i is held constant, i.e. there are some non-sense entries generated which will be irrelevant
def udiff(i,k,p):
    width = blockwidth(i)
    y = list(Ulist_by_player[i])
    if p<k:
        z = [0.]*width*(k-p) + y
        z = z[:len(Ulist)]
    if p>k:
        z = y[width*(p-k):]
        z = z + [0.]*width*(p-k)
    if p==k:
        z = y
    return subtract(z,list(Ulist_by_player[i]))


#to find the Pareto optimal equilibrium, we create a vector that sums for each action profile the payoffs of all players
welfare = [0.]*len(Ulist)
for payoff in Ulist_by_player:
    welfare = map(add,welfare ,list(payoff))

  
#construct inequality constraints and solve
neg_welfare = multiply(-1.,welfare)#objective as we will run a minimization problem
lb = [0.]*len(Ulist)
ub = [1.]*len(Ulist)
Aeq = [[1.]*len(Ulist)]
beq = (1.,)
A  = []
b = []
player = 0
while player<len(no_action):
    action = 0
    while action < no_action[player]:
        for k in range(0,no_action[player]):
            A.append(multiply(udiff(player,action,k),aik_indicator(player,action)))
            b.append(0.)
        action = action + 1
    player = player +1
#print A,b
p = LP(neg_welfare, A=A,b=b,lb=lb,ub=ub,Aeq=Aeq,beq=beq)#we use the artificial minimization problem under the constraint that action gives a weakly higher payoff than any other action; if no feasible solution is obtained than action is dominated
p.iprint = -1
try:
    r = p.minimize('pclp')
    pminw = LP(welfare, A=A,b=b,lb=lb,ub=ub,Aeq=Aeq,beq=beq)
    pminw.iprint = -1
    rminw = pminw.minimize('pclp')

except:
    print "Solver returns error. Probably, each player has a unique rationalizable action (check with rationalizability solver)."
    quit()
    
###formatting the result back into the same format as the game input
# first: rounding
outr = []
for item in r.xf:
    outr.append(round(item,3))

outrminw = []
for item in rminw.xf:
    outrminw.append(round(item,3))

def backtolist(i,inlist):
    width = blockwidth(i)
    out = []
    for k in range(0,len(inlist),width):
        temp = inlist[k:k+width]
        if i>1:
            temp = backtolist(i-1,temp)
        out.append(temp)
    return out

outmax = backtolist(len(no_action)-1,outr)
outmin = backtolist(len(no_action)-1,outrminw)

#format of output is now as in game input
print 'a correlated equilibrium maximizing the sum of payoffs is', outmax
print 'a correlated equilibrium minimizing the sum of payoffs is', outmin
