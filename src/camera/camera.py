import transformation
import numpy as np

class Camera:
  def __init__(self, width: float, height: float, fov: float, far: float, near: float):
    self.CameraMatrix = transformation.getDefaultMatrix()
    self.position = np.array([0.0, 0.0, 0.0])
    self.rotation = np.array([0.0, 0.0, 0.0])
    self.fov = fov
    self.width = width
    self.height = height
    self.far = far
    self.near = near
    self.aspectRatio = width / height
    self.updateCameraMatrix()

  def updateCameraMatrix(self):
    """Updates the camera matrix based on position and rotation"""
    self.CameraMatrix = transformation.getViewMatrix(self.position, self.rotation)

  def translate(self, translationVector: tuple[float, float, float]):
    """Translate in camera's local space"""
    # Convert angles to radians
    angleX = np.radians(self.rotation[0])  # Pitch
    angleY = np.radians(self.rotation[1])  # Yaw
    
    # Create local direction vectors
    # Forward vector includes both pitch and yaw
    forward = np.array([
        -np.sin(angleY) * np.cos(angleX),
        np.sin(angleX),
        -np.cos(angleY) * np.cos(angleX)
    ])
    
    # Right vector (only affected by yaw)
    right = np.array([
        np.cos(angleY),
        0,
        -np.sin(angleY)
    ])
    
    # Up vector is cross product of right and forward
    up = np.cross(right, forward)
    up = up / np.linalg.norm(up)  # Normalize
    
    # Combine movement in local space
    movement = (right * translationVector[0] + 
               up * translationVector[1] + 
               forward * translationVector[2])
    
    # Update position
    self.position += movement
    self.updateCameraMatrix()

  def rotate(self, rotationVector: tuple[float, float, float]):
    """Rotate camera by given angles in degrees"""
    self.rotation[0] += rotationVector[0]  # Pitch
    self.rotation[1] += rotationVector[1]  # Yaw
    self.rotation[2] += rotationVector[2]  # Roll (usually not used)
    
    # Clamp pitch rotation to avoid gimbal lock
    self.rotation[0] = np.clip(self.rotation[0], -89.0, 89.0)
    
    # Keep yaw in range [0, 360)
    self.rotation[1] = self.rotation[1] % 360.0
    
    self.updateCameraMatrix()

  def reset(self):
    """Reset camera to initial position and rotation"""
    self.position = np.array([0.0, 0.0, 0.0])
    self.rotation = np.array([0.0, 0.0, 0.0])
    self.updateCameraMatrix()

  def stabilize(self):
    """Stabilize camera rotation to nearest 90 degree angles"""
    # Round pitch to nearest 0 (looking straight)
    self.rotation[0] = 0.0
    
    # Round yaw to nearest 90 degrees
    yaw = self.rotation[1]
    yaw = round(yaw / 90.0) * 90.0
    self.rotation[1] = yaw
    
    # Reset roll
    self.rotation[2] = 0.0
    
    self.updateCameraMatrix()

