import numpy as np

class Cylinder():
    def __init__(self, radius: float, height: float, segments: int, centerPosition: tuple[float, float, float]):
        self.radius = radius
        self.height = height
        self.segments = segments  # Number of segments to approximate the circle
        self.centerPosition = centerPosition
        self.vertices = self.calculateCylinderVertices()

    def calculateCylinderVertices(self):
        x, y, z = self.centerPosition
        r = self.radius
        h = self.height
        segments = self.segments
        
        # Calculate vertices
        vertices = []
        half_height = h / 2
        
        # Top and bottom circles
        for i in range(segments):
            angle = 2 * np.pi * i / segments
            
            # Bottom circle vertex
            bottom_x = x + r * np.cos(angle)
            bottom_z = z + r * np.sin(angle)
            vertices.append([bottom_x, y - half_height, bottom_z, 1])
            
            # Top circle vertex (same x,z as bottom)
            vertices.append([bottom_x, y + half_height, bottom_z, 1])
        
        # Add center points for top and bottom faces
        vertices.append([x, y - half_height, z, 1])  # Bottom center
        vertices.append([x, y + half_height, z, 1])  # Top center
        
        return np.array(vertices)
    
    def transformVertices(self, matrix: list[float]):
        for vertex in range(len(self.vertices)):
            self.vertices[vertex] = self.transformVertex(self.vertices[vertex], matrix)

    def transformVertex(self, vertex: tuple[float, float, float, float], matrix: list[float]):
        return matrix @ vertex

    def makeCopy(self):
        """Create a deep copy of the object"""
        copy = Cylinder(self.radius, self.height, self.segments, self.centerPosition)
        copy.vertices = self.vertices.copy()
        return copy 