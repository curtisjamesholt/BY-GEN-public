import bpy
from bpy.props import *
from bpy.types import (Panel,Menu,Operator,PropertyGroup)
# //====================================================================//
#    < Menus >
# //====================================================================//

class OBJECT_MT_CustomMenu(bpy.types.Menu):
    #bl_idname = "object.custom_menu"
    bl_idname = "OBJECT_MT_ByGenCustomMenu"
    bl_label = "Select"

    def draw(self, context):
        layout = self.layout
        # Built-in operators
        layout.operator("object.select_all", text="Select/Deselect All").action = 'TOGGLE'
        layout.operator("object.select_all", text="Inverse").action = 'INVERT'
        layout.operator("object.select_random", text="Random")

#BY-GEN Main Menu Variations (FOR FUTURE USE)
class BYGEN_MT_Menu(Menu):
    bl_idname = "BYGEN_MT_Menu"
    bl_label = "BYGEN Menu"

    def draw(self, context):
        layout = self.layout
        sO = context.active_object
        wm = context.window_manager

        #No Object Selected:
        if sO is None:
            self.draw_without_active_object(layout)
            layout.separator()
            #layout.menu("CLASSNAME", text="TEXT")

        elif sO.mode == "OBJECT":
            self.draw_object_menu(layout)

    def draw_object_menu(self, layout):
        layout.separator()
        #layout.menu("CLASSNAME", text="TEXT")