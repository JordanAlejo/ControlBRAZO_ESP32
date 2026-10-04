# Brazo Robótico Dibujador

Sistema de simulación y control de un brazo robótico capaz de recibir números desde diferentes entradas, reconocer números mediante YOLO y reproducirlos mediante trazos en PyBullet.

---

## Descripción

El proyecto integra:

* **ESP32**
* **Teclado matricial**
* **Teclado del computador**
* **Python**
* **YOLO**
* **OpenCV**
* **PyBullet**
* **Comunicación Serial**

El objetivo es que el usuario pueda introducir o dibujar un número y que el sistema lo reconozca y envíe al brazo robótico para que lo reproduzca.

---

## Arquitectura

```text
                   ┌─────────────────┐
                   │     CÁMARA      │
                   └────────┬────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │      YOLO       │
                   │ Reconocimiento  │
                   │    0 - 9        │
                   └────────┬────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │      PYTHON     │
                   │ Procesamiento   │
                   └────────┬────────┘
                            │
                            │ Serial
                            ▼
                   ┌─────────────────┐
                   │      ESP32      │
                   │ Teclado /       │
                   │ Comunicación    │
                   └────────┬────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │     PYBULLET    │
                   │ Brazo robótico  │
                   └────────┬────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │ Número dibujado │
                   └─────────────────┘
```

---

# Estructura del proyecto

```text
Brazo-Robotico/
│
├── README.md
│
├── brazo.urdf
│
├── pybullet_dibujador.py
│
├── reconocer_numeros.py
│
├── esp32_teclado/
│   └── esp32_teclado.ino
│
├── YOLO/
│   ├── dataset/
│   │   ├── images/
│   │   └── labels/
│   │
│   ├── data.yaml
│   ├── train.py
│   └── best.pt
│
├── imagenes/
│   ├── arquitectura.png
│   ├── pybullet.png
│   ├── teclado_esp32.png
│   ├── reconocimiento_yolo.png
│   └── brazo_dibujando.png
│
└── requirements.txt
```

---

# Componentes principales

## 1. `brazo.urdf`

Archivo que define el modelo del brazo robótico utilizado en PyBullet.

Contiene:

* Links
* Joints
* Límites articulares
* Geometría
* Posición de los elementos
* Efector final

El brazo se carga desde Python mediante:

```python
p.loadURDF(...)
```

---

## 2. `pybullet_dibujador.py`

Es el programa principal de simulación.

Se encarga de:

* Abrir PyBullet.
* Cargar el brazo.
* Cargar el modelo `brazo.urdf`.
* Calcular la cinemática inversa.
* Mover el efector final.
* Dibujar los números.
* Borrar el número anterior.
* Recibir números desde el teclado del PC.
* Recibir números enviados por la ESP32.

### Flujo

```text
Entrada
   │
   ├── Teclado PC
   │
   └── ESP32
          │
          ▼
      Número 0-9
          │
          ▼
   Borrar número anterior
          │
          ▼
   Cinemática inversa
          │
          ▼
      Mover brazo
          │
          ▼
    Dibujar número
```

---

# 3. Teclado del computador

El programa de PyBullet puede recibir directamente números:

```text
0
1
2
3
4
5
6
7
8
9
```

Al recibir un nuevo número:

```text
Número anterior
       ↓
     BORRAR
       ↓
Nuevo número
       ↓
    DIBUJAR
```

La tecla:

```text
Q
```

permite cerrar el programa.

---

# 4. ESP32 + teclado

La ESP32 recibe las teclas del teclado matricial y envía el número mediante comunicación Serial.

Ejemplo:

```text
Teclado
   ↓
ESP32
   ↓
Serial
   ↓
PC
   ↓
PyBullet
```

La comunicación utiliza:

```text
Baudrate: 115200
```

Ejemplo de dato enviado:

```text
5
```

o:

```text
5\n
```

---

# 5. `esp32_teclado.ino`

Código encargado de:

* Configurar el teclado.
* Detectar la tecla presionada.
* Identificar los números.
* Enviar los datos por Serial.

Ejemplo:

```text
5 → ESP32 → Serial → PC
```

El código de Python recibe el dato y lo utiliza para controlar el brazo.

---

# 6. `reconocer_numeros.py`

Programa encargado del reconocimiento mediante YOLO.

Su funcionamiento es:

```text
Cámara
   ↓
OpenCV
   ↓
YOLO
   ↓
Número reconocido
   ↓
Comunicación Serial
   ↓
ESP32
   ↓
Brazo
```

El modelo debe reconocer las clases:

```text
0
1
2
3
4
5
6
7
8
9
```

---

# YOLO

El modelo utilizado debe estar entrenado específicamente para reconocer números.

Archivo principal:

```text
best.pt
```

El modelo recibe una imagen:

```text
Imagen
```

y devuelve:

```text
Número
Confianza
Posición
```

Ejemplo:

```text
5
92.4%
```

---

# Reconocimiento

El sistema utiliza una confianza mínima para evitar detecciones incorrectas.

Ejemplo:

```python
CONF_MINIMA = 0.75
```

Esto significa que una detección debe tener aproximadamente:

```text
75% o más
```

para ser enviada.

---

# Comunicación Serial

La comunicación entre Python y ESP32 utiliza:

```text
USB
Serial
115200 baud
```

Ejemplo:

```text
YOLO detecta:

5

        ↓

Python

        ↓

Serial

        ↓

ESP32

        ↓

5
```

---

# Puerto COM

El puerto de la ESP32 se configura en Python:

```python
PUERTO_ESP32 = "COM3"
```

