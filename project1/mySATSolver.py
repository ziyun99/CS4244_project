import os
import sys
import time
import random
from collections import Counter

UNSAT = "UNSAT"
SAT = "SAT"
UNIT_CLAUSE = "UNIT_CLAUSE"
TWO_CLAUSE = "TWO_CLAUSE"
UNRESOLVED = "UNRESOLVED"
CONFLICT = "CONFLICT"
TIMEOUT = "TIMEOUT"

def get_literal_value(literal):
    '''
    Args:
        literal (int):       
    Returns:
        int: Return the value of the literal. Return -1 if unassigned.
    '''
    var = abs(literal)
    if assignments[var] == -1:
        return -1   #unassigned
    if literal > 0:  
        return assignments[var]
    else:
        return 1 - assignments[var]

def get_clause_state(clause):
    '''
    Args:
        clause ({int}):       
    Returns:
        string: Return whether the clause is SAT, UNSAT, UNIT_CLAUSE 
                or (UNRESOLVED, number of unassigned literals)
    '''
    values = [get_literal_value(literal) for literal in clause]
    if max(values) == 1:
        return SAT  #SAT
    unassigned = values.count(-1)
    if unassigned == 1:
        return UNIT_CLAUSE
    elif unassigned > 1:
        if unassigned == 2:
            return TWO_CLAUSE
        else:
            return (UNRESOLVED, unassigned) #number of unassigned literals
    else:
        return UNSAT  #UNSAT

def get_formula_state(formula):
    '''
    Args:
        formula ([{int}]):       
    Returns:
        string: Return whether the formula is SAT, UNSAT or UNRESOLVED.
    '''
    for clause in formula:
        value = get_clause_state(clause)
        if value == UNSAT:
            return UNSAT
        elif value != SAT:
            return UNRESOLVED
    return SAT

def check_formula_state(formula):
    print("\nChecking formula on current assignments:", assignments)
    for clause in formula:
        check_clause_state(clause)
    print("Formula state:", get_formula_state(formula))

def check_clause_state(clause):
    values = [get_literal_value(literal) for literal in clause]
    print(clause, values, get_clause_state(clause))

def get_unit_literal(unit_clause):
    '''
    Args:
        unit_clause ({int}):       
    Returns:
        int: Return the only unassigned literal in the unit_clause.
    '''
    for literal in unit_clause:
        if get_literal_value(literal) == -1:
            return literal

def get_literal_sign(unit_literal):
    '''
    Args:
        unit_literal (int):       
    Returns:
        int: Return 1 if the literal is positive, 0 if negative.
    '''
    if unit_literal > 0:
        return 1
    return 0

def assign_implied_var(unit_clause, unit_literal):
    '''
    Assign value to decision variable, update it's decision level.
    Args:
        decision_var (int):
    '''
    global assignments, antecedents, decision_levels
    var = abs(unit_literal)
    assignments[var] = get_literal_sign(unit_literal)
    antecedents[var] = unit_clause
    decision_levels[var] = curr_level
    if debug: print(" > prop assign x{} of value_{} at lvl_{}, in clause {}".format(unit_literal,get_literal_sign(unit_literal), curr_level, unit_clause))

def unit_propagation():
    '''
    Iterated application of unit clause rule.
    Returns:
        string: Return CONFLICT if UNSAT clause is found. Return None if no conflict.
    '''
    global antecedents, decision_levels, implication_count
    i = 0
    while True:
        i += 1
        propList = []
        if debug: print("> #{} unit_prop on clauses :".format(i)) #, clauses.union(learned_clauses))
        for clause in clauses.union(learned_clauses):
            state = get_clause_state(clause)
            if state == UNSAT:
                antecedents[0] = clause
                decision_levels[0] = curr_level
                # update_graph(clause, 0)
                if debug: print("CONFLICT clause", clause)
                return CONFLICT
            elif state == UNIT_CLAUSE: 
                propList.append(clause)
            
        if len(propList) == 0:  
            if debug: print("unit prop done")
            return None
        if debug: print(" propList:", propList)
        for unit_clause in propList:
            implication_count += 1
            unit_literal = get_unit_literal(unit_clause)
            if unit_literal == None:
                if get_clause_state(unit_clause) == UNSAT:
                    antecedents[0] = unit_clause
                    decision_levels[0] = curr_level
                    # update_graph(unit_clause, 0)
                    if debug: print(" (unit_literal is None) CONFLICT clause", unit_clause)
                    return CONFLICT
            else:
                assign_implied_var(unit_clause, unit_literal)
                # update_graph(unit_clause, unit_literal)

