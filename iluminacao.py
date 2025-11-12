# iluminacao_demo.py
# Demonstração interativa de iluminação no pipeline legacy do OpenGL usando PyOpenGL (GL/GLU/GLUT).
# Foco: luzes (pontual e spotlight), atenuação, componentes de material, brilho (shininess),
# shading (flat/smooth), wireframe, normais, face culling e HUD com instruções.
#
# Controles:
#  Mouse: arraste com botão esquerdo para orbitar; roda do mouse (ou 3/4) para zoom
#  Setas ← → ↑ ↓ : move a luz 0 no plano XZ
#  PageUp/PageDown : move a luz 0 no eixo Y
#  p : alterna spotlight para a luz 0 (pontual <-> spot)
#  [ / ] : diminui / aumenta cutoff do spotlight
#  , / . : diminui / aumenta atenuação linear (k_l) da luz 0
#  ; / / : diminui / aumenta atenuação quadrática (k_q) da luz 0
#  a : alterna componente ambiente global (I_a)
#  d : alterna componente difusa da luz 0
#  s : alterna componente especular da luz 0
#  n / N : diminui / aumenta brilho (shininess) do material
#  g : alterna flat/smooth shading
#  t : wireframe on/off
#  c : face culling on/off
#  l : liga/desliga luz 0
#  k : liga/desliga luz 1 (luz secundária fixa)
#  v : alterna visualização de normais
#  r : reset
#  ESC : sair

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math

# -------------------------
# Estado global
# -------------------------
win_w, win_h = 1200, 720

# Câmera orbital
cam_dist = 8.0
cam_yaw = 30.0     # graus (em torno de Y)
cam_pitch = 20.0   # graus (em torno de X)
dragging = False
last_x, last_y = 0, 0

# Luz 0 (principal): móvel, pode virar spotlight
light0_enabled = True
light0_pos = [3.0, 4.0, 3.0, 1.0]   # w=1.0 -> luz pontual
light0_diffuse_on = True
light0_specular_on = True
light0_is_spot = False
light0_spot_dir = [-1.0, -1.0, -1.0]   # direção do cone
light0_spot_cutoff = 25.0               # graus (0..90, 180 desliga)
# Atenuação (1 / (k_c + k_l d + k_q d^2))
light0_kc = 1.0
light0_kl = 0.09
light0_kq = 0.032

# Luz 1 (secundária): fixa e mais quente
light1_enabled = True

# Ambiente global
ambient_global_on = True
ambient_global = [0.12, 0.12, 0.12, 1.0]

# Material
mat_kd = [0.8, 0.55, 0.25, 1.0]  # difuso
mat_ks = [0.9, 0.9, 0.9, 1.0]    # especular
mat_shininess = 48.0             # brilho

# Render flags
wireframe = False
use_cull = True
show_normals = False
smooth_shading = True  # GL_SMOOTH vs GL_FLAT

# -------------------------
# Utilitários de câmera
# -------------------------
def set_camera():
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    # converter yaw/pitch -> posição esférica
    yaw = math.radians(cam_yaw)
    pitch = math.radians(cam_pitch)
    cx = cam_dist * math.cos(pitch) * math.cos(yaw)
    cy = cam_dist * math.sin(pitch)
    cz = cam_dist * math.cos(pitch) * math.sin(yaw)
    gluLookAt(cx, cy, cz, 0.0, 0.8, 0.0, 0.0, 1.0, 0.0)

# -------------------------
# Inicialização OpenGL
# -------------------------
def init_gl():
    glClearColor(0.05, 0.06, 0.09, 1.0)
    glEnable(GL_MULTISAMPLE)
    glEnable(GL_DEPTH_TEST)
    if use_cull:
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)

    # Shading
    glShadeModel(GL_SMOOTH if smooth_shading else GL_FLAT)

    # Iluminação global e materiais
    glEnable(GL_LIGHTING)
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, ambient_global if ambient_global_on else [0.0,0.0,0.0,1.0])
    glEnable(GL_COLOR_MATERIAL)  # permite usar glColor como kd
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, mat_ks)
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, mat_shininess)

    # Configura luz 0
    apply_light0_state()

    # Luz 1 (fixa, quente)
    apply_light1_state()

