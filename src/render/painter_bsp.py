import numpy as np
import colorsys
import time
from scene.Cuboid import Cuboid
from scene.Pyramid import Pyramid
from scene.Prism import Prism
from scene.Cylinder import Cylinder
from scene.Octahedron import Octahedron
from typing import List, Tuple, Optional, Dict, Any, Union

# Define a type for all supported objects
SceneObject = Union[Cuboid, Pyramid, Prism, Cylinder, Octahedron]

class BSPNode:
    """Binary Space Partitioning Tree Node"""
    
    def __init__(self, polygon=None, plane=None):
        self.polygon = polygon  # The polygon stored at this node (a face of an object)
        self.plane = plane      # The plane equation coefficients (a, b, c, d) where ax+by+cz+d=0
        self.front = None       # Front child node (positive side of plane)
        self.back = None        # Back child node (negative side of plane)
    
    def is_leaf(self) -> bool:
        """Check if this node is a leaf node"""
        return self.front is None and self.back is None

class Face:
    """Represents a polygon face in 3D space"""
    
    def __init__(self, vertices: np.ndarray, color=(255, 255, 255), parent_object=None):
        """
        Args:
            vertices: List of 3D vertices that make up the face
            color: RGB color tuple
            parent_object: Reference to the parent object this face belongs to
        """
        self.vertices = vertices
        self.color = color
        self.parent_object = parent_object
        
        # Calculate face normal using first three vertices
        v1 = vertices[1][:3] - vertices[0][:3]  # Vector from v0 to v1
        v2 = vertices[2][:3] - vertices[0][:3]  # Vector from v0 to v2
        self.normal = np.cross(v1, v2)          # Cross product gives normal vector
        
        # Normalize the normal vector
        norm = np.linalg.norm(self.normal)
        if norm > 0:
            self.normal = self.normal / norm
            
        # Calculate the plane equation ax + by + cz + d = 0
        # Where (a,b,c) is the normal vector and d is the negative dot product with a point on the plane
        self.plane = np.append(self.normal, -np.dot(self.normal, vertices[0][:3]))
    
    def get_centroid(self) -> np.ndarray:
        """Calculate and return the centroid of the face"""
        return np.mean(self.vertices, axis=0)
    
    def classify_point(self, point: np.ndarray) -> float:
        """
        Classify a point with respect to this face's plane
        
        Returns:
            Positive value if point is in front of the plane
            Negative value if point is behind the plane
            Zero if point is on the plane
        """
        if len(point) == 4:  # Handle homogeneous coordinates
            point = point[:3]
            
        return np.dot(self.normal, point) + self.plane[3]
    
    def split_polygon(self, other_face) -> Tuple[Optional['Face'], Optional['Face']]:
        """
        Split another face with this face's plane
        
        Returns:
            (front_face, back_face) tuple where either may be None if no vertices on that side
        """
        # Epsilon value for floating-point comparisons
        EPSILON = 1e-5
        
        # Classify each vertex of the other face
        vertex_classifications = []
        for vertex in other_face.vertices:
            classification = self.classify_point(vertex)
            if abs(classification) < EPSILON:
                vertex_classifications.append(0)  # On plane
            elif classification > 0:
                vertex_classifications.append(1)  # Front side
            else:
                vertex_classifications.append(-1)  # Back side
        
        # Check if all vertices are on one side or on the plane
        if all(c >= 0 for c in vertex_classifications):
            return (other_face, None)  # All vertices are in front or on the plane
        elif all(c <= 0 for c in vertex_classifications):
            return (None, other_face)  # All vertices are behind or on the plane
        
        # If we got here, the polygon straddles the plane and needs to be split
        front_vertices = []
        back_vertices = []
        
        # Process each edge to find intersections with the plane
        vertex_count = len(other_face.vertices)
        for i in range(vertex_count):
            current = other_face.vertices[i]
            current_class = vertex_classifications[i]
            
            # Add current vertex to appropriate list(s)
            if current_class >= 0:
                front_vertices.append(current)
            if current_class <= 0:
                back_vertices.append(current)
            
            # Get the next vertex and its classification
            next_idx = (i + 1) % vertex_count
            next_vertex = other_face.vertices[next_idx]
            next_class = vertex_classifications[next_idx]
            
            # Skip if both vertices are on the same side or one is on the plane
            if current_class == 0 or next_class == 0 or current_class == next_class:
                continue
                
            # Calculate the intersection point
            # We have an edge crossing the plane
            # Get the two vertices that make up the edge
            v1 = current[:3]  # Get x,y,z (drop homogeneous coordinate)
            v2 = next_vertex[:3]
            
            # Calculate the distance from v1 to the plane
            dist1 = self.classify_point(v1)
            dist2 = self.classify_point(v2)
            
            # Calculate intersection parameter t where the plane intersects the edge
            # The intersection point is v1 + t * (v2 - v1)
            t = dist1 / (dist1 - dist2)
            
            # Calculate the intersection point
            intersection = v1 + t * (v2 - v1)
            
            # Add homogeneous coordinate (w=1)
            intersection_point = np.append(intersection, 1.0)
            
            # Add intersection point to both polygon parts
            front_vertices.append(intersection_point)
            back_vertices.append(intersection_point)
        
        # Create new faces if there are enough vertices
        front_face = None
        back_face = None
        
        if len(front_vertices) >= 3:
            front_face = Face(np.array(front_vertices), other_face.color, other_face.parent_object)
        
        if len(back_vertices) >= 3:
            back_face = Face(np.array(back_vertices), other_face.color, other_face.parent_object)
            
        return (front_face, back_face)

