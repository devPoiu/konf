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

target_i = Vec3(1, 0, 0)
target_j = Vec3(0, 1, 0)
target_k = Vec3(0, 0, 1)

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
    # =====================================тут===================================================
    return Vec3(
        S[0][0]*v.x + S[0][1]*v.y + S[0][2]*v.z,
        S[1][0]*v.x + S[1][1]*v.y + S[1][2]*v.z,
        S[2][0]*v.x + S[2][1]*v.y + S[2][2]*v.z
    )

def ok_matrix():
    global target_i, target_j, target_k
    try:
        t_i = Vec3(float(matrix_fields[0][0].text), float(matrix_fields[1][0].text), float(matrix_fields[2][0].text))
        t_j = Vec3(float(matrix_fields[0][1].text), float(matrix_fields[1][1].text), float(matrix_fields[2][1].text))
        t_k = Vec3(float(matrix_fields[0][2].text), float(matrix_fields[1][2].text), float(matrix_fields[2][2].text))
        S = get_scale_matrix()
    # =====================================тут===================================================
    # https://www.google.com/search?q=%23+pip+install+ursina%0Aimport+math%0Afrom+ursina+import+*%0A%0Aapp+%3D+Ursina%28%29%0Awindow.color+%3D+color.rgb%28200%2C+200%2C+200%29%0A%0Adef+sum_matrices%28mat1%2C+mat2%29%3A%0A++++return+%5B%5Bmat1%5Bi%5D%5Bj%5D+%2B+mat2%5Bi%5D%5Bj%5D+for+j+in+range%28len%28mat1%5Bi%5D%29%29%5D+for+i+in+range%28len%28mat1%29%29%5D%0A%0Adef+minis_matrices%28mat1%2C+mat2%29%3A%0A++++return+%5B%5Bmat1%5Bi%5D%5Bj%5D+-+mat2%5Bi%5D%5Bj%5D+for+j+in+range%28len%28mat1%5Bi%5D%29%29%5D+for+i+in+range%28len%28mat1%29%29%5D%0A%0Adef+mul_matrices%28mat1%2C+mat2%29%3A%0A++++rows1+%3D+len%28mat1%29%0A++++cols1+%3D+len%28mat1%29+if+rows1+%3E+0+else+0%0A++++cols2+%3D+len%28mat2%29+if+len%28mat2%29+%3E+0+else+0%0A++++mat3+%3D+%5B%5B0.0%5D+*+cols2+for+_+in+range%28rows1%29%5D%0A%0A++++for+i+in+range%28rows1%29%3A%0A++++++++for+j+in+range%28cols2%29%3A%0A++++++++++++s+%3D+0%0A++++++++++++for+q+in+range%28cols1%29%3A%0A++++++++++++++++s+%2B%3D+mat1%5Bi%5D%5Bq%5D+*+mat2%5Bq%5D%5Bj%5D%0A++++++++++++mat3%5Bi%5D%5Bj%5D+%3D+s%0A++++return+mat3%0A%0Adef+rot_X%28mat%2C+ang%29%3A%0A++++rad+%3D+math.radians%28ang%29%0A++++matt+%3D+%5B%0A++++++++%5B1%2C+0%2C+0%5D%2C%0A++++++++%5B0%2C+math.cos%28rad%29%2C+math.sin%28-rad%29%5D%2C%0A++++++++%5B0%2C+math.sin%28rad%29%2C+math.cos%28rad%29%5D%0A++++%5D%0A++++return+mul_matrices%28mat%2C+matt%29%0A%0Adef+opred%28mat%29%3A%0A++++n+%3D+len%28mat%29%0A++++if+n+%3D%3D+1%3A%0A++++++++return+mat%0A++++if+n+%3D%3D+2%3A%0A++++++++return+mat+*+mat+-+mat+*+mat%0A++++%0A++++det+%3D+0%0A++++for+j+in+range%28n%29%3A%0A++++++++sub_mat+%3D+%5B%5D%0A++++++++for+row+in+range%281%2C+n%29%3A%0A++++++++++++min_row+%3D+%5Bmat%5Brow%5D%5Bcol%5D+for+col+in+range%28n%29+if+col+%21%3D+j%5D%0A++++++++++++sub_mat.append%28min_row%29%0A++++++++sign+%3D+%28-1%29+**+j%0A++++++++det+%2B%3D+sign+*+mat%5Bj%5D+*+opred%28sub_mat%29%0A++++return+det%0A%0Adef+minor%28mat%2C+m%2C+k%29%3A%0A++++result+%3D+%5B%5D%0A++++for+i%2C+row+in+enumerate%28mat%29%3A%0A++++++++if+i+%21%3D+m%3A%0A++++++++++++result.append%28row%5B%3Ak%5D+%2B+row%5Bk%2B1%3A%5D%29%0A++++return+result%0A%0A%0Adef+inverse%28mat%29%3A%0A++++det+%3D+opred%28mat%29%0A++++if+det+%3D%3D+0%3A%0A++++++++raise+ValueError%28%22Обратная+matrix+не+существует%2C+так+как+определитель+равен+0.%22%29%0A%0A++++n+%3D+len%28mat%29%0A++++if+n+%3D%3D+1%3A%0A++++++++return+%5B%5B1+%2F+mat%5D%5D%0A%0A++++mm+%3D+%5B%5B0.0%5D+*+n+for+_+in+range%28n%29%5D%0A++++for+i+in+range%28n%29%3A%0A++++++++for+j+in+range%28n%29%3A%0A++++++++++++sub_mat+%3D+minor%28mat%2C+i%2C+j%29%0A++++++++++++sign+%3D+%28-1%29+**+%28i+%2B+j%29%0A++++++++++++mm%5Bj%5D%5Bi%5D+%3D+sign+*+opred%28sub_mat%29%0A%0A++++return+%5B%5Bmm%5Bi%5D%5Bj%5D+%2F+det+for+j+in+range%28n%29%5D+for+i+in+range%28n%29%5D%0A%0Adef+create_axis_lines%28length%3D15%2C+tick_size%3D0.1%29%3A%0A++++Entity%28model%3DMesh%28vertices%3D%5B%28-length%2C+0%2C+0%29%2C+%28length%2C+0%2C+0%29%5D%2C+mode%3D%27line%27%29%2C+color%3Dcolor.red%2C+thickness%3D3%29%0A++++Entity%28model%3DMesh%28vertices%3D%5B%280%2C+0%2C+-length%29%2C+%280%2C+0%2C+length%29%5D%2C+mode%3D%27line%27%29%2C+color%3Dcolor.blue%2C+thickness%3D3%29%0A++++Entity%28model%3DMesh%28vertices%3D%5B%280%2C+-length%2C+0%29%2C+%280%2C+length%2C+0%29%5D%2C+mode%3D%27line%27%29%2C+color%3Dcolor.green%2C+thickness%3D3%29%0A%0A++++tolch+%3D+0.0075%0A++++for+i+in+range%28-length%2C+length+%2B+1%29%3A%0A++++++++if+i+%3D%3D+0%3A+continue%0A++++++++Entity%28model%3D%27cube%27%2C+position%3D%28i%2C+0%2C+0%29%2C+scale%3D%28tolch%2C+tolch%2C+tick_size+*+2%29%2C+color%3Dcolor.red%29%0A++++++++Entity%28model%3D%27cube%27%2C+position%3D%280%2C+0%2C+i%29%2C+scale%3D%28tick_size+*+2%2C+tolch%2C+tolch%29%2C+color%3Dcolor.blue%29%0A++++++++Entity%28model%3D%27cube%27%2C+position%3D%280%2C+i%2C+0%29%2C+scale%3D%28tick_size+*+2%2C+tolch%2C+tolch%29%2C+color%3Dcolor.green%29%0A%0Acreate_axis_lines%28%29%0A%0Acube+%3D+Entity%28position%3D%280%2C+0%2C+0%29%2C+scale%3D%281%2C+1%2C+1%29%29%0A%0Aploscost+%3D+Entity%28%0A++++parent%3Dcube%2C+model%3DMesh%28%29%2C+color%3Dcolor.rgba%281%2C+1%2C+1%2C+0.7%29%2C%0A++++texture%3D%27white_cube%27%2C+double_sided%3DTrue%2C+transparency%3DTrue%0A%29%0A%0Arebra+%3D+Entity%28parent%3Dcube%2C+model%3DMesh%28mode%3D%27line%27%29%2C+color%3Dcolor.rgb%2850%2C+50%2C+50%29%2C+thickness%3D2%29%0A%0Avector_i+%3D+Entity%28parent%3Dcube%2C+model%3D%27arrow%27%2C+color%3Dcolor.rgb%28255%2C+0%2C+0%29%2C+origin%3D%28-0.5%2C+0%2C+0%29%29%0Avector_j+%3D+Entity%28parent%3Dcube%2C+model%3D%27arrow%27%2C+color%3Dcolor.rgb%280%2C+0%2C+255%29%2C+origin%3D%28-0.5%2C+0%2C+0%29%29%0Avector_k+%3D+Entity%28parent%3Dcube%2C+model%3D%27arrow%27%2C+color%3Dcolor.rgb%280%2C+255%2C+0%29%2C+origin%3D%28-0.5%2C+0%2C+0%29%29%0A%0Alocal_i+%3D+Vec3%281%2C+0%2C+0%29%0Alocal_j+%3D+Vec3%280%2C+1%2C+0%29%0Alocal_k+%3D+Vec3%280%2C+0%2C+1%29%0A%0Adef+to_ursina_coords%28v%29%3A%0A++++return+Vec3%28v.x%2C+v.z%2C+v.y%29%0A%0Adef+update_vectors%28%29%3A%0A++++tolchina+%3D+0.5%0A++++dir_i+%3D+Vec3%28local_i.x%2C+-local_i.z%2C+local_i.y%29%0A++++dir_j+%3D+Vec3%28local_j.x%2C+-local_j.z%2C+local_j.y%29%0A++++dir_k+%3D+Vec3%28local_k.x%2C+-local_k.z%2C+local_k.y%29%0A%0A++++for+arrow%2C+direction%2C+corrected_dir+in+zip%28%5Bvector_i%2C+vector_j%2C+vector_k%5D%2C+%5Blocal_i%2C+local_j%2C+local_k%5D%2C+%5Bdir_i%2C+dir_j%2C+dir_k%5D%29%3A%0A++++++++length+%3D+direction.length%28%29%0A++++++++if+length+%3E+0.01%3A%0A++++++++++++arrow.enabled+%3D+True%0A++++++++++++arrow.position+%3D+%280%2C+0%2C+0%29%0A++++++++++++dir_norm+%3D+corrected_dir+%2F+length%0A++++++++++++yaw+%3D+math.degrees%28math.atan2%28dir_norm.z%2C+dir_norm.x%29%29%0A++++++++++++pitch+%3D+math.degrees%28math.atan2%28dir_norm.y%2C+math.sqrt%28dir_norm.x+**+2+%2B+dir_norm.z+**+2%29%29%29%0A++++++++++++arrow.rotation+%3D+Vec3%280%2C+-yaw%2C+pitch%29%0A++++++++++++arrow.scale+%3D+Vec3%28length%2C+tolchina%2C+tolchina%29%0A++++++++else%3A%0A++++++++++++arrow.enabled+%3D+False%0A%0Adef+update_volume_geometry%28%29%3A%0A++++v0+%3D+to_ursina_coords%28Vec3%280%2C+0%2C+0%29%29%0A++++v1+%3D+to_ursina_coords%28local_k%29%0A++++v2+%3D+to_ursina_coords%28local_j%29%0A++++v3+%3D+to_ursina_coords%28local_j+%2B+local_k%29%0A++++v4+%3D+to_ursina_coords%28local_i%29%0A++++v5+%3D+to_ursina_coords%28local_i+%2B+local_k%29%0A++++v6+%3D+to_ursina_coords%28local_i+%2B+local_j%29%0A++++v7+%3D+to_ursina_coords%28local_i+%2B+local_j+%2B+local_k%29%0A%0A++++ploscost.model.vertices+%3D+%5B%0A++++++++v0%2C+v4%2C+v6%2C+v2%2C+v1%2C+v3%2C+v7%2C+v5%2C%0A++++++++v0%2C+v1%2C+v5%2C+v4%2C+v2%2C+v6%2C+v7%2C+v3%2C%0A++++++++v0%2C+v2%2C+v3%2C+v1%2C+v4%2C+v5%2C+v7%2C+v6%0A++++%5D%0A++++ploscost.model.triangles+%3D+%5B%0A++++++++0%2C+1%2C+2%2C+0%2C+2%2C+3%2C+4%2C+5%2C+6%2C+4%2C+6%2C+7%2C%0A++++++++8%2C+9%2C+10%2C+8%2C+10%2C+11%2C+12%2C+13%2C+14%2C+12%2C+14%2C+15%2C%0A++++++++16%2C+17%2C+18%2C+16%2C+18%2C+19%2C+20%2C+21%2C+22%2C+20%2C+22%2C+23%0A++++%5D%0A++++ploscost.model.uvs+%3D+%5B%280%2C+0%29%2C+%281%2C+0%29%2C+%281%2C+1%29%2C+%280%2C+1%29%5D+*+6%0A++++ploscost.model.generate%28%29%0A%0A++++rebra.model.vertices+%3D+%5B%0A++++++++v0%2C+v4%2C+v4%2C+v6%2C+v6%2C+v2%2C+v2%2C+v0%2C%0A++++++++v1%2C+v5%2C+v5%2C+v7%2C+v7%2C+v3%2C+v3%2C+v1%2C%0A++++++++v0%2C+v1%2C+v4%2C+v5%2C+v6%2C+v7%2C+v2%2C+v3%0A++++%5D%0A++++rebra.model.generate%28%29%0A++++update_vectors%28%29%0A%0Amatrix_fields+%3D+%5B%5D%0Astart_x%2C+start_y+%3D+0.50%2C+0.40%0Astep_x%2C+step_y+%3D+0.11%2C+0.06%0A%0Adefault_matrix+%3D+%5B%5B%221.0%22%2C+%220.0%22%2C+%220.0%22%5D%2C+%5B%220.0%22%2C+%221.0%22%2C+%220.0%22%5D%2C+%5B%220.0%22%2C+%220.0%22%2C+%221.0%22%5D%5D%0Adefault_scale+%3D+%5B%5B%221.0%22%2C+%220.0%22%2C+%220.0%22%5D%2C+%5B%220.0%22%2C+%221.0%22%2C+%220.0%22%5D%2C+%5B%220.0%22%2C+%220.0%22%2C+%221.0%22%5D%5D%0A%0Anames+%3D+%5B%22i%22%2C+%22j%22%2C+%22k%22%5D%0Afor+c+in+range%283%29%3A%0A++++Text%28text%3Dnames%5Bc%5D%2C+position%3D%28start_x+%2B+c+*+step_x%2C+start_y%29%2C+color%3Dcolor.black%29%0A%0Afor+r+in+range%283%29%3A%0A++++row_fields+%3D+%5B%5D%0A++++for+c+in+range%283%29%3A%0A++++++++f+%3D+InputField%28default_value%3Ddefault_matrix%5Br%5D%5Bc%5D%2C+position%3D%28start_x+%2B+c+*+step_x%2C+start_y+-+%28r+%2B+1%29+*+step_y%29%2C+scale%3D%280.1%2C+0.04%29%29%0A++++++++f.character_limit+%3D+6%0A++++++++row_fields.append%28f%29%0A++++matrix_fields.append%28row_fields%29%0A%0Ascale_fields+%3D+%5B%5D%0Ascale_start_y+%3D+start_y+-+4.2+*+step_y%0AText%28text%3D%22Масштаб%3A%22%2C+position%3D%28start_x%2C+scale_start_y%29%2C+color%3Dcolor.black%29%0A%0Afor+r+in+range%283%29%3A%0A++++row_fields+%3D+%5B%5D%0A++++for+c+in+range%283%29%3A%0A++++++++f+%3D+InputField%28default_value%3Ddefault_scale%5Br%5D%5Bc%5D%2C+position%3D%28start_x+%2B+c+*+step_x%2C+scale_start_y+-+%28r+%2B+1%29+*+step_y%29%2C+scale%3D%280.1%2C+0.04%29%29%0A++++++++f.character_limit+%3D+6%0A++++++++row_fields.append%28f%29%0A++++scale_fields.append%28row_fields%29%0A%0Adef+get_scale_matrix%28%29%3A%0A++++try%3A%0A++++++++return+%5B%0A++++++++++++%5Bfloat%28scale_fields%5B0%5D%5B0%5D.text%29%2C+float%28scale_fields%5B0%5D%5B1%5D.text%29%2C+float%28scale_fields%5B0%5D%5B2%5D.text%29%5D%2C%0A++++++++++++%5Bfloat%28scale_fields%5B1%5D%5B0%5D.text%29%2C+float%28scale_fields%5B1%5D%5B1%5D.text%29%2C+float%28scale_fields%5B1%5D%5B2%5D.text%29%5D%2C%0A++++++++++++%5Bfloat%28scale_fields%5B2%5D%5B0%5D.text%29%2C+float%28scale_fields%5B2%5D%5B1%5D.text%29%2C+float%28scale_fields%5B2%5D%5B2%5D.text%29%5D%0A++++++++%5D%0A++++except+%28ValueError%2C+IndexError%29%3A%0A++++++++return+%5B%5B1.0%2C+0.0%2C+0.0%5D%2C+%5B0.0%2C+1.0%2C+0.0%5D%2C+%5B0.0%2C+0.0%2C+1.0%5D%5D%0A%0Adef+apply_scale_to_vector%28v%2C+S%29%3A%0A++++return+Vec3%28%0A++++++++S%5B0%5D%5B0%5D*v.x+%2B+S%5B0%5D%5B1%5D*v.y+%2B+S%5B0%5D%5B2%5D*v.z%2C%0A++++++++S%5B1%5D%5B0%5D*v.x+%2B+S%5B1%5D%5B1%5D*v.y+%2B+S%5B1%5D%5B2%5D*v.z%2C%0A++++++++S%5B2%5D%5B0%5D*v.x+%2B+S%5B2%5D%5B1%5D*v.y+%2B+S%5B2%5D%5B2%5D*v.z%0A++++%29%0A%0Adef+ok_matrix%28%29%3A%0A++++global+local_i%2C+local_j%2C+local_k%0A++++try%3A%0A++++++++local_i+%3D+Vec3%28float%28matrix_fields%5B0%5D%5B0%5D.text%29%2C+float%28matrix_fields%5B1%5D%5B0%5D.text%29%2C+float%28matrix_fields%5B2%5D%5B0%5D.text%29%29%0A++++++++local_j+%3D+Vec3%28float%28matrix_fields%5B0%5D%5B1%5D.text%29%2C+float%28matrix_fields%5B1%5D%5B1%5D.text%29%2C+float%28matrix_fields%5B2%5D%5B1%5D.text%29%29%0A++++++++local_k+%3D+Vec3%28float%28matrix_fields%5B0%5D%5B2%5D.text%29%2C+float%28matrix_fields%5B1%5D%5B2%5D.text%29%2C+float%28matrix_fields%5B2%5D%5B2%5D.text%29%29%0A++++++++S+%3D+get_scale_matrix%28%29%0A++++++++local_i+%3D+apply_scale_to_vector%28local_i%2C+S%29%0A++++++++local_j+%3D+apply_scale_to_vector%28local_j%2C+S%29%0A++++++++local_k+%3D+apply_scale_to_vector%28local_k%2C+S%29%0A++++++++update_volume_geometry%28%29%0A++++except+%28ValueError%2C+IndexError%29%3A%0A++++++++pass%0A%0AButton%28text%3D%22ok%22%2C+position%3D%28start_x+%2B+step_x%2C+start_y+-+8.0+*+step_y%29%2C+scale%3D%280.2%2C+0.04%29%2C+color%3Dcolor.azure%2C+on_click%3Dok_matrix%29%0A%0Aсейчас+еще+докину&newwindow=1&sca_esv=b91b52423da4ab6e&sxsrf=ANbL-n783hkth76BhSFR2FeqfOoOq3uRLA%3A1770243750346&source=hp&ei=psaDabKcE-CrwPAPnOyVuQI&iflsig=AFdpzrgAAAAAaYPUtnEtTXgNwkYTf4fPe4PsZHCe3Mf4&aep=22&ved=0ahUKEwiyh53v78CSAxXgFRAIHRx2JScQteYPCBE&oq=&gs_lp=Egdnd3Mtd2l6IgBIAFAAWABwAHgAkAEAmAEAoAEAqgEAuAEByAEAmAIAoAIAmAMAkgcAoAcAsgcAuAcAwgcAyAcAgAgA&sclient=gws-wiz&mstk=AUtExfD0xFLV43Yao3ZD3UsRbL6NhW-bEYlk7yivwaNG5qgWs80YJCc7flbT9WCu7Vq3A9kgu78hsoIGDK0k0TdSfW8jMh9tNNpSn2OT4TR738fyBUyidW2okq1OLsKBru0s_MdcZcVLi4_-94PzcjuFJjvVptd7d_wngMbghtu_wJm6z1wfzp5RKQ8TuB16I_zD3XgKQixiiWRycjEQdUtGud_wR9iwFxid3QkIUEiC3_Vz2ZfaBS21tiC9qg&csuir=1&lns_mode=cvst&elids=CKvokOyE4p-bogEQARgBIhC4WjcDSCFEh7LgWFUVz_liMoABIgJsdSgbQnIKLmxmZS1kdW1teTo3YzE5MzE4ZC05YmZmLTQxZjMtODdlMC02ZGU0MzA2NzhhNWMSQAo-L2Jucy9sdS9ib3JnL2x1L2Jucy9sZW5zLWZyb250ZW5kLWFwaS9wcm9kLmxlbnMtZnJvbnRlbmQtYXBpLzBaBAoCbHU4sOaf-rPJlwNQAGoJaW1hZ2UvcG5n%2CCLDL9bCmtNeBvwEQARgBIhCq3zbmT78tcgg9XbuDMbevMoIBIgJsdSgQQnQKLmxmZS1kdW1teTpkMmZjN2NmYi04YTcxLTRiNTAtOWY1NC0xZDBjMmFmN2YxN2YSQgpAL2Jucy9sdS9ib3JnL2x1L2Jucy9sZW5zLWZyb250ZW5kLWFwaS9wcm9kLmxlbnMtZnJvbnRlbmQtYXBpLzE1N1oECgJsdTiQqcOes8mXA1AAaglpbWFnZS9wbmc&udm=50
        target_i = apply_scale_to_vector(t_i, S)
        target_j = apply_scale_to_vector(t_j, S)
        target_k = apply_scale_to_vector(t_k, S)
        update_volume_geometry()
    except (ValueError, IndexError):
        pass
    fun_def_scale()

