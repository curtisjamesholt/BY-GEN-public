#region Information
'''
This file contains classes for buildings menus, such as the
Shift+A sub-menus.
'''
#endregion
#region Module Imports
import bpy
from bpy.props import *
from bpy.types import (Panel,Menu,Operator,PropertyGroup)
#endregion
#region Template
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
#endregion
#region Main Menu
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
#endregion
#region Shift+A
def menu_func(self, context):
    layout = self.layout
    layout.operator_context = 'INVOKE_REGION_WIN'
    layout.separator()
    #layout.operator("object.bygen_generate", text="Generate Test", icon_value=custom_icons["custom_icon"].icon_id)
    layout.menu("VIEW3D_MT_bygen_add", text="BY-GEN")
    layout.separator()
#endregion
#region Shift+A => BY-GEN
class VIEW3D_MT_bygen_add(Menu):
    bl_idname = "VIEW3D_MT_bygen_add"
    bl_label = "BY-GEN"
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        #layout.menu("VIEW3D_MT_bygen_add_scatter", text="Scatter")
        layout.menu("VIEW3D_MT_bygen_add_templates", text="Templates")
        layout.menu("VIEW3D_MT_bygen_add_generators", text="Generators")
#endregion
#region Shift+A => BY-GEN => Scatter
class VIEW3D_MT_bygen_add_scatter(Menu):
    bl_idname = "VIEW3D_MT_bygen_add_scatter"
    bl_label = "Scatter"
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        layout.operator("object.bygen_scatter_city_circular", text="City Scatter - Circular")
        layout.operator("object.bygen_scatter_city_rectangular", text="City Scatter - Rectangular")
#endregion
#region Shift+A => BY-GEN => Templates
class VIEW3D_MT_bygen_add_Templates(Menu):
    bl_idname = "VIEW3D_MT_bygen_add_templates"
    bl_label = "Templates"
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        layout.menu("VIEW3D_MT_bygen_hard_add", text="Hard Surface")
        layout.menu("VIEW3D_MT_bygen_organic_add", text="Organic")
        layout.menu("VIEW3D_MT_bygen_fx_add", text="FX")
#endregion
#region Shift+A => BY-GEN => Generators
class VIEW3D_MT_bygen_add_generators(Menu):
    bl_idname = "VIEW3D_MT_bygen_add_generators"
    bl_label = "Generators"
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        # Operator Calls:
        layout.operator("object.bygen_cubic_field_generate", text="Cubic Field")
        layout.operator("object.bygen_spherical_field_generate", text="Spherical Field")
#endregion
#region Shift+A => BY-GEN => Hard Surface
class VIEW3D_MT_bygen_hard_add(Menu):
    bl_idname = "VIEW3D_MT_bygen_hard_add"
    bl_label = "Hard Surface"
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        # Operator Calls:
        layout.operator("object.bygen_hard_surface_frame_add", text="Hard Surface Frame")
        layout.operator("object.bygen_hard_surface_skin_add", text="Hard Surface Skin")
        layout.operator("object.bygen_hard_surface_skin_simple_add", text="Hard Surface Skin (Simple)")
        layout.operator("object.bygen_hard_surface_faceting_add", text="Hard Surface Faceting")
        layout.operator("object.bygen_metal_shell_add", text="Metal Shell")
        layout.operator("object.bygen_hard_padding_add", text="Hard Padding")
        layout.operator("object.bygen_midge_cell_add", text="Midge Cell")
#endregion
#region Shift+A => BY-GEN => Organic
class VIEW3D_MT_bg_organic(Menu):
    bl_idname = "VIEW3D_MT_bygen_organic_add"
    bl_label = "Organic"
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        # Operator Calls:
        layout.operator("object.bygen_organic_skin_add", text="Organic Skin")
        layout.operator("object.bygen_clay_blob_add", text="Clay Blob")
#endregion
#region Shift+A => BY-GEN => FX
class VIEW3D_MT_bygen_fx_add(Menu):
    bl_idname = "VIEW3D_MT_bygen_fx_add"
    bl_label = "FX"
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        # Operator Calls:
        layout.operator("object.bygen_point_cloud_add", text="Point Cloud")
        layout.operator("object.bygen_pixelate_add", text="Pixelate")
#endregion