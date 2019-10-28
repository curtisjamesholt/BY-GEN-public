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
bl_info = {
    "name" : "BY-GEN",
    "author" : "Curtis Holt",
    "description" : "A generative modeling toolkit by Curtis Holt.",
    "blender" : (2, 80, 1),
    "version" : (0, 0, 5),
    "location" : "View3D",
    "warning" : "",
    "category" : "Generic"
}
import bpy
import bmesh
import random
import bpy.utils.previews
import os
from mathutils import Vector, Matrix
from bpy.props import *
from bpy.types import (Panel,Menu,Operator,PropertyGroup,)

from . ui.panels import OBJECT_PT_ByGenGenerate, OBJECT_PT_ByGenModify, OBJECT_PT_ByGenTools
from . ui.menus import OBJECT_MT_CustomMenu
from . operators.generate import BYGEN_OT_Generate
from . operators.generate_calls import (BYGEN_OT_hard_surface_skin_add, BYGEN_OT_organic_skin_add, BYGEN_OT_clay_blob_add, BYGEN_OT_hard_surface_faceting_add, BYGEN_OT_template_add, 
BYGEN_OT_metal_shell_add, BYGEN_OT_hard_padding_add, BYGEN_OT_point_cloud_add, BYGEN_OT_pixelate_add, BYGEN_OT_hard_surface_skin_simple_add, BYGEN_OT_cubic_field_generate, 
BYGEN_OT_spherical_field_generate, BYGEN_OT_meta_cloud_generate, BYGEN_OT_midge_cell_add)
from . operators.modify import BYGEN_OT_Modify
from . operators.tools import BYGEN_OT_ApplyModifiers, BYGEN_OT_PurgeTextures
from . interpreter.interpreter import (BYGEN_OT_interpret_input, BYGEN_OT_interpret_output)

