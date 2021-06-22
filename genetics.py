from collections import namedtuple
from collections.abc import Callable
from functools import partial
from random import choice, choices, randint, random, randrange
from typing import Dict, List, Optional, Tuple

import genes
from genes import FitnessFunc, mutation, run_evolution

Genes = '''abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'''

Genome = List[str]
FitnessFunc = Callable[[Genome], int]


class Organism:

    def __init__(self, genome_length: int, fitness_func: FitnessFunc):
        self.genome = self.generate_gnome(genome_length)
        self._fitness_func = fitness_func
        self.fitness_value = self.calculate_fitness()

    def __len__(self):
        return len(self.genome)

    def __str__(self):
        return ''.join(self.genome)

    def generate_gnome(self, length: int) -> Genome:
        return choices(
            Genes,
            k=length
        )

    def change_organism_genome(self, genome: Genome) -> 'Organism':

        self.genome = genome
        self.fitness_value = self.calculate_fitness()
        return self

    def calculate_fitness(self) -> int:
        self.fitness_value = self._fitness_func(self.genome)
        return self.fitness_value

    def crossover(self, b: 'Organism') -> Tuple['Organism', 'Organism']:

        if len(self.genome) != len(b):
            raise ValueError("Genomes a and b must be of same length.")
        child_1_genome = []
        child_2_genome = []
        for gp1, gp2 in zip(self.genome, b.genome): 
            # random probability
            prob = random()

            if prob < 0.5:
                child_1_genome.append(gp1)
                child_2_genome.append(gp2)

            else:
                child_1_genome.append(gp2)
                child_2_genome.append(gp1)
        
        
        self.genome = child_1_genome
        b.genome = child_2_genome

        return self,b

        

    # def crossover(self, b: 'Organism') -> Tuple['Organism', 'Organism']:
    #     if len(self.genome) != len(b):
    #         raise ValueError("Genomes a and b must be of same length.")

    #     length = len(b)
    #     if length < 2:
    #         return (self, b)

    #     p = randint(1, length-1)

    #     temp_a_genome = self.genome
    #     self.genome = self.genome[:p] + b.genome[p:]
    #     b.genome = b.genome[:p]+temp_a_genome[p:]

    #     return self, b

    def mutation(self, num: int = 1, probability: float = 0.3) -> None:
        for _ in range(num):
            index = randrange(len(self.genome))
            self.genome[index] = self.genome[index] if random(
            ) > probability else choice(Genes)


class Population:

    PopulateFunc = Callable[[int, int], List[Organism]]
    SelectionFunc = Callable[[], List[Organism]]
    CrossoverFunc = Callable[[Organism, Organism], Tuple[Organism, Organism]]
    MutationFunc = Callable[[int, float], None]

    def __init__(self, size: int, genome_length: int, fitness_func: FitnessFunc, high_fitness_best: bool = True):
        self.fitness_func = fitness_func
        self.high_fitness_best = high_fitness_best
        self.size = size

        while True:
            self.population = self.generate_population(
                size, genome_length=genome_length)
            init_fitness = 0
            for organism in self.population:
                init_fitness += organism.calculate_fitness()
            if init_fitness != 0:
                break

        self.log_best_fitness: Dict[int, int] = {}

    def generate_population(self, size: int, genome_length: int) -> List[Organism]:

        return [Organism(genome_length, self.fitness_func) for _ in range(size)]

    def selection_pair(self) -> List[Organism]:
        ''' 
        Selects a pair of genome with higher probability of selecting high fitness genome.
        '''

        pop = self.population
        # return choices(
        #     population=pop,
        #     weights=[organism.fitness_value
        #             for organism in pop],
        #     k=2
        # )

        return choices(pop, k=2)

    def get_best_organisms(self) -> List[Organism]:

        self.population.sort(
            reverse=self.high_fitness_best, key=lambda organism: organism.calculate_fitness())
        return self.population

    def run_evolution(
        self,
        fitness_limit: int,
        generation_limit: int = 100,
        select_top_k_percent_for_next_gen: int = 0.1
    ) -> Tuple[List[Organism], int, Dict]:

        # Fitness_limit: Known max/optimal fitness value for the problem.
        # If unknows, use arbitary high number
        # which is acceptable as high fitness value
        # In case the fitness function is best if lower value,
        #  negate the Fitness_limit value

        for i in range(generation_limit):
            self.population = self.get_best_organisms()

            print(
                f'Best Fitness in generation {i} -> {self.population[0].fitness_value}')
            self.log_best_fitness[i] = self.population[0].fitness_value
            if self.high_fitness_best:
                if self.population[0].fitness_value >= fitness_limit:
                    break
            else:
                if self.population[0].fitness_value <= fitness_limit:
                    break

            next_generation = self.population[:int(select_top_k_percent_for_next_gen*self.size)]

            for j in range(self.size//2):
                parents = self.selection_pair()
                a, b = parents[0].crossover(parents[1])
                a.mutation()
                b.mutation()
                next_generation += [a, b]

            self.population = next_generation[:self.size]

        self.population = self.get_best_organisms()

        return self.population, i, self.log_best_fitness
