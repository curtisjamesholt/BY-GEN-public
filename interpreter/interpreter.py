#region Information
'''
This file contains code relating to the modifier stack interpreter.
There will likely be a series of issues with this code as various
aspects of the API and data structure of blend files are updated
over time.
'''
#endregion
#region Module Imports
import bpy
import bmesh
import random
from math import radians
from mathutils import Vector, Matrix
from bpy.props import *
from bpy.types import (Panel,Menu,Operator,PropertyGroup)
#endregion
#region Operators
# Operations for the Interpreter
class BYGEN_OT_interpret_input(bpy.types.Operator):
    bl_idname = "object.bygen_interpret_input"
    bl_label = "Apply Style from Text"
    bl_description = "Reads from a modifier data sheet and applies data to the selected object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Setting up the context
        scene = context.scene
        bytool = scene.by_tool

        # Beginning the interpreter procedure
        # Setting up variables before the interpretation procedure
        sO = bpy.context.active_object
        current_mod, current_mod_type = None, None
        current_tex, current_tex_type = None, None
        
        # Remove pre-existing modifiers if remove_pre_existing is true
        if bytool.remove_pre_existing:
            for mod in sO.modifiers:
                sO.modifiers.remove(mod)

        # Beginning the interpretation loop
        for line in bpy.data.texts[bytool.input_text_source].lines:
            
            # Delimiting the line by colon
            result = line.body.split(':')

            # result[0] is type
            # result[1] is value or mod/tex name
            # result[2] is mod/tex type

            # Creating Modifier - Set as current
            if result[0] == 'mod':
                current_mod = sO.modifiers.new(result[1], result[2])
                current_mod_type = result[2]

            # Creating Texture - Set as current
            if result[0] == 'tex':
                current_tex = bpy.data.textures.new(result[1], result[2])
                current_tex_type = result[2]
                if current_mod_type == "DISPLACE" or current_mod_type == "WARP" or current_mod_type == "WAVE":
                    current_mod.texture = current_tex
            
            # Assigning texture values to the current texture
            if result[0] == 'texvar':
                if result[2]!=None:
                    if "." not in result[1] and "(" not in result[1]:
                        execRegular = True
                        if result[2].isalpha() or "_" in result[2]:
                            if result[2]!='True' and result[2]!='False':
                                execRegular=False
                                to_exec = "current_tex."+result[1]+"='"+result[2]+"'"
                                exec(to_exec)
                        if execRegular == True:
                            to_exec = "current_tex."+result[1]+"="+result[2]
                            exec(to_exec)   

            # Assigning modifier values to the current modifier.
            if result[0] == 'modvar':
                if result[2] != None:
                    if "." not in result[1] and "(" not in result[1]:
                        execRegular = True
                        if result[2].isalpha() or "_" in result[2]:
                            if result[2]!='True' and result[2]!='False':
                                execRegular=False
                                to_exec = "current_mod."+result[1]+"='"+result[2]+"'"
                                exec(to_exec)
                        if execRegular == True:
                            to_exec = "current_mod."+result[1]+"="+result[2]
                            exec(to_exec)

        return {'FINISHED'}

