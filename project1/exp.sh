#!/bin/bash
python3 experiments.py random_cnf_inputs/sat/N75/ result/sat_N75.csv &&
python3 experiments.py random_cnf_inputs/unsat/N75/ result/unsat_N75.csv &&
python3 experiments.py random_cnf_inputs/sat/N100/ result/sat_N100.csv &&
python3 experiments.py random_cnf_inputs/unsat/N100/ result/unsat_N100.csv &&
python3 experiments.py random_cnf_inputs/sat/N50/ result/sat_N50.csv &&
python3 experiments.py random_cnf_inputs/unsat/N50/ result/unsat_N50.csv &&
python3 experiments.py random_cnf_inputs/sat/N125/ result/sat_N125.csv &&
python3 experiments.py random_cnf_inputs/unsat/N125/ result/unsat_N125.csv
