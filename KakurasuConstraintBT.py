import itertools as it
import copy


def create_grid(n):
    '''Create an nxn array for valid positive integers n'''

    if isinstance(n, int) and n > 0:
        grid = [[3 for i in range(n)] for j in range(n)]
        return grid
    else:
        return None


def update(row, col, val, grid, const):
    '''Update grid state then substract entries row and column from respective sums
    
    Inputs: 
        row, col: location of cell to be updated
        val: value in 0,1,3 to be updated
        grid,const: ...
    
    Returns:
        True/None if update is successful or fails
    '''
    
    if grid[row][col] != 3:
        if grid[row][col] == val:
            return True
        return None
    
    # Assign value to cell
    grid[row][col] = val
    

    if val == 1:
        # Subtract index from line sum
        const[0][row] -= (col + 1)
        const[1][col] -= (row + 1)
        
        # Fail update if constant is now negative
        if const[0][row] < 0 or const[1][col] < 0:
            return None
    
    return True


def cell(axis, index, pos):
    '''Get cells position accounting for its axis'''

    if axis == 0:
        return index, pos
    else:
        return pos, index


def trivial_line(n, axis, index, grid, const):
    '''Fill in trivial lines
    
    Inputs: 
        ...
    
    Returns:
        False if line already solved
    '''

    rem = const[axis][index]
    unknowns = []

    for pos in range(n):
        row, col = cell(axis, index, pos)
        if grid[row][col] == 3:
            unknowns.append(pos)

    if unknowns == []:
        return False
    
    # Get list of all remaining indicies in line
    weights = [pos + 1 for pos in unknowns]
    
    # Trivial case remaining constant is 0
    if rem == 0:
        

        for pos in unknowns:
            r, c = cell(axis, index, pos)
            # Update rest of line with 0s
            update(r, c, 0, grid, const)
            
            
    # Case remaining constant is total of all weights
    if rem == sum(weights):

        for pos in unknowns:
            row, col = cell(axis, index, pos)
            # All candidates must be 1
            update(row, col, 1, grid, const)
            
            
    # Case there is only 1 unknown remaining        
    if len(unknowns) == 1:
        
        # Locate the unknown
        row, col = cell(axis, index, unknowns[0])
        
        
        # If unknown equals constant assign 1 to the cell
        if unknowns[0] + 1 == rem:
            update(row, col, 1, grid, const)
        else:
            update(row, col, 0, grid, const)
        



def trivial(n, grid, const):
    'Find and fill trivial lines in grid'

    for axis in range(2):
        for index in range(n):
            trivial_line(n, axis, index, grid, const)


