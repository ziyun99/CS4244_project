import random
import math
import numpy as np
import sys

# generate a random cnf formula
def gen_random_cnf(N, K, L):
  clauses = []
  while L > 0:
    sequence = [i for i in range(1,N+1)]
    literals = random.sample(sequence, K)
    signs = [random.choice([1,-1]) for i in range(K)]
    clause = frozenset([literals[i] * signs[i] for i in range(K)])
    # print(literals, signs, clause)
    
    # if clause not in clauses:
    L -= 1
    clauses.append(clause)
  # print(len(clauses))
  return clauses

# write the cnf formula to a file
def write_cnf_file(filename, N, L, clauses):
  w = "c {}\n".format(filename)
  w += "p cnf {} {}\n".format(N, L)
  for clause in clauses:
    for literal in clause:
      w += str(literal) + " "
    w += "0\n"
  # print(w)
  file = open(filename, "w")  # append mode
  file.write(w)
  file.close()


def gen_all_inputs(dirname):
  # Total 7350 cnf files = 3 * 49 * 50
  
  N = 150               # N: number of variable  # fix value
  
  for K in range(3,6):                        # K: number of literal per clause # [3, 4, 5] 
    for R in np.arange(0.2, 10.0, 0.2):       # R: (0, 10, 0.2)
      R = round(R, 1)
      L = math.ceil(N*R)                      # L: number of clauses
      for i in range(50):                     # generate 50 formulas   
        filename = dirname + "/randN{}_K{}_R{}_L{}_{}.cnf".format(N, K, R, L, i)
        print(filename)

        clauses = gen_random_cnf(N, K, L)
        write_cnf_file(filename, N, L, clauses)

        # print(clauses)

if __name__ == "__main__":
  gen_all_inputs(sys.argv[1])