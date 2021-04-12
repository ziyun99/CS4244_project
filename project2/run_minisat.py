import pandas as pd
import os

def minisat_to_csv(dirname):
  i = 0
  all_results = []
  try:
    for dir in os.listdir(dirname):
      results = []
      for filename in os.listdir(dirname+dir):
        i += 1
        fname = filename.split('/')[-1]
        fnames = fname.split('_')
        N = int(fnames[0].split('N')[1])
        K = int(fnames[1][1:])
        R = float(fnames[2][1:])
        L = int(fnames[3][1:])
        filename = os.path.join(dirname,dir,filename)
        print(i, filename)
        Result = "TIMEOUT"
        t = None
        try: 
          !timeout 600 cryptominisat5 --verb 1 $filename > out.txt
          file1 = open('out.txt', 'r')
          Lines = file1.read().splitlines()
          
          for i in range(len(Lines)-1, 0, -1):
            line = Lines[i]
            # print(line)
            if len(line) > 0 and line[0] == 's':
              if line.split()[1] == "SATISFIABLE":
                Result = "SAT"
              else: 
                Result = "UNSAT"
              t = Lines[i-1].split()[-1]
              # print(str(t))
              res = [fname, N, K, R, L, Result, t]
              all_results.append(res)
              results.append(res)
              print(res)
          os.remove('out.txt')
        except:
          print("Error: Skipped {}".format(filename))
          pass
        # break
      output_path = "/content/drive/MyDrive/y3s2/CS4244 Project/output_" + dir +".csv"
      title = ['filename', 'N', 'K', "R", 'L', 'Result','Time']
      print("Writing csv to " + output_path)
      df = pd.DataFrame(all_results, columns=title) 
      df.to_csv(output_path)

  except KeyboardInterrupt:
    output_path = "/content/drive/MyDrive/y3s2/CS4244 Project/output.csv"
    title = ['filename', 'N', 'K', "R", 'L', 'Result','Time']
    print("Writing to " + output_path)
    df = pd.DataFrame(all_results, columns=title) 
    df.to_csv(output_path)

minisat_to_csv("/content/CS4244_project/project2/rand_cnf_inputs/")