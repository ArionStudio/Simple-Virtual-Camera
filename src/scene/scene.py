from scene.Cuboid import Cuboid
import transformation
class Scene:
  def __init__(self):
    self.objects = []
    self.defualtEdgesInCuboid = [
      (0, 1), (1, 3), (3, 2), (2, 0),
      (4, 5), (5, 7), (7, 6), (6, 4),
      (0, 4), (1, 5), (2, 6), (3, 7)
    ]

  def addObject(self, object: Cuboid, position: tuple[float, float, float], rotation: tuple[float, float, float], scale: tuple[float, float, float]): 
    modelMatrix = self.createModelMatrix(position, rotation, scale)
    # Create a copy of the object to avoid modifying the original
    objectCopy = Cuboid(object.sizes, object.centerPosition)
    objectCopy.transformVertices(modelMatrix)
    self.objects.append(objectCopy)

  def removeObject(self, object: Cuboid):
    self.objects.remove(object)

  def getObjects(self) -> list[Cuboid]:
    return self.objects

  def createModelMatrix(self, position: tuple[float, float, float], rotation: tuple[float, float, float], scale: tuple[float, float, float]) -> list[float]:
    """Creates a model matrix for object transformation"""
    modelMatrix = transformation.getDefaultMatrix()
    
    # Apply transformations in correct order:
    # 1. Scale (local space)
    # 2. Rotate (local space)
    # 3. Translate (world space)
    modelMatrix = transformation.scale(modelMatrix, scale)
    modelMatrix = transformation.rotate(modelMatrix, rotation)
    modelMatrix = transformation.translate(modelMatrix, position)
    
    return modelMatrix
