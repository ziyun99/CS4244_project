from pprint import pprint
import copy
import subprocess

YELLOW, BLUE, RED, GREEN, WHITE                 = 0, 1, 2, 3, 4

NORWEGIAN, DANE, BRIT, GERMAN, SWEDE            = 5, 6, 7, 8, 9

WATER, TEA, MILK, COFFEE, BEER                  = 10, 11, 12, 13, 14

DUNHILL, BLENDS, PALLMALL, PRINCE, BLUEMASTERS  = 15, 16, 17, 18, 19

CAT, HORSE, BIRD, FISH, DOG                     = 20, 21, 22, 23, 24

cnf = []

def get_comb_id(item, house):
    return (item * 5 + house)

def found_at(item, house):
    cnf.append([get_comb_id(item, house)])

def in_the_same_house(item1, item2):
    for house in range(1, 6):
        cnf.append([-get_comb_id(item1, house), get_comb_id(item2, house)])
        cnf.append([get_comb_id(item1, house), -get_comb_id(item2, house)])

def are_neighbours(item1, item2):
    cnf.append([-get_comb_id(item1, 1), get_comb_id(item2, 2)])
    cnf.append([-get_comb_id(item2, 1), get_comb_id(item1, 2)])
    cnf.append([-get_comb_id(item1, 5), get_comb_id(item2, 4)])
    cnf.append([-get_comb_id(item2, 5), get_comb_id(item1, 4)])
    for house in range(2, 5):
        cnf.append([-get_comb_id(item1, house), get_comb_id(item2, house-1), get_comb_id(item2, house+1)])
        cnf.append([-get_comb_id(item2, house), get_comb_id(item1, house-1), get_comb_id(item1, house+1)])
    
def on_left(item1, item2):
    for house in range(1, 5):
        cnf.append([-get_comb_id(item1, house), get_comb_id(item2, house+1)])
        cnf.append([get_comb_id(item1, house), -get_comb_id(item2, house+1)])

group_index = [0, 5, 10, 15, 20]

#For each house, there only exist 1 item of the same group. 
for house in range (1, 6):
    for group_id in group_index:
        for item in range(1, 5):
            for j in range(group_id, group_id+item):
                cnf.append([-get_comb_id(group_id+item, house), -get_comb_id(j, house)])

#For each unique item, it cannot exist in two houses.
for item in range(0, 25):
    for house in range(1, 6):
        for i in range(house+1, 6):
            cnf.append([-get_comb_id(item, house), -get_comb_id(item, i)])

#Each color, cigarette, drink, nationality, and pet must exist in at least one house.
for item in range(0, 25):
    cnf.append([get_comb_id(item, 1), get_comb_id(item, 2), get_comb_id(item, 3), get_comb_id(item, 4), get_comb_id(item, 5)])

#The Brit lives in the red house.
in_the_same_house(BRIT, RED)

#The Swede keeps dogs as pets.
in_the_same_house(SWEDE, DOG)

#The Dane drinks tea.
in_the_same_house(DANE, TEA)

#The green house is on the left of the white house.
#We are making the assumption that the green house is next to the white house, one to the left.
on_left(GREEN, WHITE)

#The green houses owner drinks coffee.
in_the_same_house(GREEN, COFFEE)

#The person who smokes Pall Mall rears birds.
in_the_same_house(PALLMALL, BIRD)

#The owner of the yellow house smokes Dunhill.
in_the_same_house(YELLOW, DUNHILL)

#The man living in the center house drinks milk.
found_at(MILK, 3)

#The Norwegian lives in the first house.
found_at(NORWEGIAN, 1)

#The man who smokes Blends lives next to the one who keeps cats. 
are_neighbours(BLENDS, CAT)

#The man who keeps the horse lives next to the man who smokes Dunhill.
are_neighbours(HORSE, DUNHILL)

#The owner who smokes Bluemasters drinks beer.
in_the_same_house(BLUEMASTERS, BEER)

#The German smokes Prince.
in_the_same_house(GERMAN, PRINCE)

#The Norwegian lives next to the blue house.
are_neighbours(NORWEGIAN, BLUE)

#The man who smokes Blends has a neighbor who drinks water.
are_neighbours(BLENDS, WATER)

# pprint(cnf)
print("total of:")
print(len(cnf))


def write_to_cnf(filename, cnf_input):
    N = 150
    L = len(cnf_input)
    # print(cnf_input)

    w = "c {}\n".format(filename)
    w += "p cnf {} {}\n".format(N, L)
    for clause in cnf_input:
        # print(clause)
        for literal in clause:
            w += str(literal) + " "
        w += "0\n"
    # print(w)
    file = open(filename, "w")
    file.write(w)
    file.close()


for house in range(1, 6):
    print("\n >> CheckSAT: Fish is found at House {}?".format(house))
    id = get_comb_id(FISH, house)
    filename = "einstein.cnf"

    cnf_input = copy.deepcopy(cnf)
    cnf_input.append([id])

    write_to_cnf(filename, cnf_input)

    bashCommand = "python3 mySATSolver.py einstein.cnf two_clause 0" 
    cmd = bashCommand.split()
    f = open("out.txt", "w")
    subprocess.call(cmd, stdout=f)

    SAT = False

    # read assignments from output
    file1 = open('out.txt', 'r')
    Lines = file1.read().splitlines()

    for i in range(len(Lines)-1, 0, -1):
        line = Lines[i].split(': ')

        if len(line) > 0 and line[0] == 'Assigmenent' and line[1] != "None":
                assignment = line[1].split(", ")

                for nationality in [NORWEGIAN, DANE, BRIT, GERMAN, SWEDE]:
                    id = get_comb_id(nationality, house)

                    if assignment[id-1] == str(id):
                        print("Nationality {} has the fish.".format(nationality)) 
                        SAT = True

    if SAT:
        print("Fish found.")
    else:
        print("UNSAT")
        
