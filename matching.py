
import random
import cPickle as pickle

def read_sc(school,student):
    """reads in data from two files: 'school' contains in line k first the capacity of school k and then the student numbers separated by ',' ordered according to k's priorities from highest to lowest priority; 'student' has in line k the preferences of student k i.e. a sequence of school numbers from best to worst separated by ',' """
    school_file = open(school,'r')
    capacity = []
    priority = []
    for line in school_file:
        line.strip()
        line = line.split(',')
        num_line = []
        for element in line:
            num_line.append(int(element))
        capacity.append(num_line.pop(0))
        priority.append(num_line)
    school_file.close()
    stud_file = open(student,'r')
    preference = []
    for line in stud_file:
        line.strip()
        line = line.split(',')
        num_line=[]
        for element in line:
            num_line.append(int(element))
        preference.append(num_line)
    stud_file.close()
    return priority, capacity, preference


def gen_sc(nschool,nstud,overcap=False,maxovercap=False,savefile=False):
    """generates a (pseudo) random school choice problem with nstud students and nschool schools; if overcap ==True, the problem will have a higher number school places than students; maxovercap is a maximum overcapacity allowed; savefile=True will OVERWRITE/save the generated example in the files school.txt and student.txt in the current working directory"""
    capacity = []
    average = float(nstud)/nschool
    i = 1
    while i<= nschool:
        capacity.append(int(random.triangular(average/10.0,3*average,0.2*average)))#draws capacity from a triangular distribution between average/5 and 5*average with mode at 0.9*average
        i = i + 1
        #print capacity, i, nschool, sum(capacity)
        if i == nschool and overcap==True and sum(capacity)<nstud:#checks that enough places for all students are available
            capacity = []
            i = 1
        if maxovercap!=False and sum(capacity)>nstud + maxovercap:
            capacity = []
            i = 1
    priority = []
    for i in range(nschool):
        x = range(nstud)
        random.shuffle(x)
        priority.append(x)
    preference = []
    for j in range(nstud):
        x = range(nschool)
        random.shuffle(x)
        preference.append(x)
    if sum(capacity)<nstud:#creates a dummy school "nschool+1" to which every student not getting a place will be matched
        for student in preference:
            student.append(nschool)
        priority.append(range(nstud))
        capacity.append(nstud)
    if savefile!=False:
        school_file = open('school.txt','w')
        for i in range(nschool):
            line = str(capacity[i]) + ','
            priority_str = str(priority[i])
            priority_str = priority_str.strip('[')
            priority_str = priority_str.strip(']')
            line = line + priority_str 
            school_file.write(line)
            school_file.write("\n")
        school_file.close()
        stud_file = open('student.txt','w')
        for i in range(nstud):
            line = str(preference[i])
            line = line.strip('[')
            line = line.strip(']')
            stud_file.write(line)
            stud_file.write("\n")
        stud_file.close()
    return priority, capacity, preference

