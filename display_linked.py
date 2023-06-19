import bpy
import blf

font_info = {
    "font_id": 0,
    "handler": None,
}


def init():
    """init function - runs once"""

    # set the font drawing routine to run every frame
    font_info["handler"] = bpy.types.SpaceView3D.draw_handler_add(
        draw_callback_px, (None, None), 'WINDOW', 'POST_PIXEL')


def draw_callback_px(self, context):
    """Draw on the viewports"""
    # BLF drawing routine
    
    width = bpy.context.area.regions[1].width
    height = bpy.context.area.regions[1].height
    
    obj = bpy.context.active_object
    u = obj.data.users
    
    font_id = font_info["font_id"]
    blf.position(font_id, width/2, height, 0)
    blf.size(font_id, 12, 72)
    
    if u > 1 :
        dis_text = obj.name + " [ " + str(u) + " ]"
        blf.color(font_id, 1, 0, 0, 1)
        blf.draw(font_id, dis_text)
    else:
        blf.color(font_id, 1, 1, 1, 1)
        blf.draw(font_id, obj.name)