def resolution_of(clauseA, clauseB):
    '''
    Return the resolution of 2 clauses.
    Args:
        clauseA ([int]):
        clauseB ([int]):         
    Returns:
        {int}: Clause
    '''
    result = set(clauseA)
    for literal in clauseB:
        if -literal in clauseA:
            # print(literal)
            result.remove(-literal)
        else:
            # print(literal)
            result.add(literal)
    return result

def uip_found(learned_clause):
    '''
    UIP (Unit Implication Point) is the point where only one literal in the 
    learned_clause that is assigned at current decision level.
    Args:
        learned_clause ({int}): 
    Returns:
        bool: if UIP is found return True.
    '''
    count = 0
    for literal in learned_clause:
        var = abs(literal)
        if decision_levels[var] == curr_level:
            count += 1
            if count > 1:
                return False
    if count == 1:
        return True
    return False

def get_backtrack_level(learned_clause):
    '''
    Backtrack level is the largest decision levels of the literals in the 
    learned_clause that is smaller than current level. Return -1 if not found.
    Args:
        learned_clause {int}: 
    Returns:
        int: backtrack_level
    '''
    if len(learned_clause) == 1:
        return 0  # backtrack to the start
    backtrack_level = -1
    for literal in learned_clause:
        var = abs(literal)
        d = decision_levels[var]
        if d > backtrack_level and d < curr_level:  #d != curr_level and 
            backtrack_level = d
    return backtrack_level

def conflict_analysis():
    '''
    Analyze conflict by resolution steps backwards from the UNSAT clause 
    (that is obtained in unit propagation) until UIP is reached.
    Returns:
        {int}: learned_clause
        int: backtrack_level
    '''
    # print("\n", curr_level, antecedents, decision_levels, "\n")
    queue = [0]  # special node antecedents[0] is the conflicting unsat clause 
    seen = set()
    learned_clause = set()
    while len(queue) > 0:
        if debug: print("    queue", queue)
        if (not learned_clause in learned_clauses) and uip_found(learned_clause):
            if debug: print("uip_found")
            break
        k = queue.pop(0)
        seen.add(k)
        clause = antecedents[k]
        if debug: print("      resolution with", clause)
        learned_clause = resolution_of(learned_clause, clause)
        if debug: print("      get learned_clause", learned_clause)
        for literal in learned_clause:
            var = abs(literal)
            if decision_levels[var] == curr_level and antecedents[var] != None and var not in queue: # and var not in seen:  #added seen to prevent non-stop loop in resolution
                queue.append(var)
                if debug: print("      append var", var)
    if uip_found(learned_clause): #debug statement: learned clause must be UIP
        if debug: print("UIP learned clause")
    else:
        if debug: print("NOT UIP learned clause")
    backtrack_level = get_backtrack_level(learned_clause)
    if debug: print("    return learned_clause, backtrack_level:", learned_clause, backtrack_level)
    return frozenset(learned_clause), backtrack_level

def two_clause_heuristic():
    '''
    Returns: 
        int: proposition with maximum occurrences in 2-clauses, i.e., 
            clauses with two literals, and break ties randomly.
    '''
    unassigned = []
    for clause in clauses.union(learned_clauses):
        state = get_clause_state(clause)
        if state == TWO_CLAUSE:
            for literal in clause:
                if get_literal_value(literal) == -1:
                    unassigned.append(abs(literal))
    if len(unassigned) == 0:
        return random_heuristic()
    unassigned_count = Counter(unassigned)
    maxValue = max(unassigned_count.values())
    variables = [key for key, value in unassigned_count.items() if value == maxValue]
    return random.choice(variables) * random.choice([1,-1])

# def not_rand_two_clause_heuristic():
#     '''
#     Returns: 
#         int: proposition with maximum occurrences in 2-clauses, i.e., 
#             clauses with two literals, and break ties randomly.
#     '''
#     unassigned = []
#     unassigned_lit = {}
#     for clause in clauses.union(learned_clauses):
#         state = get_clause_state(clause)
#         if state == TWO_CLAUSE:
#             for literal in clause:
#                 if get_literal_value(literal) == -1:
#                     unassigned.append(abs(literal))
#                     if literal not in unassigned_lit:
#                         unassigned_lit[literal] = 0
#                     unassigned_lit[literal] += 1
#     if len(unassigned) == 0:
#         return random_heuristic()
#     unassigned_count = Counter(unassigned)
#     maxValue = max(unassigned_count.values())
#     variables = [key for key, value in unassigned_count.items() if value == maxValue]

