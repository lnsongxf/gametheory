
"""" We give a game table (called "payoffs"; see below) to this program. 
It then returns the same game but with all non-rationalizable actions removed."""

from openopt import LP
import numpy as np
from operator import *
#2player game from above
#payoffs = np.array([[[0.,0.],[1.,3.],[-1.,1]],[[3.,1.],[1.,1.],[-2.,-0.]],[[5.,-1.],[1.,-1.],[2.,2.]]])
#payoffs = np.array([[[0.,0.],[1.,3.]],[[1.,1.],[2.,1.]]])
#3player game (3*3*2 action) in which only (0,1,0) is rationalizable
payoffs = np.array([[[[1.,0.,1.],[0.,3.,2.],[-1.,1,0.]],[[4.,1.,2.],[1.,1.,1.],[2.,0.,0.]],[[1.,-1.,1.],[4.,-1.,1.],[2.,2.,0.]]],[[[0.,0.,0.],[1.,3.,1.],[-1.,1,3.]],[[3.,1.,0.],[1.,1.,0.],[-2.,-0.,2.]],[[5.,-1.,0.],[1.,-1.,0.],[2.,2.,3.]]]])




dim = payoffs.shape

n = payoffs.ndim-1#number of players
no_a = [] #will contain number of actions available for each player
#as the first number is number of actions of last player etc., we eventually turn the list around
for i in dim[:-1]:
    no_a.append(i)
no_a = no_a[::-1]

#constructs payoffs of only player i when playing ai from the payoffs in "game", returns a "flat" vector
def payoffi_builder(game,ai,i):
    j = n-1#the next few lines define a list of slice object to extract i's payoffs when he plays ai from the payoff matrix; 
      #recall that the first index denotes the action of the last player in payoffs!
    obj = ()
    while j>i:
        obj = obj + (slice(0,None,1),)
        j = j-1
    obj = obj + (slice(ai,ai+1,2),)
    j = j-1
    while j>=0:
        obj = obj + (slice(0,None ,1),)
        j = j-1
    obj = obj + (slice(i,i+1,2),)
    payoffi = game[obj]
    return payoffi.flatten()


#this function gets a game and removes all actions from the game that correspond to dominated actions of Pi; 
#the game without these actions is returned
def delete_dom_act_Pi(game,i):
    no_a_game = list(game.shape) #will contain number of actions available for each player
    no_a_game.pop()#removes last element of list which simply was n: the number of payoffs in each action profile
    #as the first number is number of actions of last player etc., we turn the list around
    no_a_game = no_a_game[::-1]
    no_a_i = no_a_game.pop(i)#remove the number of actions of player i from no_a_game and put it in no_a_i
    if no_a_i==1:#if a single action remains it cannot be dominated
        return game
    var_no = np.prod(no_a_game)#size of the support of mu
    if var_no == 1:#special case: the support of mu has a single elment
        return del_dom_a_Pi_point_belief(game, i,no_a_i)
    temp_game = game
    f = [0.]*var_no   #dummy objective used below
    lb = [0.]*var_no
    ub = [1.]*var_no
    Aeq = [[1.]*var_no]
    beq = (1.,)
    j = 0
    while j<no_a_i:
        u_action = payoffi_builder(game,j,i)
        A = []
        b = []
        k = 0
        while k<no_a_i:
            u_other_action = payoffi_builder(game,k,i)
            A.append(u_other_action - u_action)#elementwise difference
            b.append(0.)
            k+=1
        p = LP(f, A=A,b=b,lb=lb,ub=ub,Aeq=Aeq,beq=beq)#we use the artificial minimization problem under the constraint that action gives a weakly higher payoff than any other action; if no feasible solution is obtained than action is dominated
        p.iprint = -1
        r = p.minimize('pclp')
        if r.stopcase!=1:#if no feasible solution was obtained then action is dominated...
            temp_game = np.delete(temp_game,j,n-i-1)#...and therefore action j is removed; recall that players are "in the wrong order"
            count = 0
            z = -1
            while count<=j:
                z+=1
                if undominated[i][z]!=-1 :
                    count+=1 
            undominated[i][z] = -1
        j+=1
    return temp_game


def del_dom_a_Pi_point_belief(game, i,no_i_a):
    to_delete = []
    U=[]
    for action in range(no_i_a):
        U.append(payoffi_builder(game,action,i))
    Umax = max(U)
    for action in range(no_i_a):
        if U[action]!=Umax:
            to_delete.append(action)
            count = 0
            z = -1
            while count<=action:
                z+=1
                if undominated[i][z]!=-1 :
                    count+=1 
            undominated[i][z] = -1
    for action in to_delete[::-1]:
        game = np.delete(game,action,n-i-1)
    return game


flag = 0#will be zero as long as not all dominated actions are removed yet

##will contain undominated actions
undominated = [range(item) for item in no_a]

temp1 = payoffs
while flag==0:
    temp2 = temp1
    for k in range(n):
        temp1 = delete_dom_act_Pi(temp1,k)
    if temp2.shape == temp1.shape:
        flag = 1


print 'game table without non-rationalizable actions is', temp1


for k in range(n):
    undominated[k] = [item for item in undominated[k] if item!=-1]
    print 'rationalizable actions of player',k,'are', undominated[k]