class BYGEN_OT_interpret_output(bpy.types.Operator):
    bl_idname = "object.bygen_interpret_output"
    bl_label = "Generate Output Text"
    bl_description = "Creates a modifier output sheet from the selected object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Setting up the context
        scene = context.scene
        bytool = scene.by_tool

        # Begin output proe
        sO = bpy.context.active_object
        output_file = bpy.data.texts.new(bytool.output_text_source)
        output_file.write("#-- Generated using BY-GEN by Curtis Holt --#\n")
        x = None
        for mod in sO.modifiers:
            output_file.write("mod:"+mod.name+":"+mod.type+"\n")
            values = dir(mod)
            #Cycle through mod values for serialisable values.
            for modvalue in values:
                try:
                    if mod.is_property_readonly(modvalue) == False and modvalue != "__module__" and modvalue !="name" and modvalue != "type" and modvalue != "vertex_group" and modvalue != "uv_layer" and modvalue != "filepath":

                        #Bring modvalue into active memory as 'y'.
                        y = eval("mod."+modvalue)

                        #Output regular data types.
                        if isinstance(y, (int,str,bool)) == True:
                            output_file.write("modvar:"+modvalue+":"+str(y)+"\n")
                        #Output float data types.
                        if isinstance(y, float) == True:
                            z = float("{0:.4f}".format(y))
                            output_file.write("modvar:"+modvalue+":"+str(z)+"\n")
                        #Output vector data types.
                        if isinstance(y, Vector) == True:
                            i = 0
                            while i <= 2:
                                try:
                                    if y[i] != None:
                                        if isinstance(y[i], float) == True:
                                            z = float("{0:.4f}".format(y[i]))
                                            output_file.write("modvar:"+modvalue+"["+str(i)+"]:"+str(z)+"\n")
                                        else:
                                            output_file.write("modvar:"+modvalue+"["+str(i)+"]:"+str(y[i])+"\n")
                                except:
                                    print("BY-GEN Debug: Vector position ["+str(i)+"] for "+modvalue+" does not exist.")
                                i+=1
                        if isinstance(y, list) == True:
                            print("DEBUG: DISCOVERED LIST FOR: "+modvalue+"\n")
                        #Other Exceptions
                        if modvalue == "relative_offset_displace":
                            i = 0
                            while i <= 2:
                                try:
                                    if y[i] != None:
                                        if isinstance(y[i], float) == True:
                                            z = float("{0:.4f}".format(y[i]))
                                            output_file.write("modvar:relative_offset_displace["+str(i)+"]:"+str(z)+"\n")
                                        else:
                                            output_file.write("modvar:relative_offset_displace["+str(i)+"]:"+str(y[i])+"\n")
                                except:
                                    print("BY-GEN Debug: Vector position ["+str(i)+"] for relative_offset_displace does not exist.")
                                i+=1
                        #Texture Exception
                        if modvalue == "texture":
                            #If there is a texture present
                            if y != None:
                                #Check to make sure this is not an external image or NONE.
                                if y.type != "IMAGE" and y.type != "NONE":

                                    #Output the name and type of the texture.
                                    output_file.write("tex:"+y.name+":"+y.type+"\n")

                                    #We do not have to worry about external data (or no data), so output generation values.
                                    #Proceed to get a list of all child elements of the current texture object.
                                    t_values = dir(y)
                                    #print(dir(y))
                                    #For each of the texture properties.
                                    for texvalue in t_values:
                                        #If it's not meta data.
                                        #if texvalue != "__module__" and texvalue !="name" and texvalue != "type" and texvalue != "name_full" and texvalue != "is_evaluated" and texvalue != "is_library_indirect" and texvalue != "users":
                                        try:
                                            if y.is_property_readonly(texvalue) == False and texvalue != "__module__" and texvalue !="name" and texvalue != "type" and texvalue != "name_full" and texvalue != "is_evaluated" and texvalue != "is_library_indirect" and texvalue != "users":
                                                j = eval("y."+texvalue)
                                                #Output regular data types.
                                                if isinstance(j, (int,str,bool)) == True:
                                                    output_file.write("texvar:"+texvalue+":"+str(j)+"\n")
                                                #Output float data types.
                                                if isinstance(j, float) == True:
                                                    z = float("{0:.4f}".format(j))
                                                    output_file.write("texvar:"+texvalue+":"+str(z)+"\n")
                                                #Output vector data types.
                                                if isinstance(j, Vector) == True:
                                                    i = 0
                                                    while i <= 2:
                                                        try:
                                                            if j[i] != None:
                                                                if isinstance(j[i], float) == True:
                                                                    z = float("{0:.4f}".format(j[i]))
                                                                    output_file.write("texvar:"+texvalue+"["+str(i)+"]:"+str(z)+"\n")
                                                                else:
                                                                    output_file.write("texvar:"+texvalue+"["+str(i)+"]:"+str(j[i])+"\n")
                                                        except:
                                                            print("BY-GEN Debug: Vector position ["+str(i)+"] for "+texvalue+" does not exist.")
                                                        i+=1
                                        except:
                                            continue
                except:
                    continue

            output_file.write("#------------------------------#\n")

        return {'FINISHED'}
#endregion