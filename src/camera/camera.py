import transformation
import numpy as np

class Camera:
  def __init__(self, width: float, height: float, fov: float, far: float, near: float):
    self.CameraMatrix = transformation.getDefaultMatrix()
    self.position = np.array([0.0, 0.0, 0.0])
    self.rotation = np.array([0.0, 0.0, 0.0])  # [pitch, yaw, roll] in degrees
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
    """Rotate camera by given angles in degrees (global space)"""
    self.rotation[0] += rotationVector[0]  # Pitch
    self.rotation[1] += rotationVector[1]  # Yaw
    self.rotation[2] += rotationVector[2]  # Roll
    
    # Clamp pitch rotation to avoid gimbal lock
    self.rotation[0] = np.clip(self.rotation[0], -179.0, 179.0)
    
    # Keep yaw in range [0, 360)
    self.rotation[1] = self.rotation[1] % 360.0
    
    self.updateCameraMatrix()

  def rotateLocal(self, rotationVector: tuple[float, float, float]):
    """Rotate camera around its local axes by given angles in degrees"""
    # Convert rotation angles to radians
    dpitch = np.radians(rotationVector[0])
    dyaw = np.radians(rotationVector[1])
    droll = np.radians(rotationVector[2])
    
    # Get current rotation angles in radians
    pitch = np.radians(self.rotation[0])
    yaw = np.radians(self.rotation[1])
    roll = np.radians(self.rotation[2])
    
    # Calculate new rotation angles
    new_pitch = pitch + dpitch
    new_yaw = yaw + dyaw
    new_roll = roll + droll
    
    # Convert back to degrees
    self.rotation[0] = np.degrees(new_pitch)
    self.rotation[1] = np.degrees(new_yaw)
    self.rotation[2] = np.degrees(new_roll)
    
    # Clamp pitch rotation to avoid gimbal lock
    self.rotation[0] = np.clip(self.rotation[0], -179.0, 179.0)
    
    # Keep yaw in range [0, 360)
    self.rotation[1] = self.rotation[1] % 360.0
    
    self.updateCameraMatrix()

  def rotateLocalMatrix(self, rotationVector: tuple[float, float, float]):
    """Rotate camera around its local axes using transformation matrices
    
    Args:
        rotationVector: A tuple of (pitch, yaw, roll) in degrees
    """
    # Convert rotation angles to radians
    dpitch = np.radians(rotationVector[0])
    dyaw = np.radians(rotationVector[1])
    droll = np.radians(rotationVector[2])
    
    # Create rotation matrices for each axis
    # Pitch rotation around local X axis
    pitch_matrix = np.array([
        [1, 0, 0, 0],
        [0, np.cos(dpitch), -np.sin(dpitch), 0],
        [0, np.sin(dpitch), np.cos(dpitch), 0],
        [0, 0, 0, 1]
    ])
    
    # Yaw rotation around local Y axis
    yaw_matrix = np.array([
        [np.cos(dyaw), 0, np.sin(dyaw), 0],
        [0, 1, 0, 0],
        [-np.sin(dyaw), 0, np.cos(dyaw), 0],
        [0, 0, 0, 1]
    ])
    
    # Roll rotation around local Z axis
    roll_matrix = np.array([
        [np.cos(droll), -np.sin(droll), 0, 0],
        [np.sin(droll), np.cos(droll), 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])
    
    # Combine rotations in the correct order: yaw -> pitch -> roll
    # This order ensures that the rotations are applied around the local axes
    combined_matrix = np.dot(roll_matrix, np.dot(pitch_matrix, yaw_matrix))
    
    # Apply the rotation to the camera matrix
    self.CameraMatrix = np.dot(combined_matrix, self.CameraMatrix)
    
    # Update rotation angles directly instead of extracting from matrix
    # This prevents the "stuck" behavior
    self.rotation[0] += rotationVector[0]  # Pitch in degrees
    self.rotation[1] += rotationVector[1]  # Yaw in degrees
    self.rotation[2] += rotationVector[2]  # Roll in degrees
    
    # Clamp pitch rotation to avoid gimbal lock
    self.rotation[0] = np.clip(self.rotation[0], -179.0, 179.0)
    
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

