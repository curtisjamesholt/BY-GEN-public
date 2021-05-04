#region Information
#                                
#               @@@@@@@@@@               
#           @@@            @@@           
#        @@@    @@@@@@@@@@    @@@        
#       @@   @@@@@@@@@@@@@@@@   @@       
#     @@   @@@@@@@@@@@@@@@@@@@@   @@     
#     @   @@@@@@@@@@@@@@@@@@@@@@   @     
#    @@  @@@@@@@@@@@@@@@@@@@@@@@@  @@    
#    @@                            @@    
#    @@                            @@    
#    @@  @@@@@@@@@@@@@@@@@@@@@@@@  @@    
#     @   @@@@@@@@@@@@@@@@@@@@@@   @     
#     @@   @@@@@@@@@@@@@@@@@@@@   @@     
#       @@   @@@@@@@@@@@@@@@@   @@       
#        @@@    @@@@@@@@@@    @@@        
#           @@@            @@@           
#               @@@@@@@@@@               
#
'''
Hi, and welcome to the BY-GEN addon codespace. Sections of code inside of the
files have been separated be region folds for easy navigation (provided your
text editor supports region folds - I recommend VS Code),
Read below to find your way around.
- __init__.py Sets up the addon and registers all of the appropriate classes.
- generate.py Contains operators called from Shift+A menu to help users call template effect objects (and object creation generators).
- modify.py Contains operators called to apply generative styles to pre-existing objects.
- scatter.py Contains operators used to help scatter objects throughout the scene. (City)
- branched_generation.py Contains operators used for branched generation techniques (Space Station)
- layered_generation.py Contains operators used for layered generation techniques (Mech)
- tools.py Contains operators used for various helper tools.
- interpreter.py Contains operators used for the modifier stack interpreter.
- panels.py Contains the classes for creating the tool panels that appear alongside the 3D viewport.
- menus.py Contains classes for creating custom menus.
'''
#endregion
#region License
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
#endregion
#region Addon Metadata
# Blender Addon Metadata
bl_info = {
    "name" : "BY-GEN",
    "author" : "Curtis Holt",
    "description" : "A generative modeling toolkit by Curtis Holt.",
    "blender" : (2, 93, 0),
    "version" : (0, 8, 0),
    "location" : "View3D",
    "warning" : "",
    "category" : "Generic"
}
#endregion
#region Module and Class Imports
# -- Modules
import bpy
import bmesh
import random
import bpy.utils.previews
import os
from mathutils import Vector, Matrix
from bpy.props import *
from bpy.types import (Panel,Menu,Operator,PropertyGroup,)
# -- BY-GEN Classes
'''
Remember, (from . ) means 'look in this directory', then you can
specify the folder name and continue down scope with another '.'
'''
from . ui.panels import (
    OBJECT_PT_ByGenGenerate, 
    OBJECT_PT_ByGenModify, 
    OBJECT_PT_ByGenTools,
    OBJECT_PT_ByGenInfo, 
    OBJECT_PT_ByGenStructuredGeneration,
    BYGEN_PT_Scene_Properties,
    BYGEN_PT_Generation_Algorithms,
    BYGEN_PT_Scattering_Algorithms,
    OBJECT_PT_BYGEN_Scattering
    )

from . ui.menus import (
    OBJECT_MT_CustomMenu, 
    BYGEN_MT_Menu,
    VIEW3D_MT_bygen_add,
    VIEW3D_MT_bygen_add_scatter,
    VIEW3D_MT_bygen_add_Templates,
    VIEW3D_MT_bygen_add_generators,
    VIEW3D_MT_bygen_hard_add,
    VIEW3D_MT_bg_organic,
    VIEW3D_MT_bygen_fx_add,
    menu_func
    )

from . operators.scatter import (
    BYGEN_OT_Scatter_City_Circular, 
    BYGEN_OT_Scatter_City_Rectangular
    )

from . operators.generate import (
    BYGEN_OT_hard_surface_solid_add,
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
    BYGEN_OT_cubic_field_generate, 
    BYGEN_OT_spherical_field_generate, 
    BYGEN_OT_meta_cloud_generate, 
    BYGEN_OT_midge_cell_add
    )

from . operators.algorithms.layered_generation import (
    BYGEN_OT_Layered_Generation
    )

