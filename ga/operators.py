import random as rnd
import numpy as np

def crossover(parent1,parent2):
    n=len(parent1)
    corsspoint1=rnd.randint(1,n-1)
    temp=parent1[0][corsspoint1:]
    parent1[0]=''.join([parent1[0][:corsspoint1],parent2[0][corsspoint1:]])
    parent2[0]=''.join([parent2[0][:corsspoint1],temp])

    corsspoint2=rnd.randint(1,n-1)
    temp=parent1[1][corsspoint2:]
    parent1[1]=''.join([parent1[1][:corsspoint2],parent2[1][corsspoint2:]])
    parent2[1]=''.join([parent2[1][:corsspoint2],temp])

    return [parent1,parent2]


def mutation(indi,rate):
    for i in range(2):
        mutate= np.random.choice([True,False], p=[rate,1-rate])
        if mutate:
            mutation_point = np.random.randint(0, len(indi[i]))
            indi[i][mutation_point] = 1 - indi[i][mutation_point]
    return indi
        
def test(aa):
    aali=list(aa)
    aali[2]="l"
    print ("".join(aali))