# //====================================================================//
#    < Global Variables >
# //====================================================================//
custom_icons = None
# //====================================================================//
#    < Properties >
# //====================================================================//
class BGProperties(PropertyGroup):

    #///////////////////////////////////////////////////////////////////
    # MISC PROPERTIES
    #///////////////////////////////////////////////////////////////////
    secret_string: StringProperty(
        name="Super secret boy band.",
        description="I don't wanna join your super secret boy band.",
        default="Indigo Bridge"
    )

    #///////////////////////////////////////////////////////////////////
    # GENERATION PROPERTIES
    #///////////////////////////////////////////////////////////////////
    #..... BOOLEANS >
    #.......... For allowing the creation of a mirror modifier for MODE_HSS.
    gen_hss_allow_mirror: BoolProperty(
        name="Allow Mirror",
        description="Allow the addition of a mirror modifier",
        default = True
        )
    
    #..... ENUMARATIONS >

    #.......... Enum for Generation Mode
    mode_generate: EnumProperty(
        name="Generation Type",
        description="The type of generation to perform",
        items=[
            ('GEN_META_CLOUD', "Meta Cloud", "")
        ],
        default="GEN_META_CLOUD"
        )
    #.......... Enum for Generation Displace Mode
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

    #.......... Float for Generation - Decimation - Collapse
    gen_decimate_collapse: FloatProperty(
        name = "Decimate Collapse",
        description = "Collapse ratio for the Decimation modifier",
        default = 0.2,
        min = 0.0,
        max = 1.0
        )
    #.......... Float for Generation - Decimation - Angle Limit
    gen_decimate_angle: FloatProperty(
        name = "Decimate Angle",
        description = "Planar angle for the Decimation modifier",
        default = 0.174533,
        min = 0.0,
        max = 1.0
        )

    #..... INTEGERS >

    

    #///////////////////////////////////////////////////////////////////
    # MODIFICATION PROPERTIES
    #///////////////////////////////////////////////////////////////////

    #..... BOOLEANS >

    #.......... For allowing the modification of objects that have pre-existing modifiers.
    modAllow: BoolProperty(
        name="Allow Old Mods",
        description="Allow modification when modifiers are present",
        default = True
        )
    #.......... For allowing the creation of a mirror modifier for MODE_HSF.
    mod_hsf_allow_mirror: BoolProperty(
        name="Allow Mirror",
        description="Allow the addition of a mirror modifier",
        default = False
        )
    #.......... For allowing the creation of a mirror modifier for MODE_HSS.
    mod_hss_allow_mirror: BoolProperty(
        name="Allow Mirror",
        description="Allow the addition of a mirror modifier",
        default = True
        )
    #.......... For allowing the creation of a triangulate modifier for MODE_MS.
    mod_mshell_allow_triangulate: BoolProperty(
        name="Triangulate",
        description="Allow the addition of a triangulate modifier",
        default = True
        )
    #.......... For allowing the creation of a triangulate modifier for MODE_OS.
    mod_oshell_allow_triangulate: BoolProperty(
        name="Triangulate",
        description="Allow the addition of a triangulate modifier",
        default = False
        )
    #.......... For allowing the creation of a triangulate modifier for MODE_HP.
    mod_hp_allow_triangulate: BoolProperty(
        name="Triangulate",
        description="Allow the addition of a triangulate modifier",
        default = False
    )
    #.......... For allowing the creation of an emissive material for MODE_PC.
    mod_pc_create_material: BoolProperty(
        name="Create Emissive Material",
        description="Allows for the creation of an emissive material",
        default=False
    )

    #..... ENUMERATIONS >

    #.......... Enum for Modify Displace Mode
    mode_mod_disp: EnumProperty(
        name="Generation Displacement Type",
        description="The displacement type for the generation",
        items=[
            ('MODE_MD_CLOUDS', "Clouds", ""),
            ('MODE_MD_DISTNOISE', "Distorted Noise", ""),
            ('MODE_MD_MARBLE', "Marble", ""),
            ('MODE_MD_MUSGRAVE', "Musgrave", ""),
            ('MODE_MD_STUCCI', "Stucci", ""),
            ('MODE_MD_VORONOI', "Voronoi", ""),
            ('MODE_MD_WOOD', "Wood", "")
        ],
        default="MODE_MD_MUSGRAVE"
    )
    #.......... Enum for Modification Mode
    mode_modify: EnumProperty(
        name="Modify Type",
        description="The type of style to apply",
        items=[
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
    
    #.......... Float for Modification - Decimation - Collapse
    mod_decimate_collapse: FloatProperty(
        name = "Decimate Collapse",
        description = "Collapse ratio for the Decimation modifier",
        default = 0.2,
        min = 0.0,
        max = 1.0
        )
    #.......... Float for Modification - Decimation - Angle Limit
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

    #Templates for Properties
    '''
    my_int: IntProperty(
        name = "Int Value",
        description="A integer property",
        default = 23,
        min = 10,
        max = 100
        )
    my_float: FloatProperty(
        name = "Float Value",
        description = "A float property",
        default = 23.7,
        min = 0.01,
        max = 30.0
        )
    my_float_vector: FloatVectorProperty(
        name = "Float Vector Value",
        description="Something",
        default=(0.0, 0.0, 0.0), 
        min= 0.0, # float
        max = 0.1
    ) 
    my_string: StringProperty(
        name="User Input",
        description=":",
        default="",
        maxlen=1024,
        )
    my_enum: EnumProperty(
        name="Dropdown:",
        description="Apply Data to attribute.",
        items=[ ('OP1', "Option 1", ""),
                ('OP2', "Option 2", ""),
                ('OP3', "Option 3", ""),
               ]
        )
    '''
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
        layout.menu("VIEW3D_MT_bygen_add_templates", text="Templates")
        layout.menu("VIEW3D_MT_bygen_add_generators", text="Generators")
        '''
        layout.menu("VIEW3D_MT_bygen_hard_add", text="Hard Surface")
        layout.menu("VIEW3D_MT_bygen_organic_add", text="Organic")
        layout.menu("VIEW3D_MT_bygen_fx_add", text="FX")
        '''

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
        #USING OTHER OPERATORS FOR PLACEHOLDERS
        layout.operator("object.bygen_cubic_field_generate", text="Cubic Field")
        layout.operator("object.bygen_spherical_field_generate", text="Spherical Field")

#Shift+A => BY-GEN => Hard Surface
class VIEW3D_MT_bygen_hard_add(Menu):
    bl_idname = "VIEW3D_MT_bygen_hard_add"
    bl_label = "Hard Surface"
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        #TEMPORARY:
        #layout.operator("object.bygen_generate", text="Generate Test", icon_value=custom_icons["custom_icon"].icon_id)
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
        #TEMPORARY
        layout.operator("object.bygen_organic_skin_add", text="Organic Skin")
        layout.operator("object.bygen_clay_blob_add", text="Clay Blob")

#Shift+A => BY-GEN => FX
class VIEW3D_MT_bygen_fx_add(Menu):
    bl_idname = "VIEW3D_MT_bygen_fx_add"
    bl_label = "FX"
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        #TEMPORARY
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
    BYGEN_OT_ApplyModifiers,
    BYGEN_OT_PurgeTextures,
    # > Basic Interface
    OBJECT_MT_CustomMenu,
    OBJECT_PT_ByGenGenerate,
    OBJECT_PT_ByGenModify,
    OBJECT_PT_ByGenTools,
    # > Menu classes
    VIEW3D_MT_bygen_add,
    VIEW3D_MT_bygen_add_Templates,
    VIEW3D_MT_bygen_add_generators,
    VIEW3D_MT_bygen_hard_add,
    VIEW3D_MT_bg_organic,
    VIEW3D_MT_bygen_fx_add,
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

    # > INTERPRETER CLASSES
    BYGEN_OT_interpret_input,
    BYGEN_OT_interpret_output
    
    #OBJECT_PT_PropTest
    #BYGEN_OT_SecretClub,
    #OBJECT_PT_ByGenTestPanel
)
#register, unregister = bpy.utils.register_classes_factory(classes)
def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    bpy.types.Scene.by_tool = PointerProperty(type=BGProperties)
    bpy.types.VIEW3D_MT_add.append(menu_func)

    #Icon Setup
    global custom_icons
    custom_icons = bpy.utils.previews.new()
    icons_dir = os.path.join(os.path.dirname(__file__), "icons")
    #script_path = bpy.context.space_data.text.filepath
    #icons_dir = os.path.join(os.path.dirname(script_path), "icons")
    custom_icons.load("custom_icon", os.path.join(icons_dir, "bygen_logo_small.png"), 'IMAGE')
    #bpy.utils.register_module(__name__)

#---------------------------------------------------------------------------
def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.by_tool
    bpy.types.VIEW3D_MT_add.remove(menu_func)

    #Icon Removal
    global custom_icons
    bpy.utils.previews.remove(custom_icons)
    #bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()