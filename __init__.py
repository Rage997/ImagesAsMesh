# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bpy
from . operator import IMPORT_OT_image_to_meshes

bl_info = {
    "name" : "ImagesAsMeshes",
    "author" : "rage",
    "description" : "",
    "blender" : (2, 93, 5),
    "version" : (0, 0, 1),
    "location" : "File > Import > Images as Meshes",
    "warning" : "",
    "category" : "Import-Export"
}

def import_images_button(self, context):
    self.layout.operator(IMPORT_OT_image_to_meshes.bl_idname,
                         text="Images as Meshes")

def register():
    bpy.utils.register_class(IMPORT_OT_image_to_meshes)
    bpy.types.TOPBAR_MT_file_import.append(import_images_button)

def unregister():
    bpy.utils.unregister_class(IMPORT_OT_image_to_meshes)
    bpy.types.TOPBAR_MT_file_import.remove(import_images_button)
