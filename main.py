
import pybullet as p
import pybullet_data
import os
import time
import traceback
import math
import serial
import serial.tools.list_ports
import msvcrt


# ============================================================
# CONFIGURACIÓN
# ============================================================

CARPETA = os.path.dirname(os.path.abspath(__file__))

URDF = os.path.join(
    CARPETA,
    "brazo.urdf"
)


# ============================================================
# CONFIGURACIÓN ESP32
# ============================================================

# CAMBIA ESTO SI TU ESP32 ESTÁ EN OTRO PUERTO
PUERTO_ESP32 = "COM3"

# Velocidad Serial
BAUDRATE = 115200

esp32 = None


# ============================================================
# POSICIÓN DEL ROBOT
# ============================================================

ROBOT_X = 1.35
ROBOT_Y = -0.70
ROBOT_Z = 0.0

ROBOT_POS = [
    ROBOT_X,
    ROBOT_Y,
    ROBOT_Z
]


# ============================================================
# PUNTA DEL BRAZO
# ============================================================

END_EFFECTOR = 4


# ============================================================
# CONFIGURACIÓN DEL DIBUJO
# ============================================================

# El dibujo está al frente del robot.

DRAW_Y = ROBOT_Y + 0.45

DRAW_X = ROBOT_X + 0.25

DRAW_Z = 0.30

NUMBER_WIDTH = 0.28

NUMBER_HEIGHT = 0.40

PEN_LIFT_HEIGHT = 0.05


# ============================================================
# LISTA DE LÍNEAS DEL DIBUJO
# ============================================================

# Aquí guardaremos todas las líneas que pertenecen
# al número actual.

lineas_dibujo = []


# ============================================================
# CONECTAR ESP32
# ============================================================

def conectar_esp32():

    global esp32

    print()
    print("========================================")
    print("        CONECTANDO CON ESP32")
    print("========================================")
    print()

    try:

        esp32 = serial.Serial(
            PUERTO_ESP32,
            BAUDRATE,
            timeout=0
        )

        time.sleep(2)

        esp32.reset_input_buffer()

        print("ESP32 conectada correctamente.")
        print("Puerto:", PUERTO_ESP32)
        print("Baudrate:", BAUDRATE)
        print()

    except Exception as error:

        print("No se pudo conectar con la ESP32.")
        print()
        print("Puerto configurado:", PUERTO_ESP32)
        print()
        print("Puedes revisar los puertos disponibles:")
        print()

        puertos = serial.tools.list_ports.comports()

        if len(puertos) == 0:

            print("No se encontraron puertos COM.")

        else:

            for puerto in puertos:

                print(
                    puerto.device,
                    "|",
                    puerto.description
                )

        print()
        print("PyBullet continuará funcionando solamente")
        print("con el teclado del computador.")
        print()

        esp32 = None


# ============================================================
# LEER ESP32
# ============================================================

def leer_esp32():

    if esp32 is None:
        return None

    try:

        if esp32.in_waiting > 0:

            dato = esp32.readline().decode(
                "utf-8",
                errors="ignore"
            ).strip()

            if dato:

                # Buscar solamente números 0-9
                for caracter in dato:

                    if caracter in "0123456789":

                        return caracter

    except Exception as error:

        print()
        print("Error leyendo ESP32:")
        print(error)
        print()

    return None


# ============================================================
# LEER TECLADO DEL COMPUTADOR
# ============================================================

def leer_teclado_pc():

    if msvcrt.kbhit():

        tecla = msvcrt.getch()

        try:

            tecla = tecla.decode(
                "utf-8"
            )

        except:

            return None

        return tecla

    return None


# ============================================================
# BORRAR DIBUJO ANTERIOR
# ============================================================

def borrar_dibujo():

    global lineas_dibujo

    if len(lineas_dibujo) == 0:
        return

    print()
    print("Borrando número anterior...")

    for linea in lineas_dibujo:

        try:

            p.removeUserDebugItem(
                linea
            )

        except:

            pass

    lineas_dibujo.clear()

    print("Número anterior eliminado.")
    print()


# ============================================================
# CONECTAR PYBULLET
# ============================================================

print("========================================")
print("       INICIANDO PYBULLET")
print("========================================")
print()


if not os.path.exists(URDF):

    print("ERROR:")
    print("No se encontró:")

    print(URDF)

    input(
        "Presiona ENTER para cerrar..."
    )

    raise SystemExit


