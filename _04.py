# pip install ursina


import math
from ursina import *

app = Ursina()

window.color = color.rgb(200, 200, 200)

def create_axis_lines(length=15, tick_size=0.1):
    Entity(model=Mesh(vertices=[(-length, 0, 0), (length, 0, 0)], mode='line'), color=color.red, thickness=3)
    Entity(model=Mesh(vertices=[(0, 0, -length), (0, 0, length)], mode='line'), color=color.blue, thickness=3)
    Entity(model=Mesh(vertices=[(0, -length, 0), (0, length, 0)], mode='line'), color=color.green, thickness=3)

    tolch = 0.0075
    for i in range(-length, length + 1):
        if i == 0: continue
        Entity(model='cube', position=(i, 0, 0), scale=(tolch, tick_size * 2, tolch), color=color.red)
        Entity(model='cube', position=(0, 0, i), scale=(tick_size * 2, tolch, tolch), color=color.blue)
        Entity(model='cube', position=(0, i, 0), scale=(tick_size * 2, tolch, tolch), color=color.green)

create_axis_lines()

cube = Entity(
    position=(0, 0, 0),
    scale=(1, 1, 1)
)

ploscost = Entity(
    parent=cube,
    model=Mesh(),
    color=color.rgba(1, 1, 1, 0.7),
    texture='white_cube',
    double_sided=True, 
    transparency=True
)

rebra = Entity(
    parent=cube,
    model=Mesh(mode='line'),
    color=color.rgb(50, 50, 50),
    thickness=2,
)

vector_i = Entity(parent=cube, model='arrow', color=color.rgb(255, 0, 0), origin=(-0.5, 0, 0))
vector_j = Entity(parent=cube, model='arrow', color=color.rgb(0, 0, 255), origin=(-0.5, 0, 0))
vector_k = Entity(parent=cube, model='arrow', color=color.rgb(0, 255, 0), origin=(-0.5, 0, 0))

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
            pitch = math.degrees(math.atan2(dir_norm.y, math.sqrt(dir_norm.x**2 + dir_norm.z**2)))
            
            arrow.rotation = Vec3(0, -yaw, pitch)
            arrow.scale = Vec3(length, tolchina, tolchina)
        else:
            arrow.enabled = False

matrix_fields = []
start_x, start_y = 0.50, 0.40
step_x, step_y = 0.11, 0.06

default_matrix = [
    ["1.0", "0.0", "0.0"],
    ["0.0", "1.0", "0.0"],
    ["0.0", "0.0", "1.0"]
]

names = ["i", "j", "k"]
for c in range(3):
    Text(text=names[c], position=(start_x + c * step_x, start_y), color=color.black)

for r in range(3):
    row_fields = []
    for c in range(3):
        f = InputField(
            default_value=default_matrix[r][c], 
            position=(start_x + c * step_x, start_y - (r + 1) * step_y), 
            scale=(0.1, 0.04)
        )
        f.character_limit = 6
        row_fields.append(f)
    matrix_fields.append(row_fields)

local_i = Vec3(1, 0, 0)
local_j = Vec3(0, 1, 0)
local_k = Vec3(0, 0, 1)

def to_ursina_coords(v):
    return Vec3(v.x, v.z, v.y)

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
        v0, v4, v6, v2,
        v1, v3, v7, v5,
        v0, v1, v5, v4,
        v2, v6, v7, v3,
        v0, v2, v3, v1,
        v4, v5, v7, v6
    ]

    ploscost.model.triangles = [
        0,  1,  2,    0,  2,  3,
        4,  5,  6,    4,  6,  7,
        8,  9,  10,   8,  10, 11,
        12, 13, 14,   12, 14, 15,
        16, 17, 18,   16, 18, 19,
        20, 21, 22,   20, 22, 23
    ]
    
    ploscost.model.uvs = [(0,0), (1,0), (1,1), (0,1)] * 6
    ploscost.model.generate()

    rebra.model.vertices = [
        v0, v4,  v4, v6,  v6, v2,  v2, v0,
        v1, v5,  v5, v7,  v7, v3,  v3, v1,
        v0, v1,  v4, v5,  v6, v7,  v2, v3
    ]
    rebra.model.generate()
    
    update_vectors()

def ok_matrix():
    global local_i, local_j, local_k
    local_i = Vec3(
        float(matrix_fields[0][0].text), 
        float(matrix_fields[1][0].text), 
        float(matrix_fields[2][0].text)
    )
    local_j = Vec3(
        float(matrix_fields[0][1].text), 
        float(matrix_fields[1][1].text), 
        float(matrix_fields[2][1].text)
    )
    local_k = Vec3(
        float(matrix_fields[0][2].text), 
        float(matrix_fields[1][2].text), 
        float(matrix_fields[2][2].text)
    )
    update_volume_geometry()
    

apply_btn = Button(
    text="ok", 
    position=(start_x + step_x, start_y - 4.5 * step_y), 
    scale=(0.2, 0.04), 
    color=color.azure,
    on_click=ok_matrix
)

def field_active():
    for row in matrix_fields:
        for f in row:
            if f.active: return True
    return False

def update():
    rot_speed = 120
    is_rotating = any(held_keys[k] for k in ['q', 'e', ';', 'k', 'o', 'l'])

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


def reset_cube():
    global local_i, local_j, local_k
    cube.rotation = (0, 0, 0)
    cube.position = (0, 0, 0)
    local_i, local_j, local_k = Vec3(1,0,0), Vec3(0,1,0), Vec3(0,0,1)
    update_volume_geometry()

    for r in range(3):
        for c in range(3):
            matrix_fields[r][c].text = default_matrix[r][c]

def reset_camera():
    cam.position = (5, 5, -10)
    cam.rotation = (25, -25, 0)


def input(key):
    if field_active(): return
    if key == 'j': cube.x += 1 
    if key == 'g': cube.x -= 1 
    if key == 'y': cube.z += 1
    if key == 'h': cube.z -= 1
    if key == 'u': cube.y += 1
    if key == 't': cube.y -= 1
    if key == 'r': reset_cube()
    if key == 'v': reset_camera()

ok_matrix()

cam = EditorCamera()
cam.position = (5, 5, -10)
cam.rotation = (25, -25, 0)

app.run()
