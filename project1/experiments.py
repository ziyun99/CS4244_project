import os
import sys
import time
import pandas as pd
from pycryptosat import Solver
import mySATSolver


def run_cryptosat(filename):
    _, _, clauses = mySATSolver.read_input(filename)
    s = Solver()
    for c in clauses:
        s.add_clause(c)
    start_time = time.time()
    sat, solution = s.solve()
    end_time = time.time()
    time_taken = float("{:.6f}".format(end_time - start_time))
    return sat, time_taken

def write_csv(all_results, output_path):
    title = ['filename','variables','clauses', 'SAT', 'time_cryptosat']
    result_title = ['result', 'time', 'branches', 'implications']
    heuristics_list = mySATSolver.heuristics_list
    
    for h in heuristics_list:
        for r in result_title:
            title.append(r + '_' + h)
    # print(len(title))

    if ".csv" not in output_path:
        output_path += ".csv"
    df = pd.DataFrame(all_results, columns=title) 
    df.to_csv(output_path)

def run_experiments(input_path):
    all_results = []
    try:
        for root, dirs, files in os.walk(input_path, topdown=False):
            for name in files:
                filename = os.path.join(root, name)
                if os.path.splitext(filename)[1] == '.cnf':
                    if "sat" or "unsat" in filename:
                        print(filename)
                        result = mySATSolver.run_experiment(filename)   
                        
                        sat, time = run_cryptosat(filename)
                        result.insert(3, sat)
                        result.insert(4, time)

                        print("Solved", result)
                        all_results.append(result)

                        # break
    except KeyboardInterrupt:
        print("KeyboardInterrupt... Stopping and saving output to csv file...")
        return all_results
    return all_results
    
def main():
    if len(sys.argv) != 3:
        print("Hi, this program will run SAT_Solver in 'mySATSolver.py' on all cnf files (on all heuristics), then output the results in a csv file.")
        print("  Usage: python3 experiments.py [cnf_dirname] [output_filename]")
        print("  - eg: python3 experiments.py CS4244_project/sat/ result/experiments.csv") 
        sys.exit()

    input_path = sys.argv[1]
    output_path = sys.argv[2] 

    if not os.path.exists(input_path):
        print("'{}' path not exits.".format(input_path))

    all_results = run_experiments(input_path)
    
    write_csv(all_results, output_path)


if __name__ == "__main__":
    main()
