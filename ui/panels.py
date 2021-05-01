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
# Generate Panel
class OBJECT_PT_ByGenGenerate(Panel):
    bl_idname = "OBJECT_PT_ByGenGenerate"
    bl_label = "BY-GEN - Generation"
    bl_space_type = "VIEW_3D"   
    bl_region_type = "UI"
    bl_category = "BY-TOOLS"
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        bytool = scene.by_tool
        layout.operator("object.bygen_meta_cloud_generate")
        layout.separator()

# Modify Panel
class OBJECT_PT_ByGenModify(Panel):
    bl_idname = "OBJECT_PT_ByGenModify"
    bl_label = "BY-GEN - Modify"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BY-TOOLS"
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

# Structured Generation Panel
class OBJECT_PT_ByGenStructuredGeneration(Panel):
    bl_idname = "OBJECT_PT_ByGenStructuredGeneration"
    bl_label = "BY-GEN - Structured Generation"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BY-TOOLS"
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        bytool = scene.by_tool
        layout.label(text="Check documentation for instructions.")
        layout.operator("object.bygen_start_layered_generation")
        layout.operator("object.bygen_start_branched_generation")

# Tools Panel
class OBJECT_PT_ByGenTools(Panel):
    bl_idname = "OBJECT_PT_ByGenTools"
    bl_label = "BY-GEN - Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BY-TOOLS"
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

# Interpreter Panel
class OBJECT_PT_ByGenInterpreter(Panel):
    bl_idname = "OBJECT_PT_ByGenInterpreter"
    bl_label = "BY-GEN - Interpreter"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BY-TOOLS"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        bytool = scene.by_tool

        #Interpreter Layout
        box = layout.box()
        box.label(text="Text Object Interpreter")
        col = box.column()
        colrow = col.row(align=True)
        colrow.label(text="Input Text Object")
        colrow = col.row(align=True)
        colrow.prop(bytool, "input_text_source", text="")
        colrow = col.row(align=True)
        colrow.prop(bytool, "remove_pre_existing", text="Remove Old Modifiers")
        colrow = col.row(align=True)
        colrow.operator("object.bygen_interpret_input")
        colrow = col.row(align=True)
        colrow.separator()
        colrow = col.row(align=True)
        colrow.label(text="Output Text Object")
        colrow = col.row(align=True)
        colrow.prop(bytool, "output_text_source", text="")
        colrow = col.row(align=True)
        colrow.operator("object.bygen_interpret_output")
        layout.separator()

# Info Panel
class OBJECT_PT_ByGenInfo(Panel):
    bl_idname = "OBJECT_PT_ByGenInfo"
    bl_label = "BY-GEN - Info"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BY-TOOLS"

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