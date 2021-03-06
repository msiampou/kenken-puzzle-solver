from csp import*
import re
import sys
import time
from functools import reduce

class KenKen(CSP):
    def __init__(self,variables,domains,neighbors,data):
        self.variables = variables
        self.domains = domains
        self.neighbors = neighbors
        self.data = data
        self.constraint = self.getConstraint

        CSP.__init__(self,variables,domains,neighbors,self.constraint)

    def getConstraint(self, A, a, B, b):
        if a==b:
            return False

        xA = xB = 0
        vars = len(self.data[2])
        for pos in range(vars):
            if A in self.data[2][pos]:
                xA = pos
            if B in self.data[2][pos]:
                xB = pos

        if self.data[1][xA] == "''":
            c1 = self.blank(a,xA)
        elif self.data[1][xA] == '+':
            c1 = self.add(A,a,xA)
        elif self.data[1][xA] == '-':
            c1 = self.sub(A,a,xA)
        elif self.data[1][xA] == '/':
            c1 = self.div(A,a,xA)
        elif self.data[1][xA] == '*':
            c1 =  self.mult(A,a,xA)

        if self.data[1][xB] == "''":
            c2 = self.blank(b,xB)
        elif self.data[1][xB] == '+':
            c2 = self.add(B,b,xB)
        elif self.data[1][xB] == '-':
            c2 = self.sub(B,b,xB)
        elif self.data[1][xB] == '/':
            c2 = self.div(B,b,xB)
        elif self.data[1][xB] == '*':
            c2 = self.mult(B,b,xB)

        return c1 and c2

    def blank(self,val,x):
        if self.data[0][x] == val:
            return True
        return False

    def add(self,var,val,x):
        vars=[]
        for v in self.data[2][x]:
            if v == var:
                vars.append(int(val))
            elif v in self.infer_assignment():
                vars.append(int(self.infer_assignment()[v]))
        if sum(vars) <= self.data[0][x] and len(vars) <= len(self.data[2][x]):
            return True
        return False

    def mult(self,var,val,x):
        vars=[]
        for v in self.data[2][x]:
            if v == var:
                vars.append(int(val))
            elif v in self.infer_assignment():
                vars.append(int(self.infer_assignment()[v]))
        if reduce(lambda x, y: x*y, vars) == self.data[0][x] and len(vars) == len(self.data[2][x]):
            return True
        elif reduce(lambda x, y: x*y, vars) <= self.data[0][x] and len(vars) < len(self.data[2][x]):
            return True
        return False

    def div(self,var,val,x):
        for v in self.data[2][x]:
            if v!= var:
                a = v
        if a in self.infer_assignment():
            b = self.infer_assignment()[a]
            return max(b, val) / min(b, val) == self.data[0][x]
        else:
            for i in self.choices(a):
                if max(i, val) / min(i, val) == self.data[0][x]:
                    return True
            return False

    def sub(self,var,val,x):
        for v in self.data[2][x]:
            if v!= var:
                a = v
        if a in self.infer_assignment():
            b = self.infer_assignment()[a]
            return max(b, val) - min(b, val) == self.data[0][x]
        else:
            for i in self.choices(a):
                if max(i, val) - min(i, val) == self.data[0][x]:
                    return True
            return False

    def BT(self):
        start = int(round(time.time()*1000))
        result = backtracking_search(self)
        end = int(round(time.time()*1000))
        return (result,end-start)

    def BT_MRV(self):
        start = int(round(time.time()*1000))
        result = backtracking_search(self, select_unassigned_variable=mrv)
        end = int(round(time.time()*1000))
        return (result,end-start)

    def FC(self):
        start = int(round(time.time()*1000))
        result = (backtracking_search(self, inference=forward_checking))
        end = int(round(time.time()*1000))
        return (result,end-start)

    def FC_MRV(self):
        start = int(round(time.time()*1000))
        result = (backtracking_search(self, select_unassigned_variable=mrv, inference=forward_checking))
        end = int(round(time.time()*1000))
        return (result,end-start)

    def MAC(self):
        start = int(round(time.time()*1000))
        result = (backtracking_search(self, select_unassigned_variable=mrv, inference=mac))
        end = int(round(time.time()*1000))
        return (result,end-start)

class Model():

    def __init__(self,lines,size):
        self.variables = self.getVariables(size)
        self.values = self.getValues(size)
        self.domains = self.getDomains()
        self.neighbors = self.getNeighbors(size)

    def getValues(self,size):
        values = []
        for i in range(size):
            values.append(i+1)
        return values

    def getDomains(self):
        domains = dict()
        for i in self.variables:
            domains[i]=self.values
        return domains

    def getVariables(self,size):
        v = []
        for i in range(size):
            for j in range(size):
                v.append('x' + str(i) + str(j))
        return v

    def getNeighbors(self,size):
        dictionary = dict()
        for coords in self.variables:
            n = []
            for j in range(size):
                if j != int(coords[2]):
                    n.append('x' + coords[1] + str(j))
                if j != int(coords[1]):
                    n.append('x' + str(j) + coords[2])
            dictionary[coords] = n
        return dictionary

    def getData(self,size,lines):
        operations = []
        variables = []
        values = []
        for line in lines:
            value, op, vars = line.split()
            count=0
            v = []
            for i in vars:
                if i>='0' and i<='9':
                    if count == 0:
                        x1 = i
                    elif count == 1:
                        x2 = i
                    count +=1
                    if count == 2:
                        v.append('x'+x1+x2)
                        count = 0
            variables.append(v)
            values.append(int(value))
            operations.append(op)
        return [values,operations,variables]

    def display(self, dic, assigns, size):
        for i in range(size):
            for j in range(size):
                string = 'x' + str(i) + str(j)
                print(str(dic[0][string]),end = " ")
            print()
        print()
        print("Solved in", dic[1],"msec")
        print(assigns, "total assignments")
        print()

