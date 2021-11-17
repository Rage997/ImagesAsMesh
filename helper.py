import bpy
import sys
import numpy as np
import math
import bmesh

def load_image(path:str) -> np.array:
    
    img = bpy.data.images.load(path)
    print('Number pixels', img.size[:])
    img.scale(50, 50) 
    print('Number pixels after compression', img.size[:])
    width, height = img.size[0], img.size[1]
    arr = np.array(img.pixels[:])
    # Blender store images as a list containing the RGBA components
    # of each pixel, Here they are converted into grayscale, and then
    # reshaped into a 2D array
    grid = np.zeros(len(arr)//4) #One channel G
    #TODO I m not sure about what happens if the image is not RGBA. 
    # Will blender automatically convert it to RGBA?
    for x in range(0, len(arr), 4):
        grid[x//4] = (arr[x]+arr[x+1]+arr[x+2])/3 #Convert img to gray code. 
    
    grid = np.reshape(grid, (width, height)) #reshape as matrix 
    
    return grid

def grid_to_mesh(grid, cell_width, cell_height, hole_func=None):
    """
    Generate mesh from 
    Arguments:
        grid (numpy array):
        cell_width (number):
        cell_width (number):
        hole_func (callable): Function that determines if a cell is a hole
            in the grid or solid
    Returns:
        vertices (list):
        faces (list):
    """
    width, height = [x+1 for x in grid.shape]
    vertex_dict = {}

    vertices = []
    faces = []

    if hole_func is None:
        hole_func = lambda x: x==0

    def vertex_id(vertex):
        """
        Returns vertex id, or assigns a new unique one if there was None.
        """
        vid = vertex_dict.get(vertex, None)

        if vid is None:
            vertices.append(vertex)
            vid = len(vertices)-1
            vertex_dict[vertex] = vid

        return vid

    # Create faces
    for cell, value in np.ndenumerate(grid):
        if hole_func(value):
            continue

        x, y = cell
        top_left = vertex_id((x, y+1))
        top_right = vertex_id((x+1, y+1))
        bottom_left = vertex_id((x, y))
        bottom_right = vertex_id((x+1, y))
        faces.append((bottom_left, bottom_right, top_right, top_left))


    # Convert vertices to real dimmensions using cell width and cell height
    vertices = [(x*cell_width, y*cell_height) for x, y in vertices]

    return vertices, faces


def createMesh(name, origin, verts, edges, faces, height = 10):

    # Create mesh and object
    me = bpy.data.meshes.new(name+'Mesh')
    ob = bpy.data.objects.new(name, me)
    ob.location = origin
    ob.show_name = True
    # Link object to scene
    bpy.context.collection.objects.link(ob)
 
    # Create mesh from given verts, edges, faces. Either edges or
    # faces should be [], or you ask for problems
    me.from_pydata(verts, edges, faces)
 
    # Update mesh with new data
    me.update(calc_edges=True)
    
    #Extrude the mesh alogn the normal to
    bm = bmesh.new()
    bm.from_mesh(me)
    up_vector = np.array([0, 0, 1])
    
    #Extrude all faces    
    #TODO exmploy a discretization in the emsh height
    extruded = bmesh.ops.extrude_face_region(bm, geom=bm.faces)
    translate_verts = [vert for vert in extruded['geom']  if isinstance(vert, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=height*up_vector, verts=translate_verts)

    bm.to_mesh(me)
    bm.free()
    return ob


def img_to_mesh(origin: (int, int, int), imgpath: str, 
                scale=(1, 1, 1), rot=(0, 0, 0)):
    
    threshold = 0.5
    # TODO: add invert flag
    invert = False
    # Load image into blender and then into numpy array
    img = load_image(imgpath)
    # Use threshold to determine what pixels are holes
    low_values_indices = img > threshold  # Where values are low
    print(low_values_indices)
    img[low_values_indices] = 0
    img[np.invert(low_values_indices)] = 255 
    # Create 2D hole grid
    verts, faces = grid_to_mesh(img, 0.5, 0.5)

    # Add third dimmension
    d_verts = [(x, y, 0.) for x, y in verts]
    d_faces = faces

    # Create mesh inside blender
    ob = createMesh('Image_mesh', origin, d_verts, [], d_faces)
    
    ob.scale = scale
    ob.rotation_euler = rot
    
    return ob

def clean_scene():
    for o in bpy.context.scene.objects:
        if o.type == 'MESH':
            o.select_set(True)
        else:
            o.select_set(False)
    bpy.ops.object.delete()   

def compute_intersection(obj1, obj2):
    obj1.select_set(True) 
    #sets the obj accessible to bpy.ops
    bpy.context.view_layer.objects.active = obj1
    
    #Create boolean modifier and set it to intersection
    tmp_obj = bpy.context.view_layer.objects.active #temp reference
    bpy.ops.object.modifier_add(type='BOOLEAN')
    tmp_obj.modifiers['Boolean'].operation = 'INTERSECT'
    tmp_obj.modifiers['Boolean'].object = obj2

    