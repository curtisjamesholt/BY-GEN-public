#                                
#               @@@@@@@@@               
#           @@@           @@@           
#        @@@    @@@@@@@@@    @@@        
#       @@   @@@@@@@@@@@@@@@   @@       
#     @@   @@@@@@@@@@@@@@@@@@@   @@     
#     @   @@@@@@@@@@@@@@@@@@@@@   @     
#    @@  @@@@@@@@@@@@@@@@@@@@@@@  @@    
#    @@                           @@    
#    @@                           @@    
#    @@  @@@@@@@@@@@@@@@@@@@@@@@  @@    
#     @   @@@@@@@@@@@@@@@@@@@@@   @     
#     @@   @@@@@@@@@@@@@@@@@@@   @@     
#       @@   @@@@@@@@@@@@@@@   @@       
#        @@@    @@@@@@@@@    @@@        
#           @@@           @@@           
#               @@@@@@@@@               
#
'''
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
bl_info = {
    "name" : "BY-GEN",
    "author" : "Curtis Holt",
    "description" : "A generative modeling toolkit by Curtis Holt.",
    "blender" : (2, 81, 0),
    "version" : (0, 0, 6),
    "location" : "View3D",
    "warning" : "",
    "category" : "Generic"
}

#Module and Class Imports
import bpy
import bmesh
import random
import bpy.utils.previews
import os
from mathutils import Vector, Matrix
from bpy.props import *
from bpy.types import (Panel,Menu,Operator,PropertyGroup,)
#BY-GEN Classes
from . ui.panels import OBJECT_PT_ByGenGenerate, OBJECT_PT_ByGenModify, OBJECT_PT_ByGenTools, OBJECT_PT_ByGenInterpreter, OBJECT_PT_ByGenInfo, OBJECT_PT_ByGenStructuredGeneration
from . ui.menus import OBJECT_MT_CustomMenu, BYGEN_MT_Menu
from . operators.scatter import (BYGEN_OT_Scatter_City_Circular, BYGEN_OT_Scatter_City_Rectangular)
from . operators.generate import (BYGEN_OT_Generate)
from . operators.layered_generation import (BYGEN_OT_Layered_Generation)
from . operators.branched_generation import (BYGEN_OT_Branched_Generation)
from . operators.generate_calls import (BYGEN_OT_hard_surface_skin_add, BYGEN_OT_organic_skin_add, BYGEN_OT_clay_blob_add, BYGEN_OT_hard_surface_faceting_add, BYGEN_OT_template_add, 
BYGEN_OT_metal_shell_add, BYGEN_OT_hard_padding_add, BYGEN_OT_point_cloud_add, BYGEN_OT_pixelate_add, BYGEN_OT_hard_surface_skin_simple_add, BYGEN_OT_cubic_field_generate, 
BYGEN_OT_spherical_field_generate, BYGEN_OT_meta_cloud_generate, BYGEN_OT_midge_cell_add)
from . operators.modify import BYGEN_OT_Modify
from . operators.tools import BYGEN_OT_ApplyModifiers, BYGEN_OT_PurgeTextures, BYGEN_OT_ClearGenerationResultCollection, BYGEN_OT_BackupGenerationResultCollection
from . interpreter.interpreter import (BYGEN_OT_interpret_input, BYGEN_OT_interpret_output)

# //====================================================================//
#    < Global Variables >
# //====================================================================//
custom_icons = None
# //====================================================================//
#    < Properties >
# //====================================================================//
class BGProperties(PropertyGroup):

    #IntProperty, FloatProperty, FloatVectorProperty, StringProperty, EnumProperty

    #Miscelaneous
    secret_string: StringProperty(
        name="Super secret boy band.",
        description="I don't wanna join your super secret boy band.",
        default="Indigo Bridge"
    )

    #///////////////////////////////////////////////////////////////////
    # GENERATION PROPERTIES
    #///////////////////////////////////////////////////////////////////
    #..... BOOLEANS >
    gen_hss_allow_mirror: BoolProperty(
        name="Allow Mirror",
        description="Allow the addition of a mirror modifier",
        default = True
        )
    #..... ENUMARATIONS >
    mode_generate: EnumProperty(
        name="Generation Type",
        description="The type of generation to perform",
        items=[
            ('GEN_META_CLOUD', "Meta Cloud", "")
        ],
        default="GEN_META_CLOUD"
        )
    mode_gen_disp: EnumProperty(
        name="Generation Displacement Type",
        description="The displacement type for the generation",
        items=[
            ('MODE_GD_CLOUDS', "Clouds", ""),
            ('MODE_GD_DISTNOISE', "Distorted Noise", ""),
            ('MODE_GD_MARBLE', "Marble", ""),
            ('MODE_GD_MUSGRAVE', "Musgrave", ""),
            ('MODE_GD_STUCCI', "Stucci", ""),
            ('MODE_GD_VORONOI', "Voronoi", ""),
            ('MODE_GD_WOOD', "Wood", "")
        ],
        default="MODE_GD_MUSGRAVE"
    )
    #..... FLOATS >
    gen_decimate_collapse: FloatProperty(
        name = "Decimate Collapse",
        description = "Collapse ratio for the Decimation modifier",
        default = 0.2,
        min = 0.0,
        max = 1.0
        )
    gen_decimate_angle: FloatProperty(
        name = "Decimate Angle",
        description = "Planar angle for the Decimation modifier",
        default = 0.174533,
        min = 0.0,
        max = 1.0
        )
    #///////////////////////////////////////////////////////////////////
    # MODIFICATION PROPERTIES
    #///////////////////////////////////////////////////////////////////
    #..... BOOLEANS >
    modAllow: BoolProperty(
        name="Allow Old Mods",
        description="Allow modification when modifiers are present",
        default = True
        )
    mod_hsf_allow_mirror: BoolProperty(
        name="Allow Mirror",
        description="Allow the addition of a mirror modifier",
        default = False
        )
    mod_hss_allow_mirror: BoolProperty(
        name="Allow Mirror",
        description="Allow the addition of a mirror modifier",
        default = True
        )
    mod_mshell_allow_triangulate: BoolProperty(
        name="Triangulate",
        description="Allow the addition of a triangulate modifier",
        default = True
        )
    mod_oshell_allow_triangulate: BoolProperty(
        name="Triangulate",
        description="Allow the addition of a triangulate modifier",
        default = False
        )
    mod_hp_allow_triangulate: BoolProperty(
        name="Triangulate",
        description="Allow the addition of a triangulate modifier",
        default = False
    )
    mod_pc_create_material: BoolProperty(
        name="Create Emissive Material",
        description="Allows for the creation of an emissive material",
        default=False
    )
    #..... ENUMERATIONS >
    mode_mod_disp: EnumProperty(
        name="Generation Displacement Type",
        description="The displacement type for the generation",
        items=[
            ('MODE_MD_CLOUDS', "Clouds", ""),
            ('MODE_MD_DISTNOISE', "Distorted Noise", ""),
            ('MODE_MD_NOISE', 'Noise', ""),
            ('MODE_MD_MARBLE', "Marble", ""),
            ('MODE_MD_MUSGRAVE', "Musgrave", ""),
            ('MODE_MD_STUCCI', "Stucci", ""),
            ('MODE_MD_VORONOI', "Voronoi", ""),
            ('MODE_MD_WOOD', "Wood", "")
        ],
        default="MODE_MD_MUSGRAVE"
    )
    mode_modify: EnumProperty(
        name="Modify Type",
        description="The type of style to apply",
        items=[
            ('MODE_DEST', "Destructor", ""),
            ('MODE_HSF', 'Hard Surface Faceting', ""),
            ('MODE_HSS', "Hard Surface Skin", ""),
            ('MODE_HP', 'Hard Padding', ""),
            ('MODE_MSHELL', 'Metal Shell', ""),
            ('MODE_OSHELL', 'Organic Shell', ""),
            ('MODE_MIDGE_CELL', 'Midge - Cell', ""),
            ('MODE_PC','FX - Point Cloud',""),
            ('MODE_PIX', 'FX - Pixelate', ""),
        ],
        default="MODE_HSF"
        )
    #..... FLOATS >
    mod_decimate_collapse: FloatProperty(
        name = "Decimate Collapse",
        description = "Collapse ratio for the Decimation modifier",
        default = 0.2,
        min = 0.0,
        max = 1.0
        )
    mod_decimate_angle: FloatProperty(
        name = "Decimate Angle",
        description = "Planar angle for the Decimation modifier",
        default = 0.174533,
        min = 0.0,
        max = 1.0
        )
    #///////////////////////////////////////////////////////////////////
    # INTERPRETER PROPERTIES
    #///////////////////////////////////////////////////////////////////
    #..... STRINGS >
    input_text_source : StringProperty(
        name = "Input Source",
        description = "Input source for the interpreter",
        default = "[Text Object Name]"
    )
    output_text_source : StringProperty(
        name = "Output Source",
        description = "Output source for the interpreter",
        default = "[Text Object Name]"
    )
    #..... BOOLEANS>
    remove_pre_existing : BoolProperty(
        name = "Remove Pre-Existing",
        description = "Remove modifiers on selected object before reading input",
        default = False
    )

# //====================================================================//
#    < Interface >
# //====================================================================//

#Shift+A => BY-GEN
class VIEW3D_MT_bygen_add(Menu):
    bl_idname = "VIEW3D_MT_bygen_add"
    bl_label = "BY-GEN"
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        layout.menu("VIEW3D_MT_bygen_add_scatter", text="Scatter")
        layout.menu("VIEW3D_MT_bygen_add_templates", text="Templates")
        layout.menu("VIEW3D_MT_bygen_add_generators", text="Generators")

#Shift+A => BY-GEN => Scatter
class VIEW3D_MT_bygen_add_scatter(Menu):
    bl_idname = "VIEW3D_MT_bygen_add_scatter"
    bl_label = "Scatter"
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        layout.operator("object.bygen_scatter_city_circular", text="City Scatter - Circular")
        layout.operator("object.bygen_scatter_city_rectangular", text="City Scatter - Rectangular")

#Shift+A => BY-GEN => Templates
class VIEW3D_MT_bygen_add_Templates(Menu):
    bl_idname = "VIEW3D_MT_bygen_add_templates"
    bl_label = "Templates"
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        layout.menu("VIEW3D_MT_bygen_hard_add", text="Hard Surface")
        layout.menu("VIEW3D_MT_bygen_organic_add", text="Organic")
        layout.menu("VIEW3D_MT_bygen_fx_add", text="FX")

#Shift+A => BY-GEN => Generators
class VIEW3D_MT_bygen_add_generators(Menu):
    bl_idname = "VIEW3D_MT_bygen_add_generators"
    bl_label = "Generators"
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        #Operator Calls:
        layout.operator("object.bygen_cubic_field_generate", text="Cubic Field")
        layout.operator("object.bygen_spherical_field_generate", text="Spherical Field")

#Shift+A => BY-GEN => Hard Surface
class VIEW3D_MT_bygen_hard_add(Menu):
    bl_idname = "VIEW3D_MT_bygen_hard_add"
    bl_label = "Hard Surface"
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        #Operator Calls:
        layout.operator("object.bygen_hard_surface_skin_add", text="Hard Surface Skin")
        layout.operator("object.bygen_hard_surface_skin_simple_add", text="Hard Surface Skin (Simple)")
        layout.operator("object.bygen_hard_surface_faceting_add", text="Hard Surface Faceting")
        layout.operator("object.bygen_metal_shell_add", text="Metal Shell")
        layout.operator("object.bygen_hard_padding_add", text="Hard Padding")
        layout.operator("object.bygen_midge_cell_add", text="Midge Cell")

#Shift+A => BY-GEN => Organic
class VIEW3D_MT_bg_organic(Menu):
    bl_idname = "VIEW3D_MT_bygen_organic_add"
    bl_label = "Organic"
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        #Operator Calls:
        layout.operator("object.bygen_organic_skin_add", text="Organic Skin")
        layout.operator("object.bygen_clay_blob_add", text="Clay Blob")

#Shift+A => BY-GEN => FX
class VIEW3D_MT_bygen_fx_add(Menu):
    bl_idname = "VIEW3D_MT_bygen_fx_add"
    bl_label = "FX"
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        #Operator Calls:
        layout.operator("object.bygen_point_cloud_add", text="Point Cloud")
        layout.operator("object.bygen_pixelate_add", text="Pixelate")

def menu_func(self, context):
    layout = self.layout
    layout.operator_context = 'INVOKE_REGION_WIN'
    layout.separator()
    #layout.operator("object.bygen_generate", text="Generate Test", icon_value=custom_icons["custom_icon"].icon_id)
    layout.menu("VIEW3D_MT_bygen_add", text="BY-GEN", icon_value=custom_icons["custom_icon"].icon_id)
    layout.separator()


# //====================================================================//
#    < Registration >
# //====================================================================//
classes = (
    #Properties
    BGProperties,
    # > From generate.py
    BYGEN_OT_Generate,
    BYGEN_OT_Modify,
    # > From layered_generation.py
    BYGEN_OT_Layered_Generation,
    # > From branched_generation.py
    BYGEN_OT_Branched_Generation,
    # > From tools.py
    BYGEN_OT_ApplyModifiers,
    BYGEN_OT_PurgeTextures,
    BYGEN_OT_ClearGenerationResultCollection,
    BYGEN_OT_BackupGenerationResultCollection,
    # > Basic Interface
    OBJECT_MT_CustomMenu,
    OBJECT_PT_ByGenGenerate,
    OBJECT_PT_ByGenModify,
    OBJECT_PT_ByGenStructuredGeneration,
    OBJECT_PT_ByGenTools,
    OBJECT_PT_ByGenInterpreter,
    OBJECT_PT_ByGenInfo,
    # > Menu classes
    BYGEN_MT_Menu,
    VIEW3D_MT_bygen_add,
    VIEW3D_MT_bygen_add_scatter,
    VIEW3D_MT_bygen_add_Templates,
    VIEW3D_MT_bygen_add_generators,
    VIEW3D_MT_bygen_hard_add,
    VIEW3D_MT_bg_organic,
    VIEW3D_MT_bygen_fx_add,
    # > From scatter.py
    BYGEN_OT_Scatter_City_Circular,
    BYGEN_OT_Scatter_City_Rectangular,
    # > From generate_calls.py
    #Templates
    BYGEN_OT_hard_surface_skin_add,
    BYGEN_OT_organic_skin_add,
    BYGEN_OT_clay_blob_add,
    BYGEN_OT_hard_surface_faceting_add,
    BYGEN_OT_template_add,
    BYGEN_OT_metal_shell_add,
    BYGEN_OT_hard_padding_add,
    BYGEN_OT_point_cloud_add,
    BYGEN_OT_pixelate_add,
    BYGEN_OT_hard_surface_skin_simple_add,
    BYGEN_OT_midge_cell_add,
    #Generators
    BYGEN_OT_cubic_field_generate,
    BYGEN_OT_spherical_field_generate,
    #Generators - Modify (req input)
    BYGEN_OT_meta_cloud_generate,
    # > From interpreter.py
    BYGEN_OT_interpret_input,
    BYGEN_OT_interpret_output
)
keys = []
def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    bpy.types.Scene.by_tool = PointerProperty(type=BGProperties)
    #Adding Shift+A Menu
    bpy.types.VIEW3D_MT_add.append(menu_func)

    #Input Registration for Menu
    wm = bpy.context.window_manager
    active_keyconfig = wm.keyconfigs.active
    addon_keyconfig = wm.keyconfigs.addon
    kc = addon_keyconfig
    if not kc:
        return

    #BY-GEN MENU PREPARATION FOR FUTURE USE
    #Register to 3D View
    '''
    km = kc.keymaps.new(name="3D View", space_type = "VIEW_3D")
    kmi = km.keymap_items.new("wm.call_menu", "U", "PRESS")
    kmi.properties.name = "BYGEN_MT_Menu"
    keys.append((km, kmi))
    '''

    #Icon Setup
    global custom_icons
    custom_icons = bpy.utils.previews.new()
    icons_dir = os.path.join(os.path.dirname(__file__), "icons")
    custom_icons.load("custom_icon", os.path.join(icons_dir, "bygen_logo_small.png"), 'IMAGE')

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.by_tool
    #Shift+A Menu
    bpy.types.VIEW3D_MT_add.remove(menu_func)
    #Icon Removal
    global custom_icons
    bpy.utils.previews.remove(custom_icons)

if __name__ == "__main__":
    register()