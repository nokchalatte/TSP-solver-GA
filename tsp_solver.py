# TSP Solver using Genetic Algorithm
# Takes in a EUC_2D TSP file from http://elib.zib.de/pub/mp-testdata/tsp/tsplib/tsp/index.html,
# gives out solution.csv and prints the total distance traveled.
# Some notes: I'm a complete beginner in this so I'm citing a lot of references :(
# Inspiration: https://medium.com/datacat/simple-genetic-algorithm-in-python-from-scratch-d87cd88626c5    

import sys
import argparse
import random
import math

shortest_distance = 0
best_route = []

# Reads the input file
def read(file):
    rawlines = file.readlines()[6:-1]
    file.close()

    coordinates = []

    # Store coordinates to array
    for line in rawlines:
        stripped = line.split()
        coordinates.append((int(stripped[0]), float(stripped[1]), float(stripped[2])))
    
    return coordinates

# Simple function to calculate distance between two coordinates
def distance(ax, ay, bx, by):
    dist = ((ax - bx)**2 + (ay - by)**2)**0.5
    return dist

# Calculate total distance
def total_distance(lst):
    length = len(lst)
    disttot = 0
    if length == 1:
        return 0
    else:
        for i in range(length-1):
            disttot += distance(lst[i][1], lst[i][2], lst[i+1][1], lst[i+1][2])
        disttot += distance(lst[0][1], lst[0][2], lst[length-1][1], lst[length-1][2])
    return disttot

# Initialize GA population, make a list of lists of coordinates
def initialize_pop(lst, numpop):
    poplist = []
    for i in range (numpop):
        copy = lst[:]
        random.shuffle(lst)
        poplist.append(copy)
    return poplist

# Evaluate the fitness of each population member and store it as a dictionary
def eval_fitness(poplist):
    fitdict = {}
    global best_route
    global shortest_distance
    dist = total_distance(poplist[0])
    fitdict[0] = 1/dist
    local_best = dist
    local_route = poplist[0]
    for i in range(1, len(poplist)):
        dist = total_distance(poplist[i])
        fitdict[i] = 1/dist
        if dist < local_best:
            local_best = dist
            local_route = poplist[i]

    # Update global best records        
    if shortest_distance == 0:
        shortest_distance = local_best
        best_route = local_route
    elif shortest_distance > local_best:
        shortest_distance = local_best
        best_route = local_route
    
    return fitdict

# Pick a parent for next generation, based on roulette wheel selection. Thank you https://stackoverflow.com/questions/10324015/fitness-proportionate-selection-roulette-wheel-selection-in-python
def pick_parent(popdict):
    totalfit = sum(popdict.values())
    selected = random.uniform(0, totalfit)
    current = 0
    for key, value in popdict.items():
        current += value
        if current > selected:
            return key

# Crossover
def crossover(a, b):
    start = random.randint(0, len(a)-2)
    end = random.randint(start+1, len(a)-1)
    child = [0] * len(a)
    slicea = a[start:(end+1)] 
    child[start:(end+1)] = slicea
    indexb = 0
    for i in range(len(a)):
        if child[i] == 0 :
            for j in range(indexb, len(b)):
                if not (b[j] in slicea):
                    child[i] = b[j]
                    indexb = j+1
                    break
    return child

# Mutation (Swap)
def mutate(a):
    probability = 0.25 #25% chance of mutation
    acopy = a[:]
    if random.random() < probability:
        i = random.randint(0, len(acopy)-1)
        j = random.randint(0, len(acopy)-1)
        temp = acopy[i]
        acopy[i] = acopy[j]
        acopy[j] = temp
    return acopy

if __name__ == "__main__":
    # Add flags for population size and number of fitness evaluation, thank you for teaching me this https://stackoverflow.com/questions/11604653/add-command-line-arguments-with-flags-in-python3/11604777
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("-p", "--population", help="Number of population")
    parser.add_argument("-f", "--fitness", help="Total number of fitness evaluation")
    args = parser.parse_args()

    inputfile = open(args.file, 'r')
    coordinates = read(inputfile)

    numpop = int(args.population)
    numfit = int(args.fitness)

    # First generation
    gen0 = initialize_pop(coordinates, numpop)

    # First fitness evaluation
    fitdict = eval_fitness(gen0)
    parentlist = gen0
    parentdict = fitdict

    # Repeat process until the number of generations (fitness evaluations) specified is reached
    for i in range(numfit):
        newgen = []
        for i in range(numpop):
            parent1 = parentlist[pick_parent(parentdict)]
            parent2 = parentlist[pick_parent(parentdict)]
            child = crossover(parent1, parent2)
            child = mutate(child)
            newgen.append(child)
        newfitdict = eval_fitness(newgen)
        parentlist = newgen
        parentdict = newfitdict
    
    # Final shortest distance
    sys.stdout.write(str(shortest_distance))

    # Writes the output file
    f = open('solution.csv', 'w')
    for index in best_route:
        f.write(str(index[0]) + "\n")
    f.close()