def extract_faces_from_cuboid(cuboid: Cuboid) -> List[Face]:
    """Extract the faces from a cuboid object"""
    vertices = cuboid.vertices
    
    # Define the 6 faces of the cuboid
    face_indices = [
        [0, 1, 3, 2],  # Front face
        [4, 6, 7, 5],  # Back face
        [0, 2, 6, 4],  # Left face
        [1, 5, 7, 3],  # Right face
        [2, 3, 7, 6],  # Top face
        [0, 4, 5, 1]   # Bottom face
    ]
    
    # Colors for faces
    colors = [
        (255, 0, 0),    # Red (Front)
        (0, 255, 0),    # Green (Back)
        (0, 0, 255),    # Blue (Left)
        (255, 255, 0),  # Yellow (Right)
        (255, 0, 255),  # Magenta (Top)
        (0, 255, 255)   # Cyan (Bottom)
    ]
    
    faces = []
    for i, indices in enumerate(face_indices):
        face_vertices = np.array([vertices[idx] for idx in indices])
        faces.append(Face(face_vertices, colors[i], cuboid))
    
    return faces

def extract_faces_from_pyramid(pyramid: Pyramid) -> List[Face]:
    """Extract the faces from a pyramid object"""
    vertices = pyramid.vertices
    
    # Define the 5 faces of the pyramid (1 square base + 4 triangular faces)
    face_indices = [
        [0, 1, 2, 3],  # Base (square)
        [0, 1, 4],     # Front triangular face
        [1, 2, 4],     # Right triangular face
        [2, 3, 4],     # Back triangular face
        [3, 0, 4]      # Left triangular face
    ]
    
    # Colors for faces
    colors = [
        (200, 100, 100),  # Base
        (100, 200, 100),  # Front face
        (100, 100, 200),  # Right face
        (200, 200, 100),  # Back face
        (200, 100, 200)   # Left face
    ]
    
    faces = []
    for i, indices in enumerate(face_indices):
        face_vertices = np.array([vertices[idx] for idx in indices])
        faces.append(Face(face_vertices, colors[i], pyramid))
    
    return faces

def extract_faces_from_prism(prism: Prism) -> List[Face]:
    """Extract the faces from a triangular prism object"""
    vertices = prism.vertices
    
    # Define the 5 faces of the prism (2 triangular ends + 3 rectangular sides)
    face_indices = [
        [0, 1, 2],     # Bottom triangular face
        [3, 4, 5],     # Top triangular face
        [0, 3, 4, 1],  # Side rectangular face 1
        [1, 4, 5, 2],  # Side rectangular face 2
        [2, 5, 3, 0]   # Side rectangular face 3
    ]
    
    # Colors for faces
    colors = [
        (255, 100, 100),  # Bottom triangle
        (100, 255, 100),  # Top triangle
        (100, 100, 255),  # Side 1
        (255, 255, 100),  # Side 2
        (255, 100, 255)   # Side 3
    ]
    
    faces = []
    for i, indices in enumerate(face_indices):
        face_vertices = np.array([vertices[idx] for idx in indices])
        faces.append(Face(face_vertices, colors[i], prism))
    
    return faces

