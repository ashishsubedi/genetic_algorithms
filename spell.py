from genetics import Organism, Population, Genome

TARGET = "hello world"


def fitness_func(genome: Genome) -> int:
    fitness = 0
    for curr_g, curr_t in zip(genome, TARGET):
        if curr_g != curr_t:
            fitness += 1
        # fitness += (ord(curr_g) - ord(curr_t))**2

    return fitness


population = Population(
    size=100,
    genome_length=len(TARGET),
    fitness_func=fitness_func,
    high_fitness_best = False
)

population, total_gen, history = population.run_evolution(
    fitness_limit = 0,
    generation_limit = 100,
    select_top_k_percent_for_next_gen = 0.1,
    
    

)



print("number of generations: ", total_gen)
print("Best Solution: ", population[0])
print("Fitness Value:",population[0].fitness_value)