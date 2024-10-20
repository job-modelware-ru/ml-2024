import random

import pybullet as p
import pybullet_data
import time

# Инициализация PyBullet
physicsClient = p.connect(p.GUI)
p.setAdditionalSearchPath(pybullet_data.getDataPath())

# Плоскость
p.loadURDF("plane.urdf")

# Установка гравитации
p.setGravity(0, 0, -9.8)


camera_target = [0, 0, 0]  # Позиция, на которую направлена камера
camera_eye = [0, -5, 2]  # Позиция камеры
camera_yaw = 45  # Угол поворота камеры по оси Z
camera_pitch = -30  # наклон камеры


# Функция для добавления статического куба
def add_static_cube(position, size=1):
    cube_id = p.loadURDF("cube.urdf", position, globalScaling=size)
    p.changeDynamics(cube_id, -1, mass=0)
    return cube_id


# Функция генерации случайного лабиринта
def generate_random_maze(width, height):
    maze = [[1] * width for _ in range(height)]

    # Начальная позиция
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

# Размеры куба и позиция в лабиринте
cube_size = 1
empty_positions = []
for i, row in enumerate(maze_layout):
    for j, cell in enumerate(row):
        if cell == 1:
            add_static_cube([-i * cube_size, j * cube_size, cube_size / 2], size=cube_size)
        else:
            empty_positions.append((i, j))

# Выбор случайной позиции для робота
start_i, start_j = random.choice(empty_positions)
startPos = [-start_i * cube_size, start_j * cube_size, 0.5]
startOrientation = p.getQuaternionFromEuler([0, 0, 0])

robotId = p.loadURDF("r2d2.urdf", startPos, startOrientation)

# Параметры симуляции
p.setRealTimeSimulation(1)

# Установка движения для R2D2
velocity = 10

# Индексы колес для движения вперед
wheel_joints = [2, 3, 6, 7]

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
    p.resetDebugVisualizerCamera(cameraDistance=5, cameraYaw=camera_yaw, cameraPitch=camera_pitch,
                                 cameraTargetPosition=camera_eye)

    # Информация о контактах между роботом и стенами
    contact_points = p.getContactPoints(robotId)

    if contact_points:
        # for joint in wheel_joints:
        #     p.setJointMotorControl2(robotId, joint, controlMode=p.VELOCITY_CONTROL, targetVelocity=0)
        # print("Робот столкнулся с преградой и остановился")
        # break
        pass
    else:
        for joint in wheel_joints:
            p.setJointMotorControl2(robotId, joint, controlMode=p.VELOCITY_CONTROL, targetVelocity=-velocity)

    # Задержка для синхронизации с реальным временем
    time.sleep(1 / 240)
