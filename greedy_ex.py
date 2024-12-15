import time
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Line3DCollection
from itertools import combinations, product

#Definimos propiedades de las cajas
class Box:
    def __init__(self, width, height, depth, value, weight, id):
        #Valores correspondientes a dimensiones espaciales
        self.width = width
        self.height = height
        self.depth = depth
        self.value = value #Valor de la caja
        self.weight = weight  #Peso
        self.id = id #Identificador de la caja
        # Definición de las posibles orientaciones de las cajas
        self.orientations = [
            (self.width, self.height, self.depth), #Orientaciones con pallet en la base
            (self.height, self.width, self.depth),
        ]
        # Calcular el volumen
        self.volume = self.width * self.height * self.depth
        # Calcular la densidad de valor (valor por volumen) -> Necesario para establecer ordenes de prioridad
        self.value_density = self.value / self.volume

#Definimos propiedades de los containers
class Container:
    def __init__(self, width, height, depth):
        self.width = width
        self.height = height
        self.depth = depth
        self.placed_boxes = []

    def can_place_box(self, box, x, y, z, orientation):
        box_width, box_height, box_depth = orientation #Asignamos los valores de orientacion de cada caja
        #Comprobamos que la caja no sobrepase limites de container
        if (x + box_width <= self.width and
            y + box_height <= self.height and
            z + box_depth <= self.depth):
            
            # Verificar si la caja se superpone con las cajas existentes
            for placed_box, (px, py, pz), placed_orientation in self.placed_boxes: #placed_boxes: lista de cajas colocadas
                pw, ph, pd = placed_orientation #Definimos dimensiones de caja colocada(anchura,altura y profundidad)
                #Condicionante que comprueba dimension por dimension la posicion
                if not (x >= px + pw or #(px,py,pz): coord esquina inf izq de una caja ya colocada
                        x + box_width <= px or
                        y >= py + ph or
                        y + box_height <= py or
                        z >= pz + pd or
                        z + box_depth <= pz):
                    return False
            return True
        return False

    def place_box(self, box, x, y, z, orientation):
        # Colocar la caja en la posición y orientación especificada
        self.placed_boxes.append((box, (x, y, z), orientation))

    def remove_last_box(self):
        # Eliminar la última caja colocada
        if self.placed_boxes:
            self.placed_boxes.pop()

    def calculate_total_value(self):
        # Calcular el valor total de las cajas colocadas
        return sum(box.value for box, _, _ in self.placed_boxes)

    def plot(self):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        # Dibujar el contenedor
        container_edges = [
            [(0, 0, 0), (self.width, 0, 0)],
            [(self.width, 0, 0), (self.width, self.height, 0)],
            [(self.width, self.height, 0), (0, self.height, 0)],
            [(0, self.height, 0), (0, 0, 0)],
            [(0, 0, self.depth), (self.width, 0, self.depth)],
            [(self.width, 0, self.depth), (self.width, self.height, self.depth)],
            [(self.width, self.height, self.depth), (0, self.height, self.depth)],
            [(0, self.height, self.depth), (0, 0, self.depth)],
            [(0, 0, 0), (0, 0, self.depth)],
            [(self.width, 0, 0), (self.width, 0, self.depth)],
            [(self.width, self.height, 0), (self.width, self.height, self.depth)],
            [(0, self.height, 0), (0, self.height, self.depth)]
        ]
        ax.add_collection3d(Line3DCollection(container_edges, colors='r', linewidths=1))

        # Dibujar las cajas colocadas solo con aristas
        for box, (x, y, z), orientation in self.placed_boxes:
            box_width, box_height, box_depth = orientation
            box_edges = [
                [(x, y, z), (x + box_width, y, z)],
                [(x + box_width, y, z), (x + box_width, y + box_height, z)],
                [(x + box_width, y + box_height, z), (x, y + box_height, z)],
                [(x, y + box_height, z), (x, y, z)],
                [(x, y, z + box_depth), (x + box_width, y, z + box_depth)],
                [(x + box_width, y, z + box_depth), (x + box_width, y + box_height, z + box_depth)],
                [(x + box_width, y + box_height, z + box_depth), (x, y + box_height, z + box_depth)],
                [(x, y + box_height, z + box_depth), (x, y, z + box_depth)],
                [(x, y, z), (x, y, z + box_depth)],
                [(x + box_width, y, z), (x + box_width, y, z + box_depth)],
                [(x + box_width, y + box_height, z), (x + box_width, y + box_height, z + box_depth)],
                [(x, y + box_height, z), (x, y + box_height, z + box_depth)]
            ]
            ax.add_collection3d(Line3DCollection(box_edges, colors='b', linewidths=1))

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')

        # Mostrar la figura
        plt.show()

