import numpy as np

class Octahedron():
    def __init__(self, size: float, centerPosition: tuple[float, float, float]):
        self.size = size
        self.centerPosition = centerPosition
        self.vertices = self.calculateOctahedronVertices()

    def calculateOctahedronVertices(self):
        x, y, z = self.centerPosition
        s = self.size
        
        # An octahedron has 6 vertices: top, bottom, left, right, front, back
        return np.array([
            [x, y + s, z, 1],      # Top vertex
            [x, y - s, z, 1],      # Bottom vertex
            [x + s, y, z, 1],      # Right vertex
            [x - s, y, z, 1],      # Left vertex
            [x, y, z + s, 1],      # Front vertex
            [x, y, z - s, 1]       # Back vertex
        ])
    
    def transformVertices(self, matrix: list[float]):
        for vertex in range(len(self.vertices)):
            self.vertices[vertex] = self.transformVertex(self.vertices[vertex], matrix)

    def transformVertex(self, vertex: tuple[float, float, float, float], matrix: list[float]):
        return matrix @ vertex

    def makeCopy(self):
        """Create a deep copy of the object"""
        copy = Octahedron(self.size, self.centerPosition)
        copy.vertices = self.vertices.copy()
        return copy 