Button(text="ok", position=(start_x + step_x + 0.065, scale_start_y - 0.01), scale=(0.19, 0.04), color=color.azure, on_click=ok_matrix)

rot_start_x = start_x + 3.5 * step_x - 0.05
rot_start_y = start_y 

Text(text="Поворот вокруг вектора:", position=(rot_start_x, rot_start_y), color=color.black)

rot_labels = ["i:", "j:", "k:"]
rot_fields = []

for r in range(3):
    Text(text=rot_labels[r], position=(rot_start_x, rot_start_y - (r + 1) * step_y + 0.01), color=color.black)
    f = InputField(default_value="0.0", position=(rot_start_x + 0.08, rot_start_y - (r + 1) * step_y), scale=(0.1, 0.04))
    f.character_limit = 6
    rot_fields.append(f)

def apply_rotations():
    global target_i, target_j, target_k
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
        [target_i.x, target_j.x, target_k.x],
        [target_i.y, target_j.y, target_k.y],
        [target_i.z, target_j.z, target_k.z]
    ]

    new_mat = mul_matrices(current_mat, rot_total)

    target_i = Vec3(new_mat[0][0], new_mat[1][0], new_mat[2][0])
    target_j = Vec3(new_mat[0][1], new_mat[1][1], new_mat[2][1])
    target_k = Vec3(new_mat[0][2], new_mat[1][2], new_mat[2][2])

    for f in rot_fields:
        f.text = "0.0"

