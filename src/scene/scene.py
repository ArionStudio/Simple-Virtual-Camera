from scene.Cuboid import Cuboid
from scene.Pyramid import Pyramid
from scene.Prism import Prism
from scene.Cylinder import Cylinder
from scene.Octahedron import Octahedron
import transformation
from typing import Union, Any

# Define a type for all supported objects
SceneObject = Union[Cuboid, Pyramid, Prism, Cylinder, Octahedron]

class Scene:
  def __init__(self):
    self.objects = []
    self.defualtEdgesInCuboid = [
      (0, 1), (1, 3), (3, 2), (2, 0),
      (4, 5), (5, 7), (7, 6), (6, 4),
      (0, 4), (1, 5), (2, 6), (3, 7)
    ]

  def addObject(self, object: SceneObject, position: tuple[float, float, float], rotation: tuple[float, float, float], scale: tuple[float, float, float]): 
    modelMatrix = self.createModelMatrix(position, rotation, scale)
    
    # Create a copy of the object based on its type
    objectCopy = self._createObjectCopy(object)
    
    # Apply transformation
    objectCopy.transformVertices(modelMatrix)
    self.objects.append(objectCopy)

  def _createObjectCopy(self, object: SceneObject) -> SceneObject:
    """Create a copy of the object based on its type"""
    if isinstance(object, Cuboid):
      return Cuboid(object.sizes, object.centerPosition)
    elif isinstance(object, Pyramid):
      return Pyramid(object.base_size, object.height, object.centerPosition)
    elif isinstance(object, Prism):
      return Prism(object.side_length, object.height, object.centerPosition)
    elif isinstance(object, Cylinder):
      return Cylinder(object.radius, object.height, object.segments, object.centerPosition)
    elif isinstance(object, Octahedron):
      return Octahedron(object.size, object.centerPosition)
    else:
      raise TypeError(f"Unsupported object type: {type(object)}")

  def removeObject(self, object: Any):
    self.objects.remove(object)

  def getObjects(self) -> list:
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
