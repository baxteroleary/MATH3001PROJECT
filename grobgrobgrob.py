from sympy import groebner, symbols
from sympy.solvers.polysys import solve_poly_system


def main(n, const):
    """Solve a Kakurasu puzzle using a Groebner basis algorithm

    Args:
        n: Grid size
        const: A 2 x n array of constants

    Returns:
        An n x n grid of 0/1 values if solvable, otherwise None
    """
    
    # Create n**2 symbolic variables and arrange into an array
    xs = symbols(f"x0:{n*n}")
    X = [[xs[i * n + j] for j in range(n)] for i in range(n)]

    F = []

    # Row constraints
    for row in range(n):
        F.append(sum((i + 1) * X[row][i] for i in range(n)) - const[0][row])

    # Column constraints
    for col in range(n):
        F.append(sum((i + 1) * X[i][col] for i in range(n)) - const[1][col])

    # Boolean constraints (x**2 - x = 0)
    for i in range(n ** 2):
        x = X[i // n][i % n]
        F.append(x**2 - x)
        
    # Perform basis reduction using Buchberger's algorithm 
    # with a lexographic ordering
    G = groebner(F, xs, order="lex")
    
    # Solve the reduced basis 
    sols = solve_poly_system(G, *xs)

    # Return None if the puzzle is unsolvable
    if not sols:
        return None

    # Convert system of variables back to a grid
    grid = []

    for i in range(n):
        row = []
        for j in range(n):
            row.append(int(sols[0][i * n + j]))
        grid.append(row)

    return grid