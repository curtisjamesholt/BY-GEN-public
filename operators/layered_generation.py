#region Information
#endregion
#region Module Imports
import bpy
import bmesh
import random
import json
from mathutils import Vector, Matrix
from bpy.props import *
from bpy.types import (Panel,Menu,Operator,PropertyGroup)
#endregion
#region Operators
class BYGEN_OT_Layered_Generation(bpy.types.Operator):
    bl_label = "Layered Generation"
    bl_idname = "object.bygen_start_layered_generation"
    bl_description = "Begins the layered generation procedure"
    bl_options = {'REGISTER', 'UNDO'}

    # Operator Properties:
    enable_generation : BoolProperty(
        name = "Enable Generation",
        description = "A lock to prevent generation until settings are prepared",
        default = False
    )
    seed_value : IntProperty(
        name = "Seed",
        description = "Seed for randomisation",
        default = 1,
        min = 1,
        max = 1000000
    )
    config_file : StringProperty(
        name = "Config Text Object",
        description = "The configuration text object",
        default = "config.gen"
    )

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        bytool = scene.by_tool

        # Box - Main Control
        box = layout.box()
        box.label(text="Main Control")
        col = box.column()
        colrow = col.row(align=True)
        colrow.prop(self, "enable_generation", expand = True, text="Enable Generation")

        # Box - Settings
        box_settings = layout.box()
        box_settings.label(text="Settings")
        col = box_settings.column()
        colrow = col.row(align=True)
        # Seed value
        colrow.label(text="Seed Value:")
        colrow = col.row(align=True)
        colrow.prop(self, "seed_value", expand=True, text="")
        colrow = col.row(align=True)
        # Config text object
        colrow.label(text="Config Text Object:")
        colrow = col.row(align=True)
        colrow.prop(self, "config_file", expand=True, text="")
        colrow = col.row(align=True)

    def execute(self, context):
        # Context Setup
        scene = context.scene
        sO = bpy.context.active_object

        # Boolean Lock
        if self.enable_generation:
            # Preparing Random Seed
            random.seed(self.seed_value)
            
            # Get world origin
            world_origin = None
            if 'WorldOrigin' not in bpy.data.objects:
                mesh = bpy.data.meshes.new("WorldOrigin")
                obj = bpy.data.objects.new(mesh.name, mesh)
                control_col = None
                if "BY-GEN Control Objects" in bpy.data.collections:
                    control_col = bpy.data.collections["BY-GEN Control Objects"]
                    control_col.objects.link(obj)
                else:
                    bpy.data.collections.new("BY-GEN Control Objects")
                    control_col = bpy.data.collections["BY-GEN Control Objects"]
                    bpy.context.scene.collection.children.link(control_col)
                    control_col.objects.link(obj)
                world_origin = bpy.data.objects['WorldOrigin']
            else:
                world_origin = bpy.data.objects['WorldOrigin']
            
            # Load in JSON config data from config.gen
            configInput = ""
            generatorList = []
            
            # Check config file exists:
            if self.config_file in bpy.data.texts:
                # Read through the config file:
                for line in bpy.data.texts[self.config_file].lines:
                    configInput = configInput + line.body
                try:
                    config = json.loads(configInput)
                    for element in config["generators"]:
                        generatorList.append(element)
                        
                except (ValueError, KeyError, TypeError):
                    print("Error parsing JSON config data.")
                
                # Initial reading from the config file
                defaultRequired = False
                # Generator Output Overrides
                collectionList = {}
                for generator in generatorList:
                    # Look for output override
                    if generator in config:
                        # If it exists, store it in collectionList
                        if "output" in config[generator]:
                            collectionList[generator] = config[generator]["output"]
                        else:
                            defaultRequired = True
                    else:
                        defaultRequired = True
                # Clearing override collections and creating if they do not exist:
                for collection in collectionList:
                    if collectionList[collection] in bpy.data.collections:
                        tempcol = bpy.data.collections[collectionList[collection]]
                        if len(tempcol.objects)>0:
                            if len(bpy.context.selected_objects)>0:
                                for so in bpy.context.selected_objects:
                                    so.select_set(False)
                            for oldObj in tempcol.objects:
                                oldObj.select_set(True)
                            bpy.ops.object.delete()
                    else:
                        bpy.data.collections.new(collectionList[collection])
                        tempcol = bpy.data.collections[collectionList[collection]]
                        bpy.context.scene.collection.children.link(tempcol)

                # Get Generation Result Reference:
                generation_result = None
                if defaultRequired:
                    if "Generation Result" in bpy.data.collections:
                        generation_result = bpy.data.collections["Generation Result"]
                        if len(generation_result.objects)>0:
                            if len(bpy.context.selected_objects)>0:
                                for so in bpy.context.selected_objects:
                                    so.select_set(False)
                            for oldObj in generation_result.objects:
                                oldObj.select_set(True)
                            bpy.ops.object.delete()
                    else:
                        bpy.data.collections.new("Generation Result")
                        generation_result = bpy.data.collections["Generation Result"]
                        bpy.context.scene.collection.children.link(generation_result)

                # Prepare Generation
                delim = "_"
                posDict = {}
                refCopies = []
                
                # Begin Generation
                for generator in generatorList:
                    # Set generation_result to the correct collection:
                    if generator in collectionList:
                        generation_result = bpy.data.collections[collectionList[generator]]
                    # Reset the posDict Dictionary
                    posDict = {}
                    refCopies = []
                    if generator in bpy.data.collections:
                        # Get proper generator collection reference:
                        colref = bpy.data.collections[generator]
                        # Cycle children of colref and search
                        for childcol in colref.children:
                            search(childcol, posDict, generation_result, config, world_origin, refCopies)
                    
                    # Delete overflow in refCopies
                    for ob in bpy.context.selected_objects:
                        ob.select_set(False)
                    if len(refCopies) > 0:
                        for ref in refCopies:
                            ref.select_set(True)
                        bpy.ops.object.delete()
                
                # After the entire generation procedure.
                posDict = {}
        
        return {'FINISHED'}    
    