def apply_light0_state():
    if light0_enabled:
        glEnable(GL_LIGHT0)
    else:
        glDisable(GL_LIGHT0)

    # posição
    glLightfv(GL_LIGHT0, GL_POSITION, light0_pos)

    # componentes on/off
    glLightfv(GL_LIGHT0, GL_DIFFUSE,  [1.0, 1.0, 1.0, 1.0] if light0_diffuse_on else [0.0,0.0,0.0,1.0])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0] if light0_specular_on else [0.0,0.0,0.0,1.0])

    # atenuação
    glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION,  light0_kc)
    glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION,    light0_kl)
    glLightf(GL_LIGHT0, GL_QUADRATIC_ATTENUATION, light0_kq)

    # spotlight
    if light0_is_spot:
        glLightfv(GL_LIGHT0, GL_SPOT_DIRECTION, light0_spot_dir)
        glLightf(GL_LIGHT0, GL_SPOT_CUTOFF, light0_spot_cutoff)  # 0..90, ou 180 desliga
        glLightf(GL_LIGHT0, GL_SPOT_EXPONENT, 16.0)              # concentração
    else:
        glLightf(GL_LIGHT0, GL_SPOT_CUTOFF, 180.0)  # sem spotlight

def apply_light1_state():
    if light1_enabled:
        glEnable(GL_LIGHT1)
    else:
        glDisable(GL_LIGHT1)

    # Luz 1 fixa
    L1_pos = [-6.0, 6.0, -4.0, 1.0]   # pontual
    L1_diff = [1.0, 0.85, 0.65, 1.0]
    L1_spec = [0.8, 0.7, 0.6, 1.0]

    glLightfv(GL_LIGHT1, GL_POSITION, L1_pos)
    glLightfv(GL_LIGHT1, GL_DIFFUSE,  L1_diff)
    glLightfv(GL_LIGHT1, GL_SPECULAR, L1_spec)

    # atenuação leve
    glLightf(GL_LIGHT1, GL_CONSTANT_ATTENUATION,  1.0)
    glLightf(GL_LIGHT1, GL_LINEAR_ATTENUATION,    0.04)
    glLightf(GL_LIGHT1, GL_QUADRATIC_ATTENUATION, 0.007)

# -------------------------
# Geometria de cena
# -------------------------
def draw_plane(size=12, step=1.0, y=0.0):
    glDisable(GL_COLOR_MATERIAL)
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [0,0,0,1])
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 1.0)
    glColor3f(0.2, 0.25, 0.3)

    half = size * 0.5
    glNormal3f(0.0, 1.0, 0.0)
    glBegin(GL_QUADS)
    glVertex3f(-half, y, -half)
    glVertex3f( half, y, -half)
    glVertex3f( half, y,  half)
    glVertex3f(-half, y,  half)
    glEnd()

    glEnable(GL_COLOR_MATERIAL)
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, mat_ks)
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, mat_shininess)

def draw_object():
    # Base/corpo principal
    glPushMatrix()
    glTranslatef(0.0, 1.0, 0.0)
    glRotatef(25, 0, 1, 0)
    glScalef(1.0, 1.0, 1.0)
    glColor3f(*mat_kd[:3])
    try:
        glutSolidTeapot(1.2)
    except Exception:
        glutSolidSphere(1.2, 48, 32)
    glPopMatrix()

    # Segundo objeto
    glPushMatrix()
    glTranslatef(-2.5, 0.6, 1.4)
    glRotatef(-35, 0, 1, 0)
    glScalef(1.6, 0.4, 1.0)
    glColor3f(0.25, 0.65, 0.75)
    glutSolidCube(2.0)
    glPopMatrix()

def draw_light_gizmos():
    # Desenha esferas indicando as luzes (com iluminação desligada p/ ver claramente)
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)

    # Projeta para desenhar texto
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluPerspective(60.0, max(win_w/float(win_h), 1e-6), 0.1, 500.0)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    set_camera()

    # Luz 0
    glPointSize(10.0)
    glBegin(GL_POINTS)
    glColor3f(1.0, 1.0, 0.2)
    glVertex3f(light0_pos[0], light0_pos[1], light0_pos[2])
    glEnd()

    # Pequena esfera
    glPushMatrix()
    glTranslatef(light0_pos[0], light0_pos[1], light0_pos[2])
    glColor3f(1.0, 1.0, 0.2)
    glutWireSphere(0.15, 10, 8)
    glPopMatrix()

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)

def draw_normals_of_teapot(step=12):
    # Visualização aproximada de normais: desenha vetores a partir de amostras na superfície
    # (apenas para demonstração; para geometrias reais, extraia normais dos vértices)
    glDisable(GL_LIGHTING)
    glColor3f(0.95, 0.4, 0.4)
    glLineWidth(1.5)

    # Amostragem grosseira de uma esfera equivalente (para visual), já que teapot não expõe vértices facilmente
    glPushMatrix()
    glTranslatef(0.0, 1.0, 0.0)
    glRotatef(25, 0, 1, 0)

    radius = 1.2
    glBegin(GL_LINES)
    for i in range(step+1):
        theta = math.pi * (i/float(step))
        for j in range(step+1):
            phi = 2*math.pi * (j/float(step))
            nx = math.sin(theta)*math.cos(phi)
            ny = math.cos(theta)
            nz = math.sin(theta)*math.sin(phi)
            x = radius*nx
            y = radius*ny
            z = radius*nz
            glVertex3f(x, y, z)
            scale = 0.35
            glVertex3f(x + nx*scale, y + ny*scale, z + nz*scale)
    glEnd()
    glPopMatrix()

    glEnable(GL_LIGHTING)

