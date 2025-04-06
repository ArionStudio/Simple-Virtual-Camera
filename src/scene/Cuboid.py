import numpy as np

class Cuboid():
  def __init__ (self, sizes: tuple[float, float, float], centerPosition: tuple[float, float, float]):
    self.sizes = sizes
    self.centerPosition = centerPosition
    self.vertices = self.calculateCuboidVertices()


  def calculateCuboidVertices(self):
    x, y, z = self.centerPosition
    w, h, d = self.sizes
    
    return np.array([
        [x - w/2, y - h/2, z - d/2, 1],
        [x + w/2, y - h/2, z - d/2, 1],
        [x - w/2, y + h/2, z - d/2, 1],
        [x + w/2, y + h/2, z - d/2, 1],
        [x - w/2, y - h/2, z + d/2, 1],
        [x + w/2, y - h/2, z + d/2, 1],
        [x - w/2, y + h/2, z + d/2, 1],
        [x + w/2, y + h/2, z + d/2, 1]
    ])
  

  def transformVertices(self, matrix: list[float]):
    for vertex in range(len(self.vertices)):
      self.vertices[vertex] = self.transformVertex(self.vertices[vertex], matrix)

  def transformVertex(self, vertex: tuple[float, float, float, float], matrix: list[float]):
    return matrix @ vertex

  def makeCopy(self):
    """Create a deep copy of the object"""
    copy = Cuboid(self.sizes, self.centerPosition)
    copy.vertices = self.vertices.copy()
    return copy

