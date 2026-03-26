import KakurasuConstraintBT as constraint
import grobgrobgrob as groebner
import copy
import random
import time
import kakurasu_SAT as SAT
import csv


def generate_grid(n):
    '''Create a random nxn Karukasu board
    
    Inputs: 
        n: Grid size
    
    Returns:
        const: A 2 x n array of constants representing a starting puzzle
        sol: nxn solution matrix of entries 0/1
    '''
    # Create random solution grid
    sol = [[random.randint(0,1) for _ in range(n)] for _ in range(n)]
    const = [[], []]
    
    # Write constants for the unsolved grid clues
    for row in range(n):
        row_sum = sum((col + 1) for col in range(n) if sol[row][col] == 1)
        const[0].append(row_sum)

    for col in range(n):
        col_sum = sum((row + 1) for row in range(n) if sol[row][col] == 1)
        const[1].append(col_sum)

    return const, sol


def check_solution(n, const, grid):
    '''Verify solution to a puzzle
    
    Inputs: 
        n: ...
        const: ...
        grid: proposed solution 
    
    Returns:
        True if solved grid matches starting solution, False otherwise
    '''
    # grid must be n x n
    if grid is None or len(grid) != n or any(len(row) != n for row in grid):
        return False
    
    # Grid must not have any unsolved cells
    if any(cell == 3 for row in grid for cell in row):
        return False

    # check row sums
    for row in range(n):
        row_sum = sum((col + 1) for col in range(n) if grid[row][col] == 1)
        if row_sum != const[0][row]:
            return False

    # check col sums
    for col in range(n):
        col_sum = sum((row + 1) for row in range(n) if grid[row][col] == 1)
        if col_sum != const[1][col]:
            return False

    return True


def write_stuff(max_n, trials = 30):
    '''Write solving times of each method to csv file
    
    Inputs: 
        max_n: desired maximum grid size to test
        trials: number of grids of each size to test
    
    Returns:
        Written csv file to directory 
    '''
    with open("test.csv", "w", newline="") as f:
        
        # Write column headers
        csv.writer(f).writerow([
            "n",
            "trial",
            "Constraint/BT",
            "SAT",
            "Groebner"])
        
        # Perform trials for n up to n_max
        for n in range(1, max_n + 1):
            for trial in range(1, trials + 1):
                const, sol = generate_grid(n)
                
                # If method solves correctly, store the time taken to solve, else FAIL
                start = time.perf_counter()
                if check_solution(n,const,constraint.main(n, copy.deepcopy(const))):
                    t1 = time.perf_counter() - start
                else:
                    t1 = "FAIL"
                    
                start = time.perf_counter()
                if check_solution(n,const,SAT.solve_kakurasu(n, copy.deepcopy(const))):
                    t2 = time.perf_counter() - start
                else:
                    t2 = "FAIL"
                   
                # Groebner basis method is very time complex so stop after n=7
                if n < 8:
                    start = time.perf_counter()
                    if check_solution(n,const,groebner.main(n,copy.deepcopy(const))):
                        t3 = time.perf_counter() - start
                    else:
                        t3 = "FAIL"
                else:
                    t3 = ""
                
                # Write solving times as rows to csv file
                csv.writer(f).writerow([n,trial,t1,t2,t3])