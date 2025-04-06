from camera.camera import Camera
from scene.scene import Scene
from scene.Cuboid import Cuboid
from render.projection import Projection
import pygame
import numpy as np

class Renderer:
  def __init__(self, width: int, height: int):
    # Initialize camera with better FOV and near/far planes
    self.camera = Camera(width, height, 90, 100, 0.1)  
    self.scene = Scene()

    # Create a cuboid with size 10 units and position it properly
    cuboid = Cuboid(
        sizes=(1.0, 1.0, 1.0),        # 1 unit size
        centerPosition=(0.0, 0.0, -5.0)  # 5 units in front of camera
    )
    
    # Add multiple cuboids in different positions
    self.scene.addObject(cuboid, (0, 0, -5), (0, 0, 0), (1, 1, 1))      # Center
    self.scene.addObject(cuboid, (2, 0, -5), (0, 0, 0), (0.5, 0.5, 0.5))  # Right
    self.scene.addObject(cuboid, (-2, 0, -5), (0, 0, 0), (0.5, 0.5, 0.5)) # Left
    self.scene.addObject(cuboid, (0, 2, -5), (0, 0, 0), (0.5, 0.5, 0.5))  # Top
    self.scene.addObject(cuboid, (0, -2, -5), (0, 0, 0), (0.5, 0.5, 0.5)) # Bottom
    self.scene.addObject(cuboid, (0, 0, -7), (0, 0, 0), (0.5, 0.5, 0.5))  # Back

    self.projection = Projection(self.camera, self.scene)

    pygame.init()
    self.screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("3D Renderer")
    
    # Set up mouse for looking around
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)
    
    self.clock = pygame.time.Clock()
    self.isRunning = True
    
    # Movement state
    self.movement = np.array([0.0, 0.0, 0.0])
    
    # Mouse sensitivity (degrees per pixel)
    self.mouseSensitivityX = 2  # Yaw sensitivity
    self.mouseSensitivityY = 2  # Pitch sensitivity
    self.rollSensitivity = 2  # Speed for Z-axis movement with middle mouse button
    
    # Movement speed
    self.moveSpeed = 10.0  # Units per second

    # Zoom settings
    self.zoomSpeed = 5.0  # FOV change per scroll
    self.minFOV = 30.0   # Maximum zoom in
    self.maxFOV = 120.0  # Maximum zoom out

    # Initial scene calculation
    self.calculateScene()

  def calculateScene(self):
    """Calculate all scene transformations and projections"""
    self.projection.projectCameraObjects()
    self.screenObjects = self.mapObjectToScreen(self.projection.getObjects())

  def drawScene(self):
    """Draw the pre-calculated scene"""
    # Clear screen with black background
    self.screen.fill((0, 0, 0))
    
    # Draw all objects using pre-calculated screen coordinates
    for screenObject in self.screenObjects:
        for edge in self.scene.defualtEdgesInCuboid:
            start_pos = screenObject[edge[0]]
            end_pos = screenObject[edge[1]]
            pygame.draw.line(self.screen, (255, 255, 255), start_pos, end_pos, 1)
    
    # Update the display
    pygame.display.flip()

  def handleCameraControls(self):
    """Handle continuous camera movement and rotation"""
    # Get keyboard state
    keys = pygame.key.get_pressed()
    
    # Reset movement vector
    self.movement.fill(0.0)
    
    # Forward/Backward (Z axis)
    if keys[pygame.K_w]: self.movement[2] += 1.0  # Forward is positive Z
    if keys[pygame.K_s]: self.movement[2] -= 1.0  # Backward is negative Z
    
    # Left/Right (X axis)
    if keys[pygame.K_a]: self.movement[0] -= 1.0  # Left is negative X
    if keys[pygame.K_d]: self.movement[0] += 1.0  # Right is positive X
    
    # Up/Down (Y axis)
    if keys[pygame.K_LSHIFT]: self.movement[1] += 1.0  # Up is positive Y
    if keys[pygame.K_LCTRL]: self.movement[1] -= 1.0   # Down is negative Y
    
    # Normalize movement vector if not zero
    length = np.linalg.norm(self.movement)
    if length > 0:
        self.movement /= length
        
        # Apply movement speed and delta time
        dt = self.clock.get_time() / 1000.0  # Convert to seconds
        self.movement *= self.moveSpeed * dt
        
        # Move camera
        self.camera.translate(tuple(self.movement))
        return True
        
    return False

  def handleMouseLook(self):
    """Handle mouse looking and roll rotation with middle mouse button"""
    # Get relative mouse movement
    dx, dy = pygame.mouse.get_rel()
    
    if dx != 0 or dy != 0:
        # Get delta time for smooth movement
        dt = self.clock.get_time() / 1000.0  # Convert to seconds
        
        # Check if middle mouse button is pressed
        if pygame.mouse.get_pressed()[1]:  # Middle button
            # Use horizontal mouse movement for Z rotation (roll)
            roll = dx * self.rollSensitivity * dt
            self.camera.rotate((0, 0, -roll))  # Negative for natural roll direction
            return True
        else:
            # Normal camera rotation (pitch and yaw)
            yaw = dx * self.mouseSensitivityX * dt
            pitch = dy * self.mouseSensitivityY * dt
            self.camera.rotate((-pitch, -yaw, 0))
            return True
        
    return False

  def handleEvents(self):
    needsRecalculation = False
    
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        self.isRunning = False
      elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
          self.isRunning = False
        elif event.key == pygame.K_r:
          self.camera.reset()
          needsRecalculation = True
        elif event.key == pygame.K_e:
          self.camera.stabilize()
          needsRecalculation = True
      elif event.type == pygame.MOUSEWHEEL:
        # Scroll up (positive y) = zoom in (decrease FOV)
        # Scroll down (negative y) = zoom out (increase FOV)
        newFOV = self.camera.fov - event.y * self.zoomSpeed
        # Clamp FOV between min and max values
        self.camera.fov = np.clip(newFOV, self.minFOV, self.maxFOV)
        needsRecalculation = True
    
    # Handle continuous camera movement
    if self.handleCameraControls():
        needsRecalculation = True
    
    # Handle mouse looking
    if self.handleMouseLook():
        needsRecalculation = True
    
    if needsRecalculation:
        self.calculateScene()

  def calculateScreenPosition(self, vertex: tuple[float, float, float, float]):
    """Convert vertex from clip space to screen space. Returns None if vertex is behind camera."""
    # Check if vertex is behind camera (w should be positive for vertices in front of camera)
    if vertex[3] <= 0:
        return None
        
    # Perform perspective division
    x = vertex[0] / vertex[3]
    y = vertex[1] / vertex[3]
    
    # Convert to screen coordinates
    x = int(self.camera.width/2 + x * self.camera.width/2)
    y = int(self.camera.height/2 - y * self.camera.height/2)
    
    return (x, y)

  def mapObjectToScreen(self, projectedObjects: list[Cuboid]):
    mappedObjects = []
    for object in projectedObjects:
        # Map all vertices of the object
        mappedObject = []
        isObjectVisible = True
        
        # Check if any vertex is behind camera
        for vertex in object.vertices:
            screenPos = self.calculateScreenPosition(vertex)
            if screenPos is None:
                isObjectVisible = False
                break
            mappedObject.append(screenPos)
            
        # Only add object if all vertices are visible
        if isObjectVisible:
            mappedObjects.append(mappedObject)
            
    return mappedObjects

  def run(self):
    while self.isRunning:
      self.handleEvents()
      self.drawScene()
      self.clock.tick(60)  # Limit to 60 FPS
    
    # Clean up
    pygame.mouse.set_visible(True)
    pygame.event.set_grab(False)
    pygame.quit()
