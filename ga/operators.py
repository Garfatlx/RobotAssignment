import random as rnd
import numpy as np
from ga.individual import Individual as ind

def crossover(parent1,parent2):
    n = len(parent1[0])  # length of each gene (should be 20)
    child1 = [None, None]
    child2 = [None, None]

    # Crossover for first gene
    crosspoint1 = rnd.randint(1, n-1)
    child1[0] = parent1[0][:crosspoint1] + parent2[0][crosspoint1:]
    child2[0] = parent2[0][:crosspoint1] + parent1[0][crosspoint1:]

    # Crossover for second gene
    crosspoint2 = rnd.randint(1, n-1)
    child1[1] = parent1[1][:crosspoint2] + parent2[1][crosspoint2:]
    child2[1] = parent2[1][:crosspoint2] + parent1[1][crosspoint2:]

    return ind(child1), ind(child2)


def mutation(indi,rate):
    indi_genes=indi.get_chromosome()
    for i in range(2):
        mutate= np.random.choice([True,False], p=[rate,1-rate])
        if mutate:
            mutation_point = np.random.randint(0, len(indi_genes[i]))
            indi_genes[i][mutation_point] = 1 - indi_genes[i][mutation_point]
    indi.set_chromosome(indi_genes)
        
def test(aa):
    aali=list(aa)
    aali[2]="l"
    print ("".join(aali))
