bl_info = {  
    "name": "RedHalo Tools",  
    "author": "Red Halo Studio",  
    "version": (0, 1, 2),  
    "blender": (2, 80, 0),  
    "location": "View 3D > Tools > Red Halo Tools",  
    "description": "",  
    "wiki_url": "",  
    "tracker_url": "",  
    "category": "Tools"
 }

import bpy, random, colorsys
from bpy.types import Menu, Operator, Panel

#
# Change Type
#
class REDHALO_OT_changeType(Operator):
    bl_idname = "redhalo_tools.change_type"
    bl_label = "Change Type"
    bl_description = "Change Type from active"
    bl_options = {'REGISTER', 'UNDO'} 

    def execute(self, context): 
        ab = bpy.context.object

        ob = bpy.context.selected_objects

        oriSelected = ob[:]

        #Copy objects
        if ab is not None:
            # for i in range(len(ob)):
            for o in ob:
                new_obj = ab.copy()
                new_obj.location = o.location
                try:
                    bpy.context.collection.objects.link(new_obj)
                except:
                    pass

        #Delete Origin objects
        for o in ob:
            bpy.data.objects.remove(o)


        return {'FINISHED'}

#
# Clear Split Normal
#
class REDHALO_OT_cleanNormal(Operator):
    bl_idname = "redhalo_tools.clear_normal"
    bl_label = "Clear Normal"
    bl_description = "Clear Split Normal Data"
    bl_options = {'REGISTER', 'UNDO'} 

    def execute(self, context): 
        selection = bpy.context.selected_objects

        for o in selection:
            bpy.context.view_layer.objects.active = o
            try:
                bpy.ops.mesh.customdata_custom_splitnormals_clear()
            except:
                print(o.name)

        return {'FINISHED'}
    
#
# Adjust Light Distance
#
class REDHALO_OT_Adjust_Light_Distance(Operator):
    bl_idname = "redhalo.adjust_light_distance"
    bl_label = "Adjust Light Distance"
    bl_description = "Adjust Light Distance\n调整灯光烦人的线长度"

    @classmethod
    def poll(self, context):
        return context.object and context.object.type == 'LIGHT'
    
    def execute(self, context):
        # lights = [obj for obj in bpy.data.objects if obj.type == 'LIGHT']
        lights = [obj for obj in bpy.context.selected_objects if obj.type == 'LIGHT']
        for light in lights:
            light.data.cutoff_distance = self.value / 100.0
        return {'FINISHED'}

    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':  # Apply
            self.value = abs(event.mouse_x - self.init_x)
            self.execute(context)
        elif event.type == 'LEFTMOUSE':  # Confirm
            return {'FINISHED'}
        elif event.type in {'RIGHTMOUSE', 'ESC'}:  # Cancel 
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        self.init_value = context.object.data.cutoff_distance
        self.init_x = event.mouse_prev_x
        self.value = event.mouse_x
        self.execute(context)

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}
    
#
# Remove Zero Face object
#
class REDHALO_OT_RemoveZeroFace(Operator):
    bl_idname = "redhalo_tools.remove_zero_face"
    bl_label = "Remove Zero Face"
    bl_description = "Remove Zero Face"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        empty_objects = []

        for obj in bpy.data.objects:
            if obj.type == "MESH":
                cnt = len(obj.data.vertices)
                if cnt == 0:                   
                    empty_objects.append(obj)
        
        for obj in empty_objects:
            bpy.data.objects.remove(obj)
        
        self.report({"INFO"}, ("[REDHALO_STUDIO]Finished!! Remove " + str(len(empty_objects)) +" Objects"))
        
        return {'FINISHED'}

#
# Render Color ID
#
def renderClrID(node,clr):

    nodes = node.node_tree.nodes
    links = node.node_tree.links

    # 1st node
    for i in nodes.keys():
        t = type(nodes[i])
        if t == bpy.types.ShaderNodeOutputMaterial:
            key = i

    parentNode = nodes[key]
    
    # MixShader Nodes
    node_mixshader = nodes.new(type = "ShaderNodeMixShader")
    node_mixshader.inputs[0].default_value = 1
    node_mixshader.location = (parentNode.location.x - 200),(parentNode.location.y)

    # Transparent Node
    node_transparent = nodes.new(type = "ShaderNodeBsdfTransparent")
    node_transparent.location = (node_mixshader.location.x-200),(node_mixshader.location.y-150)

    #node-emission shader
    node_emission = nodes.new(type="ShaderNodeEmission")
    node_emission.location = (node_mixshader.location.x-200),(node_mixshader.location.y)

    node_emission.inputs[0].default_value = clr

    #node light path
    node_lightPath = nodes.new(type="ShaderNodeLightPath")
    node_lightPath.location = (node_emission.location.x - 200),(node_emission.location.y - 200)
    
    links.new(node_mixshader.outputs[0],parentNode.inputs[0])
    links.new(node_emission.outputs[0],node_mixshader.inputs[2])
    links.new(node_transparent.outputs[0],node_mixshader.inputs[1])
    links.new(node_lightPath.outputs[0],node_emission.inputs[1])

    for i in links:
        if i.to_socket.name == "Alpha":
            # keepLinks = i.from_node
            links.new(i.from_socket, node_mixshader.inputs[0])  