Debe cambiarse según el puerto asignado por Windows.

Ejemplo:

```python
PUERTO_ESP32 = "COM5"
```

---

# Instalación

## Python

Se recomienda utilizar un entorno virtual.

```powershell
python -m venv venv
```

Activarlo:

```powershell
venv\Scripts\activate
```

Instalar dependencias:

```powershell
pip install pybullet
pip install pyserial
pip install opencv-python
pip install ultralytics
```

O utilizar:

```powershell
pip install -r requirements.txt
```

---

# Dependencias

Archivo:

```text
requirements.txt
```

Contenido recomendado:

```text
pybullet
pyserial
opencv-python
ultralytics
```

---

# Ejecución

## 1. ESP32

Abrir:

```text
esp32_teclado/esp32_teclado.ino
```

Seleccionar:

```text
Placa → ESP32
Puerto → COM correspondiente
```

Subir el programa.

---

## 2. PyBullet

Ejecutar:

```powershell
python pybullet_dibujador.py
```

Se abrirá la simulación.

El brazo podrá recibir:

```text
Teclado PC
```

o:

```text
ESP32
```

---

## 3. YOLO

Ejecutar:

```powershell
python reconocer_numeros.py
```

Se abrirá la cámara.

Cuando YOLO reconozca un número con suficiente confianza:

```text
Cámara
   ↓
YOLO
   ↓
Número
   ↓
Serial
   ↓
ESP32
   ↓
PyBullet
```

---

# Dataset YOLO

El modelo debe entrenarse utilizando imágenes de números.

Las clases son:

```text
0
1
2
3
4
5
6
7
8
9
```

Se recomienda utilizar diferentes:

* Tamaños
* Posiciones
* Inclinaciones
* Tipos de escritura
* Fondos
* Iluminaciones

---

# Estructura del Dataset

```text
dataset/
│
├── images/
│   ├── train/
│   └── val/
│
└── labels/
    ├── train/
    └── val/
```

Cada imagen debe tener su correspondiente archivo `.txt` de etiquetas.

---

# Archivo `data.yaml`

Ejemplo:

```yaml
path: ./dataset

train: images/train
val: images/val

names:
  0: "0"
  1: "1"
  2: "2"
  3: "3"
  4: "4"
  5: "5"
  6: "6"
  7: "7"
  8: "8"
  9: "9"
```

---

# Entrenamiento

Una vez preparado el dataset, se entrena el modelo YOLO.

El resultado principal será:

```text
best.pt
```

Este archivo debe colocarse en:

```text
YOLO/best.pt
```

o en la ubicación configurada en:

```python
MODELO = "best.pt"
```

---

# Imágenes del proyecto

## Arquitectura general

Agregar imagen:

```text
imagenes/arquitectura.png
```

![Arquitectura](imagenes/arquitectura.png)

---

## Brazo en PyBullet

Agregar imagen:

```text
imagenes/pybullet.png
```

![PyBullet](imagenes/pybullet.png)

---

## Teclado ESP32

Agregar imagen:

```text
imagenes/teclado_esp32.png
```

![Teclado ESP32](imagenes/teclado_esp32.png)

---

## Reconocimiento YOLO

Agregar imagen:

```text
imagenes/reconocimiento_yolo.png
```

![YOLO](imagenes/reconocimiento_yolo.png)

---

## Brazo dibujando

Agregar imagen:

```text
imagenes/brazo_dibujando.png
```

![Brazo dibujando](imagenes/brazo_dibujando.png)

---

# Flujo completo del sistema

```text
                 USUARIO
                    │
          ┌─────────┴─────────┐
          │                   │
          ▼                   ▼
     TECLADO PC          CÁMARA
          │                   │
          │                   ▼
          │                  YOLO
          │                   │
          │                   ▼
          │                 NÚMERO
          │                   │
          └─────────┬─────────┘
                    │
                    ▼
              PYTHON / SERIAL
                    │
                    ▼
                  ESP32
                    │
                    ▼
                NÚMERO 0-9
                    │
                    ▼
               PYBULLET
                    │
                    ▼
             CINEMÁTICA INVERSA
                    │
                    ▼
              BRAZO ROBÓTICO
                    │
                    ▼
             NÚMERO DIBUJADO
```

---

# Características

* [x] Simulación del brazo en PyBullet
* [x] Cinemática inversa
* [x] Dibujo de números
* [x] Números del 0 al 9
* [x] Eliminación del dibujo anterior
* [x] Control mediante teclado del PC
* [x] Control mediante ESP32
* [x] Comunicación Serial
* [x] Reconocimiento mediante YOLO
* [x] Reconocimiento mediante cámara
* [x] Envío automático del número detectado

---

# Tecnologías

| Tecnología | Función                 |
| ---------- | ----------------------- |
| Python     | Control principal       |
| PyBullet   | Simulación              |
| YOLO       | Reconocimiento          |
| OpenCV     | Cámara                  |
| ESP32      | Comunicación y teclado  |
| Serial     | Comunicación PC ↔ ESP32 |
| URDF       | Modelo del robot        |
| Git        | Control de versiones    |

---

# Autor

**Jordan Alejandro Rodriguez Torres**

Ingeniería Mecatrónica
Universidad Militar Nueva Granada

---

# Estado del proyecto

```text
Proyecto en desarrollo
```

Actualmente el sistema integra:

```text
YOLO
  +
ESP32
  +
Teclado
  +
Serial
  +
PyBullet
  +
Brazo robótico
```

El objetivo final es lograr el reconocimiento automático de un número dibujado y su reproducción mediante el brazo robótico simulado.
