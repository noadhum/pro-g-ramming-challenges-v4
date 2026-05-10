import argparse

from puzzle_solver.puzzle import Puzzle
from puzzle_solver.solver import Solver

def cli() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog='N-Puzzle Solver',
        description='N-Puzzle Solver using A* Search Algorithm.',
    )

    parser.add_argument(
        '-p'
        '-puzzle',
        nargs='+',
        type=int,
        help='The puzzle to solve'
    )

    return parser.parse_args()

def main() -> None:
    args = cli()

    puzzle = Puzzle(3, args.p_puzzle).state or Puzzle(3).state

    if len(puzzle) != 9:
        raise ValueError("'puzzle' must have length of 9.")
    
    moves = Solver(puzzle).solve()

    print('Finding optimal path...\n')

    if moves:
        print('Solution found!\n')
        print(f'Move amount: {len(moves)} \nRequired moves: {moves}')
    else:
        print('Solution no found :(')


if __name__ == '__main__':
    main()