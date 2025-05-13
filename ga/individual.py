class Individual:
    def __init__(self, chromosome):
        self.chromosome = chromosome
        self.fitness = 0

    def get_chromosome(self):
        return self.chromosome

    def set_chromosome(self, chromosome):
        self.chromosome = chromosome

    def get_fitness(self):
        return self.fitness

    def set_fitness(self, fitness):
        self.fitness = fitness

    def geno_to_phenotype(self):
        
        return self.chromosome

    def clone(self):
        return Individual([row[:] for row in self.chromosome])
    
    def replace(self, other):
        self.chromosome = other.chromosome
        self.fitness = other.fitness
