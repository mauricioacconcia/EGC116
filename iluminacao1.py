from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

angle = 0.0
mode = 1  # modo de iluminação/shading

def init():
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

    glLightfv(GL_LIGHT0, GL_POSITION, [1.0, 1.0, 1.0, 0.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])

def set_lighting():
    glDisable(GL_LIGHT1)
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.1, 0.1, 0.1, 1.0])
    glLightModeli(GL_LIGHT_MODEL_LOCAL_VIEWER, GL_FALSE)
    glShadeModel(GL_SMOOTH)

    if mode == 1:
        # Iluminação simples (Lambert)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [0.0, 0.0, 0.0, 1.0])
        glShadeModel(GL_SMOOTH)

    elif mode == 2:
        # Phong / Blinn-Phong (com brilho)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.9, 0.9, 0.9, 1.0])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 64.0)
        glLightModeli(GL_LIGHT_MODEL_LOCAL_VIEWER, GL_TRUE)

    elif mode == 3:
        # Flat shading
        glShadeModel(GL_FLAT)

    elif mode == 4:
        # Smooth shading (Gouraud)
        glShadeModel(GL_SMOOTH)

    elif mode == 5:
        # Fake global: ambiente + duas luzes
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.3, 0.3, 0.3, 1.0])
        glEnable(GL_LIGHT1)
        glLightfv(GL_LIGHT1, GL_POSITION, [-1.0, -1.0, 0.5, 0.0])
        glLightfv(GL_LIGHT1, GL_DIFFUSE, [0.4, 0.4, 0.4, 1.0])
        glLightfv(GL_LIGHT1, GL_SPECULAR, [0.3, 0.3, 0.3, 1.0])

def draw_scene():
    glPushMatrix()
    glTranslatef(-1.5, 0.0, 0.0)
    glColor3f(0.8, 0.6, 0.3)
    glutSolidSphere(1.0, 50, 50)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(1.5, 0.0, 0.0)
    glColor3f(0.4, 0.7, 1.0)
    glutSolidTeapot(1.0)
    glPopMatrix()

def display():
    global angle
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    gluLookAt(0, 0, 6, 0, 0, 0, 0, 1, 0)

    glRotatef(angle, 0, 1, 0)
    set_lighting()
    draw_scene()

    glutSwapBuffers()
    angle += 0.05

def reshape(w, h):
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, w / h, 1.0, 50.0)
    glMatrixMode(GL_MODELVIEW)

def keyboard(key, x, y):
    global mode
    if key in [b'1', b'2', b'3', b'4', b'5']:
        mode = int(key.decode())
        print(f"Modo {mode} selecionado.")
    elif key == b'\x1b':  # ESC
        exit(0)

glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
glutInitWindowSize(800, 600)
glutCreateWindow(b"Modelos de Iluminacao e Shading (1-5)")
init()
glutDisplayFunc(display)
glutIdleFunc(display)
glutReshapeFunc(reshape)
glutKeyboardFunc(keyboard)
glutMainLoop()
