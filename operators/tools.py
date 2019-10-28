import bpy
import bmesh
import random
from mathutils import Vector, Matrix
from bpy.props import *
from bpy.types import (Panel,Menu,Operator,PropertyGroup)
# //====================================================================//
#    < Operators >
# //====================================================================//
#////////// OPERATOR FOR APPLYING ALL MODIFIERS
class BYGEN_OT_ApplyModifiers(bpy.types.Operator):
    bl_idname = "object.bygen_apply_modifiers"
    bl_label = "Apply Modifiers"
    bl_description = "Applies all modifiers on the active object."
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):

        #////////// CONTEXT >
        scene = context.scene
        bytool = scene.by_tool
        if len(bpy.context.selected_objects) > 0:
            sO = bpy.context.selected_objects[0]
            for mod in sO.modifiers:
                bpy.ops.object.modifier_apply(modifier=mod.name)

        return {'FINISHED'}
#////////// OPERATOR FOR PURGING BY-GEN GENERATED TEXTURES
class BYGEN_OT_PurgeTextures(bpy.types.Operator):
    bl_idname = "object.bygen_purge_textures"
    bl_label = "Purge Textures"
    bl_description = "Removes all textures created by BY-GEN."
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):

        #////////// CONTEXT >
        scene = context.scene
        bytool = scene.by_tool

        for tex in bpy.data.textures:
            if "ByGen_TexID" in tex.name:
                bpy.data.textures.remove(tex)

        return {'FINISHED'}