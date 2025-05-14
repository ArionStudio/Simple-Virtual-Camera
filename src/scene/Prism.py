import numpy as np

class Prism():
    def __init__(self, side_length: float, height: float, centerPosition: tuple[float, float, float]):
        self.side_length = side_length
        self.height = height
        self.centerPosition = centerPosition
        self.vertices = self.calculatePrismVertices()

    def calculatePrismVertices(self):
        x, y, z = self.centerPosition
        s = self.side_length
        h = self.height
        
        # Calculate height of the equilateral triangle
        triangle_height = (np.sqrt(3) / 2) * s
        
        # Calculate vertices
        # 6 vertices: 3 for the bottom base and 3 for the top base
        half_height = h / 2
        
        return np.array([
            # Bottom base (triangular, counter-clockwise from front)
            [x, y - half_height, z + (2 * triangle_height / 3), 1],              # Front
            [x - s/2, y - half_height, z - (triangle_height / 3), 1],            # Back-left
            [x + s/2, y - half_height, z - (triangle_height / 3), 1],            # Back-right
            
            # Top base (triangular, same orientation as bottom)
            [x, y + half_height, z + (2 * triangle_height / 3), 1],              # Front
            [x - s/2, y + half_height, z - (triangle_height / 3), 1],            # Back-left
            [x + s/2, y + half_height, z - (triangle_height / 3), 1]             # Back-right
        ])
    
    def transformVertices(self, matrix: list[float]):
        for vertex in range(len(self.vertices)):
            self.vertices[vertex] = self.transformVertex(self.vertices[vertex], matrix)

    def transformVertex(self, vertex: tuple[float, float, float, float], matrix: list[float]):
        return matrix @ vertex

    def makeCopy(self):
        """Create a deep copy of the object"""
        copy = Prism(self.side_length, self.height, self.centerPosition)
        copy.vertices = self.vertices.copy()
        return copy 