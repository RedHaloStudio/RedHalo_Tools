bl_info = {  
    "name": "Red Halo Tools",  
    "author": "Red Halo Studio",  
    "version": (0, 1, 1),  
    "blender": (2, 80, 0),  
    "location": "View 3D > Tools > Red Halo Tools",  
    "description": "",  
    "wiki_url": "",  
    "tracker_url": "",  
    "category": "Tools"
 }

import bpy
from bpy.types import Operator

from .set_color_id import REDHALO_OT_setColorID
from .change_type import REDHALO_OT_changeType
from .clear_normal import REDHALO_OT_cleanNormal
from .filterSelect import REDHALO_PT_menu_filterselect, REDHALO_OT_Filter_Operator, REDHALO_MT_Filter_Menu
from .display_linked import *
from .RemoveZeroMesh import *

class VIEW3D_PT_RedHaloTools(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'    
    bl_label = "RED HALO Tools"

    def draw(self, context):    
        layout = self.layout

        split = layout.split()
        col = split.column()
        # col = layout.column(align=True)
        col.operator('redhalo_tools.set_color_id', icon='COLLAPSEMENU',text = "Color ID")
        col.operator('redhalo_tools.change_type', icon='UV_SYNC_SELECT',text = "Change Type")
        col.operator('redhalo_tools.clear_normal', icon='PANEL_CLOSE',text = "Clear Split Normal Data")
        col.operator('redhalo_tools.remove_zero_face', icon='PANEL_CLOSE',text = "Remove Zero Mesh")        

classes = (
    REDHALO_OT_setColorID, # Set Color ID Operator
    VIEW3D_PT_RedHaloTools, # UI
    REDHALO_OT_changeType, # Change Type Operator
    REDHALO_OT_cleanNormal, # Clean Split Normal Operator
    REDHALO_OT_RemoveZeroFace, # Remove Zero Mesh Operator
    
    #Filter Menu
    REDHALO_PT_menu_filterselect,
    REDHALO_OT_Filter_Operator,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.VIEW3D_HT_header.append(REDHALO_MT_Filter_Menu)
    # bpy.types.VIEW3D_MT_editor_menus.append(REDHALO_MT_Filter_Menu)
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name = 'Object Mode')
    kmi = km.keymap_items.new('redhalo_tools.filter_op', 'F', 'PRESS', alt=True)
    kmi.active = True

def unregister():
    bpy.types.VIEW3D_HT_header.remove(REDHALO_MT_Filter_Menu)

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    addon_keymaps = []
    
    wm = bpy.context.window_manager

    if wm.keyconfigs.addon:
        for km in addon_keymaps:
            for kmi in km.keymap_items:
                km.keymap_items.remove(kmi)

            wm.keyconfigs.addon.keymaps.remove(km)

    addon_keymaps.clear()
if __name__ == "__main__":
     register()
     display_linked.init()