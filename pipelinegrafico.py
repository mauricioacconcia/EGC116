# viewport_pipeline_demo.py
# Demonstração interativa do pipeline: Model/View, Projection, Viewport em PyOpenGL (GL, GLU, GLUT).
# Controles:
#  Mouse: arraste com botão esquerdo para orbitar; roda do mouse para zoom
#  p : alterna projeção (perspectiva/ortográfica)
#  [ / ] : diminui / aumenta FOV (perspectiva)
#  - / = : diminui / aumenta escala ortográfica
#  v : alterna viewport (cheio / inset)
#  z / Z : zoom in / out
#  t : alterna wireframe
#  d : alterna depth test
#  c : alterna face culling
#  r : reset
#  ESC : sair

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math

# Estado global
win_w, win_h = 1024, 640
last_x, last_y = 0, 0
dragging = False

# Câmera (orbital)
cam_distance = 6.0
cam_yaw = 35.0     # graus
cam_pitch = 20.0   # graus
target = (0.0, 0.0, 0.0)

# Projeção
proj_mode = "persp"   # "persp" ou "ortho"
fov = 60.0            # campo de visão (perspectiva)
near_plane = 0.1
far_plane = 200.0
ortho_scale = 2.5     # "zoom" ortográfico (metade do tamanho vertical)

# Render
use_depth = True
use_cull = True
wireframe = False

# Viewport
viewport_inset = False   # False: tela cheia; True: adiciona viewport secundário (inset)


def print_instructions():
    print("\nControles:")
    print("  Mouse arrastar : orbitar câmera")
    print("  Roda do mouse  : zoom")
    print("  p              : alterna projeção (perspectiva/ortográfica)")
    print("  [ / ]          : FOV - / + (perspectiva)")
    print("  - / =          : escala ortográfica - / +")
    print("  v              : alterna viewport (cheio / inset)")
    print("  z / Z          : zoom in / out")
    print("  t              : wireframe on/off")
    print("  d              : depth test on/off")
    print("  c              : face culling on/off")
    print("  r              : reset")
    print("  ESC            : sair\n")


def init_gl():
    glClearColor(0.07, 0.08, 0.1, 1.0)
    glEnable(GL_MULTISAMPLE)
    if use_depth:
        glEnable(GL_DEPTH_TEST)
    if use_cull:
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)

    # Iluminação simples
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, (5.0, 8.0, 10.0, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (1.0, 1.0, 1.0, 1.0))
    glLightfv(GL_LIGHT0, GL_SPECULAR, (0.7, 0.7, 0.7, 1.0))
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)


def set_projection(w, h):
    """Configura a matriz de projeção para o viewport atual."""
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    aspect = max(w / float(h if h > 0 else 1), 1e-6)
    if proj_mode == "persp":
        gluPerspective(fov, aspect, near_plane, far_plane)
    else:
        # Projeção ortográfica com escala controlada por ortho_scale (altura)
        top = ortho_scale
        bottom = -ortho_scale
        right = top * aspect
        left = -right
        glOrtho(left, right, bottom, top, near_plane, far_plane)
    glMatrixMode(GL_MODELVIEW)


def set_camera():
    """Configura a view (câmera) usando órbita ao redor do alvo."""
    glLoadIdentity()
    # Converter yaw/pitch para coordenadas esféricas
    yaw_rad = math.radians(cam_yaw)
    pitch_rad = math.radians(cam_pitch)
    cx = target[0] + cam_distance * math.cos(pitch_rad) * math.cos(yaw_rad)
    cy = target[1] + cam_distance * math.sin(pitch_rad)
    cz = target[2] + cam_distance * math.cos(pitch_rad) * math.sin(yaw_rad)
    gluLookAt(cx, cy, cz, target[0], target[1], target[2], 0.0, 1.0, 0.0)


