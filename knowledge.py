
class infostructure:

    def __init__(self,partitions):
        """read in partitions 
        'partitions' is a list where each element is the info partition of one player
        an info partition is a list of sets where each set is one element of the partition"""
        self.parts = partitions
        self.n = len(self.parts)#number of players

    def know(self,event,i):
        "returns the set of states in which player i knows event"
        out = set()
        info_i = self.parts[i]
        for part in info_i:
            if part.issubset(event):
                out = out.union(part)
        return out

    def common_know(self,event):
        "returns the states in which event is common knowledge"
        candidate = event
        old_candidate = set()
        while old_candidate!=candidate and len(candidate)>0:
            old_candidate = candidate
            for i in range(self.n):
                candidate = self.know(candidate,i)
        return candidate

    def common_know_in_w(self,event,w):
        "checks whether event is common knowledge in state w; returns True/False"
        if w in self.common_know(event):
            return True
        else:
            return False

    def self_evident(self,event,players):
        "checks whether event is self evident among players in list 'players' "
        for i in players:
            for part in self.parts[i]:
                if len(event.intersection(part))>0 and not part.issubset(event):
                    return False
        return True
                        

partition1 = [{1,2},{3,4,5},{6}]
partition2 = [{1},{2,3,4},{5},{6}]
ex1 = infostructure([partition1,partition2])



F = {1,2,3,4,5}
E = {1,2,3,4}
return 'F is common knowledge in states ',list(ex1.common_know(F)), '.  E is common knowledge in states ', list(ex1.common_know(E)),'.'
