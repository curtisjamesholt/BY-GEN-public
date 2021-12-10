#region Information
'''
This file contains the classes for creating the tool panels that appear
alongside the 3D viewport.
'''
#endregion
#region Module Imports
import bpy
from bpy.props import *
from bpy.types import (Panel,Menu,Operator,PropertyGroup)
#endregion
#region Panel - Tool - Generate
class OBJECT_PT_ByGenGenerate(Panel):
    bl_idname = "OBJECT_PT_ByGenGenerate"
    bl_label = "BY-GEN - Generation"
    bl_space_type = "VIEW_3D"   
    bl_region_type = "UI"
    bl_category = "BY-GEN"
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        bytool = scene.by_tool
        layout.label(text="Requires mesh input")
        layout.operator("object.bygen_meta_cloud_generate")
        layout.label(text="Does not require input")
        layout.operator("object.bygen_cubic_field_generate")
        layout.operator("object.bygen_spherical_field_generate")
        layout.separator()
#endregion
#region Panel - Tool - Modify
class OBJECT_PT_ByGenModify(Panel):
    bl_idname = "OBJECT_PT_ByGenModify"
    bl_label = "BY-GEN - Modify"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BY-GEN"
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        bytool = scene.by_tool

        box = layout.box()
        box.label(text="Modifier Styles")

        col = box.column()
        colrow = col.row(align=True)
        colrow.prop(bytool, "modAllow")
        colrow = col.row(align=True)
        colrow.label(text="Modify Mode")
        colrow = col.row(align=True)
        colrow.prop(bytool, "mode_modify", text="")

        if bytool.mode_modify == "MODE_DEST":
            colrow = col.row(align=True)
            colrow.separator()
            colrow = col.row(align=True)
            colrow.label(text="Displacement Type")
            colrow = col.row(align=True)
            colrow.prop(bytool, "mode_mod_disp", text="")

        if bytool.mode_modify == "MODE_HSFRAME":
            colrow = col.row(align = True)
            colrow.prop(bytool, "mod_hssolid_allow_mirror")
            colrow = col.row(align = True)
            colrow.operator("object.bygen_invert_solidify")

        if bytool.mode_modify == "MODE_HSF":
            colrow = col.row(align=True)
            colrow.separator()
            colrow = col.row(align=True)
            colrow.label(text="Displacement Type")
            colrow = col.row(align=True)
            colrow.prop(bytool, "mode_mod_disp", text="")
            colrow = col.row(align=True)
            colrow.prop(bytool, "mod_decimate_collapse", text="Decimate Collapse")
            colrow = col.row(align=True)
            colrow.prop(bytool, "mod_decimate_angle", text="Decimate Angle")
            colrow = col.row(align=True)
            colrow.prop(bytool, "mod_hsf_allow_mirror", text="Mirror")

        if bytool.mode_modify == "MODE_HSS":
            colrow = col.row(align=True)
            colrow.separator()
            colrow = col.row(align=True)
            colrow.prop(bytool, "mod_hss_allow_mirror", text="Mirror")

        if bytool.mode_modify == "MODE_HP":
            colrow = col.row(align=True)
            colrow.separator()
            colrow = col.row(align=True)
            colrow.prop(bytool, "mod_hp_allow_triangulate", text="Triangulate")

        if bytool.mode_modify == "MODE_MSHELL":
            colrow = col.row(align=True)
            colrow.separator()
            colrow = col.row(align=True)
            colrow.prop(bytool, "mod_mshell_allow_triangulate", text = "Triangulate")

        if bytool.mode_modify == "MODE_OSHELL":
            colrow = col.row(align=True)
            colrow.separator()
            colrow = col.row(align=True)
            colrow.prop(bytool, "mod_oshell_allow_triangulate", text="Triangulate")
            colrow = col.row(align=True)
            colrow.label(text="Displacement Type")
            colrow = col.row(align=True)
            colrow.prop(bytool, "mode_mod_disp", text="")
            colrow = col.row(align=True)
            colrow.prop(bytool, "mod_decimate_angle", text="Decimate Angle")

        if bytool.mode_modify == "MODE_PC":
            colrow = col.row(align=True)
            colrow.separator()
            colrow = col.row(align=True)
            colrow.prop(bytool, "mod_pc_create_material", text="Create Emissive Mat")

        colrow = col.row(align=True)
        colrow.separator()
        colrow = col.row(align=True)
        colrow.operator("object.bygen_modify")
        colrow = col.row(align=True)
        colrow.separator()
#endregion
#region Panel - Tool - Structured Generation
class OBJECT_PT_ByGenStructuredGeneration(Panel):
    bl_idname = "OBJECT_PT_ByGenStructuredGeneration"
    bl_label = "BY-GEN - Structured Generation"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BY-GEN"

    def draw_header(self, context):
        self.layout.label(text = "", icon = "MOD_BUILD")

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        bytool = scene.by_tool
        layout.label(text="Import template content in scene properties.")
        layout.operator("object.bygen_start_layered_generation")
        layout.operator("object.bygen_start_branched_generation")
#endregion
#region Panel - Tool - Scattering
class OBJECT_PT_BYGEN_Scattering(Panel):
    bl_idname = "OBJECT_PT_BYGEN_Scattering"
    bl_label = "BY-GEN - Scattering"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BY-GEN"

    def draw_header(self, context):
        self.layout.label(text = "", icon = "OUTLINER_OB_POINTCLOUD")

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        bytool = scene.by_tool
        layout.label(text="Import template content in scene properties.")
        layout.operator("object.bygen_scatter_city_circular")
        layout.operator("object.bygen_scatter_city_rectangular")