# -------------------------
# HUD
# -------------------------
def draw_hud():
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, win_w, 0, win_h, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    def put(x, y, s):
        glWindowPos2f(x, y)
        for ch in s.encode("utf-8"):
            glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ch)

    y = win_h - 20
    put(10, y, "Iluminacao (GL/GLU/GLUT) — luz0: pontual/spot, atenuacao, componentes; luz1: fixa")
    y -= 18
    put(10, y, f"cam: dist={cam_dist:.2f} yaw={cam_yaw:.1f} pitch={cam_pitch:.1f} | shading={'SMOOTH' if smooth_shading else 'FLAT'} | wireframe={wireframe}")
    y -= 18
    put(10, y, f"luz0: on={light0_enabled} spot={light0_is_spot} cutoff={light0_spot_cutoff:.1f} kl={light0_kl:.4f} kq={light0_kq:.4f} | dif={light0_diffuse_on} esp={light0_specular_on}")
    y -= 18
    put(10, y, f"material: shininess={mat_shininess:.1f} | ambient_global={'ON' if ambient_global_on else 'OFF'} | cull={'ON' if use_cull else 'OFF'} | normals={'ON' if show_normals else 'OFF'}")
    y -= 18
    put(10, y, "Mouse=orbita | Roda=zoom | setas/PgUp/PgDn move luz0 | p spot | [ ] cutoff | , . kl | ; / kq | a/d/s ambient/diff/spec | n/N shininess | g flat/smooth | t wire | c cull | l/k L0/L1 | v normais | r reset | ESC sair")

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)

# -------------------------
# Display / reshape
# -------------------------
def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Projeção
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    aspect = max(win_w / float(win_h if win_h>0 else 1), 1e-6)
    gluPerspective(60.0, aspect, 0.1, 500.0)

    # View
    set_camera()

    # Shading
    glShadeModel(GL_SMOOTH if smooth_shading else GL_FLAT)

    # Estado de iluminação a cada frame (posição/direção mudam)
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, ambient_global if ambient_global_on else [0.0,0.0,0.0,1.0])
    apply_light0_state()
    apply_light1_state()

    # Wireframe ou fill
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE if wireframe else GL_FILL)

    # Cena
    draw_plane(size=16, y=0.0)
    draw_object()

    if show_normals:
        draw_normals_of_teapot(step=10)

    draw_light_gizmos()
    draw_hud()

    glutSwapBuffers()

def reshape(w, h):
    global win_w, win_h
    win_w = max(1, w)
    win_h = max(1, h)
    glViewport(0, 0, win_w, win_h)

# -------------------------
# Interação
# -------------------------
def mouse(button, state, x, y):
    global dragging, last_x, last_y, cam_dist
    if button == GLUT_LEFT_BUTTON:
        dragging = (state == GLUT_DOWN)
        last_x, last_y = x, y

    # roda do mouse (em muitos GLUTs: 3=up, 4=down)
    if state == GLUT_DOWN:
        if button == 3:
            cam_dist = max(1.0, cam_dist * 0.92)
        elif button == 4:
            cam_dist = min(100.0, cam_dist / 0.92)

    glutPostRedisplay()

def motion(x, y):
    global last_x, last_y, cam_yaw, cam_pitch
    if dragging:
        dx = x - last_x
        dy = y - last_y
        last_x, last_y = x, y
        cam_yaw = (cam_yaw + dx * 0.4) % 360.0
        cam_pitch = max(-89.0, min(89.0, cam_pitch - dy * 0.3))
        glutPostRedisplay()

def special_keys(key, x, y):
    # setas e page up/down: move luz 0
    step_xy = 0.25
    step_y  = 0.25
    if key == GLUT_KEY_LEFT:
        light0_pos[0] -= step_xy
    elif key == GLUT_KEY_RIGHT:
        light0_pos[0] += step_xy
    elif key == GLUT_KEY_UP:
        light0_pos[2] -= step_xy
    elif key == GLUT_KEY_DOWN:
        light0_pos[2] += step_xy
    elif key == GLUT_KEY_PAGE_UP:
        light0_pos[1] += step_y
    elif key == GLUT_KEY_PAGE_DOWN:
        light0_pos[1] -= step_y
    glutPostRedisplay()

