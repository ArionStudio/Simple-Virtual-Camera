from camera.camera import Camera
from scene.scene import Scene
from scene.Cuboid import Cuboid
from scene.Pyramid import Pyramid
from scene.Prism import Prism
from scene.Cylinder import Cylinder
from scene.Octahedron import Octahedron
from render.projection import Projection
from render.painter_bsp import PainterBSP, Face
import pygame
import numpy as np
from typing import List
import colorsys

class PainterRenderer:
    def __init__(self, width: int, height: int):
        # Initialize camera with better FOV and near/far planes
        self.camera = Camera(width, height, 90, 100, 0.1)  
        
        # Initialize camera position and direction
        # Camera is placed at the origin looking forward (positive Z)
        self.camera.position = np.array([0.0, 0.0, 0.0])
        self.camera.rotation = np.array([0.0, 0.0, 0.0])
        self.camera.updateCameraMatrix()
        
        self.scene = Scene()

        # Create different primitive shapes
        self.setupTestScene()
        
        self.projection = Projection(self.camera, self.scene)
        self.painter_bsp = PainterBSP()

        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("3D Renderer with Painter's Algorithm & BSP")
        
        # Set up mouse for looking around
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        
        self.clock = pygame.time.Clock()
        self.isRunning = True
        
        # Movement state
        self.movement = np.array([0.0, 0.0, 0.0])
        
        # Mouse sensitivity (degrees per pixel)
        self.mouseSensitivityX = 45  # Yaw sensitivity in degrees per pixel
        self.mouseSensitivityY = 45  # Pitch sensitivity in degrees per pixel
        self.rollSensitivity = 45  # Roll sensitivity in degrees per second
        
        # Movement speed
        self.moveSpeed = 10.0  # Units per second

        # Zoom settings
        self.zoomSpeed = 5.0  # FOV change per scroll
        self.keyboardZoomSpeed = 2.0  # FOV change per keyboard press
        self.minFOV = 30.0   # Maximum zoom in
        self.maxFOV = 120.0  # Maximum zoom out

        # Color settings
        self.max_bsp_layers = 20  # Maximum BSP layers we expect
        self.color_schemes = ["rainbow", "heatmap", "blues"]
        self.color_scheme = "rainbow"  # Default color scheme

        # Debug info
        self.showDebugInfo = False
        self.showLayerNumbers = False  # Toggle for showing layer numbers on faces
        self.font = pygame.font.SysFont('Arial', 16)
        self.small_font = pygame.font.SysFont('Arial', 12)

        # Initial scene calculation
        self.calculateScene()

    def setupTestScene(self):
        # Create primitive objects
        standard_cuboid = Cuboid(
            sizes=(1.0, 1.0, 1.0),
            centerPosition=(0.0, 0.0, 5.0)
        )
        
        large_cuboid = Cuboid(
            sizes=(2.0, 2.0, 2.0),
            centerPosition=(0.0, 0.0, 5.0)
        )
        
        flat_cuboid = Cuboid(
            sizes=(3.0, 0.2, 3.0),
            centerPosition=(0.0, 0.0, 5.0)
        )
        
        tall_cuboid = Cuboid(
            sizes=(0.5, 3.0, 0.5),
            centerPosition=(0.0, 0.0, 5.0)
        )
        
        # Create pyramid
        pyramid = Pyramid(
            base_size=1.2,
            height=1.5,
            centerPosition=(0.0, 0.0, 5.0)
        )
        
        # Create prism
        prism = Prism(
            side_length=1.0,
            height=1.5,
            centerPosition=(0.0, 0.0, 5.0)
        )
        
        # Create cylinder
        cylinder = Cylinder(
            radius=0.8,
            height=1.6,
            segments=12,
            centerPosition=(0.0, 0.0, 5.0)
        )
        
        # Create octahedron
        octahedron = Octahedron(
            size=0.8,
            centerPosition=(0.0, 0.0, 5.0)
        )
        
        # Add basic cuboid arrangement for testing
        self.scene.addObject(standard_cuboid, (0, 0, 5), (0, 0, 0), (1, 1, 1))        # Center
        self.scene.addObject(standard_cuboid, (2, 0, 5), (0, 0, 0), (0.5, 0.5, 0.5))  # Right
        self.scene.addObject(standard_cuboid, (-2, 0, 5), (0, 0, 0), (0.5, 0.5, 0.5)) # Left
        self.scene.addObject(standard_cuboid, (0, 2, 5), (0, 0, 0), (0.5, 0.5, 0.5))  # Top
        self.scene.addObject(standard_cuboid, (0, -2, 5), (0, 0, 0), (0.5, 0.5, 0.5)) # Bottom
        self.scene.addObject(standard_cuboid, (0, 0, 8), (0, 0, 0), (0.5, 0.5, 0.5))  # Further front
        
        # Add additional objects for complex testing
        
        # Intersecting objects to test BSP splitting
        self.scene.addObject(large_cuboid, (3, 3, 7), (30, 45, 0), (0.7, 0.7, 0.7))   # Rotated large cuboid
        self.scene.addObject(standard_cuboid, (3, 3, 6), (0, 0, 0), (1, 1, 1))        # Intersecting with the above
        
        # Add pyramid
        self.scene.addObject(pyramid, (-4, -2, 6), (0, 30, 0), (1, 1, 1))            # Pyramid with rotation
        self.scene.addObject(pyramid, (-4, -2, 8), (45, 0, 0), (0.8, 0.8, 0.8))      # Another pyramid behind
        
        # Add prism
        self.scene.addObject(prism, (4, -2, 6), (0, 45, 0), (1, 1, 1))               # Prism with rotation
        self.scene.addObject(prism, (4, -2, 8), (30, 60, 0), (0.8, 0.8, 0.8))        # Another prism behind
        
        # Add cylinder
        self.scene.addObject(cylinder, (-3, 2, 6), (30, 0, 0), (1, 1, 1))            # Cylinder with rotation
        self.scene.addObject(cylinder, (-3, 2, 8), (0, 30, 0), (0.8, 0.8, 0.8))      # Another cylinder behind
        
        # Add octahedron
        self.scene.addObject(octahedron, (3, 2, 6), (0, 45, 0), (1, 1, 1))           # Octahedron with rotation
        self.scene.addObject(octahedron, (3, 2, 8), (45, 45, 0), (0.8, 0.8, 0.8))    # Another octahedron behind
        
        # Complex arrangement with mixed shapes to test occlusion
        # Flat platform with objects on it
        self.scene.addObject(flat_cuboid, (0, -3, 10), (0, 0, 0), (1, 1, 1))         # Flat platform
        self.scene.addObject(pyramid, (-1, -2, 10), (0, 30, 0), (0.7, 0.7, 0.7))     # Pyramid on platform
        self.scene.addObject(prism, (1, -2, 10), (0, -30, 0), (0.7, 0.7, 0.7))       # Prism on platform
        
        # Column with objects nearby
        self.scene.addObject(tall_cuboid, (-4, 0, 7), (0, 0, 0), (1, 1, 1))          # Tall column
        self.scene.addObject(cylinder, (-4, 2, 7), (0, 0, 0), (0.6, 0.6, 0.6))       # Cylinder on top of column
        self.scene.addObject(octahedron, (-5, 0, 7), (0, 0, 0), (0.6, 0.6, 0.6))     # Octahedron next to column
        
        # Additional complex arrangement
        self.scene.addObject(pyramid, (5, 0, 12), (0, 30, 0), (0.8, 0.8, 0.8))       # Far right pyramid
        self.scene.addObject(octahedron, (6, 0, 11), (45, 45, 0), (0.8, 0.8, 0.8))   # Far right octahedron
        self.scene.addObject(prism, (7, 0, 10), (30, 0, 0), (0.8, 0.8, 0.8))         # Far right prism
        
        # Partially overlapping objects from camera view
        self.scene.addObject(large_cuboid, (-6, 1, 9), (0, 15, 0), (0.9, 0.9, 0.9))  # Large cuboid
        self.scene.addObject(cylinder, (-7, 1, 8), (0, 0, 0), (0.6, 0.6, 0.6))       # Cylinder partially behind

    def calculateScene(self):
        """Calculate all scene transformations and projections"""
        self.projection.projectCameraObjects()
        self.screenFaces = self.prepareScreenFaces()

    def get_color_for_bsp_layer(self, layer_index, total_layers):
        """
        Get a color for a specific BSP layer based on the selected color scheme
        
        Args:
            layer_index: Index of the layer in BSP ordering (0 = furthest, higher = closer)
            total_layers: Total number of layers in the scene
            
        Returns:
            RGB color tuple
        """
        # Normalize layer index to 0-1 range
        normalized_pos = layer_index / max(1, total_layers - 1)
        
        if self.color_scheme == "rainbow":
            # Full rainbow spectrum (HSV color wheel)
            # Start with blue (240°), go through green, yellow, to red (0°)
            hue = (1 - normalized_pos) * 0.8  # Use 80% of the color wheel (blue to red)
            saturation = 0.9
            value = 0.9
            r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
            return (int(r * 255), int(g * 255), int(b * 255))
            
        elif self.color_scheme == "heatmap":
            # Heat map: blue (cold/far) to red (hot/close)
            if normalized_pos < 0.5:
                # Blue to green (far to mid)
                ratio = normalized_pos * 2
                return (0, int(ratio * 255), int((1 - ratio) * 255))
            else:
                # Green to red (mid to close)
                ratio = (normalized_pos - 0.5) * 2
                return (int(ratio * 255), int((1 - ratio) * 255), 0)
                
        elif self.color_scheme == "blues":
            # Different shades of blue - stronger contrast
            blue = int(180 + normalized_pos * 75)  # 180-255 range for blue
            green = int(normalized_pos * 200)      # 0-200 range for green
            red = int(normalized_pos * 50)         # 0-50 range for red
            return (red, green, blue)
            
        else:
            # Fallback to grayscale
            gray = int(normalized_pos * 200) + 55  # 55-255 range
            return (gray, gray, gray)

    def prepareScreenFaces(self) -> List[dict]:
        """
        Extract faces from objects, determine rendering order with BSP, and map to screen coordinates
        
        Returns:
            List of face dictionaries with screen coordinates and colors
        """
        # Get the original objects
        original_objects = self.scene.getObjects()
        
        # Re-build the BSP tree with original objects (world space)
        # This needs to be done every frame to update rendering order
        self.painter_bsp.build_bsp_tree(original_objects)
        
        # Get the order of faces for rendering in back-to-front order
        # This will change based on camera position
        faces_in_order = self.painter_bsp.get_rendering_order(self.camera.position)
        total_faces = len(faces_in_order)
        
        # Project all vertices to screen space
        screen_faces = []
        
        for i, face in enumerate(faces_in_order):
            # Get color for this BSP layer - back-to-front order (0 = furthest back)
            # This ensures colors update as the BSP ordering changes
            color = self.get_color_for_bsp_layer(i, total_faces)
            
            # Map the face vertices to screen coordinates
            screen_verts = []
            vertices_behind_camera = 0
            
            for vert in face.vertices:
                # Apply camera transformation to get to camera space
                cam_space_vert = self.camera.CameraMatrix @ vert
                
                # Check if vertex is behind camera
                if cam_space_vert[2] <= 0:
                    vertices_behind_camera += 1
                
                # Apply projection to get to clip space
                clip_space_vert = self.projection.getProjectionMatrix() @ cam_space_vert
                
                # Perspective divide to get to normalized device coordinates
                if clip_space_vert[3] != 0:
                    ndc = clip_space_vert / clip_space_vert[3]
                else:
                    ndc = clip_space_vert
                
                # Map to screen space (even if off-screen or behind camera)
                screen_x = (ndc[0] + 1) * 0.5 * self.camera.width
                screen_y = (1 - (ndc[1] + 1) * 0.5) * self.camera.height  # Y is flipped in screen space
                
                screen_verts.append((screen_x, screen_y))
            
            # Skip faces if ALL vertices are behind the camera
            if vertices_behind_camera == len(face.vertices):
                continue
            
            # Calculate distance to camera for debugging info
            centroid = face.get_centroid()
            distance = np.linalg.norm(centroid[:3] - self.camera.position[:3])
            
            # Store all data about this face
            screen_faces.append({
                'vertices': screen_verts,
                'color': color,
                'bsp_layer': i,
                'distance': distance
            })
        
        return screen_faces

    def drawScene(self):
        """Draw the pre-calculated scene using the Painter's Algorithm"""
        # Clear screen with black background
        self.screen.fill((0, 0, 0))
        
        # Draw all faces in back-to-front order (already sorted by the BSP tree)
        for face in self.screenFaces:
            vertices = face['vertices']
            
            # Draw the face as a filled polygon (only if it has enough vertices)
            try:
                if len(vertices) >= 3:
                    pygame.draw.polygon(self.screen, face['color'], vertices)
                    pygame.draw.polygon(self.screen, (255, 255, 255), vertices, 1)
                    
                    # Draw layer number if enabled
                    if self.showLayerNumbers and len(vertices) >= 3:
                        # Calculate centroid in screen space
                        centroid_x = sum(v[0] for v in vertices) / len(vertices)
                        centroid_y = sum(v[1] for v in vertices) / len(vertices)
                        
                        # Determine text color (inverted from face color for visibility)
                        color = face['color']
                        text_color = (255 - color[0], 255 - color[1], 255 - color[2])
                        
                        # Create text surface with layer number
                        layer_text = self.small_font.render(str(face['bsp_layer']), True, text_color)
                        
                        # Draw text at face centroid
                        text_rect = layer_text.get_rect(center=(centroid_x, centroid_y))
                        self.screen.blit(layer_text, text_rect)
            except (ValueError, TypeError, pygame.error) as e:
                # Skip problematic polygons - this can happen when vertices are outside view frustum
                continue
        
        # Draw debug info if enabled
        if self.showDebugInfo:
            self.drawDebugInfo()
        
        # Update the display
        pygame.display.flip()
    
    def drawDebugInfo(self):
        """Draw debug information on screen"""
        # Calculate some debug statistics
        if self.screenFaces:
            bsp_layers = max(face['bsp_layer'] for face in self.screenFaces) + 1
            min_dist = min(face['distance'] for face in self.screenFaces)
            max_dist = max(face['distance'] for face in self.screenFaces)
            dist_range = f"{min_dist:.1f} - {max_dist:.1f}"
            
            # Get depth order information
            depth_info = {}
            for face in self.screenFaces:
                layer = face['bsp_layer']
                dist = face['distance']
                if layer not in depth_info:
                    depth_info[layer] = []
                depth_info[layer].append(dist)
        else:
            bsp_layers = 0
            dist_range = "N/A"
            depth_info = {}
            
        # Get total BSP layers from the painter algorithm
        total_bsp_layers = getattr(self.painter_bsp, 'layer_count', 0)
        
        # Get BSP statistics
        bsp_stats = self.painter_bsp.get_stats()
            
        # Prepare debug text
        info_text = [
            f"Camera Position: {np.round(self.camera.position, 1)}",
            f"Camera Rotation: {np.round(self.camera.rotation, 1)}",
            f"FOV: {self.camera.fov:.1f}°",
            f"FPS: {int(self.clock.get_fps())}",
            "",
            "BSP Statistics:",
            f"Layers Visible/Total: {bsp_layers}/{total_bsp_layers}",
            f"Tree Depth: {bsp_stats['tree_depth']}",
            f"Total Faces: {bsp_stats['total_faces']}",
            f"Rendered Faces: {len(self.screenFaces)}",
            f"Build Time: {bsp_stats['build_time']*1000:.1f} ms",
            f"Traverse Time: {bsp_stats['traverse_time']*1000:.1f} ms",
            f"Color Scheme: {self.color_scheme.capitalize()}",
            f"Distance Range: {dist_range}",
            f"Show Layer Numbers: {self.showLayerNumbers} (F2)",
            "",
            "BSP Layers (back-to-front):"
        ]
        
        # Add layer-specific information if we have faces
        if depth_info:
            # Sort layers by order (from 0 to max)
            sorted_layers = sorted(depth_info.keys())
            for layer in sorted_layers:
                distances = depth_info[layer]
                avg_dist = sum(distances) / len(distances)
                color = self.get_color_for_bsp_layer(layer, bsp_layers)
                color_str = f"({color[0]}, {color[1]}, {color[2]})"
                info_text.append(f"  Layer {layer}: {len(distances)} faces, avg dist: {avg_dist:.1f}, color: {color_str}")
        
        info_text.extend([
            "",
            "Controls:",
            "WASD: Move | Arrows: Rotate | +/-: Zoom",
            "Mouse: Look | Space: Stabilize | F1: Debug",
            "F2: Toggle Layer Numbers | C: Cycle Color",
            "ESC: Exit"
        ])
        
        # Draw text
        y_offset = 10
        for line in info_text:
            text_surface = self.font.render(line, True, (255, 255, 255))
            self.screen.blit(text_surface, (10, y_offset))
            y_offset += 20
            
        # Draw BSP color legend
        self.drawColorLegend()
        
        # Draw BSP layer visualization
        if depth_info:
            self.drawBSPLayerVisualization(depth_info, bsp_layers)

    def drawColorLegend(self):
        """Draw a color legend showing BSP layer colors"""
        legend_width = 200
        legend_height = 20
        x_start = self.camera.width - legend_width - 10
        y_start = 10
        
        # Draw legend background
        pygame.draw.rect(self.screen, (50, 50, 50), 
                        (x_start - 5, y_start - 5, 
                         legend_width + 10, legend_height + 30))
        
        # Draw legend title
        title_surface = self.font.render(f"BSP Layers ({self.color_scheme}):", True, (255, 255, 255))
        self.screen.blit(title_surface, (x_start, y_start))
        y_start += 20
        
        # Draw the color gradient
        steps = min(legend_width, self.max_bsp_layers)
        segment_width = legend_width / steps
        
        for i in range(steps):
            # Get color for this segment
            color = self.get_color_for_bsp_layer(i, steps)
            
            # Draw a segment of the legend
            x_pos = int(x_start + i * segment_width)
            width = int(segment_width) + 1  # +1 to avoid gaps
            pygame.draw.rect(self.screen, color, 
                           (x_pos, y_start, width, legend_height))
        
        # Draw labels
        pygame.draw.rect(self.screen, (255, 255, 255), 
                        (x_start, y_start, legend_width, legend_height), 1)
        back_text = self.font.render("Back", True, (255, 255, 255))
        front_text = self.font.render("Front", True, (255, 255, 255))
        self.screen.blit(back_text, (x_start, y_start + legend_height + 5))
        self.screen.blit(front_text, (x_start + legend_width - 40, y_start + legend_height + 5))

    def drawBSPLayerVisualization(self, depth_info, total_layers):
        """Draw a visualization of BSP layers showing ordering and distances"""
        # Configuration
        viz_width = 250
        viz_height = 150
        x_start = self.camera.width - viz_width - 10
        y_start = 100
        
        # Draw background
        pygame.draw.rect(self.screen, (30, 30, 30), 
                       (x_start - 5, y_start - 25, 
                        viz_width + 10, viz_height + 30))
        
        # Draw title
        title_surface = self.font.render("BSP Layer Visualization", True, (255, 255, 255))
        self.screen.blit(title_surface, (x_start, y_start - 20))
        
        # Calculate min/max distances for scaling
        all_distances = []
        for layer_distances in depth_info.values():
            all_distances.extend(layer_distances)
            
        if not all_distances:
            return
            
        min_dist = min(all_distances)
        max_dist = max(all_distances)
        dist_range = max(0.1, max_dist - min_dist)  # Avoid division by zero
        
        # Draw layer dots
        for layer, distances in depth_info.items():
            # Get color for this layer
            color = self.get_color_for_bsp_layer(layer, total_layers)
            
            # Draw a dot for each face in this layer
            for dist in distances:
                # Scale distance to x-coordinate
                x_pos = x_start + int((dist - min_dist) / dist_range * viz_width)
                
                # Y position based on layer (from bottom to top)
                y_pos = y_start + viz_height - int((layer + 1) / (total_layers + 1) * viz_height)
                
                # Draw dot
                pygame.draw.circle(self.screen, color, (x_pos, y_pos), 3)
        
        # Draw axes
        pygame.draw.line(self.screen, (200, 200, 200), 
                       (x_start, y_start + viz_height), 
                       (x_start + viz_width, y_start + viz_height), 1)  # X-axis
        pygame.draw.line(self.screen, (200, 200, 200), 
                       (x_start, y_start), 
                       (x_start, y_start + viz_height), 1)  # Y-axis
        
        # Draw labels
        near_label = self.font.render(f"{min_dist:.1f}", True, (200, 200, 200))
        far_label = self.font.render(f"{max_dist:.1f}", True, (200, 200, 200))
        distance_label = self.font.render("Distance", True, (200, 200, 200))
        layer_label = self.font.render("Layer", True, (200, 200, 200))
        
        self.screen.blit(near_label, (x_start - 5, y_start + viz_height + 5))
        self.screen.blit(far_label, (x_start + viz_width - 20, y_start + viz_height + 5))
        self.screen.blit(distance_label, (x_start + viz_width // 2 - 25, y_start + viz_height + 5))
        self.screen.blit(layer_label, (x_start - 40, y_start + viz_height // 2 - 10))

    def handleCameraControls(self):
        """Handle continuous camera movement and rotation"""
        # Get keyboard state
        keys = pygame.key.get_pressed()
        
        # Get delta time for smooth movement
        dt = self.clock.get_time() / 1000.0  # Convert to seconds
        
        # Reset movement vector
        movement = np.zeros(3)
        camera_changed = False
        
        # Calculate forward direction vector (based on yaw only)
        yaw = np.radians(self.camera.rotation[1])
        forward = np.array([
            -np.sin(yaw),
            0,
            -np.cos(yaw)
        ])
        
        # Calculate right direction vector
        right = np.array([
            np.cos(yaw),
            0,
            -np.sin(yaw)
        ])
        
        # Forward/Backward (Z axis)
        if keys[pygame.K_w]:
            movement -= forward
            camera_changed = True
        if keys[pygame.K_s]:
            movement += forward
            camera_changed = True
        
        # Left/Right (X axis)
        if keys[pygame.K_a]:
            movement += right
            camera_changed = True
        if keys[pygame.K_d]:
            movement -= right
            camera_changed = True
        
        # Up/Down (Y axis)
        if keys[pygame.K_LSHIFT]:
            movement[1] += 1.0
            camera_changed = True
        if keys[pygame.K_LCTRL]:
            movement[1] -= 1.0
            camera_changed = True
        
        # Apply movement if any keys were pressed
        if camera_changed:
            # Normalize movement vector if not zero
            length = np.linalg.norm(movement)
            if length > 0:
                movement /= length
                
                # Apply movement speed and delta time
                movement *= self.moveSpeed * dt
                
                # Move camera - make sure to update only the first 3 elements of position
                self.camera.position[:3] += movement
                self.camera.updateCameraMatrix()
            
        return camera_changed
    
    def handleArrowsAsCameraControls(self):
        """Handle camera rotation with arrow keys"""
        # Get pressed keys
        keys = pygame.key.get_pressed()
        
        # Get delta time for smooth movement
        dt = self.clock.get_time() / 1000.0  # Convert to seconds
        rotation_speed = 60.0 * dt  # Degrees per second
        
        camera_changed = False
        
        # Handle roll (Alt + Left/Right)
        if keys[pygame.K_LALT] or keys[pygame.K_RALT]:
            if keys[pygame.K_LEFT]:
                self.camera.rotate((0, 0, rotation_speed))  # Roll left
                camera_changed = True
            elif keys[pygame.K_RIGHT]:
                self.camera.rotate((0, 0, -rotation_speed))  # Roll right
                camera_changed = True
        # Handle normal rotation
        else:
            if keys[pygame.K_UP]:
                self.camera.rotate((rotation_speed, 0, 0))  # Pitch up
                camera_changed = True
            elif keys[pygame.K_DOWN]:
                self.camera.rotate((-rotation_speed, 0, 0))  # Pitch down
                camera_changed = True
            if keys[pygame.K_LEFT]:
                self.camera.rotate((0, rotation_speed, 0))  # Yaw left
                camera_changed = True
            elif keys[pygame.K_RIGHT]:
                self.camera.rotate((0, -rotation_speed, 0))  # Yaw right
                camera_changed = True
        
        return camera_changed

    def handleKeyboardZoom(self):
        """Handle zoom in/out with keyboard + and - keys"""
        keys = pygame.key.get_pressed()
        
        camera_changed = False
        
        # Zoom in with plus key
        if keys[pygame.K_PLUS] or keys[pygame.K_KP_PLUS] or keys[pygame.K_EQUALS]:
            self.camera.fov -= self.keyboardZoomSpeed
            camera_changed = True
            
        # Zoom out with minus key
        if keys[pygame.K_MINUS] or keys[pygame.K_KP_MINUS]:
            self.camera.fov += self.keyboardZoomSpeed
            camera_changed = True
        
        # Clamp FOV to reasonable range
        if camera_changed:
            self.camera.fov = np.clip(self.camera.fov, self.minFOV, self.maxFOV)
            
        return camera_changed

    def handleMouseLook(self):
        """Handle mouse looking and roll rotation with middle mouse button"""
        # Get current mouse position
        current_x, current_y = pygame.mouse.get_pos()
        
        # If this is the first frame, initialize last_mouse_pos
        if not hasattr(self, 'last_mouse_pos'):
            self.last_mouse_pos = (current_x, current_y)
            return False
            
        # Calculate mouse movement
        dx = current_x - self.last_mouse_pos[0]
        dy = current_y - self.last_mouse_pos[1]
        
        # Update last position
        self.last_mouse_pos = (current_x, current_y)
        
        # Check if any mouse button is pressed
        if pygame.mouse.get_pressed()[0]:  # Left button - look
            # Get delta time for smooth movement
            dt = self.clock.get_time() / 1000.0  # Convert to seconds
            
            # Scale mouse movement to rotation amount
            yaw_change = -dx * 0.2  # Negate for expected direction
            pitch_change = -dy * 0.2  # Negate for expected direction
            
            # Apply rotation
            if dx != 0 or dy != 0:
                self.camera.rotate((pitch_change, yaw_change, 0))
                return True
                
        elif pygame.mouse.get_pressed()[1]:  # Middle button - roll
            # Get delta time for smooth movement
            dt = self.clock.get_time() / 1000.0  # Convert to seconds
            
            # Scale mouse movement to rotation amount
            roll_change = dx * 0.2
            
            # Apply roll
            if dx != 0:
                self.camera.rotate((0, 0, roll_change))
                return True
                
        return False

    def handleEvents(self):
        """Process all input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.isRunning = False
            elif event.type == pygame.KEYDOWN:
                # ESC key quits
                if event.key == pygame.K_ESCAPE:
                    self.isRunning = False
                # R key resets camera
                elif event.key == pygame.K_r:
                    self.camera.reset()
                    return True
                # Space key stabilizes camera (snaps to nearest 90 degrees)
                elif event.key == pygame.K_SPACE:
                    self.camera.stabilize()
                    return True
                # F1 key toggles debug info
                elif event.key == pygame.K_F1:
                    self.showDebugInfo = not self.showDebugInfo
                # F2 key toggles layer numbers
                elif event.key == pygame.K_F2:
                    self.showLayerNumbers = not self.showLayerNumbers
                # C key cycles through color schemes
                elif event.key == pygame.K_c:
                    self.cycleColorScheme()
                    return True
            # Mouse wheel for zoom
            elif event.type == pygame.MOUSEWHEEL:
                # Change FOV based on scroll direction
                self.camera.fov -= event.y * self.zoomSpeed
                # Clamp FOV to reasonable range
                self.camera.fov = np.clip(self.camera.fov, self.minFOV, self.maxFOV)
                return True
                
        return False
    
    def cycleColorScheme(self):
        """Cycle through available color schemes"""
        current_index = self.color_schemes.index(self.color_scheme)
        next_index = (current_index + 1) % len(self.color_schemes)
        self.color_scheme = self.color_schemes[next_index]

    def run(self):
        """Main render loop"""
        while self.isRunning:
            # Handle input events
            camera_changed = self.handleEvents()
            
            # Handle continuous camera controls
            if self.handleCameraControls():
                camera_changed = True
            
            # Handle arrow key camera rotation
            if self.handleArrowsAsCameraControls():
                camera_changed = True
            
            # Handle keyboard zoom controls
            if self.handleKeyboardZoom():
                camera_changed = True
            
            # Handle mouse looking
            if self.handleMouseLook():
                camera_changed = True
            
            # Always recalculate scene - this ensures BSP colors update with camera movement
            self.calculateScene()
            
            # Draw current scene state
            self.drawScene()
            
            # Cap the frame rate
            self.clock.tick(60)
            
            # Update window title with FPS
            pygame.display.set_caption(f"3D Renderer with Painter's Algorithm & BSP - FPS: {int(self.clock.get_fps())}")
        
        pygame.quit() 