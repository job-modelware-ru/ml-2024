import pybullet as p
import pybullet_data
import time

physicsClient = p.connect(p.GUI)
p.setAdditionalSearchPath(pybullet_data.getDataPath())

# Плоскость
p.loadURDF("plane.urdf")

# Гравитация
p.setGravity(0, 0, -9.8)

# Загрузка робота R2D2
startPos = [0, 0, 0.5]
startOrientation = p.getQuaternionFromEuler([0, 0, 0])
robotId = p.loadURDF("r2d2.urdf", startPos, startOrientation)

# Статическая преграда
wallPosition = [0, 2.5, 0.5]
wallOrientation = p.getQuaternionFromEuler([0, 0, 0])
wallId = p.loadURDF("cube.urdf", wallPosition, wallOrientation, globalScaling=2)

p.changeDynamics(wallId, -1, mass=0)

# Параметры симуляции
p.setRealTimeSimulation(1)

# Установка движения для R2D2
velocity = 10

# Индексы колес для движения вперед
wheel_joints = [2, 3, 6, 7]

while True:
    # Информация о контактах между роботом и стеной
    contact_points = p.getContactPoints(robotId, wallId)

    if contact_points:
        for joint in wheel_joints:
            p.setJointMotorControl2(robotId, joint, controlMode=p.VELOCITY_CONTROL, targetVelocity=0)
        print("Робот столкнулся с преградой и остановился")
        break
    else:
        for joint in wheel_joints:
            p.setJointMotorControl2(robotId, joint, controlMode=p.VELOCITY_CONTROL, targetVelocity=-velocity)

    # Задержка для синхронизации с реальным временем
    time.sleep(1 / 240)


# p.connect(p.GUI)
# p.setAdditionalSearchPath(pybullet_data.getDataPath())
# robotId = p.loadURDF("r2d2.urdf")
#
# # Получаем количество суставов робота и их информацию
# num_joints = p.getNumJoints(robotId)
# for joint_index in range(num_joints):
#     joint_info = p.getJointInfo(robotId, joint_index)
#     print(f"Joint {joint_index}: {joint_info}")