def keyboard(key, x, y):
    global wireframe, use_cull, smooth_shading, show_normals
    global ambient_global_on, light0_enabled, light1_enabled
    global light0_diffuse_on, light0_specular_on, light0_is_spot, light0_spot_cutoff
    global light0_kl, light0_kq, mat_shininess, cam_dist

    k = key.decode("utf-8") if isinstance(key, bytes) else key

    if k == '\x1b':  # ESC
        try:
            glutLeaveMainLoop()
        except Exception:
            pass
        import sys; sys.exit(0)

    elif k == 't':
        wireframe = not wireframe

    elif k == 'c':
        use_cull = not use_cull
        if use_cull: glEnable(GL_CULL_FACE)
        else:        glDisable(GL_CULL_FACE)

    elif k == 'g':
        smooth_shading = not smooth_shading

    elif k == 'v':
        show_normals = not show_normals

    elif k == 'a':
        ambient_global_on = not ambient_global_on

    elif k == 'l':
        light0_enabled = not light0_enabled

    elif k == 'k':
        light1_enabled = not light1_enabled

    elif k == 'd':
        light0_diffuse_on = not light0_diffuse_on

    elif k == 's':
        light0_specular_on = not light0_specular_on

    elif k == 'n':
        mat_shininess = max(1.0, mat_shininess - 4.0)
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, mat_shininess)
    elif k == 'N':
        mat_shininess = min(256.0, mat_shininess + 4.0)
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, mat_shininess)

    elif k == 'p':
        light0_is_spot = not light0_is_spot

    elif k == '[':
        if light0_is_spot:
            light0_spot_cutoff = max(5.0, light0_spot_cutoff - 2.0)
    elif k == ']':
        if light0_is_spot:
            light0_spot_cutoff = min(90.0, light0_spot_cutoff + 2.0)

    elif k == ',':
        light0_kl = max(0.0, light0_kl - 0.005)
    elif k == '.':
        light0_kl = min(1.0, light0_kl + 0.005)

    elif k == ';':
        light0_kq = max(0.0, light0_kq - 0.002)
    elif k == '/':
        light0_kq = min(1.0, light0_kq + 0.002)

    elif k == 'r':
        reset_state()

    glutPostRedisplay()

def reset_state():
    global cam_dist, cam_yaw, cam_pitch
    global light0_enabled, light1_enabled, light0_pos
    global light0_diffuse_on, light0_specular_on, light0_is_spot, light0_spot_cutoff
    global light0_kc, light0_kl, light0_kq
    global ambient_global_on, mat_shininess, wireframe, use_cull, smooth_shading, show_normals

    cam_dist = 8.0
    cam_yaw = 30.0
    cam_pitch = 20.0

    light0_enabled = True
    light1_enabled = True
    light0_pos = [3.0, 4.0, 3.0, 1.0]
    light0_diffuse_on = True
    light0_specular_on = True
    light0_is_spot = False
    light0_spot_cutoff = 25.0
    light0_kc = 1.0
    light0_kl = 0.09
    light0_kq = 0.032

    ambient_global_on = True
    mat_shininess = 48.0
    wireframe = False
    use_cull = True
    smooth_shading = True
    show_normals = False

    if use_cull:
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, mat_shininess)

# -------------------------
# Main
# -------------------------
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH | GLUT_MULTISAMPLE)
    glutInitWindowSize(win_w, win_h)
    glutCreateWindow(b"PyOpenGL Iluminacao: Pontual, Spotlight, Atenuacao, Shading, Materiais (GL/GLU/GLUT)")

    init_gl()
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutMouseFunc(mouse)
    glutMotionFunc(motion)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_keys)
    glutIdleFunc(lambda: glutPostRedisplay())

    print_controls()
    glutMainLoop()

def print_controls():
    print("\nControles:")
    print("  Mouse arrastar : orbitar camera")
    print("  Roda do mouse  : zoom")
    print("  Setas/PgUp/PgDn: move luz 0 (X/Z/Y)")
    print("  p              : alterna spotlight para luz 0")
    print("  [ / ]          : cutoff spotlight - / +")
    print("  , / .          : atenuacao linear k_l - / +")
    print("  ; / /          : atenuacao quadratica k_q - / +")
    print("  a              : ambient global on/off")
    print("  d              : componente difusa da luz 0 on/off")
    print("  s              : componente especular da luz 0 on/off")
    print("  n / N          : shininess material - / +")
    print("  g              : flat/smooth shading")
    print("  t              : wireframe on/off")
    print("  c              : face culling on/off")
    print("  l              : liga/desliga luz 0")
    print("  k              : liga/desliga luz 1")
    print("  v              : mostrar normais on/off")
    print("  r              : reset")
    print("  ESC            : sair\n")

if __name__ == "__main__":
    main()
