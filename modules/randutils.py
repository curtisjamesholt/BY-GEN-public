#region Information
'''
This module contains useful functions for building random selection
operations.
'''
#endregion
#region Module Imports
import bpy
import random
#endregion
#region Functions
# Return a single value from a provided list
def choose_from_list(choices):
    return choices[random.randint(0,len(choices)-1)]

# Return a list containing a single value from each list
def choose_from_each_list(choices_list):
    return_list = []
    for l in choices_list:
        return_list.append(l[random.randint(0,len(l)-1)])
    return return_list

# Returns a reference to an object in the given collection
def choose_object_from_collection(collection_name):
    rand_index = random.randint(0,len(bpy.data.collections[collection_name]))
    return bpy.data.collections[collection_name].objects[rand_index]

# Returns a random material from the total list of materials 
def choose_random_material():
    rand_index = random.randint(0,len(bpy.data.materials))
    return bpy.data.materials[rand_index]
#endregion