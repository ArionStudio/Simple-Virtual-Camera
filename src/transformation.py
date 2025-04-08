import numpy as np

def radians(degrees: float) -> float:
  return degrees * np.pi / 180

def degrees(radians: float) -> float:
  return radians * 180 / np.pi

def getDefaultMatrix() -> list[float]:
  return np.array([
    [1, 0, 0, 0],
    [0, 1, 0, 0],
    [0, 0, 1, 0],
    [0, 0, 0, 1]
  ])

def getTranslationMatrix(position: tuple[float, float, float]) -> list[float]:
   return np.array([
      [1, 0, 0, position[0]],
      [0, 1, 0, position[1]],
      [0, 0, 1, position[2]],
      [0, 0, 0, 1]
   ])

def getScaleMatrix(scale: tuple[float, float, float]) -> list[float]:
   return np.array([
      [scale[0], 0, 0, 0],
      [0, scale[1], 0, 0],
      [0, 0, scale[2], 0],
      [0, 0, 0, 1]
   ])

def getXRotationMatrix(angle: float) -> list[float]:
  return np.array([
    [1, 0, 0, 0],
    [0, np.cos(angle), -np.sin(angle), 0],
    [0, np.sin(angle), np.cos(angle), 0],
    [0, 0, 0, 1]
  ])

def getYRotationMatrix(angle: float) -> list[float]:
  return np.array([
    [np.cos(angle), 0, np.sin(angle), 0],
    [0, 1, 0, 0],
    [-np.sin(angle), 0, np.cos(angle), 0],
    [0, 0, 0, 1]
  ])  

def getZRotationMatrix(angle: float) -> list[float]:
  return np.array([
    [np.cos(angle), -np.sin(angle), 0, 0],
    [np.sin(angle), np.cos(angle), 0, 0],
    [0, 0, 1, 0],
    [0, 0, 0, 1]
  ])

def getRotationMatrix(angles: tuple[float, float, float]) -> list[float]:
    # Convert angles from degrees to radians
    angleX = radians(angles[0])
    angleY = radians(angles[1])
    angleZ = radians(angles[2])
    
    # Create rotation matrices for each axis
    Rx = getXRotationMatrix(angleX)
    Ry = getYRotationMatrix(angleY)
    Rz = getZRotationMatrix(angleZ)
    
    # Rotation order: Y -> X -> Z (standard for camera)
    return Rz @ Rx @ Ry

def getViewMatrix(position: np.ndarray, rotation: np.ndarray) -> list[float]:
    """Creates a view matrix for camera at given position with rotation"""
    # First create rotation matrix for camera orientation
    # We negate the angles because we're rotating the world in opposite direction
    Rx = getXRotationMatrix(-np.radians(rotation[0]))
    Ry = getYRotationMatrix(-np.radians(rotation[1]))
    Rz = getZRotationMatrix(-np.radians(rotation[2]))
    
    # Combine rotations in correct order (Z * X * Y for camera)
    # This matches the order in rotateLocalMatrix
    R = Rz @ Rx @ Ry
    
    # Create translation matrix (move world in opposite direction of camera)
    T = getTranslationMatrix((-position[0], -position[1], -position[2]))
    
    # View matrix = R * T (first translate world, then rotate it)
    return R @ T

# Translation X, Y, Z functions
def translate(matrix: list[float], translationVector: tuple[float, float, float], isCamera: bool = False):
    """Apply translation to matrix. For camera transformations, set isCamera=True"""
    if isCamera:
        # For camera, translation is applied first (right multiply)
        return matrix @ getTranslationMatrix(translationVector)
    else:
        # For models, translation is applied last (left multiply)
        return getTranslationMatrix(translationVector) @ matrix

# Rotation on X, Y, Z functions
def rotate(matrix: list[float], rotationVector: tuple[float, float, float], isCamera: bool = False):
    """Apply rotation to matrix. For camera transformations, set isCamera=True"""
    if isCamera:
        # For camera, rotation is applied last (right multiply)
        return matrix @ getRotationMatrix(rotationVector)
    else:
        # For models, rotation is applied first (left multiply)
        return getRotationMatrix(rotationVector) @ matrix

# Scale X, Y, Z functions
def scale(matrix: list[float], scaleVector: tuple[float, float, float], isCamera: bool = False):
    """Apply scale to matrix. For camera transformations, set isCamera=True"""
    if isCamera:
        # For camera, scale is applied first (right multiply)
        return matrix @ getScaleMatrix(scaleVector)
    else:
        # For models, scale is applied last (left multiply)
        return getScaleMatrix(scaleVector) @ matrix