def optimize_container(container, boxes):
    # Comenzamos el contador para saber el tiempo que tarda en encontrar la solución
    start_time = time.time()

    # Ordenar las cajas por peso en orden descendente (más pesadas primero)
    boxes = sorted(boxes, key=lambda box: box.weight, reverse=True)

    # Limpiar el contenedor para la nueva optimización
    container.placed_boxes.clear()
    
    # Lista para las cajas que no pudieron ser colocadas
    not_placed_boxes = []

    # Probar colocar cada caja en la mejor posición disponible usando el enfoque greedy
    for box in boxes:
        best_position = None
        best_orientation = None
        placed = False
        min_wasted_volume = float('inf')  # Iniciamos el volumen desperdiciado como muy alto

        # Probar todas las orientaciones posibles de la caja
        for orientation in box.orientations:
            box_width, box_height, box_depth = orientation
            
            # Probar todas las posiciones posibles en el contenedor, comenzando desde la base (z=0)
            for z in range(container.height):
                for y in range(container.depth):
                    for x in range(container.width):
                        if container.can_place_box(box, x, y, z, orientation):
                            # Calcular el volumen desperdiciado si colocamos la caja aquí
                            wasted_volume = (container.width * container.height * container.depth) - (box_width * box_height * box_depth)

                            # Si esta posición desperdicia menos volumen y está en la base o más abajo, la preferimos
                            if wasted_volume < min_wasted_volume and z == 0:  # Priorizamos las posiciones bajas
                                min_wasted_volume = wasted_volume
                                best_position = (x, y, z)
                                best_orientation = orientation
                                placed = True
                                
                            # Si z > 0 (es decir, la caja no está en la base), también podemos colocar si es eficiente
                            elif wasted_volume < min_wasted_volume and z > 0:
                                min_wasted_volume = wasted_volume
                                best_position = (x, y, z)
                                best_orientation = orientation
                                placed = True
        
        # Si encontramos la mejor posición y orientación, colocamos la caja
        if best_position and best_orientation:
            container.place_box(box, *best_position, best_orientation)
        else:
            # Si no encontramos lugar adecuado, añadimos la caja a la lista de no colocadas
            not_placed_boxes.append(box)

    # Calcular el valor total de las cajas colocadas en el contenedor
    total_value = container.calculate_total_value()

    # Detenemos temporizador y presentamos tiempo total de ejecución
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Tiempo total de ejecución: {elapsed_time:.2f} segundos")

    # Devolvemos el valor total y las cajas que no pudieron colocarse
    return total_value, not_placed_boxes


# Función para colocar una lista de cajas en el contenedor usando enfoque greedy
def place_boxes_in_container(container, boxes, orientations):
    for box, orientation in zip(boxes, orientations):  # Emparejamos cada caja con su orientación
        placed = False  # Establecemos si la caja ha sido colocada o no
        # Probar todas las posiciones posibles en el contenedor, comenzando desde la base (z=0)
        for z in range(container.height):  # Comenzamos el bucle desde la base
            for y in range(container.depth):  # Colocamos desde el frente hacia el fondo
                for x in range(container.width):  # Colocamos de izquierda a derecha
                    if container.can_place_box(box, x, y, z, orientation):
                        container.place_box(box, x, y, z, orientation)
                        placed = True  # La caja ha sido colocada, rompemos los bucles
                        break
                if placed:
                    break
            if placed:
                break
        if not placed:
            return False  # Si alguna caja no se puede colocar, fallar
    return True  # Si todas se colocan, devolvemos True

