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

    files: CollectionProperty(type=bpy.types.OperatorFileListElement, options={'HIDDEN', 'SKIP_SAVE'})
    height: FloatProperty(name="Height", description="Height of the created mesh",
                           default=1.0, min=0.001, soft_min=0.001, subtype='DISTANCE', unit='LENGTH')
    invert: BoolProperty(name="Invert mesh", default=False, description="Inverts how the mesh is generated.")
    directory: StringProperty(maxlen=1024, subtype='FILE_PATH', options={'HIDDEN', 'SKIP_SAVE'})

    def execute(self, context):
        print('Rendering all NFTs...')

        if context.active_object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        # path = '/home/rage/Documents/3d_projects/img_to_mesh/rose.png'
        for f in self.files:
            print(f.name)
            path = os.path.join(self.directory, f.name)
            img_to_mesh((0,0,0), f.name)

        # context.preferences.edit.use_enter_edit_mode = editmode
        return {'FINISHD'}

    def draw(self, context):
        # --- Import Options --- #
        layout = self.layout
        box = layout.box()

        box.label(text="Import Options:", icon='IMPORT')
        row = box.row()
        row.active = bpy.data.is_saved
        row.prop(self, "files")

        box.prop(self, "height")
        box.prop(self, "invert")
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}