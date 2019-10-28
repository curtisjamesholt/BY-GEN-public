import bpy
from bpy.props import *
from bpy.types import (Panel,Menu,Operator,PropertyGroup)
# //====================================================================//
#    < Menus >
# //====================================================================//
class OBJECT_MT_CustomMenu(bpy.types.Menu):
    bl_idname = "object.custom_menu"
    bl_label = "Select"

    def draw(self, context):
        layout = self.layout

        # Built-in operators
        layout.operator("object.select_all", text="Select/Deselect All").action = 'TOGGLE'
        layout.operator("object.select_all", text="Inverse").action = 'INVERT'
        layout.operator("object.select_random", text="Random")