Button(text="ok", position=(rot_start_x + 0.2 , rot_start_y - 0.12), scale=(0.08, 0.04), color=color.orange, on_click=apply_rotations)

def non_activ():
    for f in rot_fields:
        f.active = False
    for row in matrix_fields:
        for f in row:
            f.active = False
    for row in scale_fields:
        for f in row:
            f.active = False

def fun_def_scale():
    for r in range(3):
            for c in range(3):
                scale_fields[r][c].text = default_scale[r][c]

def reset_cube():
    global local_i, local_j, local_k, target_i, target_j, target_k
    cube.rotation, cube.position = (0, 0, 0), (0, 0, 0)
    
    local_i = Vec3(1, 0, 0)
    local_j = Vec3(0, 1, 0)
    local_k = Vec3(0, 0, 1)
    
    target_i = Vec3(1, 0, 0)
    target_j = Vec3(0, 1, 0)
    target_k = Vec3(0, 0, 1)
    
    update_volume_geometry()
    
    for r in range(3):
        for c in range(3):
            matrix_fields[r][c].text = default_matrix[r][c]
            scale_fields[r][c].text = default_scale[r][c]
            
    for f in rot_fields:
        f.text = "0.0"

def field_active():
    if any(f.active for row in matrix_fields for f in row): return True
    if any(f.active for row in scale_fields for f in row): return True
    if any(f.active for f in rot_fields): return True
    return False

