# pip install ursina
import math
from ursina import *

app = Ursina()
window.color = color.rgb(200, 200, 200)

def sum_matrices(mat1, mat2):
    return [[mat1[i][j] + mat2[i][j] for j in range(len(mat1[i]))] for i in range(len(mat1))]

def minis_matrices(mat1, mat2):
    return [[mat1[i][j] - mat2[i][j] for j in range(len(mat1[i]))] for i in range(len(mat1))]

def mul_matrices(mat1, mat2):
    rows1 = len(mat1)
    cols1 = len(mat1) if rows1 > 0 else 0
    cols2 = len(mat2) if len(mat2) > 0 else 0
    mat3 = [[0.0] * cols2 for _ in range(rows1)]

    for i in range(rows1):
        for j in range(cols2):
            s = 0
            for q in range(cols1):
                s += mat1[i][q] * mat2[q][j]
            mat3[i][j] = s
    return mat3

def rot_X(mat, ang):
    rad = math.radians(ang)
    matt = [
        [1, 0, 0],
        [0, math.cos(rad), math.sin(-rad)],
        [0, math.sin(rad), math.cos(rad)]
    ]
    return mul_matrices(mat, matt)

def opred(mat):
    n = len(mat)
    if n == 1:
        return mat
    if n == 2:
        return mat * mat - mat * mat
    
    det = 0
    for j in range(n):
        sub_mat = []
        for row in range(1, n):
            min_row = [mat[row][col] for col in range(n) if col != j]
            sub_mat.append(min_row)
        sign = (-1) ** j
        det += sign * mat[j] * opred(sub_mat)
    return det

def minor(mat, m, k):
    result = []
    for i, row in enumerate(mat):
        if i != m:
            result.append(row[:k] + row[k+1:])
    return result


def inverse(mat):
    det = opred(mat)
    if det == 0:
        raise ValueError("Обратная matrix не существует, так как определитель равен 0.")

    n = len(mat)
    if n == 1:
        return [[1 / mat]]

    mm = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            sub_mat = minor(mat, i, j)
            sign = (-1) ** (i + j)
            mm[j][i] = sign * opred(sub_mat)

    return [[mm[i][j] / det for j in range(n)] for i in range(n)]

def create_axis_lines(length=15, tick_size=0.1):
    Entity(model=Mesh(vertices=[(-length, 0, 0), (length, 0, 0)], mode='line'), color=color.red, thickness=3)
    Entity(model=Mesh(vertices=[(0, 0, -length), (0, 0, length)], mode='line'), color=color.blue, thickness=3)
    Entity(model=Mesh(vertices=[(0, -length, 0), (0, length, 0)], mode='line'), color=color.green, thickness=3)

    tolch = 0.0075
    for i in range(-length, length + 1):
        if i == 0: continue
        Entity(model='cube', position=(i, 0, 0), scale=(tolch, tolch, tick_size * 2), color=color.red)
        Entity(model='cube', position=(0, 0, i), scale=(tick_size * 2, tolch, tolch), color=color.blue)
        Entity(model='cube', position=(0, i, 0), scale=(tick_size * 2, tolch, tolch), color=color.green)

create_axis_lines()

cube = Entity(position=(0, 0, 0), scale=(1, 1, 1))

ploscost = Entity(
    parent=cube, model=Mesh(), color=color.rgba(1, 1, 1, 0.7),
    texture='white_cube', double_sided=True, transparency=True
)

rebra = Entity(parent=cube, model=Mesh(mode='line'), color=color.rgb(50, 50, 50), thickness=2)

vector_i = Entity(parent=cube, model='arrow', color=color.rgb(255, 0, 0), origin=(-0.5, 0, 0))
vector_j = Entity(parent=cube, model='arrow', color=color.rgb(0, 0, 255), origin=(-0.5, 0, 0))
vector_k = Entity(parent=cube, model='arrow', color=color.rgb(0, 255, 0), origin=(-0.5, 0, 0))

local_i = Vec3(1, 0, 0)
local_j = Vec3(0, 1, 0)
local_k = Vec3(0, 0, 1)

def to_ursina_coords(v):
    return Vec3(v.x, v.z, v.y)