try:

    # ========================================================
    # CONEXIÓN PYBULLET
    # ========================================================

    p.connect(
        p.GUI
    )

    p.setAdditionalSearchPath(
        pybullet_data.getDataPath()
    )

    p.resetSimulation()

    p.setGravity(
        0,
        0,
        -9.81
    )


    # ========================================================
    # PISO
    # ========================================================

    p.loadURDF(
        "plane.urdf"
    )


    # ========================================================
    # CARGAR BRAZO
    # ========================================================

    robot = p.loadURDF(
        URDF,
        ROBOT_POS,
        useFixedBase=True
    )


    # ========================================================
    # INFORMACIÓN DEL ROBOT
    # ========================================================

    cantidad_joints = p.getNumJoints(
        robot
    )

    print()
    print("========================================")
    print("       BRAZO CARGADO CORRECTAMENTE")
    print("========================================")
    print()

    print(
        "Cantidad de joints:",
        cantidad_joints
    )

    print()

    for i in range(cantidad_joints):

        info = p.getJointInfo(
            robot,
            i
        )

        nombre = info[1].decode(
            "utf-8"
        )

        print(
            "Joint",
            i,
            "|",
            nombre,
            "| tipo:",
            info[2]
        )

    print()


    # ========================================================
    # CREAR TABLERO
    # ========================================================

    tablero_collision = p.createCollisionShape(
        p.GEOM_BOX,
        halfExtents=[
            NUMBER_WIDTH * 2,
            0.015,
            NUMBER_HEIGHT * 1.5
        ]
    )

    tablero_visual = p.createVisualShape(
        p.GEOM_BOX,
        halfExtents=[
            NUMBER_WIDTH * 2,
            0.015,
            NUMBER_HEIGHT * 1.5
        ],
        rgbaColor=[
            0.85,
            0.85,
            0.85,
            1
        ]
    )

    p.createMultiBody(
        baseMass=0,
        baseCollisionShapeIndex=tablero_collision,
        baseVisualShapeIndex=tablero_visual,
        basePosition=[
            DRAW_X,
            DRAW_Y + 0.03,
            DRAW_Z + NUMBER_HEIGHT / 2
        ]
    )


    # ========================================================
    # POSICIÓN DE LA PUNTA
    # ========================================================

    def obtener_posicion_punta():

        estado = p.getLinkState(
            robot,
            END_EFFECTOR,
            computeForwardKinematics=True
        )

        return estado[4]


    # ========================================================
    # MOVER BRAZO
    # ========================================================

    def mover_a(x, y, z):

        angulos = p.calculateInverseKinematics(
            robot,
            END_EFFECTOR,
            [
                x,
                y,
                z
            ]
        )

        for i in range(
            min(
                len(angulos),
                cantidad_joints
            )
        ):

            p.setJointMotorControl2(
                bodyIndex=robot,
                jointIndex=i,
                controlMode=p.POSITION_CONTROL,
                targetPosition=angulos[i],
                force=500
            )


    # ========================================================
    # MOVER Y ESPERAR
    # ========================================================

    def ir_a_punto(x, y, z):

        mover_a(
            x,
            y,
            z
        )

        for _ in range(25):

            p.stepSimulation()

            time.sleep(
                1 / 240
            )


    # ========================================================
    # PUNTO DE DIBUJO
    # ========================================================

    def punto(x, z):

        return [
            DRAW_X + x,
            DRAW_Y,
            DRAW_Z + z
        ]


    # ========================================================
    # DIBUJAR TRAZO
    # ========================================================

    def dibujar_trazo(puntos):

        global lineas_dibujo

        if len(puntos) < 2:
            return


        # ----------------------------------------------------
        # PRIMER PUNTO
        # ----------------------------------------------------

        primero = puntos[0]

        ir_a_punto(
            primero[0],
            primero[1],
            primero[2]
        )


        # ----------------------------------------------------
        # VARIABLE ANTERIOR
        # ----------------------------------------------------

        anterior = primero


        # ----------------------------------------------------
        # DIBUJAR CADA SEGMENTO
        # ----------------------------------------------------

        for actual in puntos[1:]:

            pasos = 15

            punto_anterior = list(
                anterior
            )

            for i in range(
                1,
                pasos + 1
            ):

                t = i / pasos

                x = (
                    anterior[0]
                    +
                    (actual[0] - anterior[0]) * t
                )

                y = (
                    anterior[1]
                    +
                    (actual[1] - anterior[1]) * t
                )

                z = (
                    anterior[2]
                    +
                    (actual[2] - anterior[2]) * t
                )

                ir_a_punto(
                    x,
                    y,
                    z
                )


                # --------------------------------------------
                # CREAR LÍNEA PERMANENTE
                # --------------------------------------------

                linea = p.addUserDebugLine(
                    punto_anterior,
                    [
                        x,
                        y,
                        z
                    ],
                    lineWidth=5,
                    lifeTime=0
                )

                # Guardamos la línea para poder borrarla
                lineas_dibujo.append(
                    linea
                )

                punto_anterior = [
                    x,
                    y,
                    z
                ]

            anterior = actual


    # ========================================================
    # TRAZO LOCAL
    # ========================================================

    def trazo_local(lista):

        puntos = []

        for x, z in lista:

            puntos.append(
                punto(
                    x,
                    z
                )
            )

        dibujar_trazo(
            puntos
        )


    # ========================================================
    # NÚMERO 0
    # ========================================================

    def numero_0():

        puntos = []

        pasos = 40

        for i in range(
            pasos + 1
        ):

            angulo = (
                2
                * math.pi
                * i
                / pasos
            )

            x = (
                NUMBER_WIDTH / 2
                * 0.75
                * math.cos(
                    angulo
                )
            )

            z = (
                NUMBER_HEIGHT / 2
                * math.sin(
                    angulo
                )
            )

            puntos.append(
                punto(
                    x,
                    z + NUMBER_HEIGHT / 2
                )
            )

        dibujar_trazo(
            puntos
        )


    # ========================================================
    # NÚMERO 1
    # ========================================================

    def numero_1():

        trazo_local([
            (-0.07, NUMBER_HEIGHT),
            (0.00, NUMBER_HEIGHT + 0.05),
            (0.00, 0.00)
        ])

        trazo_local([
            (-0.10, 0.00),
            (0.10, 0.00)
        ])


    # ========================================================
    # NÚMERO 2
    # ========================================================

    def numero_2():

        trazo_local([
            (-0.13, NUMBER_HEIGHT),
            (0.10, NUMBER_HEIGHT),
            (0.13, NUMBER_HEIGHT - 0.06),
            (-0.13, 0.02),
            (0.13, 0.02)
        ])


    # ========================================================
    # NÚMERO 3
    # ========================================================

    def numero_3():

        trazo_local([
            (-0.10, NUMBER_HEIGHT),
            (0.10, NUMBER_HEIGHT),
            (0.12, NUMBER_HEIGHT - 0.10),
            (0.00, NUMBER_HEIGHT / 2),
            (0.12, NUMBER_HEIGHT / 2 - 0.05),
            (0.10, 0.00),
            (-0.10, 0.00)
        ])


    # ========================================================
    # NÚMERO 4
    # ========================================================

    def numero_4():

        trazo_local([
            (0.08, 0.00),
            (0.08, NUMBER_HEIGHT)
        ])

        trazo_local([
            (0.08, 0.00),
            (-0.13, 0.00),
            (0.03, NUMBER_HEIGHT)
        ])


    # ========================================================
    # NÚMERO 5
    # ========================================================

    def numero_5():

        trazo_local([
            (0.12, NUMBER_HEIGHT),
            (-0.12, NUMBER_HEIGHT),
            (-0.12, NUMBER_HEIGHT / 2),
            (0.10, NUMBER_HEIGHT / 2),
            (0.13, NUMBER_HEIGHT / 2 - 0.05),
            (0.10, 0.00),
            (-0.12, 0.00)
        ])


    # ========================================================
    # NÚMERO 6
    # ========================================================

    def numero_6():

        trazo_local([
            (0.10, NUMBER_HEIGHT),
            (-0.08, NUMBER_HEIGHT),
            (-0.13, 0.10),
            (-0.05, 0.00),
            (0.10, 0.00),
            (0.13, 0.06),
            (0.10, NUMBER_HEIGHT / 2),
            (-0.10, NUMBER_HEIGHT / 2)
        ])


    # ========================================================
    # NÚMERO 7
    # ========================================================

    def numero_7():

        trazo_local([
            (-0.13, NUMBER_HEIGHT),
            (0.13, NUMBER_HEIGHT),
            (-0.02, 0.00)
        ])


    # ========================================================
    # NÚMERO 8
    # ========================================================

    def numero_8():

        trazo_local([
            (0.00, NUMBER_HEIGHT),
            (-0.10, NUMBER_HEIGHT),
            (-0.10, NUMBER_HEIGHT / 2),
            (0.10, NUMBER_HEIGHT / 2),
            (0.10, NUMBER_HEIGHT),
            (0.00, NUMBER_HEIGHT),
            (-0.10, NUMBER_HEIGHT / 2),
            (-0.10, 0.00),
            (0.10, 0.00),
            (0.10, NUMBER_HEIGHT / 2)
        ])


    # ========================================================
    # NÚMERO 9
    # ========================================================

    def numero_9():

        trazo_local([
            (-0.10, NUMBER_HEIGHT / 2),
            (-0.10, NUMBER_HEIGHT),
            (0.10, NUMBER_HEIGHT),
            (0.12, NUMBER_HEIGHT / 2),
            (0.00, NUMBER_HEIGHT / 2),
            (-0.10, NUMBER_HEIGHT / 2)
        ])

        trazo_local([
            (0.10, NUMBER_HEIGHT / 2),
            (0.10, 0.00)
        ])


    # ========================================================
    # DICCIONARIO
    # ========================================================

    numeros = {

        "0": numero_0,
        "1": numero_1,
        "2": numero_2,
        "3": numero_3,
        "4": numero_4,
        "5": numero_5,
        "6": numero_6,
        "7": numero_7,
        "8": numero_8,
        "9": numero_9

    }


    # ========================================================
    # CONECTAR ESP32
    # ========================================================

    conectar_esp32()


    # ========================================================
    # MENÚ
    # ========================================================

    print()
    print("========================================")
    print("          BRAZO DIBUJADOR")
    print("========================================")
    print()

    print("ENTRADAS DISPONIBLES:")
    print()

    print("1. Teclado del computador")
    print("2. Teclado conectado a ESP32")
    print()

    print("Números disponibles: 0 - 9")
    print()

    print("Presiona Q en el computador para salir.")
    print()

    print("========================================")
    print()


    # ========================================================
    # BUCLE PRINCIPAL
    # ========================================================

    while True:


        # ====================================================
        # ACTUALIZAR PYBULLET
        # ====================================================

        p.stepSimulation()


        # ====================================================
        # REVISAR TECLADO PC
        # ====================================================

        numero_pc = leer_teclado_pc()


        if numero_pc is not None:

            numero_pc = numero_pc.strip()


            # ------------------------------------------------
            # SALIR
            # ------------------------------------------------

            if numero_pc.lower() == "q":

                print()
                print("Cerrando programa...")
                break


            # ------------------------------------------------
            # NÚMERO DESDE PC
            # ------------------------------------------------

            if numero_pc in numeros:

                print()
                print(
                    "Número recibido desde PC:",
                    numero_pc
                )

                # BORRAR ANTES DE DIBUJAR
                borrar_dibujo()

                print(
                    "Dibujando:",
                    numero_pc
                )

                print()

                numeros[
                    numero_pc
                ]()

                print()
                print(
                    "Número",
                    numero_pc,
                    "terminado."
                )
                print()


        # ====================================================
        # REVISAR ESP32
        # ====================================================

        numero_esp32 = leer_esp32()


        if numero_esp32 is not None:

            print()
            print(
                "Número recibido desde ESP32:",
                numero_esp32
            )

            # BORRAR ANTES DE DIBUJAR
            borrar_dibujo()

            print(
                "Dibujando:",
                numero_esp32
            )

            print()

            numeros[
                numero_esp32
            ]()

            print()
            print(
                "Número",
                numero_esp32,
                "terminado."
            )
            print()


        # ====================================================
        # PEQUEÑA PAUSA
        # ====================================================

        time.sleep(
            1 / 240
        )


except Exception as error:

    print()
    print("========================================")
    print("              ERROR")
    print("========================================")
    print()

    print(error)

    print()
    print("DETALLES:")
    print()

    traceback.print_exc()

    print()

    input(
        "Presiona ENTER para cerrar..."
    )


finally:

    try:

        if esp32 is not None:

            esp32.close()

    except:

        pass


    try:

        p.disconnect()

    except:

        pass