class schoolchoice:
    def __init__(self,priority, capacity, preference):
        """read in data: priorities is a list of lists where the kth lower level list is the priority of school k, capacity is a list of school capacities (same order of schools as in priority), preferences is a list of lists where the ith sublist is the preference ranking of student i"""
        self.priority = priority
        self.capacity = capacity
        self.preference = preference
        self.nschool = len(capacity)
        if self.nschool != len(priority):
            print "input error: capacity and priority list must have same length"
        self.nstud = len(preference)
        self.gs_match = []#will contain Gale Shapley match if this is calculated
        self.boston_match = []
        self.ttc_match = []
    #
    def gs(self):
        """uses the Gale Shapley student proposing algorithm to solve the matching problem"""
        flag = 0 #dummy used to indicate whether the algorithm has finished
        pref = list(self.preference) #useful as the algorithm manipulates this list
        while flag == 0:
            flag = 1
            match = []#contains list of lists where the kth lower level list are the students matched with school k
            unmatched = []#list of unmatched students
            for i in range(self.nschool):
                proposers = filter(lambda x: i==pref[x][0],self.priority[i])# list of students proposing to i in this round
                if len(proposers)<=self.capacity[i]:
                    match.append(proposers)
                else:
                    match.append(proposers[:self.capacity[i]])
                    unmatched = unmatched +proposers[self.capacity[i]:]
            if unmatched != []:
                flag = 0
                for j in unmatched:
                    pref[j]=pref[j][1:]#pref[j].pop(0) #deletes the top preference for the unmatched
        self.gs_match = list(match)
        return match
    #
    def ttc(self):
        """Uses the top trading cycle algorithm on the matching problem"""
        unmatched = range(self.nstud)#unmatched students
        match = [[] for i in range(self.nschool)]#contains list of lists where the kth lower level list are the students matched with school k
        pref = list(self.preference)
        priori = list(self.priority)
        counter = list(self.capacity)
        while unmatched != []:
            cyc_stud = [unmatched[0]]
            cyc_school = [pref[unmatched[0]][0]]
            cyc_closed = False#indicates whether we have a cycle
            while cyc_closed == False:
                top_stud = priori[cyc_school[len(cyc_school)-1]][0]#student with highest priority in last school in cyc_school
                if top_stud in cyc_stud:
                    cyc_closed = True
                    cyc_stud = cyc_stud[cyc_stud.index(top_stud):] #deletes the students that are not par tof the cycle
                    for stud in cyc_stud:
                        school0 = pref[stud][0]#the school to which stud is matched
                        unmatched.remove(stud)#removes the student from unmatched
                        match[school0].append(stud)#adds the student to match
                        counter[school0] = counter[school0] - 1#decreases capacity counter
                        for k in range(self.nschool):#removes the matched student from all schools priorities
                            try:#using "try" avoids error if stud is not elligible at a certain school, i.e. not in its priority ranking
                                priori[k].remove(stud)
                            except:
                                pass
                        if counter[school0] == 0:#removes schools that have no capacity left from remaining students preferences
                            for j in range(self.nstud):
                                try:#the remove command below returns an error if a student did not list school0 in his preferences
                                    pref[j].remove(school0)
                                except:
                                    pass
                else:
                    cyc_stud.append(top_stud)
                top_school = pref[cyc_stud[len(cyc_stud)-1]][0]#most preferred school of last student in cyc_stud
                if top_school in cyc_school and cyc_closed == False:
                    cyc_closed = True
                    cyc_school = cyc_school[cyc_school.index(top_school):]
                    for school in cyc_school:
                        stud = priori[school][0]#student to which school points
                        unmatched.remove(stud)#student is removed from unmatched
                        match[school].append(stud)#adds the student to match
                        counter[school] = counter[school] - 1#reduce counter by 1
                        for k in range(self.nschool):#removes the matched student from all schools priorities
                            try:#using "try" avoids error if stud is not elligible at a certain school, i.e. not in its priority ranking
                                priori[k].remove(stud)
                            except:
                                pass
                        if counter[school] == 0:#removes schools that have no capacity left from remaining students preferences
                            for j in range(self.nstud):
                                try:
                                    pref[j].remove(school)
                                except:
                                    pass
                elif cyc_closed == False:
                    cyc_school.append(top_school)
        self.ttc_match = list(match)
        return match
    #
    def boston(self):
        """uses the Boston school matching algorithm to solve the matching problem"""
        flag = 0 #dummy used to indicate whether the algorithm has finished
        pref = list(self.preference) #useful as the algorithm manipulates this list
        capa = list(self.capacity) #useful as the algorithm manipulates this list
        match = [[] for i in range(self.nschool)] #list of nschool empty lists, kth list is list of students at school k
        while flag == 0:
            flag = 1
            unmatched = []#list of unmatched students
            for i in range(self.nschool):
                proposers = filter(lambda x: i==pref[x][0] and x not in match[i],self.priority[i])# list of students proposing to i in this round
                if len(proposers)<=capa[i]:
                    match[i] = match[i] + proposers
                    capa[i] = capa[i] - len(proposers)
                else:
                    match[i] = match[i] + proposers[:capa[i]]
                    unmatched = unmatched + proposers[capa[i]:]
                    capa[i] = 0
            if unmatched != []:
                flag = 0
                for j in unmatched:
                    pref[j].pop(0) #deletes the top preference for the unmatched
        self.boston_match = list(match)
        return match

def save_scp(scp,filename):
    """saves an existing school choice problem with name scp as filename; advantage: will also save previously calculated matches and not only preferences etc."""
    with open(filename,'wb') as output:
        pickle.dump(scp,output,pickle.HIGHEST_PROTOCOL)

def open_scp(filename):
    """returns a previously as 'filename' saved school choice problem"""
    with open(filename,'rb') as input:
        return pickle.load(input)

def save_match(match,filename_school='match_school.txt',filename_student='match_student.txt'):
    """saves a given match in 2 files: 'match_school' contains in line k the student numbers matched to school k; 'match_student' contains in line k the school matched to student k"""
    student_lst1 = []
    school_lst = open(filename_school,'w')
    for school in range(len(match)):
        for student in match[school]:
            student_lst1.append((student,school))
        line = str(match[school])
        line = line.strip('[')
        line = line.strip(']')
        school_lst.write(line)
        school_lst.write('\n')
    student_lst1 = sorted(student_lst1)
    student_lst = open(filename_student,'w')
    for item in student_lst1:
        student_lst.write(str(item[1]))
        student_lst.write('\n')
    student_lst.close()
    school_lst.close()