class REDHALO_OT_setColorID(Operator):
    bl_idname = "redhalo_tools.set_color_id"
    bl_label = "Set Color ID for Render"
    bl_description = "Set Color ID for Render\n设置渲染的颜色ID，建议使用此功能前保存一下场景\n可能无法撤销"
    bl_options = {'REGISTER', 'UNDO'} 

    def execute(self, context): 

        #Deselect all objects
        bpy.ops.object.select_all(action='DESELECT')
        
        # Delete all lights
        allLights = [l for l in bpy.context.scene.objects if l.type == "LIGHT"]
        for i in allLights:
            bpy.data.objects.remove(i, do_unlink=True)        

        #Set oject property
        for o in bpy.context.scene.objects:
            # befor 3.00
            if bpy.app.version < (3, 0, 0):
                obj_vis = o.cycles_visibility
                obj_vis.diffuse = False
                obj_vis.glossy = False
                obj_vis.transmission = False
                obj_vis.scatter = False
                obj_vis.shadow = False

            # 3.00 later
            else:
                o.visible_diffuse = False
                o.visible_glossy = False
                o.visible_transmission = False
                o.visible_volume_scatter = False
                o.visible_shadow = False
                
        #all materials in scene
        AllMats = bpy.data.materials[:]

        #Set Color
        clr_o = [(1,0,0),(1,0.5,0),(1,1,0),(0,1,0),(0,1,1),(0,0.5,1),(0,0,1),(0.5,0,1),(1,0,1),(1,0,0.5)]
        clr_f = clr_o

        MatsNum = len(AllMats)

        if MatsNum > 10 :
            if MatsNum > 160:
                li = 160
            else:
                li = MatsNum

            randseek = 0.255
            for i in range(10,li):
                oi = i % 10
                clr_c = clr_o[oi]

                while clr_c in clr_f:
                    hsv = colorsys.rgb_to_hsv(clr_c[0], clr_c[1], clr_c[2])
                    hsv_s = 1 - random.randint(0,3)*randseek
                    hsv_v = 1 - random.randint(0,3)*randseek

                    clr_c = colorsys.hsv_to_rgb(hsv[0], hsv_s, hsv_v)
                
                clr_f.append(clr_c)

        if MatsNum > 160 :
            
            for i in range(160, MatsNum):
                
                clr_new = (random.random(), random.random(), random.random())

                while clr_new in clr_f:
                    clr_new = (random.random(), random.random(), random.random())

                clr_f.append(clr_new)


        if MatsNum > 0:
            for i in range(MatsNum):
                # All Material Use Nodes
                if AllMats[i].use_nodes == False:
                    AllMats[i].use_nodes = True

                clr = clr_f[i] + (1,)
                renderClrID(AllMats[i], clr)
            if MatsNum > 160:
                self.report({"INFO"}, ("[REDHALO_STUDIO]Finished!! Converted " + str(MatsNum) +" Materials"))
            else:
                self.report({"INFO"}, ("[REDHALO_STUDIO]Finished!! Converted " + str(MatsNum) +" Materials, Some issue after 160 materials"))
        else:
            self.report({'ERROR'}, "No material in scene")

        # Set Cycles
        bpy.context.scene.cycles.use_adaptive_sampling = False
        bpy.context.scene.cycles.samples = 96
        bpy.context.scene.cycles.max_bounces = 1
        bpy.context.scene.cycles.film_exposure = 1

        # Color Management
        bpy.context.scene.view_settings.view_transform = "Standard"
        bpy.context.scene.view_settings.look = "None"

        return {'FINISHED'}