# Ejemplo de uso
boxes = [
    # Cajas de peso pesado (peso > 15)
    Box(3, 4, 2, 100, 20, "Caja 1"),   # Caja 1: Peso 20, dimensiones (3x4x2)
    Box(5, 2, 3, 90, 18, "Caja 2"),    # Caja 2: Peso 18, dimensiones (5x2x3)
    Box(4, 4, 4, 120, 22, "Caja 3"),   # Caja 3: Peso 22, dimensiones (4x4x4)
    Box(3, 3, 6, 110, 21, "Caja 4"),   # Caja 4: Peso 21, dimensiones (3x3x6)
    Box(2, 5, 3, 95, 19, "Caja 5"),    # Caja 5: Peso 19, dimensiones (2x5x3)
    Box(3, 6, 3, 115, 23, "Caja 6"),   # Caja 6: Peso 23, dimensiones (3x6x3)

    # Cajas de peso medio (peso entre 10 y 15)
    Box(2, 3, 4, 60, 12, "Caja 7"),    # Caja 7: Peso 12, dimensiones (2x3x4)
    Box(3, 4, 2, 65, 14, "Caja 8"),    # Caja 8: Peso 14, dimensiones (3x4x2)
    Box(5, 3, 2, 75, 15, "Caja 9"),    # Caja 9: Peso 15, dimensiones (5x3x2)
    Box(4, 2, 3, 70, 13, "Caja 10"),   # Caja 10: Peso 13, dimensiones (4x2x3)
    Box(2, 2, 4, 55, 11, "Caja 11"),   # Caja 11: Peso 11, dimensiones (2x2x4)
    Box(3, 3, 3, 85, 14, "Caja 12"),   # Caja 12: Peso 14, dimensiones (3x3x3)
    Box(2, 4, 3, 80, 13, "Caja 13"),   # Caja 13: Peso 13, dimensiones (2x4x3)
    Box(4, 3, 2, 77, 14, "Caja 14"),   # Caja 14: Peso 14, dimensiones (4x3x2)
    Box(3, 5, 2, 82, 15, "Caja 15"),   # Caja 15: Peso 15, dimensiones (3x5x2)

    # Cajas de peso ligero (peso < 10)
    Box(2, 3, 2, 40, 8, "Caja 16"),    # Caja 16: Peso 8, dimensiones (2x3x2)
    Box(1, 3, 3, 45, 9, "Caja 17"),    # Caja 17: Peso 9, dimensiones (1x3x3)
    Box(2, 2, 2, 35, 7, "Caja 18"),    # Caja 18: Peso 7, dimensiones (2x2x2)
    Box(3, 2, 1, 30, 6, "Caja 19"),    # Caja 19: Peso 6, dimensiones (3x2x1)
    Box(1, 2, 3, 25, 5, "Caja 20"),    # Caja 20: Peso 5, dimensiones (1x2x3)
    Box(2, 1, 1, 20, 4, "Caja 21"),    # Caja 21: Peso 4, dimensiones (2x1x1)
    Box(2, 1, 2, 28, 7, "Caja 22"),    # Caja 22: Peso 7, dimensiones (2x1x2)
    Box(1, 3, 2, 32, 8, "Caja 23"),    # Caja 23: Peso 8, dimensiones (1x3x2)
    Box(2, 2, 1, 27, 6, "Caja 24"),    # Caja 24: Peso 6, dimensiones (2x2x1)
    Box(1, 1, 2, 22, 5, "Caja 25"),    # Caja 25: Peso 5, dimensiones (1x1x2)
    Box(2, 1, 3, 35, 9, "Caja 26"),    # Caja 26: Peso 9, dimensiones (2x1x3)
    Box(1, 2, 2, 33, 8, "Caja 27"),    # Caja 27: Peso 8, dimensiones (1x2x2)
    Box(2, 1, 1, 26, 5, "Caja 28"),    # Caja 28: Peso 5, dimensiones (2x1x1)
    Box(1, 1, 1, 20, 4, "Caja 29"),    # Caja 29: Peso 4, dimensiones (1x1x1)
    Box(3, 2, 2, 38, 9, "Caja 30")     # Caja 30: Peso 9, dimensiones (3x2x2)
]


container = Container(8, 8, 8) # Definición de las dimensiones del container

# Optimizar la colocación de cajas en el contenedor
best_value, not_placed = optimize_container(container, boxes)

# Visualizar el contenedor con la mejor combinación de cajas
print(f"Mejor valor total: {best_value}")
print(f"Número de cajas no colocadas: {len(not_placed)}")  # Mostrar cuántas cajas no fueron colocadas
print(f"Cajas no colocadas: {[box.id for box in not_placed]}")
container.plot()
