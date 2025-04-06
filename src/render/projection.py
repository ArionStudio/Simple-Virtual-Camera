from camera.camera import Camera
from scene.scene import Scene
from scene.Cuboid import Cuboid
import numpy as np

class Projection:
  def __init__(self, camera: Camera, scene: Scene):
    self.camera = camera
    self.scene = scene

  def projectCameraObjects(self):
    self.objects = []
    projectionMatrix = self.getProjectionMatrix()
    viewMatrix = self.getViewMatrix()

    for obj in self.scene.getObjects():
      # Create a deep copy and apply transformations
      objCopy = obj.makeCopy()
      objCopy.transformVertices(projectionMatrix @ viewMatrix)
      self.objects.append(objCopy)

  def getProjectionMatrix(self) -> np.ndarray:
    """Creates a perspective projection matrix"""
    fovRad = np.radians(self.camera.fov)
    f = 1.0 / np.tan(fovRad / 2)
    aspect = self.camera.aspectRatio
    near = self.camera.near
    far = self.camera.far
    
    # Calculate projection matrix components for better depth handling
    a = -(far + near) / (far - near)
    b = -(2 * far * near) / (far - near)
    
    return np.array([
        [f / aspect, 0, 0, 0],
        [0, f, 0, 0],
        [0, 0, a, b],
        [0, 0, -1, 0]
    ])

  def getViewMatrix(self) -> np.ndarray:
    return self.camera.CameraMatrix

  def getObjects(self):
    return self.objects
  