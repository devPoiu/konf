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
    return [[mat[i][j] for j in range(len(mat[i])) if j != k] for i in range(len(mat)) if i != m]

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

def format_matrix_html(matrix):
    return '\n'.join([' '.join([str(0 if round(num, 4) == 0.0 else round(num, 4)) for num in row]) for row in matrix])

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
Text(text="Масштаб:", position=(start_x, scale_start_y), color=color.black)

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

Button(text="ok", position=(start_x + step_x, start_y - 8.0 * step_y), scale=(0.2, 0.04), color=color.azure, on_click=ok_matrix)

ui_x, ui_y = -0.68, 0.45
left_step_x, left_step_y = 0.08, 0.045

label_op = Text(text="Операция (add, sub, mult, inv):", position=(ui_x, ui_y), color=color.black)
input_op = InputField(default_value="add", position=(ui_x + 0.10, ui_y - 0.04), scale=(0.20, 0.035))
label_A = Text(text="Матрица А:", position=(ui_x, ui_y - 0.09), color=color.black)
matrix_A_fields = []
for r in range(3):
    row_fields = []
    for c in range(3):
        val = "1.0" if r == c else "0.0"
        f = InputField(default_value=val, position=(ui_x + 0.04 + c * left_step_x, ui_y - 0.13 - r * left_step_y), scale=(0.075, 0.038))
        f.character_limit = 6
        row_fields.append(f)
    matrix_A_fields.append(row_fields)
label_B = Text(text="Матрица B:", position=(ui_x, ui_y - 0.28), color=color.black)
matrix_B_fields = []
for r in range(3):
    row_fields = []
    for c in range(3):
        val = "2.0" if r == c else "0.0"
        f = InputField(default_value=val, position=(ui_x + 0.04 + c * left_step_x, ui_y - 0.32 - r * left_step_y), scale=(0.075, 0.038))
        f.character_limit = 6
        row_fields.append(f)
    matrix_B_fields.append(row_fields)
result_title = Text(text="", position=(ui_x, ui_y - 0.48), color=color.dark_gray, scale=1.1)
result_output = Text(text="", position=(ui_x, ui_y - 0.53), color=color.black, scale=1.2)

def process_matrices():
    global local_i, local_j, local_k
    result_title.text, result_output.text = "", ""
    result_title.color = color.dark_gray
    current_operation = input_op.text.strip().lower()

    try:
        matrix_A = []
        for r in range(3):
            row = []
            for c in range(3):
                text_val = matrix_A_fields[r][c].text.strip()
                if not text_val: raise ValueError("Заполните все ячейки матрицы А!")
                row.append(float(text_val))
            matrix_A.append(row)

        result_matrix, title_text = None, ""

        if current_operation != 'inv':
            matrix_B = []
            for r in range(3):
                row = []
                for c in range(3):
                    text_val = matrix_B_fields[r][c].text.strip()
                    if not text_val: raise ValueError("Заполните все ячейки матрицы B!")
                    row.append(float(text_val))
                matrix_B.append(row)

            if current_operation in ('add', 'sub'):
                result_matrix = sum_matrices(matrix_A, matrix_B) if current_operation == 'add' else minis_matrices(matrix_A, matrix_B)
                title_text = f"Результат {'сложения' if current_operation == 'add' else 'вычитания'} (A {'+' if current_operation == 'add' else '-'} B):"
            elif current_operation == 'mult':
                result_matrix = mul_matrices(matrix_A, matrix_B)
                title_text = "Результат умножения (A * B):"
            else:
                raise ValueError("Неизвестная операция! Используйте: add, sub, mult, inv")
        else:
            result_matrix = inverse(matrix_A)
            title_text = f"Определитель A = {round(opred(matrix_A), 4)}"

        result_title.text = title_text
        result_output.text = format_matrix_html(result_matrix)

        local_i = Vec3(result_matrix[0][0], result_matrix[1][0], result_matrix[2][0])
        local_j = Vec3(result_matrix[0][1], result_matrix[1][1], result_matrix[2][1])
        local_k = Vec3(result_matrix[0][2], result_matrix[1][2], result_matrix[2][2])
        
        for r in range(3):
            for c in range(3):
                matrix_fields[r][c].text = f"{result_matrix[r][c]:.1f}"
        update_volume_geometry()

    except ValueError:
        result_title.color, result_title.text = color.red, "Ошибка ввода:"
        result_output.text = "Убедитесь, что все ячейки содержат числа!"
    except Exception as e:
        result_title.color, result_title.text, result_output.text = color.red, "Ошибка:", str(e)

Button(text="Вычислить", position=(ui_x + 0.075, ui_y - 0.72), scale=(0.15, 0.04), color=color.azure, on_click=process_matrices)

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
    if input_op.active: return True
    if any(f.active for row in matrix_A_fields for f in row): return True
    if any(f.active for row in matrix_B_fields for f in row): return True
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
    if key == 'scroll up': camera.z = min(-3, camera.z + 1.5)
    if key == 'scroll down': camera.z = max(-50, camera.z - 1.5)

def update():
    if input_op.text.strip().lower() == 'inv':
        label_B.enabled = False
        for row in matrix_B_fields:
            for f in row: f.enabled = False
    else:
        label_B.enabled = True
        for row in matrix_B_fields:
            for f in row: f.enabled = True

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