#     v = random.choice(variables)
#     if abs(v) not in unassigned_lit:
#         lit = -abs(v)
#     elif -abs(v) not in unassigned_lit:
#         lit = abs(v)
#     elif unassigned_lit[abs(v)] > unassigned_lit[-abs(v)]:
#         lit = abs(v)
#     else:
#         lit = -abs(v) 
#     # return random.choice(variables) * random.choice([1,-1])
#     return lit

def DLCS_heuristic():
    '''
    Returns: 
        int: proposition with maximum occurrences in all UNRESOLVED clauses, break ties randomly,
             assigned true if +ve literal count is larger than -ve count, false otherwise.
    '''
    unassigned_var = []
    unassigned_lit = {}
    for clause in clauses.union(learned_clauses):
        state = get_clause_state(clause)
        if state != SAT and clause != UNSAT:
            for literal in clause:
                if get_literal_value(literal) == -1:
                    unassigned_var.append(abs(literal))
                    if literal not in unassigned_lit:
                        unassigned_lit[literal] = 0
                    unassigned_lit[literal] += 1
    # literals =  max(unassigned_var,key=unassigned_var.count)
    if len(unassigned_var) == 0:
        return random_heuristic()
    unassigned_var_count = Counter(unassigned_var)
    maxValue = max(unassigned_var_count.values())
    variables = [key for key, value in unassigned_var_count.items() if value == maxValue]
    v = random.choice(variables)
    if abs(v) not in unassigned_lit:
        lit = -abs(v)
    elif -abs(v) not in unassigned_lit:
        lit = abs(v)
    elif unassigned_lit[abs(v)] > unassigned_lit[-abs(v)]:
        lit = abs(v)
    else:
        lit = -abs(v) 
    # return random.choice(variables) * random.choice([1,-1])
    return lit

def get_var_freq():
    # variable frequency in initial set of input clauses
    global var_frequency
    if len(var_frequency) == 0:
        var_frequency = {x:0 for x in range(1, len(assignments))}
        for clause in clauses:
            for literal in clause:
                var_frequency[abs(literal)] += 1

def max_freq_heuristic():
    '''
    Returns: 
        int: unassigned proposition with maximum occurrences in the initial input clauses.
    '''
    global var_frequency
    if len(var_frequency) == 0:
        get_var_freq()
    # Find maximum variable such that variable is unassigned.
    literal = 0
    max_freq = -1
    for x in range(1, len(assignments)):
        # print(x)
        if assignments[x] == -1 and var_frequency[x] > max_freq:
            max_freq = var_frequency[x]
            literal = x
    return literal*random.choice([1,-1])

def vsids_init():
    vsids_score = {x:0 for x in range(-num_vars, num_vars+1)}
    for clause in clauses:
        for literal in clause:
            vsids_score[literal] += 1
    return vsids_score

def update_vsids():
    global conflict_count, vsids_score
    conflict_count += 1
    for literal in antecedents[0]:  #antecedents[0] is the conflict clause
        vsids_score[literal] += 1
    if conflict_count % 256 == 0:
        # half score every 256 conflicts (decay score to give priority to recently learned clause)
        for literal in range(-num_vars, num_vars+1):
            vsids_score[literal] = vsids_score[literal]/2
    # sort priority queue after each decay only

def vsids_heuristic():
    global vsids_score
    literal = 0
    max_score = -1
    for x in range(-num_vars, num_vars+1):
        if assignments[abs(x)] == -1 and vsids_score[x] > max_score:
            max_score = vsids_score[x] 
            literal = x
    return literal

def random_heuristic():
    '''
    Returns: 
        int: randomly chosen unassigned proposition 
    '''
    global inputs
    if(len(inputs) > 0):
        return inputs.pop(0)
    unassigned = [x for x in range(1, len(assignments)) if assignments[x] == -1]
    return random.choice(unassigned) * random.choice([1,-1])

def pick_branching_variable():
    '''
    Returns:
        int: picked decision variable and it's assignemnt value
            (positive if assign to True, negative if assign to False)
    '''
    return heuristic()

def all_var_assigned():
    '''
    Returns:
        bool: if all variables are assigned return True.
    '''
    return not (-1 in assignments[1:])

