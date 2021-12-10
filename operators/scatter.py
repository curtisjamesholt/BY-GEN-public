#region Information
#endregion
#region Module Imports
import bpy
import bmesh
import random
from mathutils import Vector, Matrix
from math import sqrt
from bpy.props import *
from bpy.types import (Panel,Menu,Operator,PropertyGroup)
from .. modules.spatial import measure
#endregion
#region Operators
class BYGEN_OT_Scatter_City_Circular(bpy.types.Operator):
    bl_idname = "object.bygen_scatter_city_circular"
    bl_label = "City Scatter - Circular"
    bl_description = "Scatters objects like a city"
    bl_options = {'REGISTER', 'UNDO'}
    
    # Operator Properties
    seed_value : IntProperty(
        name = "Seed",
        description = "Seed for randomisation",
        default = 1,
        min = 1,
        max = 1000000
    )
    rad : FloatProperty(
        name = "Radius",
        description = "Radius of the city scattering",
        default = 20.0,
        min = 1.0,
        max = 100000        
    )
    maxb : IntProperty(
        name = "Max Buildings",
        description = "Maximum number of building objects",
        default = 200,
        min = 1,
        max = 100000
    )
    collection_large : StringProperty(
        name = "Collection Large",
        description = "The collection to choose an object from",
        default = "Buildings_Large"
    )
    rad_large : FloatProperty(
        name = "Large Radius",
        description = "Boundary for large objects",
        default = 4.0,
        min = 0.0,
        max = 100000
    )
    collection_medium : StringProperty(
        name = "Collection - Medium",
        description = "Medium sized objects to choose from",
        default = "Buildings_Medium"
    )
    rad_medium : FloatProperty(
        name = "Medium Radius",
        description = "Boundary for medium objects",
        default = 13,
        min = 0.0,
        max = 100000
    )
    collection_small : StringProperty(
        name = "Collection - Small",
        description = "Small sized objects to choose from",
        default = "Buildings_Small"
    )
    rad_small : FloatProperty(
        name = "Small Radius",
        description = "Boundary for small objects",
        default = 15.0,
        min = 0.0,
        max = 100000
    )
    rotation_variation : BoolProperty(
        name = "Rotation Variation",
        description = "Allow variation in the rotation of objects",
        default = True
    )
    threshold : FloatProperty(
        name = "Neighbour Threshold",
        description = "Minimum distance between neighbouring buildings",
        default = 2,
        min = 0.0,
        max = 10000
    )
    max_cycles : IntProperty(
        name = "Max Cycles",
        description = "Maximum number of loop times to prevent infinite loops",
        default = 1000,
        min = 5,
        max = 100000
    )
    
    def execute(self, context):
        # Setting up scene context
        scene = context.scene
        
        # Preparing Random Seed
        random.seed(self.seed_value)
        
        # Initializing number_of_buildings
        number_of_buildings = 0
        
        # Initializing number_of_cycles
        number_of_cycles = 0
        
        # Preparing common radians
        r90 = 1.570796
        r180 = 3.141593
        
        # Initializing the cellList
        cellList = []
        
        # Get the collection references
        # Large Objects
        objCollectionLarge = None
        if self.collection_large in bpy.data.collections:
            objCollectionLarge = bpy.data.collections[self.collection_large]
        #M edium Objects
        objCollectionMedium = None
        if self.collection_medium in bpy.data.collections:
            objCollectionMedium = bpy.data.collections[self.collection_medium]
        # Small Objects
        objCollectionSmall = None
        if self.collection_small in bpy.data.collections:
            objCollectionSmall = bpy.data.collections[self.collection_small]

        # Look for generation result collection
        resultCollection = None
        if "Generation Result" in bpy.data.collections:
            resultCollection = bpy.data.collections["Generation Result"]
            # Clear anything in generation result
            if len(resultCollection.objects)>0:
                if len(bpy.context.selected_objects)>0:
                    for so in bpy.context.selected_objects:
                        so.select_set(False)
                for oldObj in resultCollection.objects:
                    oldObj.select_set(True)
                bpy.ops.object.delete()
        else:
            bpy.data.collections.new("Generation Result")
            resultCollection = bpy.data.collections["Generation Result"]
            bpy.context.scene.collection.children.link(resultCollection)
        
        # Begin generation procedure
        # While number of generated buildings is less than max:
        while (number_of_buildings < self.maxb) and (number_of_cycles < self.max_cycles):
            # Immediatly increment number_of_cycles
            number_of_cycles+=1
            # Get random Vector on XY plane around origin:
            posx = random.uniform(-self.rad,self.rad)
            posy = random.uniform(-self.rad,self.rad)
            newpos = Vector((posx,posy,0.0))
            origin = Vector((0.0,0.0,0.0))
            
            # If new vector is within radius:
            if measure(newpos,origin) <= self.rad:
                # Good position, check existing entries
                canCreate = False
                
                # If buildings already placed:
                if len(cellList) > 0:
                    
                    # Assume distance is clear until proven wrong:
                    distanceClear = True
                    
                    # For every old building:
                    for cell in cellList:
                        # If distance between new vector and old building large enough:
                        if measure(newpos, cell) > self.threshold:
                            # Distance is clear, leave boolean true
                            pass
                        else:
                            # Distance not clear, make boolean false
                            distanceClear = False
                            
                    # Considering clear distance and changing canCreate
                    if distanceClear == True:
                        canCreate = True
                    if distanceClear == False:
                        canCreate = False
                        
                else:
                    # Nothing in cell list, allow first object:
                    canCreate = True
                
                # If we are allowed to create object:    
                if canCreate:
                    # Create Object here
                    # Deciding which collection to take an object from:
                    vecdist = measure(newpos, origin)
                    objtype = 0
                    objCollection = objCollectionLarge
                    if vecdist < self.rad_large:
                        objCollection = objCollectionLarge
                    if vecdist > self.rad_large and vecdist < self.rad_medium:
                        objCollection = objCollectionMedium
                    if vecdist > self.rad_medium:# and vecdist < self.rad_small:
                        objCollection = objCollectionSmall
                    
                    # Prep and future prefix check:
                    object_names = []
                    if objCollection is not None:
                        for obj_ref in objCollection.objects:
                            if 'prefix' not in obj_ref.name:
                                object_names.append(obj_ref.name)
                        
                        # If the number of objects in collection is more than 0:
                        if len(object_names) > 0:
                            
                            # Selecting the original object to duplicate:
                            randID = random.randint(0,len(object_names)-1)
                            
                            # Creating the new object:
                            new_obj = objCollection.objects[object_names[randID]]
                            new_object = bpy.data.objects.new(name=new_obj.name, object_data=new_obj.data)
                            
                            # Linking new object to result collection:
                            resultCollection.objects.link(new_object)
                            
                            # Checking viewport and render visibility:
                            new_object.hide_viewport = False
                            new_object.hide_render = False
                            
                            # Moving the new object to good vector:
                            new_object.location = newpos
                            
                            # Rotating the new object:
                            if self.rotation_variation:
                                rotObj = random.randint(0,2)
                                if rotObj == 1:
                                    rotChoice = random.randint(0,3)
                                    if rotChoice == 0:
                                        # 90+
                                        old_euler = new_object.rotation_euler
                                        old_euler[2] += r90
                                        new_object.rotation_euler = old_euler
                                    if rotChoice == 1:
                                        # 90-
                                        old_euler = new_object.rotation_euler
                                        old_euler[2] -= r90
                                        new_object.rotation_euler = old_euler
                                    if rotChoice == 2:
                                        # 180
                                        old_euler = new_object.rotation_euler
                                        old_euler[2] += r180
                                        new_object.rotation_euler = old_euler
                        # Add new Vector to cellList
                        cellList.append(newpos)
                        # Add to the number_of_buildings value:
                        number_of_buildings+=1
                        # Completed building creation
                
            else:
                # Not a good position, re-roll cycle
                pass
        
        return {'FINISHED'}

