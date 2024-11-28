import numpy as np
import matplotlib
from PIL import Image  # Do wczytywania mapy terenu
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import matplotlib.animation as animation


# 1. Generowanie mapy wysokości na podstawie zdjęcia satelitarnego
def generate_terrain_from_image(image_path, size):
    #Wczytywanie mapy wysokości na podstawie zdjęcia
    img = Image.open(image_path).convert('L')  # Konwersja na obraz w skali szarości
    img = img.resize(size)  # Zmiana rozmiaru obrazu na siatkę symulacji
    terrain = np.array(img) / 255 * 100  # Normalizacja wysokości do zakresu 0-100
    return terrain.astype(int)


# 2. Wyświetlanie mapy wysokości
def display_height_map(height_map, title="Mapa wysokości terenu"):
    #Wyświetlanie mapy wysokości terenu
    plt.imshow(height_map, cmap="terrain", interpolation='nearest')
    plt.title(title)
    plt.axis('off')
    plt.colorbar(label="Wysokość")
    plt.show()


# 3. Parametry symulacji
def initialize_params(grid_size, terrain_height):
    #Inicjalizacja parametrów symulacji
    return {
        'rain_intensity': 5,  # Intensywność opadów
        'terrain_height': terrain_height,  # Wysokość terenu
        'water_level': np.zeros(grid_size, dtype=float),  # Poziom wody
        'humidity': np.random.rand(*grid_size) * 100,  # Wilgotność w %
        'temperature': np.random.rand(*grid_size) * 30,  # Temperatura w stopniach
        'vegetation_density': np.random.rand(*grid_size),  # Gęstość roślinności
        'wind_direction': (1, 0),  # Kierunek wiatru (x, y)
        'barriers': np.zeros(grid_size, dtype=bool)  # Bariery
    }


# 4. Reguły przejść
def update_flood(grid, params):
    #Symulowanie rozprzestrzenianie się wody i ognia
    height = params['terrain_height']
    water_level = params['water_level']
    rain = params['rain_intensity']
    changes = 0

    # Dodanie "deszczu" do każdej komórki
    water_level += rain

    # Iteracja przez komórki
    for x in range(grid.shape[0]):
        for y in range(grid.shape[1]):
            if grid[x, y] == 'land' and water_level[x, y] > height[x, y]:
                grid[x, y] = 'flooded'
                changes += 1
            elif grid[x, y] == 'flooded':
                neighbors = [(x + dx, y + dy) for dx in [-1, 0, 1] for dy in [-1, 0, 1]
                             if 0 <= x + dx < grid.shape[0] and 0 <= y + dy < grid.shape[1]]
                for nx, ny in neighbors:
                    if grid[nx, ny] == 'land' and water_level[nx, ny] < water_level[x, y]:
                        water_level[nx, ny] += 0.1 * (water_level[x, y] - water_level[nx, ny])
                        changes += 1
            elif grid[x, y] == 'fire':
                # Rozprzestrzenianie ognia na sąsiadów
                neighbors = [(x + dx, y + dy) for dx in [-1, 0, 1] for dy in [-1, 0, 1]
                             if 0 <= x + dx < grid.shape[0] and 0 <= y + dy < grid.shape[1]]
                for nx, ny in neighbors:
                    if grid[nx, ny] == 'green_area' and params['humidity'][nx, ny] < 30:
                        grid[nx, ny] = 'fire'
                        changes += 1

    print(f"Liczba zmian w tym kroku: {changes}")
    return grid


# 5. Dodawanie bariery (tamy) w trakcie symulacji
def add_barrier(params, x, y, radius=3):
    #Dodanie tamy do symulacji
    for i in range(max(0, x - radius), min(params['terrain_height'].shape[0], x + radius + 1)):
        for j in range(max(0, y - radius), min(params['terrain_height'].shape[1], y + radius + 1)):
            params['barriers'][i, j] = True
            params['terrain_height'][i, j] += 50  # Podniesienie terenu w miejscu tamy


# 6. Gaszenie pożaru
def extinguish_fire(grid, params, x, y, radius=3):
    #Gaszenie pożaru w określonym obszarze
    for i in range(max(0, x - radius), min(grid.shape[0], x + radius + 1)):
        for j in range(max(0, y - radius), min(grid.shape[1], y + radius + 1)):
            if grid[i, j] == 'fire':
                grid[i, j] = 'land'
                params['humidity'][i, j] += 50  # Zwiększenie wilgotności


# 7. Animacja wyników
def animate_simulation(grid_states, interval=500, save_to_file=False):
    #Tworzenie animacji na żywo z kroków symulacji
    fig, ax = plt.subplots()
    color_map = {'land': 0, 'flooded': 1, 'green_area': 2, 'rock': 3, 'fire': 4}
    numeric_grid = np.vectorize(lambda x: color_map.get(x, 0))(grid_states[0])
    im = ax.imshow(numeric_grid, cmap="nipy_spectral", interpolation='nearest')

    def update(frame):
        numeric_grid = np.vectorize(lambda x: color_map.get(x, 0))(grid_states[frame])
        im.set_array(numeric_grid)
        ax.set_title(f"Krok {frame + 1}")
        return [im]

    ani = animation.FuncAnimation(fig, update, frames=len(grid_states), interval=interval, blit=True)

    if save_to_file:
        ani.save("simulation.mp4", fps=2, extra_args=['-vcodec', 'libx264'])
        print("Animacja zapisana jako 'simulation.mp4'.")
    else:
        plt.show()


# 8. Główna pętla symulacji
def run_simulation(image_path, grid_size=(50, 50), steps=20):
    #Uruchomienie symulacji
    terrain_height = generate_terrain_from_image(image_path, grid_size)
    grid = np.full(grid_size, 'land', dtype=object)
    params = initialize_params(grid_size, terrain_height)

    # Początkowe zalanie centralnej komórki
    grid[grid_size[0] // 2, grid_size[1] // 2] = 'flooded'
    params['water_level'][grid_size[0] // 2, grid_size[1] // 2] += 50

    # Dodanie zielonych obszarów i skał
    for x in range(grid_size[0]):
        for y in range(grid_size[1]):
            if terrain_height[x, y] > 70:
                grid[x, y] = 'rock'
            elif terrain_height[x, y] < 30:
                grid[x, y] = 'green_area'

    display_height_map(params['terrain_height'], title="Mapa wysokości terenu")
    grid_states = [grid.copy()]

    for step in range(steps):
        print(f"Krok {step + 1}: Symulacja działa.")
        if step == 5:
            add_barrier(params, x=20, y=20, radius=5)  # Dodanie tamy w kroku 5
        if step == 10:
            extinguish_fire(grid, params, x=30, y=30, radius=5)  # Gaszenie pożaru w kroku 10
        grid = update_flood(grid, params)
        grid_states.append(grid.copy())

    animate_simulation(grid_states, interval=500, save_to_file=False)


# 9. Uruchomienie symulacji
run_simulation("map_image.png")
