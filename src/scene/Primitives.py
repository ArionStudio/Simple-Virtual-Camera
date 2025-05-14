import numpy as np
import math

class Pyramid:
    def __init__(self, base_width, height, position):
        self.base_width = base_width
        self.height = height
        self.position = position
        self.vertices = self.calculate_vertices()
        
    def calculate_vertices(self):
        x, y, z = self.position
        w = self.base_width / 2
        h = self.height
        
        return np.array([
            # Base vertices (bottom square)
            [x - w, y, z - w, 1],  # 0: bottom-left
            [x + w, y, z - w, 1],  # 1: bottom-right
            [x + w, y, z + w, 1],  # 2: top-right
            [x - w, y, z + w, 1],  # 3: top-left
            
            # Apex
            [x, y + h, z, 1]       # 4: top point
        ])
    
    def transformVertices(self, matrix):
        for vertex in range(len(self.vertices)):
            self.vertices[vertex] = matrix @ self.vertices[vertex]
            
    def makeCopy(self):
        """Create a deep copy of the object"""
        copy = Pyramid(self.base_width, self.height, self.position)
        copy.vertices = self.vertices.copy()
        return copy

class Prism:
    def __init__(self, width, height, depth, position):
        self.width = width
        self.height = height
        self.depth = depth
        self.position = position
        self.vertices = self.calculate_vertices()
        
    def calculate_vertices(self):
        x, y, z = self.position
        w = self.width / 2
        h = self.height / 2
        d = self.depth / 2
        
        return np.array([
            # Bottom triangle
            [x, y - h, z - d, 1],      # 0: bottom front
            [x - w, y - h, z + d, 1],  # 1: bottom left
            [x + w, y - h, z + d, 1],  # 2: bottom right
            
            # Top triangle
            [x, y + h, z - d, 1],      # 3: top front
            [x - w, y + h, z + d, 1],  # 4: top left
            [x + w, y + h, z + d, 1],  # 5: top right
        ])
        
    def transformVertices(self, matrix):
        for vertex in range(len(self.vertices)):
            self.vertices[vertex] = matrix @ self.vertices[vertex]
            
    def makeCopy(self):
        """Create a deep copy of the object"""
        copy = Prism(self.width, self.height, self.depth, self.position)
        copy.vertices = self.vertices.copy()
        return copy

class Cylinder:
    def __init__(self, radius, height, position, segments=8):
        self.radius = radius
        self.height = height
        self.position = position
        self.segments = segments  # Number of sides for approximation
        self.vertices = self.calculate_vertices()
        
    def calculate_vertices(self):
        x, y, z = self.position
        r = self.radius
        h = self.height / 2
        
        vertices = []
        
        # Generate vertices for top and bottom circles
        for i in range(self.segments):
            angle = 2 * math.pi * i / self.segments
            
            # Bottom circle
            vertices.append([
                x + r * math.cos(angle),
                y - h,
                z + r * math.sin(angle),
                1
            ])
            
            # Top circle
            vertices.append([
                x + r * math.cos(angle),
                y + h,
                z + r * math.sin(angle),
                1
            ])
            
        # Center points for top and bottom caps
        vertices.append([x, y - h, z, 1])  # Bottom center
        vertices.append([x, y + h, z, 1])  # Top center
        
        return np.array(vertices)
        
    def transformVertices(self, matrix):
        for vertex in range(len(self.vertices)):
            self.vertices[vertex] = matrix @ self.vertices[vertex]
            
    def makeCopy(self):
        """Create a deep copy of the object"""
        copy = Cylinder(self.radius, self.height, self.position, self.segments)
        copy.vertices = self.vertices.copy()
        return copy
        
    def getFaces(self):
        """
        Returns the indices for each face of the cylinder.
        Each face is defined by vertex indices.
        """
        faces = []
        num_sides = self.segments
        
        # Bottom center is at vertices[-2], top center at vertices[-1]
        bottom_center_idx = len(self.vertices) - 2
        top_center_idx = len(self.vertices) - 1
        
        # Side faces (rectangles)
        for i in range(num_sides):
            bottom_idx = i * 2
            top_idx = i * 2 + 1
            next_bottom_idx = (i * 2 + 2) % (num_sides * 2)
            next_top_idx = (i * 2 + 3) % (num_sides * 2)
            
            faces.append([bottom_idx, next_bottom_idx, next_top_idx, top_idx])
            
        # Bottom cap (triangles)
        for i in range(num_sides):
            bottom_idx = i * 2
            next_bottom_idx = (i * 2 + 2) % (num_sides * 2)
            faces.append([bottom_idx, next_bottom_idx, bottom_center_idx])
            
        # Top cap (triangles)
        for i in range(num_sides):
            top_idx = i * 2 + 1
            next_top_idx = (i * 2 + 3) % (num_sides * 2)
            faces.append([top_idx, next_top_idx, top_center_idx])
            
        return faces

class Octahedron:
    def __init__(self, size, position):
        self.size = size
        self.position = position
        self.vertices = self.calculate_vertices()
        
    def calculate_vertices(self):
        x, y, z = self.position
        s = self.size
        
        return np.array([
            [x, y + s, z, 1],    # 0: top
            [x, y - s, z, 1],    # 1: bottom
            [x + s, y, z, 1],    # 2: right
            [x - s, y, z, 1],    # 3: left
            [x, y, z + s, 1],    # 4: front
            [x, y, z - s, 1],    # 5: back
        ])
        
    def transformVertices(self, matrix):
        for vertex in range(len(self.vertices)):
            self.vertices[vertex] = matrix @ self.vertices[vertex]
            
    def makeCopy(self):
        """Create a deep copy of the object"""
        copy = Octahedron(self.size, self.position)
        copy.vertices = self.vertices.copy()
        return copy 