from genetics import Organism, Population, Genome
from collections import namedtuple
from functools import partial


Thing = namedtuple('Things', ['name', 'value', 'weight'])



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

weight_limit = 50


def my_genes():
    return [0,1]


def fitness_func(genome: Genome,things: [Thing], weight_limit: int) -> int:
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


def genome_to_things(organism:Organism, things: [Thing])-> [Thing]:
    result = []

    for i, thing in enumerate(things):
        if organism.genome[i] == 1:
            result += [thing.name]

    return result


population = Population(
    size=100,
    genome_length=len(things),
    fitness_func=partial(fitness_func,things=things,weight_limit=weight_limit),
    high_fitness_best = True,
    gene_representation_func=my_genes
)

population, total_gen, history = population.run_evolution(
    # fitness_limit = 0,
    fitness_limit = 190,
    generation_limit = 300,
    select_top_k_percent_for_next_gen = 0.1,
    
    

)



print("number of generations : max fitness value ")
# print(history)
print("Best Solution: ", genome_to_things(population[0],things))
print("Fitness Value:",history[total_gen])