def input(key):
    print(key)
    if field_active():
        if key == 'enter':
            ok_matrix()
            apply_rotations()
            non_activ()
        return
    if key == 'j': cube.x += 1 
    if key == 'g': cube.x -= 1 
    if key == 'y': cube.z += 1
    if key == 'h': cube.z -= 1
    if key == 'u': cube.y += 1
    if key == 't': cube.y -= 1
    if key == 'r': 
        reset_cube()
        non_activ()
    if key == 'v': reset_camera()
    if key == 'enter': 
        ok_matrix()
        apply_rotations()
        non_activ()
    if key == 'escape up': application.quit()
    if key == 'scroll up': camera.z = min(-3, camera.z + 1.5)
    if key == 'scroll down': camera.z = max(-50, camera.z - 1.5)

def update():
    global local_i, local_j, local_k
    
    animation_speed = 4.0
    
    if 'target_i' in globals():
        local_i = lerp(local_i, target_i, time.dt * animation_speed)
        local_j = lerp(local_j, target_j, time.dt * animation_speed)
        local_k = lerp(local_k, target_k, time.dt * animation_speed)
        
        update_volume_geometry()
        
        if local_i != target_i or local_j != target_j or local_k != target_k:
            matrix_fields[0][0].text = f"{local_i.x:.1f}"
            matrix_fields[1][0].text = f"{local_i.y:.1f}"
            matrix_fields[2][0].text = f"{local_i.z:.1f}"
            
            matrix_fields[0][1].text = f"{local_j.x:.1f}"
            matrix_fields[1][1].text = f"{local_j.y:.1f}"
            matrix_fields[2][1].text = f"{local_j.z:.1f}"
            
            matrix_fields[0][2].text = f"{local_k.x:.1f}"
            matrix_fields[1][2].text = f"{local_k.y:.1f}"
            matrix_fields[2][2].text = f"{local_k.z:.1f}"

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