# Rectangular City Scatter Method:
class BYGEN_OT_Scatter_City_Rectangular(bpy.types.Operator):
    bl_idname = "object.bygen_scatter_city_rectangular"
    bl_label = "City Scatter - Rectangular"
    bl_description = "Scatters objects like a city"
    bl_options = {'REGISTER', 'UNDO'}

    # Operator Properties:
    seed_value : IntProperty(
        name = "Seed",
        description = "Seed for randomisation",
        default = 1,
        min = 1,
        max = 1000000
    )
    collection_name : StringProperty(
        name = "Collection Name",
        description = "The collection to choose an object from",
        default = "Buildings"
    )
    random_placement : BoolProperty(
        name = "Random Placement",
        description = "Randomize whether a building will be placed",
        default = False
    )
    rotation_variation : BoolProperty(
        name = "Rotation Variation",
        description = "Allow variation in the rotation of objects",
        default = True
    )
    city_offset : FloatProperty(
        name = "City Offset",
        description = "Position offset for the origin of the city",
        default = 10
    )
    x_size : IntProperty(
        name = "X-Size",
        description = "Size of grid X axis",
        default = 10,
        min = 1,
        max = 1000000
    )
    y_size : IntProperty(
        name = "Y-Size",
        description = "Size of grid Y axis",
        default = 10,
        min = 1,
        max = 1000000
    )
    cell_size : IntProperty(
        name = "Cell Size",
        description = "Size of a grid cell",
        default = 2,
        min = 1,
        max = 1000000
    )

    def execute(self, context):
        
        # Setting up context
        scene = context.scene

        # Preparing Random Seed
        random.seed(self.seed_value)

        # Pseudo procedure:
        # 1 - Get 2D cell grid
        cellList = []
        x_count = self.x_size
        y_count = self.y_size

        # Preparing radian vars for angle rotations
        r90 = 1.570796
        r180 = 3.141593

        # Get the collection reference
        objCollection = None
        if self.collection_name in bpy.data.collections:
            objCollection = bpy.data.collections[self.collection_name]

        resultCollection = None
        if "Generation Result" in bpy.data.collections:
            resultCollection = bpy.data.collections["Generation Result"]
            # Clear anything in generation result
            if len(resultCollection.objects)>0:
                if len(bpy.context.selected_objects)>0:
                    for so in bpy.context.selected_objects:
                        so.select_set(False)
                for oldObj in resultCollection.objects:
                    oldObj.select_set(True)
                bpy.ops.object.delete()
        else:
            bpy.data.collections.new("Generation Result")
            resultCollection = bpy.data.collections["Generation Result"]
            bpy.context.scene.collection.children.link(resultCollection)
        
        # Loop variables
        column_index = 0
        curX = (0-self.cell_size) - self.city_offset 
        curY = (0-self.cell_size)
        currentCell = Vector((0,0,0))
        # Look through X axis (columns)
        while column_index < x_count:
            # Assessing columns
            curX += self.cell_size
            currentCell[1] = 0 - self.city_offset
            row_index = 0
            # Look through Y axis (rows)
            while row_index < y_count:
                # Assessing rows
                newCell = Vector((curX, currentCell[1]+self.cell_size, 0))
                currentCell = newCell
                storeCell = random.randint(0,1)
                if self.random_placement:
                    if storeCell == 1:
                        cellList.append(Vector((currentCell[0],currentCell[1],currentCell[2])))
                else:
                    cellList.append(Vector((currentCell[0],currentCell[1],currentCell[2])))
                row_index += 1
            column_index+=1
        # Begin creating objects for each cell:
        if objCollection != None:
            for element in cellList:
                object_names = []
                for obj_ref in objCollection.objects:
                    if 'prefix' not in obj_ref.name:
                        object_names.append(obj_ref.name)
                if len(object_names) > 0:
                    # Selecting the original object to duplicate:
                    randID = random.randint(0,len(object_names)-1)
                    # Creating the new object:
                    new_obj = objCollection.objects[object_names[randID]]
                    new_object = bpy.data.objects.new(name=new_obj.name, object_data=new_obj.data)
                    # Linking new object to result collection:
                    resultCollection.objects.link(new_object)
                    # Checking viewport and render visibility:
                    new_object.hide_viewport = False
                    new_object.hide_render = False
                    # Moving the new object:
                    new_object.location = element
                    # Rotating the new object:
                    if self.rotation_variation:
                        rotObj = random.randint(0,2)
                        if rotObj == 1:
                            rotChoice = random.randint(0,3)
                            if rotChoice == 0:
                                # 90+
                                old_euler = new_object.rotation_euler
                                old_euler[2] += r90
                                new_object.rotation_euler = old_euler
                            if rotChoice == 1:
                                # 90-
                                old_euler = new_object.rotation_euler
                                old_euler[2] -= r90
                                new_object.rotation_euler = old_euler
                            if rotChoice == 2:
                                # 180
                                old_euler = new_object.rotation_euler
                                old_euler[2] += r180
                                new_object.rotation_euler = old_euler

        cellList = []
        return {'FINISHED'}
#endregion
#region Registration
classes = (
    BYGEN_OT_Scatter_City_Circular,
    BYGEN_OT_Scatter_City_Rectangular
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