def extract_faces_from_cylinder(cylinder: Cylinder) -> List[Face]:
    """Extract the faces from a cylinder object"""
    vertices = cylinder.vertices
    num_segments = cylinder.segments
    
    faces = []
    
    # Top and bottom center indices
    bottom_center_idx = len(vertices) - 2
    top_center_idx = len(vertices) - 1
    
    # Side rectangular faces
    for i in range(num_segments):
        bottom_idx = i * 2
        top_idx = i * 2 + 1
        next_bottom_idx = (i * 2 + 2) % (num_segments * 2)
        next_top_idx = (i * 2 + 3) % (num_segments * 2)
        
        # Create rectangular side face
        face_vertices = np.array([
            vertices[bottom_idx],
            vertices[next_bottom_idx], 
            vertices[next_top_idx], 
            vertices[top_idx]
        ])
        
        # Use color based on segment position for variety
        hue = i / num_segments
        r, g, b = colorsys.hsv_to_rgb(hue, 0.7, 0.9)
        color = (int(r * 255), int(g * 255), int(b * 255))
        
        faces.append(Face(face_vertices, color, cylinder))
    
    # Bottom triangular faces (forming the circle)
    for i in range(num_segments):
        bottom_idx = i * 2
        next_bottom_idx = (i * 2 + 2) % (num_segments * 2)
        
        face_vertices = np.array([
            vertices[bottom_idx],
            vertices[next_bottom_idx],
            vertices[bottom_center_idx]
        ])
        
        faces.append(Face(face_vertices, (100, 100, 150), cylinder))
    
    # Top triangular faces (forming the circle)
    for i in range(num_segments):
        top_idx = i * 2 + 1
        next_top_idx = (i * 2 + 3) % (num_segments * 2)
        
        face_vertices = np.array([
            vertices[top_idx],
            vertices[next_top_idx],
            vertices[top_center_idx]
        ])
        
        faces.append(Face(face_vertices, (150, 100, 100), cylinder))
    
    return faces

def extract_faces_from_octahedron(octahedron: Octahedron) -> List[Face]:
    """Extract the faces from an octahedron object"""
    vertices = octahedron.vertices
    
    # Define the 8 triangular faces of the octahedron
    face_indices = [
        [0, 2, 4],  # Top-Right-Front
        [0, 4, 3],  # Top-Front-Left
        [0, 3, 5],  # Top-Left-Back
        [0, 5, 2],  # Top-Back-Right
        [1, 2, 4],  # Bottom-Right-Front
        [1, 4, 3],  # Bottom-Front-Left
        [1, 3, 5],  # Bottom-Left-Back
        [1, 5, 2]   # Bottom-Back-Right
    ]
    
    # Generate colors for each face
    colors = []
    for i in range(8):
        # Use hue to generate different colors
        hue = i / 8
        r, g, b = colorsys.hsv_to_rgb(hue, 0.8, 0.9)
        colors.append((int(r * 255), int(g * 255), int(b * 255)))
    
    faces = []
    for i, indices in enumerate(face_indices):
        face_vertices = np.array([vertices[idx] for idx in indices])
        faces.append(Face(face_vertices, colors[i], octahedron))
    
    return faces

def extract_faces_from_object(obj: SceneObject) -> List[Face]:
    """Extract faces from any supported object type"""
    try:
        if isinstance(obj, Cuboid):
            return extract_faces_from_cuboid(obj)
        elif isinstance(obj, Pyramid):
            return extract_faces_from_pyramid(obj)
        elif isinstance(obj, Prism):
            return extract_faces_from_prism(obj)
        elif isinstance(obj, Cylinder):
            return extract_faces_from_cylinder(obj)
        elif isinstance(obj, Octahedron):
            return extract_faces_from_octahedron(obj)
        else:
            raise TypeError(f"Unsupported object type: {type(obj)}")
    except IndexError as e:
        print(f"Warning: Could not extract faces from {type(obj).__name__}: {e}")
        return []  # Return empty list if extraction fails

