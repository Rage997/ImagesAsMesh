import bpy
from . helper import img_to_mesh 
from bpy.props import (
    StringProperty,
    BoolProperty,
    EnumProperty,
    FloatProperty,
    CollectionProperty,
)
import os

class IMPORT_OT_image_to_meshes(bpy.types.Operator):
    """[summary]

    Args:
        bpy ([type]): [description]

    Returns:
        [type]: [description]
    """    

    bl_idname = "import_image.to_mesh"
    bl_label = "Import Images as Meshes"
    bl_options = {"REGISTER", "UNDO"}

    directory: StringProperty(maxlen=1024, subtype='FILE_PATH', options={'HIDDEN', 'SKIP_SAVE'})
    files: CollectionProperty(type=bpy.types.OperatorFileListElement, options={'HIDDEN', 'SKIP_SAVE'})
    height: FloatProperty(name="Height", description="Height of the created mesh",
                           default=1.0, min=0.001, soft_min=0.001, subtype='DISTANCE', unit='LENGTH')
                           
    epsilon: FloatProperty(name="Height", description="Threshold controling how the mesh is generated. If invert is False, \
                            the higher the value the denser the mesh.",
                           default=0.5, min=0.0, max=1)
    invert: BoolProperty(name="Invert mesh", default=False, description="Inverts the process on which the mesh is generated")

    def execute(self, context):
        print('Rendering all NFTs...')

        for f in self.files:
            print(f.name)
            path = os.path.join(self.directory, f.name)
            # img_to_mesh((0,0,0), path)
            img_to_mesh(imgpath=path,
                        invert=self.invert,
                        epsilon=self.epsilon,
                        height=self.height)

        return {'FINISHED'}

    def draw(self, context):
        # --- Import Options --- #
        layout = self.layout
        box = layout.box()

        box.label(text="Import Options:", icon='IMPORT')
        row = box.row()
        row.active = bpy.data.is_saved
        row.prop(self, "files")

        box.prop(self, "epsilon")
        box.prop(self, "invert")
        box.prop(self, "height")
        
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}