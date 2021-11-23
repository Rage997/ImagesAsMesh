import bpy
import sys
import numpy as np
import math
import bmesh

def load_image(path:str, scale_factor=0.5) -> np.array:
    
    img = bpy.data.images.load(path)
    print('Number pixels', img.size[:])
    scale_x, scale_y = img.size[0]*scale_factor, img.size[1]*scale_factor 
    img.scale(int(scale_x), int(scale_x)) 
    
    width, height = img.size[0], img.size[1]
    print('Number pixels after compression ({}, {})'.format(width, height))
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
    print(grid.shape)
    return grid

def grid_to_mesh(grid, cell_width, cell_height):
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
#    width, height = [x+1 for x in grid.shape]
#    print(width, height)
    vertex_dict = {}

    vertices = []
    faces = []

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
#        print(value)
        if value==0:
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


def post_import(obj):

    '''
    Performs post import operations such as select object and set
    origin to the center of mass.
    '''

    obj.select_set(True)
    bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')
    obj.select_set(False)

def img_to_mesh(imgpath: str,
                resolution=50,
                invert=False,
                epsilon=0.5,
                height=10,
                scale=(1, 1, 1),
                rot=(0, 0, 0)):

    """Loads an image as a mesh in Blender.

    Args:
        imgpath (str): path to the image
        invert (bool, optional): invert the procedure on how the mesh is generated. Defaults to False.
        epsilon (float, optional): threshold controling how the mesh is generated. 
                                    If not inverted, the higher the value the denser
                                    the mesh. Defaults to 0.5.
        scale (tuple, optional): scale the mesh. Defaults to (1, 1, 1).
        rot (tuple, optional): rotates the mesh. Defaults to (0, 0, 0).

    Returns:
        object: the new blender's object
    """    
    
    # Load image into blender and then into numpy array
    img = load_image(imgpath, scale_factor=resolution/100)
    # Use threshold epsilon to determine what pixels are holes
    # and which pixels are voxel
    low_values_indices = img > epsilon
    if invert:
        img[low_values_indices] = 1
        img[np.invert(low_values_indices)] = 0 
    else:    
        img[low_values_indices] = 0
        img[np.invert(low_values_indices)] = 1 
    
    # Create 2D hole grid
    verts, faces = grid_to_mesh(img, 1, 1)

    # Add third dimmension
    d_verts = [(x, y, 0.) for x, y in verts]
    d_faces = faces

    # Create mesh inside blender
    # TODO this is lazy coding. I should set the origin here
    # not in the post_import() function.
    origin = (0, 0, 0)
    obj = createMesh('Image_mesh', origin, d_verts, [], d_faces, height=height)
    
    obj.scale = scale
    obj.rotation_euler = rot
    
    post_import(obj)

    return obj

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

    
# Testing or if you want to run the script from commandline
if __name__ == "__main__":
    clean_scene()
    img_to_mesh("/home/rage/Documents/3d_projects/ImagesAsMesh/images/pink_rose.jpg", invert=True)