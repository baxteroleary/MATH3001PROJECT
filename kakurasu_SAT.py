from pysat.formula import IDPool
from pysat.pb import PBEnc
from pysat.solvers import Glucose3


def solve_kakurasu(n, const):
    """Solve a Kakurasu puzzle using a SAT solver.

    Inputs:
        n: Grid size
        const: A 2 x n array of constants:

    Returns:
        An n x n grid of 0/1 values if solvable, otherwise None.
    """
    
    # Create variable pool of n**2 variables
    vpool = IDPool(start_from=n * n + 1)
    clauses = []

    # Add row constraints as clauses
    for row in range(n):
        literals = [row * n + col + 1 for col in range(n)]
        weights = [col + 1 for col in range(n)]
        
        # Convert equations to cnf
        cnf = PBEnc.equals(
            lits=literals,
            weights=weights,
            bound=const[0][row],
            vpool=vpool)
        
        clauses.extend(cnf.clauses)

    # Add column constraints as clauses
    for col in range(n):
        literals = [row * n + col + 1 for row in range(n)]
        weights = [row + 1 for row in range(n)]
        
        # Convert equals to cnf
        cnf = PBEnc.equals(
            lits=literals,
            weights=weights,
            bound=const[1][col],
            vpool=vpool)

        clauses.extend(cnf.clauses)

    # Solve using Glucose3
    with Glucose3() as solver:
        for clause in clauses:
            solver.add_clause(clause)
        
        # If solver can't solve return none
        if not solver.solve():
            return None
        
        # Get a model if the formula was satisfied
        model = set(solver.get_model())

    # Map model to an n x n solution grid.
    grid = []
    for row in range(n):
        row_sol = []
        for col in range(n):
            var = row * n + col + 1
            # Cell is solved if its corresponding variable is in the model
            row_sol.append(1 if var in model else 0)
        grid.append(row_sol)

    return grid