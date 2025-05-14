
import random
import numpy as np
from ga.individual import Individual
from ga.operators import crossover, mutation
from ga.HeapSort import sort

class NavigatorGA:
    def __init__(self, population_size ,mutation_rate,robot,generations=50,simulationsteps=20,stepsize=10):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.simulationsteps = simulationsteps
        self.population = self.generate_population()
        self.fitness_scores = np.zeros(population_size)
        self.best_individual = None
        self.robot = robot
        self.stepsize = stepsize
        self.generations = generations

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

        # map_score = np.log(np.sum(np.abs(robot_clone.get_mapped_grid()))/10000)
        map_score = np.sum(np.abs(robot_clone.get_mapped_grid()))
        if collision:
            fitness =1
        else:
            fitness = map_score*np.abs((robot_clone.vl + robot_clone.vr) / 2)
        individual.set_fitness(fitness)
        print(f"Fitness: {fitness}")
    
    def select_parents(self):
        fitness_values = [individual.get_fitness() for individual in self.population]
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
        self.evaluate_fitness(offspring1)
        self.evaluate_fitness(offspring2)
        return offspring1, offspring2
    
    def mutate(self, individual):
        """
        Mutates an individual with a certain mutation rate.
        """
        mutation(individual, self.mutation_rate)
        # individual.replace(mutated_chromosome)

    def get_navigation(self):
        """
        Main loop for the genetic algorithm.
        """
        for i in range(self.population_size):
                self.evaluate_fitness(self.population[i])
        sort(self.population)
        for generation in range(self.generations):
    
            
            parent1 = self.select_parents()
            parent2 = self.select_parents()
            offspring1, offspring2 = self.crossover(parent1, parent2)
            self.mutate(offspring1)
            self.mutate(offspring2)
            self.population[-1].replace(offspring1)
            self.population[-2].replace(offspring2)

            sort(self.population)

            self.best_individual = self.population[0]
            print(f"Generation {generation + 1}: Best Fitness = {self.best_individual.get_fitness()}")
        return self.best_individual.get_chromosome()

if __name__ == "__main__":
    # Example usage
    ga_agent = NavigatorGA(10, 0.01, None, generations=50, simulationsteps=20, stepsize=10)
    ga_agent.generate_population()
    print(ga_agent.population[0].get_chromosome())
    