def update_vectors():
    tolchina = 0.5
    dir_i = Vec3(local_i.x, -local_i.z, local_i.y)
    dir_j = Vec3(local_j.x, -local_j.z, local_j.y)
    dir_k = Vec3(local_k.x, -local_k.z, local_k.y)

    for arrow, direction, corrected_dir in zip([vector_i, vector_j, vector_k], [local_i, local_j, local_k], [dir_i, dir_j, dir_k]):
        length = direction.length()
        if length > 0.01:
            arrow.enabled = True
            arrow.position = (0, 0, 0)
            dir_norm = corrected_dir / length
            yaw = math.degrees(math.atan2(dir_norm.z, dir_norm.x))
            pitch = math.degrees(math.atan2(dir_norm.y, math.sqrt(dir_norm.x ** 2 + dir_norm.z ** 2)))
            arrow.rotation = Vec3(0, -yaw, pitch)
            arrow.scale = Vec3(length, tolchina, tolchina)
        else:
            arrow.enabled = False

def update_volume_geometry():
    v0 = to_ursina_coords(Vec3(0, 0, 0))
    v1 = to_ursina_coords(local_k)
    v2 = to_ursina_coords(local_j)
    v3 = to_ursina_coords(local_j + local_k)
    v4 = to_ursina_coords(local_i)
    v5 = to_ursina_coords(local_i + local_k)
    v6 = to_ursina_coords(local_i + local_j)
    v7 = to_ursina_coords(local_i + local_j + local_k)

    ploscost.model.vertices = [
        v0, v4, v6, v2, v1, v3, v7, v5,
        v0, v1, v5, v4, v2, v6, v7, v3,
        v0, v2, v3, v1, v4, v5, v7, v6
    ]
    ploscost.model.triangles = [
        0, 1, 2, 0, 2, 3, 4, 5, 6, 4, 6, 7,
        8, 9, 10, 8, 10, 11, 12, 13, 14, 12, 14, 15,
        16, 17, 18, 16, 18, 19, 20, 21, 22, 20, 22, 23
    ]
    ploscost.model.uvs = [(0, 0), (1, 0), (1, 1), (0, 1)] * 6
    ploscost.model.generate()

    rebra.model.vertices = [
        v0, v4, v4, v6, v6, v2, v2, v0,
        v1, v5, v5, v7, v7, v3, v3, v1,
        v0, v1, v4, v5, v6, v7, v2, v3
    ]
    rebra.model.generate()
    update_vectors()

matrix_fields = []
start_x, start_y = 0.50, 0.40
step_x, step_y = 0.11, 0.06

default_matrix = [["1.0", "0.0", "0.0"], ["0.0", "1.0", "0.0"], ["0.0", "0.0", "1.0"]]
default_scale = [["1.0", "0.0", "0.0"], ["0.0", "1.0", "0.0"], ["0.0", "0.0", "1.0"]]

names = ["i", "j", "k"]
for c in range(3):
    Text(text=names[c], position=(start_x + c * step_x, start_y), color=color.black)

for r in range(3):
    row_fields = []
    for c in range(3):
        f = InputField(default_value=default_matrix[r][c], position=(start_x + c * step_x, start_y - (r + 1) * step_y), scale=(0.1, 0.04))
        f.character_limit = 6
        row_fields.append(f)
    matrix_fields.append(row_fields)

scale_fields = []
scale_start_y = start_y - 4.2 * step_y
Text(text="Масштаб:", position=(start_x - 0.05, scale_start_y), color=color.black)

for r in range(3):
    row_fields = []
    for c in range(3):
        f = InputField(default_value=default_scale[r][c], position=(start_x + c * step_x, scale_start_y - (r + 1) * step_y), scale=(0.1, 0.04))
        f.character_limit = 6
        row_fields.append(f)
    scale_fields.append(row_fields)

def get_scale_matrix():
    try:
        return [
            [float(scale_fields[0][0].text), float(scale_fields[0][1].text), float(scale_fields[0][2].text)],
            [float(scale_fields[1][0].text), float(scale_fields[1][1].text), float(scale_fields[1][2].text)],
            [float(scale_fields[2][0].text), float(scale_fields[2][1].text), float(scale_fields[2][2].text)]
        ]
    except (ValueError, IndexError):
        return [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]

