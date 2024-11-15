import csv
from colorama import Fore, Style, init
from tqdm import tqdm
import random

init(autoreset=True)


def parse_rules(album_number):
    """Parse album number to create 3 rule numbers and add rule 190"""
    str_number = str(album_number)
    rules = [int(str_number[i:i + 2]) % 256 for i in range(0, 6, 2)]
    rules.append(190)
    return rules


def apply_rule(rule, left, center, right):
    """Apply the cellular automaton rule to the given cell"""
    pattern = (left << 2) | (center << 1) | right
    return (rule >> pattern) & 1


def initialize_cells(size, centered=True):
    """Initialize the cellular automaton with a centered active cell or random values"""
    if centered:
        cells = [0] * size
        cells[size // 2] = 1  # Centered initial active cell
    else:
        cells = [random.randint(0, 1) for _ in range(size)]
    return cells


def simulate_automaton(size, iterations, album_number, boundary='periodic'):
    """Simulate the 1D cellular automaton"""
    rules = parse_rules(album_number)
    cells = initialize_cells(size)
    history = [cells[:]]

    for _ in tqdm(range(iterations), desc="Simulating Cellular Automaton"):
        new_cells = [0] * size
        for i in range(size):
            left = cells[i - 1] if i > 0 or boundary == 'periodic' else 0
            right = cells[(i + 1) % size] if i < size - 1 or boundary == 'periodic' else 0
            rule_index = i % len(rules)
            new_cells[i] = apply_rule(rules[rule_index], left, cells[i], right)
        cells = new_cells[:]
        history.append(cells)

    return history


def save_to_csv(history, filename='output.csv'):
    """Save the automaton history to a CSV file with iteration headers"""
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Iteration"] + [f"Cell_{i}" for i in range(len(history[0]))])
        for i, row in enumerate(history):
            writer.writerow([i] + row)


def display_history(history):
    """Display the history with enhanced visualization in the terminal"""
    print("\nEnhanced Cellular Automaton Visualization:\n")
    for i, step in enumerate(history):
        row = "".join([f"{Fore.GREEN}█" if cell else f"{Fore.LIGHTBLACK_EX}░" for cell in step])
        print(f"{i:2}: {row}")


def main():
    try:
        size = int(input("Enter the grid size (number of cells): "))
        iterations = int(input("Enter the number of iterations: "))
        album_number = 414420
        boundary_type = input("Choose boundary condition (periodic/absorbing): ").strip().lower()

        if size <= 0 or iterations <= 0:
            raise ValueError("Size and iterations must be greater than 0.")

        if boundary_type not in ['periodic', 'absorbing']:
            raise ValueError("Boundary condition must be 'periodic' or 'absorbing'.")

        # Simulation with option to toggle boundary condition
        while True:
            history = simulate_automaton(size, iterations, album_number, boundary_type)
            save_to_csv(history)
            display_history(history)

            toggle = input("Would you like to toggle the boundary condition and re-run? (yes/no): ").strip().lower()
            if toggle == 'yes':
                boundary_type = 'absorbing' if boundary_type == 'periodic' else 'periodic'
                print(f"\nBoundary condition switched to {boundary_type}.\n")
            else:
                break

        print("Simulation completed. Results saved to 'output.csv'.")

    except ValueError as e:
        print("Error:", e)


if __name__ == "__main__":
    main()
