from collections import namedtuple
from collections.abc import Callable
from functools import partial
from itertools import accumulate
from random import choice, choices, randint, random, randrange
from typing import Any, Dict, List, Optional, Tuple, Union



Genome = List[Union[str,int]]
FitnessFunc = Callable[[Genome], int]
GeneFunc = Callable[[], Any]


def default_gene_representation() -> Any:
    return '''abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOP
            QRSTUVWXYZ 1234567890, .-;:_!"#%&/()=?@${[]}'''


class Organism:

    def __init__(self, genome_length: int, fitness_func: FitnessFunc, genes_representation_func: GeneFunc):

        self._gene_representation_func = genes_representation_func
        self._fitness_func = fitness_func

        self.Genes = genes_representation_func()
        self.genome = self.generate_gnome(genome_length)

        self.fitness_value = self.calculate_fitness()

    def __len__(self):
        return len(self.genome)

    def __str__(self):
        return ''.join(str(self.genome))
    def __repr__(self):
        return ''.join(str(self.genome))

    def generate_gnome(self, length: int) -> Genome:
        return choices(
            self.Genes,
            k=length
        )

    def change_organism_genome(self, genome: Genome) -> 'Organism':

        self.genome = genome
        self.fitness_value = self.calculate_fitness()
        return self

    def calculate_fitness(self) -> int:
        self.fitness_value = self._fitness_func(self.genome)
        return self.fitness_value

    # def crossover(self, b: 'Organism') -> Tuple['Organism', 'Organism']:

    #     if len(self.genome) != len(b):
    #         raise ValueError("Genomes a and b must be of same length.")
    #     child_1_genome = []
    #     child_2_genome = []
    #     for gp1, gp2 in zip(self.genome, b.genome):
    #         # random probability
    #         prob = random()

    #         if prob < 0.5:
    #             child_1_genome.append(gp1)
    #             child_2_genome.append(gp2)

    #         else:
    #             child_1_genome.append(gp2)
    #             child_2_genome.append(gp1)

    #     # self.genome = child_1_genome
    #     # b.genome = child_2_genome

    #     # self.calculate_fitness()
    #     # b.calculate_fitness()
    #     new_a = Organism(len(b),self._fitness_func,self._gene_representation_func).change_organism_genome(child_1_genome)
    #     new_b = Organism(len(b),self._fitness_func,self._gene_representation_func).change_organism_genome(child_2_genome)

    #     return new_a,new_b

    def crossover(self, b: 'Organism') -> Tuple['Organism', 'Organism']:
        # Single point crossover

        if len(self.genome) != len(b):
            raise ValueError("Genomes a and b must be of same length.")

        length = len(b)
        if length < 2:
            return (self, b)

        p = randint(1, length-1)

        new_a = Organism(length, self._fitness_func, self._gene_representation_func).change_organism_genome(
            self.genome[:p] + b.genome[p:])
        new_b = Organism(length, self._fitness_func, self._gene_representation_func).change_organism_genome(
            b.genome[:p]+self.genome[p:])

        return new_a, new_b

    def mutation(self, num: int = 2, probability: float = 0.3) -> None:
        for _ in range(num):
            index = randrange(len(self.genome))
            self.genome[index] = self.genome[index] if random(
            ) > probability else choice(self.Genes)


class Population:

    PopulateFunc = Callable[[int, int], List[Organism]]
    SelectionFunc = Callable[[], List[Organism]]
    CrossoverFunc = Callable[[Organism, Organism], Tuple[Organism, Organism]]
    MutationFunc = Callable[[int, float], None]

    def __init__(self, size: int, genome_length: int, fitness_func: FitnessFunc, high_fitness_best: bool = True,gene_representation_func: GeneFunc = default_gene_representation):
        self.fitness_func = fitness_func
        self.high_fitness_best = high_fitness_best
        self._gene_representation_func = gene_representation_func

        self.size = size
        self.probability_dist = []

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

        return [Organism(genome_length, self.fitness_func,self._gene_representation_func) for _ in range(size)]

    def selection_pair(self) -> List[Organism]:
        ''' 
        Selects a pair of genome with higher probability of selecting high fitness genome.
        '''

        pop = self.population
        return choices(
            population=pop,
            cum_weights=self.probability_dist,
            k=2
        )

        # return choices(pop, k=2)

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

        for _ in range(self.size//3):
            self.probability_dist.append(randint(30, 50))

        for _ in range((self.size - self.size//3)+3):
            self.probability_dist.append(randint(5, 15))

        self.probability_dist = self.probability_dist[:self.size]
        self.probability_dist = list(accumulate(self.probability_dist))

        for i in range(generation_limit):
            self.get_best_organisms()

            print(
                f'Best Fitness in generation {i} -> {self.population[0].fitness_value}, {self.population[0]}'
            )
            self.log_best_fitness[i] = (
                self.population[0].fitness_value, self.population[0])
            if self.high_fitness_best:
                if self.population[0].fitness_value >= fitness_limit:
                    break
            else:
                if self.population[0].fitness_value <= fitness_limit:
                    break

            next_generation = self.population[:int(
                select_top_k_percent_for_next_gen*self.size)]

            for j in range(self.size//2):
                parents = self.selection_pair()
                a, b = parents[0].crossover(parents[1])
                a.mutation()
                b.mutation()
                next_generation += [a, b]

            self.population = next_generation[:self.size]

        self.population = self.get_best_organisms()

        return self.population, i, self.log_best_fitness