from . operators.algorithms.branched_generation import (
    BYGEN_OT_Branched_Generation
    )

from . operators.modify import (
    BYGEN_OT_Modify
    )

from . operators.tools import (
    BYGEN_OT_ApplyModifiers, 
    BYGEN_OT_PurgeTextures, 
    BYGEN_OT_ClearGenerationResultCollection, 
    BYGEN_OT_BackupGenerationResultCollection
    )

from . operators.templates import (
    BYGEN_OT_Import_Template_Space_Station,
    BYGEN_OT_Import_Template_Mech,
    BYGEN_OT_Import_Template_Weapon,
    BYGEN_OT_Import_Template_City_Circular,
    BYGEN_OT_Import_Template_City_Rectangular
)

#endregion
#region Global Variables and Properties
custom_icons = None
class BGProperties(PropertyGroup):

    # Common Types: 
    # IntProperty, 
    # FloatProperty, 
    # FloatVectorProperty, 
    # StringProperty, 
    # EnumProperty

    # Miscellaneous
    secret_string: StringProperty(
        name="Super secret boy band.",
        description="I don't wanna join your super secret boy band.",
        default="Indigo Bridge"
    )

    #///////////////////////////////////////////////////////////////////
    # GENERATION PROPERTIES
    #///////////////////////////////////////////////////////////////////
    
    # Booleans
    gen_hss_allow_mirror: BoolProperty(
        name="Allow Mirror",
        description="Allow the addition of a mirror modifier",
        default = True
        )
    
    # Enumerations
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

    # Floats
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
    
    # Booleans
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

    # Enumerations
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

    # Floats
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
    
    # Strings
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
    # Booleans
    remove_pre_existing : BoolProperty(
        name = "Remove Pre-Existing",
        description = "Remove modifiers on selected object before reading input",
        default = False
    )
#endregion
#region Class Registration
classes = (
    # Properties
    BGProperties,
    # modify.py
    BYGEN_OT_Modify,
    # layered_generation.py
    BYGEN_OT_Layered_Generation,
    # branched_generation.py
    BYGEN_OT_Branched_Generation,
    # tools.py
    BYGEN_OT_ApplyModifiers,
    BYGEN_OT_PurgeTextures,
    BYGEN_OT_ClearGenerationResultCollection,
    BYGEN_OT_BackupGenerationResultCollection,
    # Panel Classes
    OBJECT_MT_CustomMenu,
    OBJECT_PT_ByGenGenerate,
    OBJECT_PT_ByGenModify,
    OBJECT_PT_ByGenStructuredGeneration,
    OBJECT_PT_BYGEN_Scattering,
    OBJECT_PT_ByGenTools,
    OBJECT_PT_ByGenInfo,
    BYGEN_PT_Scene_Properties,
    BYGEN_PT_Generation_Algorithms,
    BYGEN_PT_Scattering_Algorithms,
    # Menu Classes
    BYGEN_MT_Menu,
    VIEW3D_MT_bygen_add,
    VIEW3D_MT_bygen_add_scatter,
    VIEW3D_MT_bygen_add_Templates,
    VIEW3D_MT_bygen_add_generators,
    VIEW3D_MT_bygen_hard_add,
    VIEW3D_MT_bg_organic,
    VIEW3D_MT_bygen_fx_add,
    # scatter.py
    BYGEN_OT_Scatter_City_Circular,
    BYGEN_OT_Scatter_City_Rectangular,
    # generate.py
    BYGEN_OT_hard_surface_solid_add,
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
    # Generators
    BYGEN_OT_cubic_field_generate,
    BYGEN_OT_spherical_field_generate,
    # Generators - Modify (req input)
    BYGEN_OT_meta_cloud_generate,
    # Templates
    BYGEN_OT_Import_Template_Space_Station,
    BYGEN_OT_Import_Template_Mech,
    BYGEN_OT_Import_Template_Weapon,
    BYGEN_OT_Import_Template_City_Circular,
    BYGEN_OT_Import_Template_City_Rectangular
)
keys = []
def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    bpy.types.Scene.by_tool = PointerProperty(type=BGProperties)
    # Adding Shift+A Menu
    bpy.types.VIEW3D_MT_add.append(menu_func)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.by_tool
    # Shift+A Menu
    bpy.types.VIEW3D_MT_add.remove(menu_func)

if __name__ == "__main__":
    register()
#endregion