#
# Filter Select
#
def filterSelect(type):
    types = ["mesh", "curve", "surf", "meta", "font", "pointcloud", "volume", "grease_pencil", "armature", "lattice", "empty", "light", "light_probe", "camera", "speaker"]

    if type == "all":
        for attr in types:
            exec("bpy.context.space_data.show_object_select_" + attr + " = True")
    else:
        for attr in types:
            re = "False"
            
            attr_s = "bpy.context.space_data.show_object_select_" + attr + " = "
            if type == attr:
                re = "True"
            exec(attr_s + re)

class REDHALO_OT_Filter_Operator(Operator):
    bl_idname = "redhalo_tools.filter_op"
    bl_label = "Filter Objects"

    def get_items(self, context):        
        types = ["all", "mesh", "curve", "surf", "meta", "font", "pointcloud", "volume", "grease_pencil", "armature", "lattice", "empty", "light", "light_probe", "camera", "speaker"]

        return [(ob, "", "") for ob in types]

    action : bpy.props.EnumProperty(
        items = get_items
    )

    def execute(self, context):
        for ob in  context.selected_objects:
            ob.select_set(False)
        types = ["all", "mesh", "curve", "surf", "meta", "font", "pointcloud", "volume", "grease_pencil", "armature", "lattice", "empty", "light", "light_probe", "camera", "speaker"]

        f = bpy.context.scene.filter_option
        
        for i in types:
            if self.action == i:
                filterSelect(i)
                bpy.context.scene.filter_option = i

        return {"FINISHED"}

class REDHALO_MT_FilterSelect(Menu):
    bl_idname = "PIE_MT_filterselect"
    bl_label = "Filter Select"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        box = pie.split().box().column()        