def assign_decision_var(decision_var):
    '''
    Assign value to decision variable, update it's decision level.
    Args:
        decision_var (int):
    '''
    global curr_level, assignments, decision_levels
    var = abs(decision_var)
    assignments[var] = get_literal_sign(decision_var)
    # antecedents[var] = None
    decision_levels[var] = curr_level
    if debug: print("\ndec assign x{} of value_{} at lvl_{}".format(decision_var,get_literal_sign(decision_var), curr_level))


def backtrack(backtrack_level):
    '''
    Remove assignments of variables that were assigned at higher than the backtrack level.
    Args:
        backtrack_level (int):
    '''
    global assignments, antecedents, decision_levels
    for var in range(len(assignments)):
        if decision_levels[var] > backtrack_level:
            assignments[var] = -1
            antecedents[var] = None
            decision_levels[var] = -1

def solveCDCL():
    global curr_level, learned_clauses, assignments, antecedents, decision_levels, branching, var_frequency
    curr_level = 0
    if unit_propagation() == CONFLICT:
        return UNSAT
    branching = 0
    while not all_var_assigned():
        if time.time() - start_time > timeout_limit:
            return TIMEOUT
        dec_var = pick_branching_variable() #random_heuristic() #two_clause_heuristic() #max_occurence_heuristic() 
        branching += 1
        curr_level += 1
        # if branching > 60:
        #   break
        assign_decision_var(dec_var)
        while unit_propagation() == CONFLICT:
            if heuristic.__name__ == "vsids_heuristic": update_vsids()
            learned_clause, b = conflict_analysis()
            if b < 0:
                return UNSAT
            learned_clauses.add(learned_clause)
            backtrack(b)
            curr_level = b
    return SAT

def initialize_and_run_solver(show_result=True):
    global curr_level, branching, implication_count, conflict_count
    global learned_clauses, assignments, antecedents, decision_levels
    global var_frequency, vsids_score
    global debug, inputs, clauses 
    global start_time, time_taken

    curr_level = 0
    branching = 0
    implication_count = 0
    conflict_count = 0

    learned_clauses = set()
    assignments = [-1] * (num_vars+1)
    antecedents =  [None] * (num_vars+1)  # List of clauses
    decision_levels = [-1] * (num_vars+1)

    var_frequency = {}
    vsids_score = vsids_init()

    inputs = []  # for debug purpose: by specifying pick sequence in random heuristic
    # print("clauses", clauses)
    # print("\n", curr_level, learned_clauses, assignments, antecedents, decision_levels, "\n")

    start_time = time.time()
    sat_result = solveCDCL()
    end_time = time.time()
    time_taken = float("{:.6f}".format(end_time - start_time))
    # print(sat_result)
    # print("\n", curr_level, branching, learned_clauses, assignments, antecedents, decision_levels, "\n")

    if show_result:
        print_and_write_output(sat_result)

    return sat_result, time_taken, branching, implication_count

def print_and_write_output(sat_result):
    # sat_result can be SAT/UNSAT/TIMEOUT
    output_assignments = "None"
    if sat_result == SAT:
        output_assignments = []
        for i, x in enumerate(assignments[1:]):
            j = i+1
            if x == 0:
                output_assignments.append(-j)
            else:
                output_assignments.append(j)
    verified_result = "None"
    
    if is_known_solution: 
        if sat_result == SAT:
            if "sat" in input_cnf:
                verified_result = "Correct"
                print("Correct!")
            else:
                verified_result = "Wrong"
                print("ERRORRRRR")
                return 
        elif sat_result == UNSAT:
            if "unsat" in input_cnf:
                verified_result = "Correct"
                print("Correct!")
            else:
                verified_result = "Wrong"
                print("ERRORRRRR")
                return 
    
    w = "\nInput file: {}, \nClause: {}, \nVariables: {}, \nTime: {}, \nHeuristic: {}, \nBranches: {}, \nImplication: {}, \nLearned clauses: {}, \nResult: {} ({}), \nAssigmenent: {}\n".format(input_cnf, num_clauses, num_vars, time_taken, heuristic.__name__, branching, implication_count, len(learned_clauses), sat_result, verified_result, output_assignments)
    print(w)
    
    output_file = output_path
    if not os.path.exists(output_file):
        os.mkdir(output_file)
    if is_known_solution:        
        if verified_result == "Correct":
            output_file += "correct.txt"
        else:
            output_file += "wrong.txt"
    else:
        output_file += "solved.txt"
    file1 = open(output_file, "a")  # append mode
    file1.write(w)
    file1.close()
    print("result append to file: ", output_file, "\n")
    
