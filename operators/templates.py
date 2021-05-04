#region Information
'''
This file contains operators that manage the importing of template
content into the user's blend file.
'''
#endregion
#region Module Imports
import os
import bpy
import bmesh
import random
from mathutils import Vector, Matrix
from bpy.props import *
from bpy.types import (Panel,Menu,Operator,PropertyGroup)
#endregion
#region Template - Branched - Space Station
class BYGEN_OT_Import_Template_Space_Station(bpy.types.Operator):
    bl_idname = "object.bygen_import_template_space_station"
    bl_label = "Import Space Station Template"
    bl_description = "Imports the space station template for branched generation."
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        # Setting up context
        scene = context.scene
        bytool = scene.by_tool

        # Appending Space Station template into blend file
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'resources/demo_space_station.blend\\Collection\\'))
        colname = "Generator_SpaceStation"
        bpy.ops.wm.append(filename = colname, directory = path)
        return {"FINISHED"}
#endregion
#region Template - Layered - Mech
class BYGEN_OT_Import_Template_Mech(bpy.types.Operator):
    bl_idname = "object.bygen_import_template_mech"
    bl_label = "Import Mech Template"
    bl_description = "Imports the mech template for layered generation."
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        # Settings up the context
        scene = context.scene
        bytool = scene.by_tool
        # Appending Mech template into blend file
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'resources/demo_mech.blend\\Collection\\'))
        path_txt = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'resources/demo_mech.blend\\Text\\'))
        colname = "Generator_Mech"
        configname = "config.gen"
        bpy.ops.wm.append(filename = colname, directory = path)
        bpy.ops.wm.append(filename = configname, directory = path_txt)
        return {"FINISHED"}
#endregion
#region Template - Layered - Weapon
class BYGEN_OT_Import_Template_Weapon(bpy.types.Operator):
    bl_idname = "object.bygen_import_template_weapon"
    bl_label = "Import Weapon Template"
    bl_description = "Imports the weapon template for layered generation."
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        # Settings up the context
        scene = context.scene
        bytool = scene.by_tool
        # Appending Mech template into blend file
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'resources/demo_weapon.blend\\Collection\\'))
        path_txt = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'resources/demo_weapon.blend\\Text\\'))
        colname = "Generator_Weapon"
        configname = "config.gen"
        bpy.ops.wm.append(filename = colname, directory = path)
        bpy.ops.wm.append(filename = configname, directory = path_txt)
        return {"FINISHED"}
#endregion
#region Template - Scatter - City (Circular)
class BYGEN_OT_Import_Template_City_Circular(bpy.types.Operator):
    bl_idname = "object.bygen_import_city_circular"
    bl_label = "Import City (Circular)"
    bl_description = "Imports collections for city scattering (circular)."
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        # Settings up the context
        scene = context.scene
        bytool = scene.by_tool
        # Appending Mech template into blend file
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'resources/demo_city_circular.blend\\Collection\\'))
        colname = "City_Circular"
        bpy.ops.wm.append(filename = colname, directory = path)
        return {"FINISHED"}
#endregion
#region Template - Scatter - City (Rectangular)
class BYGEN_OT_Import_Template_City_Rectangular(bpy.types.Operator):
    bl_idname = "object.bygen_import_city_rectangular"
    bl_label = "Import City (Rectangular)"
    bl_description = "Imports collections for city scattering (rectangular)."
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        # Settings up the context
        scene = context.scene
        bytool = scene.by_tool
        # Appending Mech template into blend file
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'resources/demo_city_rectangular.blend\\Collection\\'))
        colname = "City_Rectangular"
        bpy.ops.wm.append(filename = colname, directory = path)
        return {"FINISHED"}
#endregion