def order_consts(n, consts):
    'Order constants by magnitude for priority searching'

    ordered = []

    for i in range(2 * n):
        # Create a list of 3-tuples containing each constant,
        # its axis and its location
        ordered.append([consts[i // n][i % n], i // n, i % n])
        
    
    # Return sorted constants in descending order of magnitude
    return sorted(ordered, reverse=True, key=lambda x: x[0])
    


def feasible_sums(candidates, constant):
    'Find all possible combinations of candidates that sum to the line constant'

    solutions = []

    for size in range(len(candidates) + 1):
        
        # Iterate all combinations of candidate weight sums
        for comb in it.combinations(candidates, size):
            

            if sum(comb) == constant:
                # If a combination sums to the constant record as a possible solution
                solutions.append(comb)

    return solutions


def zero_line_sum(n, axis, index, grid, const):
    'Eliminate all remaining candidates'
    
    changed = False
    
    for pos in range(n):
        row, col = cell(axis, index, pos)
        if grid[row][col] == 3:
            if update(row, col, 0, grid, const) is None:
                return None
            changed = True
    return changed
            

def process_line(n, axis, index, grid, const):
    ''' Perform reduction of indicies 
    
    Inputs: 
        ...
    
    Returns:
        True/None if update is successful or fails
    '''
    rem = const[axis][index]
    if rem < 0:
        return None

    # Eliminate candidates whose weight > remaining sum
    for pos in range(n):
        row, col = cell(axis, index, pos)
        if grid[row][col] == 3 and (pos + 1) > rem:
            if update(row, col, 0, grid, const) is None:
                return None
            return True

    # Collect unknowns
    unknowns = []
    for pos in range(n):
        row, col = cell(axis, index, pos)
        if grid[row][col] == 3:
            unknowns.append(pos)

    # If no unknowns left, remainder must be exactly 0
    if not unknowns:
        return None if rem != 0 else False

    weights = [pos + 1 for pos in unknowns]

    # Bound checks
    if rem > sum(weights):
        return None

    # If rem is nonzero, it must be at least one remaining weight (otherwise impossible)
    if rem != 0 and rem < min(weights):
        return None

    sols = feasible_sums(weights, rem)
    if not sols:
        return None

    # Unique solution subset: force all cells
    if len(sols) == 1:
        sol_set = set(sols[0])
        for pos in unknowns:
            row, col = cell(axis, index, pos)
            if (pos + 1) in sol_set:
                if update(row, col, 1, grid, const) is None:
                    return None
            else:
                if update(row, col, 0, grid, const) is None:
                    return None
        return True

    # Multiple solutions: find common weights and never-used weights
    common = set(sols[0])
    for s in sols[1:]:
        common &= set(s)

    appear = set()
    for s in sols:
        appear |= set(s)

    changed = False
    for pos in unknowns:
        w = pos + 1
        row, col = cell(axis, index, pos)

        if w in common:
            if update(row, col, 1, grid, const) is None:
                return None
            changed = True
        elif w not in appear:
            if update(row, col, 0, grid, const) is None:
                return None
            changed = True

    if changed:
        return True

    # If rem is bigger than sum of all but the largest, largest must be 1
    largest_pos = max(unknowns)
    sum_without_largest = sum((p + 1) for p in unknowns if p != largest_pos)

    if rem > sum_without_largest:
        row, col = cell(axis, index, largest_pos)
        if update(row, col, 1, grid, const) is None:
            return None
        return True

    return False


def largest(n, grid, const):
    'Sorting by largest constants, perform reduction by method of sum constraints'

    progress = True

    while progress:
        progress = False
        candidates = order_consts(n, const)

        for value, axis, index in candidates:
            if value == 0:
                x = zero_line_sum(n, axis, index, grid, const)
                if x is None:
                    return None
                if x:
                    progress = True
                    break
                else:
                    continue

            res = process_line(n, axis, index, grid, const)
            if res is None:
                return None
            if res is True:
                progress = True
                break
    return True

def propagate(n, grid, const):
    'Main algorithm'

    while True:
        before_grid = copy.deepcopy(grid)
        before_const = copy.deepcopy(const)

        trivial(n, grid, const)
        if largest(n, grid, const) is None:
            return None

        if grid == before_grid and const == before_const:
            break

    return True  # propagation completed


def score_line(axis,index,n, grid, const):
    ''' Algorithm to score a line on a custom heuristic
    
    Inputs: 
        ...
    
    Returns: Length of unknowns in line & line slack
        
    '''
    # If line is completed return None
    rem = const[axis][index]
    if rem == 0:
        return None  
    
    unknowns = []
    weights_sum = 0
    
    # Compute list of unknowns and weight sums
    for pos in range(n):
        row, col = cell(axis, index, pos)
        if grid[row][col] == 3:
            unknowns.append(pos)
            weights_sum += (pos + 1)
    
    # If there are no unknowns return None
    if not unknowns:
        return None

    # Slack is our comparison tool between lines
    slack = weights_sum - rem  
    
    return (len(unknowns), slack)

def find_unknown(n, grid, const):
    ''' Custom heuristic algorithm selecting cell to be backtracked
        prioritising fewest number of unknowns and then slack if unknowns are tied
    
    Inputs: 
        ...
    
    Returns:
        
    '''
    
    # Create a base heuristic for which all cells will be better
    # best = [axis, index, unknown_count, slack]
    best = [-1, -1, 10**9, 10**9]

    # Rows
    for row in range(n):
        score = score_line(0,row,n,grid,const)
        if score is None:
            continue
        no_unk, slack = score
        # If line has better metrics set it as the current best
        if no_unk < best[2] or (no_unk == best[2] and slack < best[3]):
            best = [0, row, no_unk, slack]

    # Columns
    for col in range(n):
        score = score_line(1,col,n,grid,const)
        if score is None:
            continue
        no_unk, slack = score
        if (no_unk < best[2]) or (no_unk == best[2] and slack < best[3]):
            best = [1, col, no_unk, slack]

    # If no cell has been selected pick first unknwown in grid
    if best[0] == -1:
        for row in range(n):
            for col in range(n):
                if grid[row][col] == 3:
                    return (row, col)
        return None

    axis, index = best[0], best[1]

    # Return highest index unknown in that line
    if axis == 0:
        for col in reversed(range(n)):
            if grid[index][col] == 3:
                return (index, col)
    else:
        for row in reversed(range(n)):
            if grid[row][index] == 3:
                return (row, index)

    # Again if no cell has been selected pick first unknown in grid
    for row in range(n):
        for col in range(n):
            if grid[row][col] == 3:
                return (row, col)
    return None


def solve_bt(n, grid, const):
    ''' Main backtracking algorithm
    
    Inputs: 
        ...
    
    Returns:
        A solved grid if solveable, otherwise None
    '''
    # Run main propagation, if None grid is invalid
    if propagate(n, grid, const) is None:
        return None

    # Get cell to be backtracked
    pos = find_unknown(n, grid, const)
    
    # If didnt pick one check whether grid is already solved
    if pos is None:
        for axis in range(2):
            for idx in range(n):
                if const[axis][idx] != 0:
                    return None
        return grid  # solved

    row, col = pos
    
    # Go through cases where cell is 0 or 1
    for guess in (0, 1):
        #Create copies of the grid
        g2 = copy.deepcopy(grid)
        c2 = copy.deepcopy(const)
        
        # if cell can't be updated choose other value
        if update(row, col, guess, g2, c2) is None:
            continue

        # Recursively call the function with new guess to try
        sol = solve_bt(n, g2, c2)
        if sol is not None:
            return sol
    
    return None


def main(n, const):
    grid = create_grid(n)
    sol = solve_bt(n, grid, const)
    return sol