#endregion
#region Panel - Tool - Tools
class OBJECT_PT_ByGenTools(Panel):
    bl_idname = "OBJECT_PT_ByGenTools"
    bl_label = "BY-GEN - Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BY-GEN"

    def draw_header(self, context):
        self.layout.label(text = "", icon = "TOOL_SETTINGS")

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        bytool = scene.by_tool

        #Operations Layout
        box = layout.box()
        box.label(text="Useful Operations")
        col = box.column()
        colrow = col.row(align=True)
        colrow.operator("object.bygen_apply_modifiers")
        colrow = col.row(align=True)
        colrow.operator("object.bygen_purge_textures")
        colrow = col.row(align=True)
        colrow.operator("object.bygen_clear_generation_result")
        colrow = col.row(align=True)
        colrow.operator("object.bygen_backup_generation_result")
#endregion
#region Panel - Tool - Info
class OBJECT_PT_ByGenInfo(Panel):
    bl_idname = "OBJECT_PT_ByGenInfo"
    bl_label = "BY-GEN - Info"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BY-GEN"

    def draw_header(self, context):
        self.layout.label(text = "", icon = "INFO")

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        bytool = scene.by_tool

        #Operations Layout
        box = layout.box()
        box.label(text = "Created by Curtis Holt")


        #---------- Box - Support
        b = box.box()
        b.label(text="Support")
        column = b.column()

        row = column.row()
        row.scale_y = 1.2
        row.operator("wm.url_open", text = "Gumroad", icon='WORLD').url = "https://gumroad.com/l/BY-GEN"
        row.operator("wm.url_open", text = "Donate", icon='WORLD').url = "https://www.curtisholt.online/donate"
        #----------

        #---------- Box - Social
        b = box.box()
        b.label(text="Social")
        column = b.column()

        row = column.row()
        row.scale_y = 1.2
        row.operator("wm.url_open", text="YouTube", icon='FILE_MOVIE').url = "https://www.youtube.com/CurtisHolt"
        row.operator("wm.url_open", text="Twitter", icon='COMMUNITY').url = "https://www.twitter.com/curtisjamesholt"
        
        row = column.row()
        row.scale_y = 1.2
        row.operator("wm.url_open", text="Website", icon='WORLD').url = "https://www.curtisholt.online"
        row.operator("wm.url_open", text="Instagram", icon='COMMUNITY').url = "https://www.instagram.com/curtisjamesholt"
        #----------
#endregion
#region Panel - Scene Properties - BY-GEN
class Scene_Panel:
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_options = {"DEFAULT_CLOSED"}

class BYGEN_PT_Scene_Properties(Scene_Panel, bpy.types.Panel):
    bl_label = "BY-GEN"
    bl_idname = "BYGEN_PT_Scene_Properties"
    def draw(self, context):
        layout = self.layout
        layout.label(text="Import template content and run operations.")

class BYGEN_PT_Generation_Algorithms(Scene_Panel, bpy.types.Panel):
    bl_parent_id = "BYGEN_PT_Scene_Properties"
    bl_idname = "BYGEN_PT_Generation_Algorithms"
    bl_label = "Generation Algorithms"
    def draw(self, context):
        layout = self.layout

        #---------- Box - Branched Generation
        b = layout.box()
        b.label(text = "Branched Generation")        
        col = b.column()
        row = col.row()
        row.label(text="Call 'Branched Generation' from the 3D View toolbar or the search window.")
        row = col.row()
        row.operator("object.bygen_import_template_space_station")
        #----------

        #---------- Box - Layered Generation
        b = layout.box()
        b.label(text = "Layered Generation")        
        col = b.column()
        row = col.row()
        row.label(text="Call 'Layered Generation' from the 3D View toolbar or the search window.")
        row = col.row()
        row.label(text="Position reference objects must be active in viewport (but can be hidden).")
        row = col.row()
        row.label(text="Templates will import a config.gen file into the text editor.")
        row = col.row()
        row.operator("object.bygen_import_template_mech")
        row = col.row()
        row.operator("object.bygen_import_template_weapon")
        #----------

class BYGEN_PT_Scattering_Algorithms(Scene_Panel, bpy.types.Panel):
    bl_parent_id = "BYGEN_PT_Scene_Properties"
    bl_idname = "BYGEN_PT_Scattering_Algorithms"
    bl_label = "Scattering Algorithms"
    def draw(self, context):
        layout = self.layout

        #---------- Box - City Scattering
        b = layout.box()
        b.label(text = "City Scattering")        
        col = b.column()
        row = col.row()
        row.label(text="Call city scatter from the 3D View toolbar or the search window.")
        row = col.row()
        row.operator("object.bygen_import_city_circular")
        row = col.row()
        row.operator("object.bygen_import_city_rectangular")
        #----------
#endregion
#region Registration
classes = (
    #OBJECT_PT_ByGenGenerate,
    #OBJECT_PT_ByGenModify,
    OBJECT_PT_ByGenStructuredGeneration,
    OBJECT_PT_BYGEN_Scattering,
    OBJECT_PT_ByGenTools,
    OBJECT_PT_ByGenInfo,
    BYGEN_PT_Scene_Properties,
    BYGEN_PT_Generation_Algorithms,
    BYGEN_PT_Scattering_Algorithms
)
def register():
    # Importing register class
    from bpy.utils import register_class

    # Registering main classes:
    for cls in classes:
        register_class(cls)

def unregister():
    # Importing unregister class
    from bpy.utils import unregister_class

    # Unregistering main classes:
    for cls in reversed(classes):
        unregister_class(cls)
#endregion