def apply_scale_to_vector(v, S):
    return Vec3(
        S[0][0]*v.x + S[0][1]*v.y + S[0][2]*v.z,
        S[1][0]*v.x + S[1][1]*v.y + S[1][2]*v.z,
        S[2][0]*v.x + S[2][1]*v.y + S[2][2]*v.z
    )

def ok_matrix():
    global local_i, local_j, local_k
    try:
        local_i = Vec3(float(matrix_fields[0][0].text), float(matrix_fields[1][0].text), float(matrix_fields[2][0].text))
        local_j = Vec3(float(matrix_fields[0][1].text), float(matrix_fields[1][1].text), float(matrix_fields[2][1].text))
        local_k = Vec3(float(matrix_fields[0][2].text), float(matrix_fields[1][2].text), float(matrix_fields[2][2].text))
        S = get_scale_matrix()
        local_i = apply_scale_to_vector(local_i, S)
        local_j = apply_scale_to_vector(local_j, S)
        local_k = apply_scale_to_vector(local_k, S)
        update_volume_geometry()
    except (ValueError, IndexError):
        pass

Button(text="ok", position=(start_x + step_x + 0.065, scale_start_y - 0.01), scale=(0.19, 0.04), color=color.azure, on_click=ok_matrix)

rot_start_x = start_x + 3.5 * step_x
rot_start_y = start_y 

Text(text="Поворот вокруг оси:", position=(rot_start_x, rot_start_y), color=color.black)

rot_labels = ["X:", "Y:", "Z:"]
rot_fields = []

for r in range(3):
    Text(text=rot_labels[r], position=(rot_start_x, rot_start_y - (r + 1) * step_y + 0.01), color=color.black)
    f = InputField(default_value="0.0", position=(rot_start_x + 0.08, rot_start_y - (r + 1) * step_y), scale=(0.1, 0.04))
    f.character_limit = 6
    rot_fields.append(f)

def apply_rotations():
    global local_i, local_j, local_k
    try:
        ang_x = float(rot_fields[0].text)
        ang_y = float(rot_fields[1].text)
        ang_z = float(rot_fields[2].text)
    except ValueError:
        return

    rad_x = math.radians(ang_x)
    cx, sx = math.cos(rad_x), math.sin(rad_x)
    rot_x = [
        [1.0, 0.0, 0.0],
        [0.0, cx, -sx],
        [0.0, sx, cx]
    ]

    rad_y = math.radians(ang_y)
    cy, sy = math.cos(rad_y), math.sin(rad_y)
    rot_y = [
        [cy, 0.0, sy],
        [0.0, 1.0, 0.0],
        [-sy, 0.0, cy]
    ]

    rad_z = math.radians(ang_z)
    cz, sz = math.cos(rad_z), math.sin(rad_z)
    rot_z = [
        [cz, -sz, 0.0],
        [sz, cz, 0.0],
        [0.0, 0.0, 1.0]
    ]

    rot_total = mul_matrices(mul_matrices(rot_x, rot_y), rot_z)

    current_mat = [
        [local_i.x, local_j.x, local_k.x],
        [local_i.y, local_j.y, local_k.y],
        [local_i.z, local_j.z, local_k.z]
    ]

    new_mat = mul_matrices(current_mat, rot_total)

    local_i = Vec3(new_mat[0][0], new_mat[1][0], new_mat[2][0])
    local_j = Vec3(new_mat[0][1], new_mat[1][1], new_mat[2][1])
    local_k = Vec3(new_mat[0][2], new_mat[1][2], new_mat[2][2])

    matrix_fields[0][0].text = f"{local_i.x:.2f}"
    matrix_fields[1][0].text = f"{local_i.y:.2f}"
    matrix_fields[2][0].text = f"{local_i.z:.2f}"

    matrix_fields[0][1].text = f"{local_j.x:.2f}"
    matrix_fields[1][1].text = f"{local_j.y:.2f}"
    matrix_fields[2][1].text = f"{local_j.z:.2f}"

    matrix_fields[0][2].text = f"{local_k.x:.2f}"
    matrix_fields[1][2].text = f"{local_k.y:.2f}"
    matrix_fields[2][2].text = f"{local_k.z:.2f}"

    update_volume_geometry()

    for f in rot_fields:
        f.text = "0.0"

