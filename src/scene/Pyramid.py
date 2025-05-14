import numpy as np

class Pyramid():
    def __init__(self, base_size: float, height: float, centerPosition: tuple[float, float, float]):
        self.base_size = base_size
        self.height = height
        self.centerPosition = centerPosition
        self.vertices = self.calculatePyramidVertices()

    def calculatePyramidVertices(self):
        x, y, z = self.centerPosition
        w = self.base_size
        h = self.height
        
        # Calculate vertices
        # Base vertices (square base)
        base_y = y - h/2  # Base is centered at y - h/2
        
        # 5 vertices: 4 for the base and 1 for the apex
        return np.array([
            # Base vertices (counter-clockwise from bottom-left)
            [x - w/2, base_y, z - w/2, 1],  # Front-left
            [x + w/2, base_y, z - w/2, 1],  # Front-right
            [x + w/2, base_y, z + w/2, 1],  # Back-right
            [x - w/2, base_y, z + w/2, 1],  # Back-left
            # Apex (top vertex)
            [x, y + h/2, z, 1]
        ])
    
    def transformVertices(self, matrix: list[float]):
        for vertex in range(len(self.vertices)):
            self.vertices[vertex] = self.transformVertex(self.vertices[vertex], matrix)

    def transformVertex(self, vertex: tuple[float, float, float, float], matrix: list[float]):
        return matrix @ vertex

    def makeCopy(self):
        """Create a deep copy of the object"""
        copy = Pyramid(self.base_size, self.height, self.centerPosition)
        copy.vertices = self.vertices.copy()
        return copy 