class REDHALO_PT_menu_filterselect(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'HEADER'
    bl_label = "Filter"
    bl_ui_units_x = 5

    bpy.types.Scene.filter_option = bpy.props.StringProperty(name="Filter Option", default = "all")

    def draw(self, context):
        layout = self.layout
        layout.operator("redhalo_tools.filter_op", text="All", icon="ALIGN_JUSTIFY").action = "all"
        layout.separator()
        layout.operator("redhalo_tools.filter_op", text="Mesh", icon="MESH_CUBE").action = "mesh"
        layout.operator("redhalo_tools.filter_op", text="Light", icon="LIGHT").action = "light"
        layout.operator("redhalo_tools.filter_op", text="Camera", icon="CAMERA_DATA").action = "camera"
        layout.operator("redhalo_tools.filter_op", text="Empty", icon="EMPTY_DATA").action = "empty"
        layout.operator("redhalo_tools.filter_op", text="Curve", icon="CURVE_DATA").action = "curve"
        layout.operator("redhalo_tools.filter_op", text="Font", icon="FONT_DATA").action = "font"
        layout.separator()
        layout.operator("redhalo_tools.filter_op", text="Surface", icon="SURFACE_DATA").action = "surf"
        # layout.operator("redhalo_tools.filter_op", text="Hair", icon="HAIR_DATA").action = "hair"
        layout.operator("redhalo_tools.filter_op", text="Point Cloud", icon="POINTCLOUD_DATA").action = "pointcloud"
        layout.operator("redhalo_tools.filter_op", text="Meta", icon="META_DATA").action = "meta"
        layout.operator("redhalo_tools.filter_op", text="Volume", icon="SNAP_VOLUME").action = "volume"
        layout.operator("redhalo_tools.filter_op", text="Grease Pencil", icon="GREASEPENCIL").action = "grease_pencil"
        layout.operator("redhalo_tools.filter_op", text="Armature", icon="ARMATURE_DATA").action = "armature"
        layout.operator("redhalo_tools.filter_op", text="Lattice", icon="LATTICE_DATA").action = "lattice"
        layout.operator("redhalo_tools.filter_op", text="Light Probe", icon="LIGHTPROBE_GRID").action = "light_probe"
        layout.operator("redhalo_tools.filter_op", text="Speaker", icon="SPEAKER").action = "speaker"

def REDHALO_MT_Filter_Menu(self, context):
    if bpy.context.mode == "OBJECT":
        op_text = "F : " + bpy.context.scene.filter_option.capitalize()
        self.layout.popover("REDHALO_PT_menu_filterselect", text = op_text, icon = "PLUS")

class REDHALO_MT_PIE_Filter(Menu):
    bl_idname = "REDHALO_MT_select_mode_pie_filter"
    bl_label = "RedHalo Filter Select"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # operator_enum will just spread all available options
        # for the type enum of the operator on the pie
        pie.operator("redhalo_tools.filter_op", text="Mesh", icon="MESH_CUBE").action = "mesh"
        pie.operator("redhalo_tools.filter_op", text="Camera", icon="CAMERA_DATA").action = "camera"
        # BOTTOM
        pie.menu(REDHALO_MT_PIE_FilterOther.bl_idname, text="Others", icon="PREFERENCES")           
        
        pie.operator("redhalo_tools.filter_op", text="All", icon="ALIGN_JUSTIFY").action = "all"
        pie.operator("redhalo_tools.filter_op", text="Light", icon="LIGHT").action = "light"
        pie.operator("redhalo_tools.filter_op", text="Curve", icon="CURVE_DATA").action = "curve"
        pie.operator("redhalo_tools.filter_op", text="Font", icon="FONT_DATA").action = "font"
        pie.operator("redhalo_tools.filter_op", text="Empty", icon="EMPTY_DATA").action = "empty"  

class REDHALO_MT_PIE_FilterOther(Menu):
    bl_idname = "REDHALO_MT_menu_filterselect_other"
    bl_label = "Filter Select (other)"
    
    def draw(self, context):
        layout = self.layout
        layout.operator("redhalo_tools.filter_op", text="Surface", icon="SURFACE_DATA").action = "surf"
        # layout.operator("redhalo_tools.filter_op", text="Hair", icon="STRANDS").action = "hair"
        layout.operator("redhalo_tools.filter_op", text="Point Cloud", icon="POINTCLOUD_DATA").action = "pointcloud"
        layout.operator("redhalo_tools.filter_op", text="Meta", icon="META_DATA").action = "meta"
        layout.operator("redhalo_tools.filter_op", text="Volume", icon="SNAP_VOLUME").action = "volume"
        layout.operator("redhalo_tools.filter_op", text="Grease Pencil", icon="GREASEPENCIL").action = "grease_pencil"
        layout.operator("redhalo_tools.filter_op", text="Armature", icon="ARMATURE_DATA").action = "armature"
        layout.operator("redhalo_tools.filter_op", text="Lattice", icon="LATTICE_DATA").action = "lattice"

        layout.operator("redhalo_tools.filter_op", text="Light Probe", icon="OUTLINER_OB_LIGHTPROBE").action = "light_probe"
        layout.operator("redhalo_tools.filter_op", text="Speaker", icon="SPEAKER").action = "speaker"

#
# UI Panel
#
class VIEW3D_PT_RedHaloTools(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'RedHalo'
    bl_label = "RED HALO Tools"

    def draw(self, context):    
        layout = self.layout
        split = layout.split()
        col = split.column()
        col.operator('redhalo_tools.set_color_id', icon='COLLAPSEMENU',text = "Color ID")
        col.operator('redhalo_tools.change_type', icon='UV_SYNC_SELECT',text = "Change Type")
        col.operator('redhalo_tools.clear_normal', icon='PANEL_CLOSE',text = "Clear Split Normal Data")
        col.operator('redhalo_tools.remove_zero_face', icon='PANEL_CLOSE',text = "Remove Zero Mesh")
        col.operator("redhalo.adjust_light_distance", text="Adjust Light Distance", icon="FIXED_SIZE")

classes = (
    REDHALO_OT_setColorID, # Set Color ID Operator
    VIEW3D_PT_RedHaloTools, # UI
    REDHALO_OT_changeType, # Change Type Operator
    REDHALO_OT_cleanNormal, # Clean Split Normal Operator
    REDHALO_OT_RemoveZeroFace, # Remove Zero Mesh Operator
    REDHALO_OT_Adjust_Light_Distance,
    #Filter Menu
    REDHALO_PT_menu_filterselect,
    REDHALO_OT_Filter_Operator,
    REDHALO_MT_PIE_Filter,
    REDHALO_MT_PIE_FilterOther
)

addon_keymaps = []

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    # bpy.types.VIEW3D_HT_header.append(REDHALO_MT_Filter_Menu)
    
    wm = bpy.context.window_manager
    if wm.keyconfigs.addon:
            km = wm.keyconfigs.addon.keymaps.new(name='Object Mode')
            kmi = km.keymap_items.new('wm.call_menu_pie', 'F', 'PRESS', alt = True)
            kmi.properties.name = "REDHALO_MT_select_mode_pie_filter"
            addon_keymaps.append((km, kmi))

def unregister():
    # bpy.types.VIEW3D_HT_header.remove(REDHALO_MT_Filter_Menu)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)
    addon_keymaps.clear()

if __name__ == "__main__":
     register()