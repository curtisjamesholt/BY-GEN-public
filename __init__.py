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
    "blender" : (3, 0, 0),
    "version" : (9,1,1),
    "location" : "View3D",
    "warning" : "",
    "category" : "Generic"
}
#endregion
#region Module and Class Imports
# -- Core Modules
import bpy
import bmesh
import random
import bpy.utils.previews
import os
from mathutils import Vector, Matrix
from bpy.props import *
from bpy.types import (Panel,Menu,Operator,PropertyGroup,)

# -- BY-GEN Modules
from . import effects

from . ui import panels

from . ui import menus

from . operators import scatter

from . operators import generate

from . operators.algorithms import layered_generation

from . operators.algorithms import branched_generation

from . operators import modify

from . operators import tools

from . operators import templates
#endregion
#region Global Variables and Properties
custom_icons = None
class BGProperties(PropertyGroup):
    # Miscellaneous
    secret_string: StringProperty(
        name="Super secret boy band.",
        description="I don't wanna join your super secret boy band.",
        default="Indigo Bridge"
    )
#region Generation Properties
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
#endregion
#region Modification Properties
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
    mod_hssolid_allow_mirror : BoolProperty(
        name = "Allow Mirror",
        description = "Allow the addition of a mirror modifier",
        default = True
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
            ('MODE_HSFRAME', "Hard Surface Frame", ""),
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
#endregion
#region Interpreter Properties
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
#region Surface Effect Properties
# Booleans
    se_unique_collection: BoolProperty(
        name="Make Collection Unique",
        description="Make the imported collection unique",
        default = False
        )
#endregion
#region Mesh Effect Properties
# Booleans
    mp_unique_collection: BoolProperty(
        name="Make Collection Unique",
        description="Make the imported collection unique",
        default = False
        )
    ms_unique_collection: BoolProperty(
        name="Make Collection Unique",
        description="Make the imported collection unique",
        default = False
        )
#endregion
#region Volume Effects Properties
    ve_unique_collection: BoolProperty(
        name="Make Collection Unique",
        description="Make the imported collection unique",
        default = False
        )
#endregion
#endregion
#region Class Registration
classes = (
    # Properties
    BGProperties,
)
keys = []
def register():
    # Importing register class
    from bpy.utils import register_class

    # Registering main classes (external):
    effects.register() # surface_effects.py
    modify.register() # operators / modify.py
    tools.register() # operators / tools.py
    menus.register() # ui / menus.py
    panels.register() # ui / panels.py
    generate.register() # operators / generate.py
    scatter.register() # operators / scatter.py
    templates.register() # operators / templates.py
    layered_generation.register() # operators / algorithms / layered_generation.py
    branched_generation.register() # operators / algorithms / branched_generation.py

    # Registering main classes:
    for cls in classes:
        register_class(cls)

    # Creating pointer to property collection:
    bpy.types.Scene.by_tool = PointerProperty(type=BGProperties)

def unregister():
    # Importing unregister class
    from bpy.utils import unregister_class

    # Unregistering main classes:
    for cls in reversed(classes):
        unregister_class(cls)

    # Unregistering main classes (external):
    branched_generation.unregister() # operators / algorithms / branched_generation.py
    layered_generation.unregister() # operators / algorithms / layered_generation.py
    templates.unregister() # operators / templates.py
    scatter.unregister() # operators / scatter.py
    generate.unregister() # operators / generate.py
    panels.unregister() # ui / panels.py
    menus.unregister() # ui / menus.py
    tools.unregister() # operators / tools.py
    modify.unregister() # operators / modify.py
    effects.unregister() # surface_effects.py

    # Deleting pointer to property collection:
    del bpy.types.Scene.by_tool

if __name__ == "__main__":
    register()
#endregion