def draw_axes(length=2.0, thickness=2.0):
    glDisable(GL_LIGHTING)
    glLineWidth(thickness)
    glBegin(GL_LINES)
    # X: vermelho
    glColor3f(1.0, 0.1, 0.1); glVertex3f(0, 0, 0); glVertex3f(length, 0, 0)
    # Y: verde
    glColor3f(0.1, 1.0, 0.1); glVertex3f(0, 0, 0); glVertex3f(0, length, 0)
    # Z: azul
    glColor3f(0.1, 0.4, 1.0); glVertex3f(0, 0, 0); glVertex3f(0, 0, length)
    glEnd()
    glEnable(GL_LIGHTING)


def draw_grid(size=10, step=1.0):
    glDisable(GL_LIGHTING)
    glColor3f(0.35, 0.35, 0.4)
    glLineWidth(1.0)
    glBegin(GL_LINES)
    half = size * step * 0.5
    n = int(size)
    for i in range(-n, n + 1):
        x = i * step
        glVertex3f(x, 0, -half); glVertex3f(x, 0, half)
        glVertex3f(-half, 0, x); glVertex3f(half, 0, x)
    glEnd()
    glEnable(GL_LIGHTING)


def draw_object():
    # Um objeto simples: base + teapot
    glPushMatrix()
    glTranslatef(0.0, 0.5, 0.0)
    glColor3f(0.9, 0.6, 0.2)
    try:
        glutSolidTeapot(1.0)
    except Exception:
        # Fallback: cubo se teapot indisponível
        glutSolidCube(2.0)
    glPopMatrix()

    # Um segundo objeto
    glPushMatrix()
    glTranslatef(-1.8, 0.3, 1.2)
    glRotatef(30, 0, 1, 0)
    glScalef(1.0, 0.3, 1.0)
    glColor3f(0.2, 0.8, 0.8)
    glutSolidCube(2.0)
    glPopMatrix()


def draw_hud_text():
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    # Projeção 2D para texto
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
    put(10, y, f"Proj: {proj_mode.upper()}  FOV: {int(fov)}  Ortho scale: {ortho_scale:.2f}  Dist: {cam_distance:.2f}")
    y -= 18
    put(10, y, "Controles: Mouse=orbita | Roda=zoom | p proj | [ ] FOV | - = Ortho | v viewport | t wire | d depth | c cull | r reset | ESC sair")

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    if use_depth:
        glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)


def render_scene():
    draw_grid(size=12, step=0.5)
    draw_axes(length=2.5, thickness=2.0)
    draw_object()


def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Viewport principal
    glViewport(0, 0, win_w, win_h)
    set_projection(win_w, win_h)
    set_camera()
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE if wireframe else GL_FILL)
    render_scene()

    # Viewport inset opcional (mostra outra projeção para comparar)
    if viewport_inset:
        inset_w = int(0.35 * win_w)
        inset_h = int(0.35 * win_h)
        inset_x = win_w - inset_w - 16
        inset_y = 16

        # Desenhar moldura do inset em modo 2D
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, win_w, 0, win_h, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glColor3f(0.9, 0.9, 0.95)
        glBegin(GL_LINE_LOOP)
        glVertex2f(inset_x - 2, inset_y - 2)
        glVertex2f(inset_x + inset_w + 2, inset_y - 2)
        glVertex2f(inset_x + inset_w + 2, inset_y + inset_h + 2)
        glVertex2f(inset_x - 2, inset_y + inset_h + 2)
        glEnd()
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        if use_depth:
            glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)

        # Alterna automaticamente a projeção no inset para comparação
        glViewport(inset_x, inset_y, inset_w, inset_h)
        # Usa a projeção oposta no inset
        orig_mode = proj_mode
        try:
            alt_mode = "ortho" if proj_mode == "persp" else "persp"
            # Configura projeção alternativa temporária
            save_mode = orig_mode
            globals()["proj_mode"] = alt_mode
            set_projection(inset_w, inset_h)
            set_camera()
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE if wireframe else GL_FILL)
            render_scene()
        finally:
            globals()["proj_mode"] = orig_mode

    draw_hud_text()
    glutSwapBuffers()