Button(text="ok", position=(rot_start_x + 0.2 , rot_start_y - 0.12), scale=(0.08, 0.04), color=color.orange, on_click=apply_rotations)

def reset_cube():
    global local_i, local_j, local_k
    cube.rotation, cube.position = (0, 0, 0), (0, 0, 0)
    local_i, local_j, local_k = Vec3(1, 0, 0), Vec3(0, 1, 0), Vec3(0, 0, 1)
    update_volume_geometry()
    for r in range(3):
        for c in range(3):
            matrix_fields[r][c].text = default_matrix[r][c]
            scale_fields[r][c].text = default_scale[r][c]

def field_active():
    if any(f.active for row in matrix_fields for f in row): return True
    if any(f.active for row in scale_fields for f in row): return True
    return False

def input(key):
    print(key)
    if field_active():
        if key == 'enter':
            ok_matrix()
            for row in matrix_fields:
                for f in row:
                    f.active = False
        return
    if key == 'j': cube.x += 1 
    if key == 'g': cube.x -= 1 
    if key == 'y': cube.z += 1
    if key == 'h': cube.z -= 1
    if key == 'u': cube.y += 1
    if key == 't': cube.y -= 1
    if key == 'r': reset_cube()
    if key == 'v': reset_camera()
    if key == 'enter': ok_matrix()
    if key == 'escape up': application.quit()
    if key == 'scroll up': camera.z = min(-3, camera.z + 1.5)
    if key == 'scroll down': camera.z = max(-50, camera.z - 1.5)

def update():
    rot_speed = 120
    is_rotating = any(held_keys[k] for k in ['q', 'e', ';', 'k', 'o', 'l'])

    if not field_active():
        if held_keys['q']: cube.rotation_z -= time.dt * rot_speed
        if held_keys['e']: cube.rotation_z += time.dt * rot_speed
        if held_keys[';']: cube.rotation_y += time.dt * rot_speed
        if held_keys['k']: cube.rotation_y -= time.dt * rot_speed
        if held_keys['o']: cube.rotation_x -= time.dt * rot_speed
        if held_keys['l']: cube.rotation_x += time.dt * rot_speed

    if is_rotating and not field_active():
        i_world = cube.right * local_i.x + cube.forward * local_i.y + cube.up * local_i.z
        j_world = cube.right * local_j.x + cube.forward * local_j.y + cube.up * local_j.z
        k_world = cube.right * local_k.x + cube.forward * local_k.y + cube.up * local_k.z

        matrix_values = [
            [i_world.x, j_world.x, k_world.x],
            [i_world.y, j_world.y, k_world.y],
            [i_world.z, j_world.z, k_world.z]
        ]
        for r in range(3):
            for c in range(3):
                matrix_fields[r][c].text = f"{matrix_values[r][c]:.1f}"

    update_vectors()
    update_camera()

update_volume_geometry()

def update_camera():
    camera_hinge.position = cube.position
    
    if mouse.right:
        camera_hinge.rotation_y += mouse.velocity[0] * 400
        camera_tilt.rotation_x -= mouse.velocity[1] * 400
        camera_tilt.rotation_x = clamp(camera_tilt.rotation_x, -80, 80)

camera_hinge = Entity(position=cube.position, rotation_y=-30)
camera_tilt = Entity(parent=camera_hinge, rotation_x=35)

camera.parent = camera_tilt
camera.position = (0, 0, -20)
camera.look_at(cube)

def reset_camera():
    camera_hinge.position = cube.position
    camera_hinge.rotation_y = -30
    camera_hinge.rotation_z = 0
    camera_tilt.rotation_x = 35
    camera_tilt.rotation_y = 0
    camera_tilt.rotation_z = 0
    camera.position = (0, 0, -20)
    camera.look_at(cube)

reset_camera()

app.run()
