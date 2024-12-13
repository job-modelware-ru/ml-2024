import random
import numpy as np
import pybullet as p
import pybullet_data
import time

# Инициализация PyBullet
physicsClient = p.connect(p.GUI)
p.setAdditionalSearchPath(pybullet_data.getDataPath())

# Плоскость
plane_id = p.loadURDF("plane.urdf")
texture_id = p.loadTexture("floor.jpg")
p.changeVisualShape(plane_id, -1, textureUniqueId=texture_id)

# Установка гравитации
p.setGravity(0, 0, -9.8)

camera_target = [0, 0, 0]  # Позиция, на которую направлена камера
camera_eye = [-6, 6, 5]  # Позиция камеры
camera_yaw = 45  # Угол поворота камеры по оси Z
camera_pitch = -80  # наклон камеры


# Функция для добавления статического куба
def add_static_cube(position, size=1):
    cube_id = p.loadURDF("cube.urdf", position, globalScaling=size)
    p.changeDynamics(cube_id, -1, mass=0)
    return cube_id


# Функция генерации случайного лабиринта
def generate_random_maze(width, height):
    maze = [[1] * width for _ in range(height)]

    start_x, start_y = 1, 1
    maze[start_y][start_x] = 0
    walls = [(start_x, start_y)]

    while walls:
        x, y = walls.pop(random.randint(0, len(walls) - 1))

        neighbors = []
        if x > 1 and maze[y][x - 2] == 1:  # Запад
            neighbors.append((x - 2, y))
        if x < width - 2 and maze[y][x + 2] == 1:  # Восток
            neighbors.append((x + 2, y))
        if y > 1 and maze[y - 2][x] == 1:  # Север
            neighbors.append((x, y - 2))
        if y < height - 2 and maze[y + 2][x] == 1:  # Юг
            neighbors.append((x, y + 2))

        if neighbors:
            walls.append((x, y))
            new_x, new_y = random.choice(neighbors)

            # Убираем стену между текущей позицией и новой
            maze[(y + new_y) // 2][(x + new_x) // 2] = 0
            maze[new_y][new_x] = 0
            walls.append((new_x, new_y))

    return maze


maze_width = 15
maze_height = 15
maze_layout = generate_random_maze(maze_width, maze_height)

# Вывод лабиринта с координатами
cell_width = len(str(maze_width)) + 2

print(" " * (cell_width + 2) + "".join(str(col).rjust(cell_width) for col in range(len(maze_layout[0]))))

print(" " * (cell_width + 3) + "-" * (len(maze_layout[0]) * cell_width))

for i, row in enumerate(maze_layout):
    print(str(i).rjust(cell_width) + " |" + "".join(str(cell).rjust(cell_width) for cell in row))

p.resetDebugVisualizerCamera(cameraDistance=5, cameraYaw=camera_yaw, cameraPitch=camera_pitch,
                             cameraTargetPosition=camera_eye)

# Размеры куба и позиция в лабиринте
cube_size = 1
empty_positions = []
for i, row in enumerate(maze_layout):
    for j, cell in enumerate(row):
        if cell == 1:
            add_static_cube([-i * cube_size, j * cube_size, cube_size / 2], size=cube_size)
        else:
            empty_positions.append((i, j))


# Функция выбора целевой точки
def select_goal():
    print("Выберите способ установки целевой точки:")
    print("1. Случайно")
    print("2. Ввести координаты вручную")
    choice = input("Введите 1 или 2:")

    if choice == "1":
        return random.choice(empty_positions)
    elif choice == "2":
        while True:
            try:
                x = int(input(f"Введите x-координату (0-{maze_width - 1}): "))
                y = int(input(f"Введите y-координату (0-{maze_height - 1}): "))
                if (x, y) in empty_positions:
                    return x, y
                else:
                    print("Ошибка: Координаты не принадлежат доступным позициям. Попробуйте снова.")
            except ValueError:
                print("Ошибка: Введите целые числа для координат. Попробуйте снова.")
    else:
        print("Некорректный выбор. Устанавливается случайная целевая точка.")
        return random.choice(empty_positions)


# Выбор позиции для робота и цели
start_i, start_j = random.choice(empty_positions)
print(f"Позиция робота (x, y) = ({start_i}, {start_j})")
goal_i, goal_j = select_goal()
startPos = [-start_i * cube_size, start_j * cube_size, 0.5]
goalPos = [-goal_i * cube_size, goal_j * cube_size, 0.5]
startOrientation = p.getQuaternionFromEuler([0, 0, 0])

sphere_radius = 0.5
sphereId = p.createCollisionShape(p.GEOM_SPHERE, radius=sphere_radius)
sphere_visual = p.createVisualShape(p.GEOM_SPHERE, radius=sphere_radius, rgbaColor=[0, 255, 255, 1])
robotId = p.createMultiBody(baseMass=1, baseCollisionShapeIndex=sphereId, baseVisualShapeIndex=sphere_visual,
                            basePosition=startPos)

# Параметры Q-learning
actions = [(0, cube_size), (0, -cube_size), (cube_size, 0), (-cube_size, 0)]
Q_table = np.zeros((maze_width, maze_height, len(actions)))
alpha = 0.1
gamma = 0.9
epsilon = 0.2


def get_state(robot_pos):
    x, y, _ = robot_pos
    i, j = -int(x // cube_size), int(y // cube_size)
    return max(0, min(i, maze_width - 1)), max(0, min(j, maze_height - 1))


# Целевая позиция
target_position = [goalPos[0], goalPos[1], 0.5]
target_id = add_static_cube(target_position, size=0.5)
successful_trajectories = []

visited_states = set()
iterations = 500
episode = 0
while episode <= iterations:
    done = False
    robot_pos = startPos
    state = get_state(robot_pos)
    trajectory = [robot_pos]
    visited_states.clear()
    visited_count = 0  # Счетчик отслеживания повторных посещений

    while not done:
        if random.uniform(0, 1) < epsilon:
            action_index = random.choice(range(len(actions)))
        else:
            action_index = np.argmax(Q_table[state[0], state[1]])

        dx, dy = actions[action_index]
        new_pos = [robot_pos[0] + dx, robot_pos[1] + dy, robot_pos[2]]
        new_state = get_state(new_pos)

        if (maze_width > new_state[0] >= 0 == maze_layout[new_state[0]][new_state[1]]
                and 0 <= new_state[1] < maze_height):  # Внутри лабиринта

            if new_state in visited_states:
                reward = -0.5  # Штраф за повторное посещение
                visited_count += 1
            else:
                reward = 0.1  # Обычная награда за движение
                visited_states.add(new_state)
                visited_count = 0  # Сброс счётчика

            robot_pos = new_pos
            # Достижение целевой точки
            if new_state == (goal_i, goal_j):
                reward = 10
                trajectory.append(robot_pos)
                successful_trajectories.append(trajectory)
                break
        else:
            reward = -10  # Штраф за столкновение со стеной
            done = True

        # Обновление Q-таблицы
        best_next_action = np.max(Q_table[new_state[0], new_state[1]])
        Q_table[state[0], state[1], action_index] += alpha * (
                reward + gamma * best_next_action - Q_table[state[0], state[1], action_index]
        )

        trajectory.append(robot_pos)
        state = new_state

        # Прерывание эпизода из-за циклических действий
        if visited_count >= 5:
            print("Прерывание из-за цикла")
            done = True

    if epsilon > 0.01:
        epsilon *= 0.995
    episode += 1
    if episode == iterations and not successful_trajectories:
        iterations += 1

# Параметры симуляции
p.setRealTimeSimulation(1)
if successful_trajectories:
    print("Есть траектория")
while True:
    # Управление камерой
    keys = p.getKeyboardEvents()
    if p.B3G_UP_ARROW in keys:
        camera_eye[1] += 0.1
    if p.B3G_DOWN_ARROW in keys:
        camera_eye[1] -= 0.1
    if p.B3G_LEFT_ARROW in keys:
        camera_eye[0] -= 0.1
    if p.B3G_RIGHT_ARROW in keys:
        camera_eye[0] += 0.1
    if p.B3G_SPACE in keys:
        camera_eye[2] += 0.1
    if p.B3G_CONTROL in keys:
        camera_eye[2] -= 0.1
    if p.B3G_PAGE_UP in keys:
        camera_pitch += 0.1
    if p.B3G_PAGE_DOWN in keys:
        camera_pitch -= 0.1
    if p.B3G_END in keys:
        break
    p.resetDebugVisualizerCamera(cameraDistance=5, cameraYaw=camera_yaw, cameraPitch=camera_pitch,
                                 cameraTargetPosition=camera_eye)

    time.sleep(1 / 240)

# Отрисовка итоговой траектории
p.changeDynamics(robotId, -1, mass=0)  # Не учитываем физику робота для правильной отрисовки
if successful_trajectories:
    best_trajectory = min(successful_trajectories, key=len)  # Находим кратчайшую траекторию
    for pos in best_trajectory:
        p.resetBasePositionAndOrientation(robotId, pos, p.getQuaternionFromEuler([0, 0, 0]))
        time.sleep(1 / 5)
