import bpy

class REDHALO_OT_RemoveZeroFace(bpy.types.Operator):
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