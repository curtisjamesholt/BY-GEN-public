#region Information
#endregion
#region Module Imports
import bpy
from .. modules.easybpy import *
import bmesh
import random
from mathutils import Vector, Matrix
from bpy.props import *
from bpy.types import (Panel,Menu,Operator,PropertyGroup)
#endregion
#region Operators
# Operator for applying all modifiers
class BYGEN_OT_ApplyModifiers(bpy.types.Operator):
    bl_idname = "object.bygen_apply_modifiers"
    bl_label = "Apply Modifiers"
    bl_description = "Applies all modifiers on the active object."
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        # Setting up context
        scene = context.scene
        bytool = scene.by_tool
        if len(bpy.context.selected_objects) > 0:
            sO = bpy.context.selected_objects[0]
            for mod in sO.modifiers:
                bpy.ops.object.modifier_apply(modifier=mod.name)

        return {'FINISHED'}

# Operator for purging BY-GEN generated textures
class BYGEN_OT_PurgeTextures(bpy.types.Operator):
    bl_idname = "object.bygen_purge_textures"
    bl_label = "Purge Textures"
    bl_description = "Removes all textures created by BY-GEN."
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        # Setting up context
        scene = context.scene
        bytool = scene.by_tool

        for tex in bpy.data.textures:
            if "ByGen_TexID" in tex.name:
                bpy.data.textures.remove(tex)

        return {'FINISHED'}

# Operator for clearing the generation result collection
class BYGEN_OT_ClearGenerationResultCollection(bpy.types.Operator):
    bl_idname = "object.bygen_clear_generation_result"
    bl_label = "Clear Generation Result"
    bl_description = "Cleares the Generation Result collection if it exists"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        # Setting up context
        scene = context.scene
        bytool = scene.by_tool

        # Deselect selected objects
        deselect_all_objects()

        generation_result = None
        if 'Generation Result' in bpy.data.collections:
            generation_result = bpy.data.collections['Generation Result']
        if generation_result != None:
            if len(generation_result.objects) > 0:
                for childObject in generation_result.objects:
                    childObject.select_set(True)
                bpy.ops.object.delete()

        return {'FINISHED'}

# Operator for making a copy of the generation result collection
class BYGEN_OT_BackupGenerationResultCollection(bpy.types.Operator):
    bl_idname = "object.bygen_backup_generation_result"
    bl_label = "Backup Generation Result"
    bl_description = "Moves the contents of the Generation Result collection into a new collection"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        # Setting up context
        scene = context.scene
        bytool = scene.by_tool
        randID = random.randint(1,9999)

        newcolname = "Generation_Output_"+str(randID)
        newcol = bpy.data.collections.new(newcolname)
        bpy.context.scene.collection.children.link(newcol)
        generation_result = bpy.data.collections["Generation Result"]
        for childObject in generation_result.objects:
            generation_result.objects.unlink(childObject)
            newcol.objects.link(childObject)

        return {'FINISHED'}
#endregion