def reshape(w, h):
    global win_w, win_h
    win_w = max(1, w)
    win_h = max(1, h)
    glViewport(0, 0, win_w, win_h)


def mouse(button, state, x, y):
    global dragging, last_x, last_y, cam_distance
    if button == GLUT_LEFT_BUTTON:
        dragging = (state == GLUT_DOWN)
        last_x, last_y = x, y
    # Roda do mouse (3 = up, 4 = down em freeglut)
    if button == 3 and state == GLUT_DOWN:
        cam_distance = max(0.5, cam_distance * 0.9)
    elif button == 4 and state == GLUT_DOWN:
        cam_distance = min(100.0, cam_distance / 0.9)
    glutPostRedisplay()


def motion(x, y):
    global last_x, last_y, cam_yaw, cam_pitch
    if dragging:
        dx = x - last_x
        dy = y - last_y
        last_x, last_y = x, y
        cam_yaw = (cam_yaw + dx * 0.4) % 360.0
        cam_pitch = max(-89.9, min(89.9, cam_pitch - dy * 0.3))
        glutPostRedisplay()


def keyboard(key, x, y):
    global proj_mode, fov, ortho_scale, viewport_inset
    global wireframe, use_depth, use_cull, cam_distance
    k = key.decode("utf-8") if isinstance(key, bytes) else key

    if k == '\x1b':  # ESC
        glutLeaveMainLoop() if hasattr(glutLeaveMainLoop, "__call__") else exit(0)

    elif k == 'p':
        proj_mode = "ortho" if proj_mode == "persp" else "persp"

    elif k == '[':
        if proj_mode == "persp":
            fov = max(10.0, fov - 2.0)
    elif k == ']':
        if proj_mode == "persp":
            fov = min(120.0, fov + 2.0)

    elif k == '-':
        if proj_mode == "ortho":
            ortho_scale = max(0.5, ortho_scale * 0.92)
    elif k == '=':
        if proj_mode == "ortho":
            ortho_scale = min(50.0, ortho_scale / 0.92)

    elif k == 'v':
        viewport_inset = not viewport_inset

    elif k == 't':
        wireframe = not wireframe

    elif k == 'd':
        use_depth = not use_depth
        if use_depth:
            glEnable(GL_DEPTH_TEST)
        else:
            glDisable(GL_DEPTH_TEST)

    elif k == 'c':
        use_cull = not use_cull
        if use_cull:
            glEnable(GL_CULL_FACE)
        else:
            glDisable(GL_CULL_FACE)

    elif k == 'z':
        cam_distance = max(0.5, cam_distance * 0.92)
    elif k == 'Z':
        cam_distance = min(100.0, cam_distance / 0.92)

    elif k == 'r':
        reset_state()

    glutPostRedisplay()


def reset_state():
    global cam_distance, cam_yaw, cam_pitch, proj_mode
    global fov, near_plane, far_plane, ortho_scale
    global use_depth, use_cull, wireframe, viewport_inset

    cam_distance = 6.0
    cam_yaw = 35.0
    cam_pitch = 20.0
    proj_mode = "persp"
    fov = 60.0
    near_plane = 0.1
    far_plane = 200.0
    ortho_scale = 2.5
    use_depth = True
    use_cull = True
    wireframe = False
    viewport_inset = False
    if use_depth:
        glEnable(GL_DEPTH_TEST)
    if use_cull:
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)


def idle():
    glutPostRedisplay()


def main():
    print_instructions()
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH | GLUT_MULTISAMPLE)
    glutInitWindowSize(win_w, win_h)
    glutCreateWindow(b"PyOpenGL - Pipeline: Projection, View, Viewport (GL/GLU/GLUT)")
    init_gl()
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutMouseFunc(mouse)
    glutMotionFunc(motion)
    glutKeyboardFunc(keyboard)
    glutIdleFunc(idle)
    glutMainLoop()


if __name__ == "__main__":
    main()
