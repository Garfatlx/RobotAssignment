import random
import numpy as np
from HeapSort import sort
from individual import Individual


TARGET = "HELLO WORLD"
ALPHABET = [chr(i) for i in range(65, 91)] + [' ']
POP_SIZE = 10
FITNESS_FACTOR = 100 # Equals the max fitness achivebal (individual == target) has this as Fitness
MUTATION_RATE = 0.01

#use Minimum Edit Distance as fitness
def fitness_MED(target,individual):
    lenTarget=len(target)
    lenIndividual=len(individual)
    delCost=1
    insCost=1
    d=np.zeros((lenIndividual+1,lenTarget+1))
    for i in range(1,lenTarget+1):
        d[i,0]=d[i-1,0]+delCost
    for i in range(1,lenIndividual+1):
        d[0,i]=d[0,i-1]+insCost
    for i in range(1,lenTarget+1):
        for j in range(1,lenIndividual+1):
            if target[i-1]==individual[j-1]:
                subCost=0
            else:
                subCost=2
            d[i,j]=np.min([d[i-1,j]+delCost,d[i,j-1]+insCost,d[i-1,j-1]+subCost])

    return d[lenTarget,lenIndividual]

def fitness_test(target, individual):
    # Initialize fitness score
    fitness = 0
    
    # 1. Matched characters
    for i in range(len(target)):
        if target[i] == individual[i]:
            fitness += 10
    
    # 2. Occurrence of same letters
    target_letter_count = {letter: target.count(letter) for letter in set(target)}
    individual_letter_count = {letter: individual.count(letter) for letter in set(individual)}
    for letter, count in target_letter_count.items():
        if letter in individual_letter_count:
            fitness += min(count, individual_letter_count[letter]) * 5
    
    # 3. Similarity of patterns (e.g., consecutive characters)
    for i in range(len(target) - 1):
        if target[i:i+2] == individual[i:i+2]:
            fitness += 20
    
    return fitness * FITNESS_FACTOR / (50 + 35 * (len(TARGET) - 2))

def selection(population):
    fitness_values = [individual.fitness for individual in population]
    total_fitness = sum(fitness_values)
    probabilities = [fitness / total_fitness for fitness in fitness_values]
    selected_index = np.random.choice(len(population), p=probabilities)
    return population[selected_index]

def crossover(pair1,pair2,population, mutation_rate):
    pair1text = pair1.geno_to_phenotype()
    pair2text = pair2.geno_to_phenotype()
    

    crosspoint = random.randint(1, len(pair1text) - 1)  # Select crossoverpoint random

    offspring1_text = pair1text[:crosspoint] + pair2text[crosspoint:]   # perform crossover
    offspring2_text = pair2text[:crosspoint] + pair1text[crosspoint:]

    population[-1].set_chromosome(list(offspring1_text))    #update offspring 
    population[-2].set_chromosome(list(offspring2_text))

    population[-1].set_fitness(fitness_test(TARGET, offspring1_text))   # calculate fitness
    population[-2].set_fitness(fitness_test(TARGET, offspring2_text))

    mutation(population[-1], mutation_rate)     # Mutate offspring
    mutation(population[-2], mutation_rate)

def mutation(individual, rate):
    chromosome = individual.get_chromosome()  #list of chars of the individual

    changed = False
    for i,_ in enumerate(chromosome):
        if random.choices([True,False],weights=[rate, 1-rate])[0]:
            chromosome[i]=random.choices(ALPHABET)[0]
            changed=True
    if changed:
        individual.set_chromosome(chromosome)
        individual.set_fitness(fitness_test(TARGET,"".join(chromosome)))

def swap(individual, rate):
    """
    swaps two chars of an individual with probability of rate
    """
    chromosome = individual.get_chromosome()  #list of chars of the individual

    if random.random() < rate:
         a = random.randint(0, len(chromosome) - 1)
         b = random.randint(0, len(chromosome) - 1)

         temp = chromosome[a]
         chromosome[a] = chromosome[b]
         chromosome[b] = temp
         

def generate_population(size, target_length):
    """
    gernerates population, 
    args:   size,       population size; number of individuals in population (int)
            target_length,    length of the individuals (int)
    """
    population = []
    
    for i in range(size):
        temp_chromosome = [random.choice(ALPHABET) for _ in range(target_length)]
        population.append(Individual(temp_chromosome))
        population[i].set_fitness(fitness_test(TARGET,"".join(temp_chromosome)))
    sort(population)    # Sorts population --> The first one is the best

    return population
 

def main(pop_size, target, max_generations, mutation_rate):
    global TARGET
    TARGET=target
    population = generate_population(pop_size, len(target))
    for generation in range(max_generations):
        if population[0].geno_to_phenotype() == target:
            # print(f"Solution found in generation {generation + 1}. population size {mutation_rate}")
            return generation + 1
        
        parent1 = selection(population)
        parent2 = selection(population)
        crossover(parent1, parent2, population, mutation_rate)
        sort(population)  # Sorts population after crossover
        # print(population[0].geno_to_phenotype())
    return -1  # Solution not found within max generations
    
    # n=0
    # while population[0].geno_to_phenotype() != target:  # We can use the first one ([0]) because it is sorted
    #     pair1=selection(population)
    #     pair2=selection(population)
    #     crossover(pair1,pair2,population)
    #     sort(population)
    #     n=n+1
    #     #print('Fittest object of population: ', population[0].geno_to_phenotype(),'Best object fitness: ', population[0].get_fitness(),'n: ', n)
    #     if n % 1000 == 0:
    #         print('Fittest object of population: ', population[0].geno_to_phenotype(),'Best object fitness: ', population[0].get_fitness(),'n: ', n, 'pop size: ', pop_size)
    # return n

def test():
    """
    For testing our methods in big scale with changing population sizes etc.
    """
    n_s = []    # list of list of n Values
    p_size = 4 # Starting population size (If p_size << target length or at all <~4 n gets really big because we only have 2 individuals --> mutations likely kills 'trained' characteristics)
    #main(pop_size = POP_SIZE, target = TARGET)
    for i in range(10):
        n_ = []
        count = 0
        while count <= 10:  # Reruns the mehtod with the same parameters several times to get an average Value of n
            n_.append(main(p_size, TARGET, MUTATION_RATE))
            count += 1
        n_s.append(n_)
        p_size = p_size * 2
    print(n_s)


if __name__ == "__main__":
    # pop = generate_population(1, len(TARGET))
    # swap(pop[0], 1)
    main(pop_size = POP_SIZE, target = TARGET, max_generations = 10000, mutation_rate = MUTATION_RATE)