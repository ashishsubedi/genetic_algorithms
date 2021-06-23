from collections import namedtuple
from random import choices, randint, random, randrange
from typing import Callable, List, Tuple, Dict
from functools import partial

Genome = List[int]  # for eg: [0,1,1,0,1,1,0]
Population = List[Genome]
Thing = namedtuple('Things', ['name', 'value', 'weight'])

FitnessFunc = Callable[[Genome], int]
PopulateFunc = Callable[[],Population]
SelectionFunc = Callable[[Population,FitnessFunc], Tuple[Genome,Genome]]
CrossoverFunc = Callable[[Genome,Genome], Tuple[Genome,Genome]]
MutationFunc = Callable[[Genome], Genome]

def generate_genome(length: int) -> Genome:
    return choices([0, 1], k=length)


def generate_population(size: int, genome_length: int) -> Population:
    return [generate_genome(genome_length) for _ in range(size)]


def fitness(genome: Genome, things: [Thing], weight_limit: int) -> int:
    if len(genome) != len(things):
        raise ValueError("Genome and Things must be of same size")

    w, v = 0, 0

    for i, thing in enumerate(things):
        if genome[i] == 1:
            w += thing.weight
            v += thing.value

            if w > weight_limit:
                return 0

    return v


def selection_pair(population: Population, fitness_func: FitnessFunc) -> Population:
    ''' 
    Selects a pair of genome with higher probability of selecting high fitness genome.
    '''
    return choices(
        population=population,
        weights=[fitness_func(genome) for genome in population],
        k=2
    )


def single_point_crossover(a: Genome, b: Genome) -> Tuple[Genome, Genome]:
    if len(a) != len(b):
        raise ValueError("Genomes a and b must be of same length.")

    length = len(a)
    if length < 2:
        return (a, b)

    p = randint(1, length-1)
    return a[:p] + b[p:], b[:p]+a[p:]


def mutation(genome: Genome, num: int = 1, probability: float = 0.5) -> Genome:
    for _ in range(num):
        index = randrange(len(genome))
        genome[index] = genome[index] if random(
        ) > probability else abs(genome[index]-1)

    return genome

def run_evolution(
    populate_func: PopulateFunc,
    fitness_func: FitnessFunc,
    fitness_limit: int,
    selection_func: SelectionFunc = selection_pair,
    crossover_func: CrossoverFunc = single_point_crossover,
    mutation_func: MutationFunc = mutation,
    generation_limit: int = 100
) -> Tuple[Population,int,Dict]:

    #Fitness_limit: Known max/optimal fitness value for the problem.
    # If unknows, use arbitary high number 
    # which is acceptable as high fitness value


    
    # Make sure initial population has fitness > 0
    while True:
        population = populate_func()
        init_fitness = 0
        for genome in population:
            init_fitness += fitness_func(genome)
        if init_fitness > 0:
            break
    
    log_best_fitness :Dict[int,int] = {}


    for i in range(generation_limit):
        population.sort(reverse=True,key=lambda genome:fitness_func(genome))

        # print(f'Best Fitness in generation {i} -> {fitness_func(population[0])}')
        log_best_fitness[i] = fitness_func(population[0])

        if fitness_func(population[0]) >= fitness_limit:
            break

        next_generation = population[:2]

        for j in range(len(population)//2 -1):
            parents = selection_func(population, fitness_func)
            a,b = crossover_func(parents[0],parents[1])
            a = mutation_func(a)
            b = mutation_func(b)
            next_generation += [a,b]

        population = next_generation
    
    population.sort(reverse=True,key=lambda genome:fitness_func(genome))

    return population, i, log_best_fitness


def genome_to_things(genome:Genome, things: [Thing])-> [Thing]:
    result = []

    for i, thing in enumerate(things):
        if genome[i] == 1:
            result += [thing.name]

    return result



if __name__ == '__main__':
    weight_limit=50
    things = [
        Thing('Pen',60,10),
        Thing('Laptop',130,70),
        Thing('Pot',50,30),
        Thing('Earphone',120,20),
        Thing('Mouse',70,30),
        Thing('Keyboard',70,40),
        Thing('Drawing Pad',80,35),
        Thing('Laptop Stand',50,30),
    ]


    population, generations, best_fitnesses = run_evolution(
        populate_func= partial(
            generate_population,size=10,genome_length = len(things)
        ),
        fitness_func= partial(
            fitness, things=things, weight_limit=weight_limit
        ),
        fitness_limit = 190,
        generation_limit = 100
    )

    print("number of generations: ", generations)
    print("Best Solution: ", genome_to_things(population[0],things))
    print("Fitness Value:",fitness(population[0],things=things, weight_limit=weight_limit))