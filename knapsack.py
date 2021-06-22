import genes
from collections import namedtuple
from functools import partial


Thing = namedtuple('Things', ['name', 'value', 'weight'])


weight_limit = 50
things = [
    Thing('Pen', 60, 10),
    Thing('Laptop', 130, 70),
    Thing('Pot', 50, 30),
    Thing('Earphone', 120, 20),
    Thing('Mouse', 70, 30),
    Thing('Keyboard', 70, 40),
    Thing('Drawing Pad', 80, 35),
    Thing('Laptop Stand', 50, 30),
]


population, generations, best_fitnesses = genes.run_evolution(
    populate_func=partial(genes.generate_population,
                        size=10, genome_length=len(things)),
    fitness_func=partial(genes.fitness, things=things,
                        weight_limit=weight_limit),
    fitness_limit=190,
    generation_limit=100

)

print("number of generations : max fitness value ")
print(best_fitnesses)
print("Best Solution: ", genes.genome_to_things(population[0],things))
print("Fitness Value:",best_fitnesses[generations])