def read_input(cnf_file):
    f = open(cnf_file, 'r')
    Lines = f.readlines()
    clauses = []
    num_vars, num_clauses = 0, 0
    for line in Lines:
        line = line.strip()
        if len(line) < 1:
            continue
        if line[0] == 'c':
            continue
        if line[0] == 'p':
            num_vars, num_clauses = int(line.split()[-2]), int(line.split()[-1])
        else:
            literals = line.split()[:-1]
            clause = [int(i) for i in literals if abs(int(i)) > 0 and abs(int(i)) <= num_vars]
            if len(clause) > 0:
                clauses.append(clause)  
                # print(line, clause)
    return num_vars, num_clauses, clauses

def get_clauses_set(clauses):
    clauses_set = set()
    for clause in clauses:
        valid = True
        for x in clause:
            if -x in clause:
                valid = False
            if valid:
                clauses_set.add(frozenset(clause))
    return clauses_set

def get_read_input():
    global input_cnf, num_vars, num_clauses, clauses
    num_vars, num_clauses, clauses = read_input(input_cnf)
    clauses = get_clauses_set(clauses)
    num_clauses = len(clauses)
    print("num_vars:", num_vars, "num_clauses:", num_clauses)
    # print("clauses:", clauses)
    return num_vars, num_clauses

def run_from_file(path):
    global input_cnf, is_known_solution
    input_cnf = path
    if h == 'all':
        run_experiment(path, show_result=True)
        return
    if "sat" in path or "unsat" in path:
        is_known_solution = True
    else:
        is_known_solution = False
    get_read_input()
    initialize_and_run_solver()

def run_from_dir(path):
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            filename = os.path.join(root, name)
            #  print(os.path.join(root, name), os.path.splitext(filename))
            if os.path.splitext(filename)[1] == '.cnf':
                print(filename)
                if h == 'all':
                    run_experiment(filename, show_result=True)
                else:
                    run_from_file(filename)

def run_experiment(path, show_result=False):
    global input_cnf, debug, heuristic

    debug = False
    input_cnf = path
    num_vars, num_clauses = get_read_input()
    row = [input_cnf.split('/')[-1], num_vars, num_clauses]
    # run solver using each heuristic
    for h in heuristics_list:
        if debug: print(h)
        heuristic = heuristics[h]
        result = initialize_and_run_solver(show_result=show_result)  # return sat_result, time_taken, branching, implication_count
        for i in result:
            row.append(i)
        # print(row)
    return row


heuristics = {"random": random_heuristic, "two_clause": two_clause_heuristic, "max_freq": max_freq_heuristic, "DLCS": DLCS_heuristic, "VSIDS": vsids_heuristic} #, "VSADS": vsads_heuristic} #"two_clause": two_clause_heuristic, 
heuristics_list = [h for h in heuristics.keys()]
timeout_limit = 600 # 10 mins
is_known_solution = False
output_path = "result/"

def main():
    # Usage: python mySATSolver.py [file/folder] [heuristic choice] [debug]
    # Output: appended to ./result.txt

    global debug, heuristics, heuristic, h
    if len(sys.argv) != 4:
        print("\nHi, this program will run SAT_Solver on input cnf files (based on input heuristic), then append the result to a text file in 'result/'.")
        print("\nUsage: (3 input parameters required)")
        print("    python3 mySATSolver.py <file/dir path> <heuristic choice: {} or 'all'> <allow debug: 0 or 1>".format(heuristics_list))
        print("\neg: python3 mySATSolver.py CS4244_project/sat/uf20-91/uf20-01.cnf two_clause 0\n")
        sys.exit()
    
    path = sys.argv[1]

    h = sys.argv[2]
    debug = bool(int(sys.argv[3])>0)
    print("input path: {}, branching heuristic: {}, debug: {}".format(path, h, debug))

    if h != "all":
        if h not in heuristics:
            print("'{}' is not a valid heuristic in {}.".format(h, heuristics_list))
            return
        else:
            heuristic = heuristics[h]

    if os.path.isdir(path):
        run_from_dir(path)
    elif os.path.isfile(path):  
        run_from_file(path)
    else:  
        print("File not exists." )

if __name__ == "__main__":
    main()