if __name__ == '__main__':

    print("\n\n------ SOLVING A 2 X 2 PUZZLE ------")
    with open("../input/k2.kk", 'r') as f:
        size = 2
        lines = f.readlines()
    f.close()
    m = Model(lines,size)
    kenken = KenKen(m.variables,m.domains,m.neighbors,m.getData(size,lines))

    print("\nUsing BT algorithm:")
    m.display(kenken.BT(), kenken.nassigns, size)
    print("\nUsing BT and MRV algorithms:")
    m.display(kenken.BT_MRV(), kenken.nassigns, size)
    print("\nUsing FC algorithm:")
    m.display(kenken.FC(), kenken.nassigns, size)
    print("\nUsing FC and MRV algorithms:")
    m.display(kenken.FC_MRV(), kenken.nassigns, size)
    print("\nUsing MAC algorithm:")
    m.display(kenken.MAC(), kenken.nassigns, size)

    print("\n\n------ SOLVING A 4 X 4 PUZZLE ------")
    with open("../input/k4.kk", 'r') as f:
        size = 4
        lines = f.readlines()
    f.close()
    m = Model(lines,size)
    kenken = KenKen(m.variables,m.domains,m.neighbors,m.getData(size,lines))

    print("\nUsing BT algorithm:")
    m.display(kenken.BT(), kenken.nassigns, size)
    print("\nUsing BT and MRV algorithms:")
    m.display(kenken.BT_MRV(), kenken.nassigns, size)
    print("\nUsing FC algorithm:")
    m.display(kenken.FC(), kenken.nassigns, size)
    print("\nUsing FC and MRV algorithms:")
    m.display(kenken.FC_MRV(), kenken.nassigns, size)
    print("\nUsing MAC algorithm:")
    m.display(kenken.MAC(), kenken.nassigns, size)

    print("\n\n------ SOLVING A 5 X 5 PUZZLE ------")
    with open("../input/k5.kk", 'r') as f:
        size = 5
        lines = f.readlines()
    f.close()
    m = Model(lines,size)
    kenken = KenKen(m.variables,m.domains,m.neighbors,m.getData(size,lines))

    print("\nUsing BT algorithm:")
    m.display(kenken.BT(), kenken.nassigns, size)
    print("\nUsing BT and MRV algorithms:")
    m.display(kenken.BT_MRV(), kenken.nassigns, size)
    print("\nUsing FC algorithm:")
    m.display(kenken.FC(), kenken.nassigns, size)
    print("\nUsing FC and MRV algorithms:")
    m.display(kenken.FC_MRV(), kenken.nassigns, size)
    print("\nUsing MAC algorithm:")
    m.display(kenken.MAC(), kenken.nassigns, size)

    print("\n\n------ SOLVING A 6 X 6 PUZZLE ------")
    with open("../input/k6.kk", 'r') as f:
        size = 6
        lines = f.readlines()
    f.close()
    m = Model(lines,size)
    kenken = KenKen(m.variables,m.domains,m.neighbors,m.getData(size,lines))

    print("\nUsing BT algorithm:")
    m.display(kenken.BT(), kenken.nassigns, size)
    print("\nUsing BT and MRV algorithms:")
    m.display(kenken.BT_MRV(), kenken.nassigns, size)
    print("\nUsing FC algorithm:")
    m.display(kenken.FC(), kenken.nassigns, size)
    print("\nUsing FC and MRV algorithms:")
    m.display(kenken.FC_MRV(), kenken.nassigns, size)
    print("\nUsing MAC algorithm:")
    m.display(kenken.MAC(), kenken.nassigns, size)

    print("\n\n------ SOLVING A 8 X 8 PUZZLE ------")
    with open("../input/k8.kk", 'r') as f:
        size = 8
        lines = f.readlines()
    f.close()
    m = Model(lines,size)
    kenken = KenKen(m.variables,m.domains,m.neighbors,m.getData(size,lines))

    print("\nUsing BT algorithm:")
    m.display(kenken.BT(), kenken.nassigns, size)
    print("\nUsing BT and MRV algorithms:")
    m.display(kenken.BT_MRV(), kenken.nassigns, size)
    print("\nUsing FC algorithm:")
    m.display(kenken.FC(), kenken.nassigns, size)
    print("\nUsing FC and MRV algorithms:")
    m.display(kenken.FC_MRV(), kenken.nassigns, size)
    print("\nUsing MAC algorithm:")
    m.display(kenken.MAC(), kenken.nassigns, size)
