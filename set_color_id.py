import bpy
import random
import colorsys
from bpy.types import Operator 


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