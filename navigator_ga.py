
import random
import numpy as np
from ga.individual import Individual
from ga.operators import crossover, mutation

class NavigatorGA:
    def __init__(self, population_size ,mutation_rate,robot,simulationsteps=20,stepsize=10):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.simulationsteps = simulationsteps
        self.population = self.generate_population()
        self.fitness_scores = np.zeros(population_size)
        self.best_individual = None
        self.robot = robot
        self.stepsize = stepsize

    def generate_population(self):
        """
        Generates a population of individuals with random chromosomes.
        """
        population = []
        for _ in range(self.population_size):
            chromosome=np.random.choice([-1,0,1],size=(2,self.simulationsteps)).tolist()
            population.append(Individual(chromosome))
        return population
    
    def evaluate_fitness(self, individual):
        """
        Evaluates the fitness of an individual.
        """
        robot_clone= self.robot.clone()
        collision = False
        for i in range(self.simulationsteps):
            for j in range(self.stepsize):
                if individual.get_chromosome()[0][i] != -1: robot_clone.set_vl(individual.get_chromosome()[0][i])
                if individual.get_chromosome()[1][i] != -1: robot_clone.set_vr(individual.get_chromosome()[1][i])
                robot_clone.move(robot_clone.vl, robot_clone.vr)
                collision=collision or robot_clone.get_collision()
                if collision: break
            if collision: break

        map_score = np.log(np.sum(np.abs(robot_clone.get_mapped_grid()))/10000)
        if collision:
            fitness = -100
        else:
            fitness = map_score*(robot_clone.vl + robot_clone.vr) / 2
        individual.set_fitness(fitness)
    
    def select_parents(self):
        fitness_values = [individual.get_fitness for individual in self.population]
        total_fitness = sum(fitness_values)
        probabilities = [fitness / total_fitness for fitness in fitness_values]
        selected_index = np.random.choice(len(self.population), p=probabilities)
        return self.population[selected_index]
    
    def crossover(self, parent1, parent2):
        """
        Performs crossover between two parents to create offspring.
        """
        parent1clone = parent1.clone()
        parent2clone = parent2.clone()
        offspring1, offspring2 = crossover(parent1clone.get_chromosome(), parent2clone.get_chromosome())
        offspring1=self.evaluate_fitness(offspring1)
        return Individual(offspring1), Individual(offspring2)
    
    def mutate(self, individual):
        """
        Mutates an individual with a certain mutation rate.
        """
        mutated_chromosome = mutation(individual.clone(), self.mutation_rate)
        individual.replace(mutated_chromosome)
if __name__ == "__main__":
    # Example usage
    print(np.random.choice([-1,0,1],size=(2,10)))
    