class BSPTree:
    """A Binary Space Partitioning tree"""
    
    def __init__(self):
        self.root = None
        self.face_count = 0  # Track number of faces in tree
    
    def build_tree(self, faces: List[Face]) -> BSPNode:
        """
        Recursively build a BSP tree from a list of faces
        
        Args:
            faces: List of Face objects to organize into a BSP tree
            
        Returns:
            The root node of the BSP tree
        """
        if not faces:
            return None
        
        # Use a better heuristic for selecting a good partition face
        # For simplicity, we'll use the first face but more sophisticated
        # approaches could be implemented here
        partition_face = faces[0]
        node = BSPNode(polygon=partition_face, plane=partition_face.plane)
        
        front_list = []
        back_list = []
        
        # Classify the remaining faces
        for face in faces[1:]:
            front_part, back_part = partition_face.split_polygon(face)
            
            if front_part:
                front_list.append(front_part)
                self.face_count += 1
            if back_part:
                back_list.append(back_part)
                self.face_count += 1
        
        # Recursively build sub-trees
        if front_list:
            node.front = self.build_tree(front_list)
        if back_list:
            node.back = self.build_tree(back_list)
            
        return node
    
    def create_from_objects(self, objects: List[SceneObject]):
        """Build a BSP tree from a list of 3D objects"""
        all_faces = []
        
        # Extract all faces from all objects
        for obj in objects:
            try:
                faces = extract_faces_from_object(obj)
                all_faces.extend(faces)
            except Exception as e:
                print(f"Warning: Error processing {type(obj).__name__}: {e}")
        
        if not all_faces:
            print("Warning: No faces were extracted from objects")
            return
            
        self.face_count = len(all_faces)
        # Build the tree
        self.root = self.build_tree(all_faces)
    
    def traverse_back_to_front(self, node: BSPNode, camera_position: np.ndarray, result: List[Face] = None):
        """
        Traverse the BSP tree from back to front relative to a camera position
        
        Args:
            node: The current node being traversed
            camera_position: The position of the camera
            result: List to fill with faces in back-to-front order
        
        Returns:
            List of Face objects in back-to-front order
        """
        if result is None:
            result = []
            
        if node is None:
            return result
            
        # Classify camera position relative to the node's plane
        if node.polygon is not None:
            classification = node.polygon.classify_point(camera_position)
            
            if classification > 0:  # Camera is in front of the plane
                # Process the back side first, then the node, then the front side
                self.traverse_back_to_front(node.back, camera_position, result)
                
                # Add the current polygon
                # Check if it faces the camera (back-face culling)
                if np.dot(node.polygon.normal, camera_position[:3] - node.polygon.vertices[0][:3]) > 0:
                    result.append(node.polygon)
                
                self.traverse_back_to_front(node.front, camera_position, result)
            else:  # Camera is behind the plane
                # Process the front side first, then the node, then the back side
                self.traverse_back_to_front(node.front, camera_position, result)
                
                # Add the current polygon
                # For back facing polygons, we need to check if it faces away from the camera
                if np.dot(node.polygon.normal, camera_position[:3] - node.polygon.vertices[0][:3]) < 0:
                    result.append(node.polygon)
                
                self.traverse_back_to_front(node.back, camera_position, result)
        
        return result

class PainterBSP:
    """
    Painter's Algorithm using BSP tree for correct depth ordering
    This class manages the rendering order of 3D objects
    """
    
    def __init__(self):
        self.bsp_tree = BSPTree()
        self.last_camera_position = None
        self.layer_count = 0
        
        # Statistics for debugging
        self.stats = {
            'total_faces': 0,
            'tree_depth': 0,
            'build_time': 0,
            'traverse_time': 0
        }
    
    def build_bsp_tree(self, objects: List[SceneObject]):
        """Build a BSP tree from scene objects"""
        # Time the tree building process
        start_time = time.time()
        
        # Build the tree
        self.bsp_tree.create_from_objects(objects)
        
        # Calculate tree depth
        self.stats['tree_depth'] = self._calculate_tree_depth(self.bsp_tree.root)
        self.stats['total_faces'] = self.bsp_tree.face_count
        self.stats['build_time'] = time.time() - start_time
        
    def _calculate_tree_depth(self, node: BSPNode, current_depth: int = 1) -> int:
        """Calculate the maximum depth of the BSP tree"""
        if node is None:
            return 0
            
        # Get depth of front and back subtrees
        front_depth = self._calculate_tree_depth(node.front, current_depth + 1) if node.front else current_depth
        back_depth = self._calculate_tree_depth(node.back, current_depth + 1) if node.back else current_depth
        
        # Return max depth between front and back subtrees
        return max(front_depth, back_depth)
        
    def get_rendering_order(self, camera_position: np.ndarray) -> List[Face]:
        """
        Get the faces in back-to-front order relative to camera position
        
        Args:
            camera_position: The position of the camera in world space
            
        Returns:
            List of faces sorted in back-to-front order for correct rendering
        """
        if self.bsp_tree.root is None:
            return []
        
        # Time the traversal
        start_time = time.time()
        
        # Always recompute the rendering order
        rendering_order = self.bsp_tree.traverse_back_to_front(self.bsp_tree.root, camera_position)
        self.layer_count = len(rendering_order)
        self.last_camera_position = camera_position.copy()
        
        # Update statistics
        self.stats['traverse_time'] = time.time() - start_time
        
        return rendering_order
        
    def get_stats(self) -> dict:
        """Get statistics about the BSP tree and traversal"""
        return self.stats 