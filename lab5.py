import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt5.QtGui import QMovie
import sys


def initialize_grid(size, pattern='random'):
    """Initialize the grid with a specified pattern."""
    grid = np.zeros((size, size), dtype=int)

    if pattern == 'glider':
        glider = [(1, 0), (2, 1), (0, 2), (1, 2), (2, 2)]
        for dx, dy in glider:
            grid[1 + dx, 1 + dy] = 1
    elif pattern == 'glider_gun':
        gun = [
            (5, 1), (5, 2), (6, 1), (6, 2),
            (5, 11), (6, 11), (7, 11), (4, 12), (8, 12), (3, 13), (9, 13),
            (3, 14), (9, 14), (6, 15), (4, 16), (8, 16), (5, 17), (6, 17), (7, 17),
            (6, 18),
            (3, 21), (4, 21), (5, 21), (3, 22), (4, 22), (5, 22), (2, 23), (6, 23),
            (1, 25), (2, 25), (6, 25), (7, 25),
            (3, 35), (4, 35), (3, 36), (4, 36)
        ]
        for dx, dy in gun:
            grid[dx, dy] = 1
    elif pattern == 'oscillator':
        oscillator = [(1, 0), (1, 1), (1, 2)]
        for dx, dy in oscillator:
            grid[1 + dx, 1 + dy] = 1
    elif pattern == 'still':
        block = [(0, 0), (0, 1), (1, 0), (1, 1)]
        for dx, dy in block:
            grid[1 + dx, 1 + dy] = 1
    elif pattern == 'random':
        grid = np.random.randint(2, size=(size, size))

    return grid


def count_neighbors(grid, x, y, boundary_type):
    """Count live neighbors with boundary conditions."""
    size = grid.shape[0]
    neighbors = 0

    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue

            nx, ny = x + dx, y + dy

            if boundary_type == 'periodic':
                nx %= size
                ny %= size
            elif boundary_type == 'reflective':
                if nx < 0 or nx >= size or ny < 0 or ny >= size:
                    continue

            neighbors += grid[nx, ny]

    return neighbors


def update_grid(grid, boundary_type, virus=False, battle=False):
    """Update the grid based on Game of Life rules with optional virus and battle modes."""
    size = grid.shape[0]
    new_grid = np.zeros_like(grid)

    for x in range(size):
        for y in range(size):
            live_neighbors = count_neighbors(grid, x, y, boundary_type)

            if virus:
                if grid[x, y] == 1:
                    new_grid[x, y] = 1 if live_neighbors in [2, 3] else 0
                elif grid[x, y] == 2:
                    new_grid[x, y] = 0  # Infected cells die in the next step
                else:
                    if live_neighbors == 3:
                        new_grid[x, y] = 2 if np.random.rand() < 0.1 else 1  # 10% infection chance
            elif battle:
                if grid[x, y] == 1:
                    new_grid[x, y] = 1 if live_neighbors in [2, 3] else 0
                elif grid[x, y] == 2:
                    new_grid[x, y] = 2 if live_neighbors in [2, 3] else 0
                else:
                    faction = [0, 0, 0]
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            if dx == 0 and dy == 0:
                                continue
                            nx, ny = (x + dx) % size, (y + dy) % size
                            faction[grid[nx, ny]] += 1
                    new_grid[x, y] = np.argmax(faction)
            else:
                if grid[x, y] == 1:
                    new_grid[x, y] = 1 if live_neighbors in [2, 3] else 0
                else:
                    new_grid[x, y] = 1 if live_neighbors == 3 else 0

    return new_grid


def visualize_simulation(grid, steps, boundary_type, virus=False, battle=False, save_as_gif=True):
    """Visualize the simulation and save it as a GIF."""
    size = grid.shape[0]

    def update(frame):
        nonlocal grid
        im.set_array(grid)
        grid = update_grid(grid, boundary_type, virus, battle)
        return [im]

    fig, ax = plt.subplots()
    cmap = 'viridis' if battle else 'binary'
    im = ax.imshow(grid, cmap=cmap, interpolation='nearest')
    ax.set_xticks([])
    ax.set_yticks([])

    ani = animation.FuncAnimation(fig, update, frames=steps, interval=200, blit=True)

    if save_as_gif:
        gif_path = 'game_of_life_advanced.gif'
        ani.save(gif_path, writer='pillow')
        print(f"Animation saved as '{gif_path}'")
        return gif_path
    else:
        plt.show()
        return None


def display_gif(file_path):
    """Display the generated GIF using PyQt5."""
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("GIF Viewer")
    label = QLabel(window)
    label.setGeometry(10, 10, 640, 480)

    movie = QMovie(file_path)
    label.setMovie(movie)
    movie.start()

    window.setGeometry(100, 100, 640, 480)
    window.show()
    sys.exit(app.exec_())


def main():
    matplotlib.use('TkAgg')
    size = 200
    steps = 15
    pattern = input("Choose initial pattern (glider/glider_gun/oscillator/random/still): ").strip().lower()
    boundary_type = input("Choose boundary condition (periodic/reflective): ").strip().lower()
    mode = input("Choose mode (standard/virus/battle): ").strip().lower()

    if pattern not in ['glider', 'glider_gun', 'oscillator', 'random', 'still']:
        raise ValueError("Invalid pattern selected.")
    if boundary_type not in ['periodic', 'reflective']:
        raise ValueError("Invalid boundary condition selected.")
    if mode not in ['standard', 'virus', 'battle']:
        raise ValueError("Invalid mode selected.")

    virus = (mode == 'virus')
    battle = (mode == 'battle')

    grid = initialize_grid(size, pattern)
    gif_path = visualize_simulation(grid, steps, boundary_type, virus, battle, save_as_gif=True)

    if gif_path:
        display_gif(gif_path)


if __name__ == "__main__":
    main()
