import bpy
from bpy.props import *
from bpy.types import (Panel,Menu,Operator,PropertyGroup)
# //====================================================================//
#    < Panels >
# //====================================================================//
class OBJECT_PT_ByGenGenerate(Panel):
    bl_idname = "object.custom_panel"
    bl_label = "BY-GEN - Generation"
    bl_space_type = "VIEW_3D"   
    bl_region_type = "UI"
    bl_category = "BY-TOOLS"
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        bytool = scene.by_tool

        '''
        layout.prop(bytool, "mode_generate", text="Generation Mode")
        '''
        '''
        if bytool.mode_generate == "MODE_HSF":
            layout.prop(bytool, "mode_gen_disp", text="Displacement Type")
            layout.prop(bytool, "gen_decimate_collapse", text="Decimate Collapse")
            layout.prop(bytool, "gen_decimate_angle", text="Decimate Angle")

        if bytool.mode_generate == "MODE_HSS":
            layout.prop(bytool, "gen_hss_allow_mirror", text="Allow Mirror")
        '''
        layout.operator("object.bygen_meta_cloud_generate")
        #layout.menu(OBJECT_MT_CustomMenu.bl_idname, text="Presets", icon="SCENE")
        layout.separator()

class OBJECT_PT_ByGenModify(Panel):
    bl_idname = "object.bygenmodify"
    bl_label = "BY-GEN - Modify"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BY-TOOLS"
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        bytool = scene.by_tool

        layout.prop(bytool, "modAllow")
        layout.prop(bytool, "mode_modify", text="Modify Mode")

        if bytool.mode_modify == "MODE_HSF":
            layout.prop(bytool, "mode_mod_disp", text="Displacement Type")
            layout.prop(bytool, "mod_decimate_collapse", text="Decimate Collapse")
            layout.prop(bytool, "mod_decimate_angle", text="Decimate Angle")
            layout.prop(bytool, "mod_hsf_allow_mirror", text="Mirror")

        if bytool.mode_modify == "MODE_HSS":
            layout.prop(bytool, "mod_hss_allow_mirror", text="Mirror")

        if bytool.mode_modify == "MODE_HP":
            layout.prop(bytool, "mod_hp_allow_triangulate", text="Triangulate")

        if bytool.mode_modify == "MODE_MSHELL":
            layout.prop(bytool, "mod_mshell_allow_triangulate", text = "Triangulate")

        if bytool.mode_modify == "MODE_OSHELL":
            layout.prop(bytool, "mod_oshell_allow_triangulate", text="Triangulate")
            layout.prop(bytool, "mode_mod_disp", text="Displacement Type")
            layout.prop(bytool, "mod_decimate_angle", text="Decimate Angle")

        if bytool.mode_modify == "MODE_PC":
            layout.prop(bytool, "mod_pc_create_material", text="Create Emissive Mat")

        layout.separator()
        layout.operator("object.bygen_modify")
        #layout.menu(OBJECT_MT_CustomMenu.bl_idname, text="Presets", icon="SCENE")
        layout.separator()
class OBJECT_PT_ByGenTools(Panel):
    bl_idname = "object.bygentools"
    bl_label = "BY-GEN - Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BY-TOOLS"
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        bytool = scene.by_tool

        box = layout.box()
        box.label(text="Operations")
        col = box.column()
        colrow = col.row(align=True)
        colrow.operator("object.bygen_apply_modifiers")
        colrow = col.row(align=True)
        colrow.operator("object.bygen_purge_textures")

        box = layout.box()
        box.label(text="Interpreter")
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

        #layout.prop(bytool, "my_int")
        #layout.prop(bytool, "my_float")
        #layout.prop(bytool, "my_float_vector", text="")
        #layout.prop(bytool, "my_string")
        
        #layout.operator("object.bygen_apply_modifiers")
        #layout.operator("object.bygen_purge_textures")
        
        #layout.operator("object.bygen_secret_club")
        #layout.menu(OBJECT_MT_CustomMenu.bl_idname, text="Presets", icon="SCENE")
        layout.separator()

'''
class OBJECT_PT_PropTest(Panel):
    bl_idname = "panel.panel4"
    bl_label = "Panel4"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "mesh"
 
    def draw(self, context):
        self.layout.operator("object.bygen_apply_modifiers", icon='MESH_CUBE', text="Add Cube 4")
'''