def search(generator, posDict, generation_result, config, world_origin, refCopies):
    
    # Get list
    object_names = []
    for obj_ref in generator.objects:
        if 'pos' not in obj_ref.name:
            object_names.append(obj_ref.name)
            
    # Create object
    if len(object_names) > 0:
        randID = random.randint(0,len(object_names)-1)
        new_obj = generator.objects[object_names[randID]]
        # Create the object:
        newObject = new_obj.copy()
        newObject.data = new_obj.data.copy()
        newObject.animation_data_clear()
        
        # Create copies of pos_ref objects and add to a list
        new_posrefs = []
        for obj_ref in generator.objects:
            if 'pos' in obj_ref.name:
                if obj_ref in new_obj.children:
                    # Found posrefs, create new ones
                    posrefcopy = obj_ref.copy()
                    # posrefcopy.data = obj_ref.data.copy()
                    posrefcopy.animation_data_clear()
                    # Make child of newObject
                    posrefcopy.parent = newObject
                    posrefcopy.matrix_parent_inverse = newObject.matrix_world.inverted()
                    # Link to GenerationResult
                    generation_result.objects.link(posrefcopy)
                    # Add new posrefcopy to new_posrefs list
                    new_posrefs.append(posrefcopy)
                    
        if len(new_posrefs) > 0:
            refCopies.extend(new_posrefs)
            
        # Link New Object to Generation Result:
        generation_result.objects.link(newObject)
        
        # Change Visibility of New Object:
        newObject.hide_viewport = False
        newObject.hide_render = False
        
        # Read old pos refs from dictionary:
        if generator.name in posDict:
            temp = posDict[generator.name].matrix_world.translation
            newObject.location = temp
            
            if generator.name in config:
                if "allow_rotation" in config[generator.name]:
                    if config[generator.name]["allow_rotation"] == True:
                        newObject.rotation_euler = posDict[generator.name].rotation_euler
                        
            bpy.context.view_layer.update()
            
        # Add any pos ref copies to posDict since movement has been made to the main object
        if len(new_posrefs) > 0:
            for pos_check in new_posrefs:
                if "pos_" in pos_check.name:
                    param, value = pos_check.name.split("_", 1)
                    final, extend = value.split(".",1)
                    posDict[final] = pos_check
                    
        # Check for Behaviour overrides in config.gen for this generator:
        if generator.name in config:
            mod_mirror = None
            if "mirror_x" in config[generator.name]:
                if mod_mirror == None:
                    mod_mirror = newObject.modifiers.new("Mirror", 'MIRROR')
                    mod_mirror.mirror_object = world_origin
                mod_mirror.use_axis[0] = config[generator.name]["mirror_x"]
            if "mirror_y" in config[generator.name]:
                if mod_mirror == None:
                    mod_mirror = newObject.modifiers.new("Mirror", 'MIRROR')
                    mod_mirror.mirror_object = world_origin
                mod_mirror.use_axis[1] = config[generator.name]["mirror_y"]
            if "mirror_z" in config[generator.name]:
                if mod_mirror == None:
                    mod_mirror = newObject.modifiers.new("Mirror", 'MIRROR')
                    mod_mirror.mirror_object = world_origin
                mod_mirror.use_axis[2] = config[generator.name]["mirror_z"]
                
        # Check for child collections and re-initiate search:
        for child in generator.children:
            search(child, posDict, generation_result)
#endregion