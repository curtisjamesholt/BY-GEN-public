'''
This file contains operators which are called from the
Shift+A Menu.
'''
import bpy
import bmesh
import random
from math import radians
from mathutils import Vector, Matrix
from bpy.props import *
from bpy.types import (Panel,Menu,Operator,PropertyGroup)
from . generate import BYGEN_OT_Generate
# //====================================================================//
#    < Operator Calls >
# //====================================================================//
# Operators for generation techniques.
class BYGEN_OT_cubic_field_generate(bpy.types.Operator):
    bl_idname = "object.bygen_cubic_field_generate"
    bl_label = "Cubic Field"
    bl_description = "Generates a cubic field"
    bl_options = {'REGISTER', 'UNDO'}

    #Operator Properties
    seed_value : IntProperty(
        name = "Seed",
        description = "Seed for randomisation",
        default = 1,
        min = 1,
        max = 1000000
    )
    number_of_cubes : IntProperty(
        name = "Number of Cubes",
        description = "Number of cubes to create",
        default = 25,
        min=1,
        max=10000
    )
    position_deviation : FloatVectorProperty(
        name = "Position Deviation",
        description = "Maximum possible deviation from creation point",
        default = (5.0,5.0,5.0),
        min = -1000.0,
        max = 1000.0
    )
    uniform_scale : BoolProperty(
        name = "Uniform Property",
        description = "Use uniform scale for all dimensions",
        default = True
    )
    scale_min : FloatVectorProperty(
        name = "Minimum Size Deviation",
        description = "Minimum possible size deviation",
        default = (-0.9,-0.9,-0.9),
        min=-0.9,
        max=1000.0
    )
    scale_max : FloatVectorProperty(
        name = "Maximum Size Deviation",
        description = "Maximum possible size deviation",
        default = (-0.5,-0.5,-0.5),
        min=-0.9,
        max=1000.0
    )
    add_bevel : BoolProperty(
        name = "Add Bevel",
        description = "Adds a bevel modifier to the result",
        default = False
    )
    kick_rotation : BoolProperty(
        name = "Kick Rotation",
        description = "Add a random deviation to the rotation of cubes",
        default = True
    )
    join_cubes : BoolProperty(
        name = "Join Cubes",
        description = "Join cubes into one object",
        default = True
    )

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        bytool = scene.by_tool

        box = layout.box()
        box.label(text="Parameters")
        
        col = box.column()

        col.label(text="Random Seed")
        colrow = col.row(align=True)
        colrow.prop(self, "seed_value", expand = True, text="")

        colrow = col.row(align=True)
        col.label(text="Number of Cubes")
        colrow = col.row(align=True)
        colrow.prop(self, "number_of_cubes", expand=True, text="")

        colrow = col.row(align=True)
        col.label(text="Position Deviation")
        colrow = col.row(align=True)
        colrow.prop(self, "position_deviation", expand=True, text="")

        colrow = col.row(align=True)
        col.label(text="Scale Deviation Min")
        colrow = col.row(align=True)
        colrow.prop(self, "scale_min", expand=True, text="")

        colrow = col.row(align=True)
        col.label(text="Scale Deviation Max")
        colrow = col.row(align=True)
        colrow.prop(self, "scale_max", expand=True, text="")

        box = layout.box()
        box.label(text="Settings")

        column = box.column()

        row = column.row()
        row.prop(self, "uniform_scale", expand=True, text="Uniform Scale")
        row.prop(self, "kick_rotation", expand = True, text = "Kick Rotation")
        
        row = column.row()
        row.prop(self, "join_cubes", expand = True, text = "Join Cubes")
        if self.join_cubes == True:
            row.prop(self, "add_bevel", expand=True, text="Add Bevel")
        

    def execute(self, context):
        #//////////// CONTEXT >
        scene = context.scene
        bytool = scene.by_tool
        #//////////// BEGIN GENERATION PROCEDURE >
        
        
        random.seed(self.seed_value)

        created_cubes = []

        #For number of cubes
        for x in range(self.number_of_cubes):
            #Create Cube
            bpy.ops.mesh.primitive_cube_add()
            sO = bpy.context.active_object
            
            #Modify Cube

            #Get Old Location
            original_location = sO.location
            #Position Diversion Values
            pos_x_diversion = random.uniform(-self.position_deviation[0], self.position_deviation[0])
            pos_y_diversion = random.uniform(-self.position_deviation[1], self.position_deviation[1])
            pos_z_diversion = random.uniform(-self.position_deviation[2], self.position_deviation[2])
            new_location = original_location
            new_location[0] = new_location[0] + pos_x_diversion
            new_location[1] = new_location[1] + pos_y_diversion
            new_location[2] = new_location[2] + pos_z_diversion
            sO.location = new_location

            #Get Old Scale
            original_scale = sO.scale
            #Scale Diversion Values
            scale_x_diversion = random.uniform(self.scale_min[0], self.scale_max[0])
            scale_y_diversion = random.uniform(self.scale_min[1], self.scale_max[1])
            scale_z_diversion = random.uniform(self.scale_max[2], self.scale_max[2])
            new_scale = original_scale
            if self.uniform_scale == True:
                new_scale[0] = new_scale[0] + scale_x_diversion
                new_scale[1] = new_scale[1] + scale_x_diversion
                new_scale[2] = new_scale[2] + scale_x_diversion
            else:
                new_scale[0] = new_scale[0] + scale_x_diversion
                new_scale[1] = new_scale[1] + scale_y_diversion
                new_scale[2] = new_scale[2] + scale_z_diversion
            sO.scale = new_scale

            if self.kick_rotation == True:
                #Get old Rotation
                original_rotation = sO.rotation_euler
                #Rotation Diversion Values
                rot_x_diversion = random.randint(-360, 360)
                rot_y_diversion = random.randint(-360, 360)
                rot_z_diversion = random.randint(-360, 360)
                new_rot = original_rotation
                new_rot[0] = new_rot[0] + rot_x_diversion
                new_rot[1] = new_rot[1] + rot_y_diversion
                new_rot[2] = new_rot[2] + rot_z_diversion
                #sO.rotation_euler = new_rot
                sO.rotation_euler = (radians(new_rot[0]), radians(new_rot[1]), radians(new_rot[2]))

            created_cubes.append(sO)
            
        if self.join_cubes:
            for x in created_cubes:
                #created_cubes[x].select_set(True)
                x.select_set(True)
            bpy.ops.object.join()
            sO = bpy.context.active_object
            #Post-Join Operations
            #Adding bevel modifier
            if self.add_bevel==True:
                mod_bevel = sO.modifiers.new('Bevel', 'BEVEL')

        return {'FINISHED'}
class BYGEN_OT_spherical_field_generate(bpy.types.Operator):
    bl_idname = "object.bygen_spherical_field_generate"
    bl_label = "Spherical Field"
    bl_description = "Generates a spherical field"
    bl_options = {'REGISTER', 'UNDO'}

    #Operator Properties
    seed_value : IntProperty(
        name = "Seed",
        description = "Seed for randomisation",
        default = 1,
        min = 1,
        max = 1000000
    )
    number_of_spheres : IntProperty(
        name = "Number of Spheres",
        description = "Number of spheres to create",
        default = 25,
        min=1,
        max=10000
    )
    position_deviation : FloatVectorProperty(
        name = "Position Deviation",
        description = "Maximum possible deviation from creation point",
        default = (5.0,5.0,5.0),
        min = -1000.0,
        max = 1000.0
    )
    uniform_scale : BoolProperty(
        name = "Uniform Property",
        description = "Use uniform scale for all dimensions",
        default = True
    )
    scale_min : FloatVectorProperty(
        name = "Minimum Size Deviation",
        description = "Minimum possible size deviation",
        default = (-0.9,-0.9,-0.9),
        min=-0.9,
        max=1000.0
    )
    scale_max : FloatVectorProperty(
        name = "Maximum Size Deviation",
        description = "Maximum possible size deviation",
        default = (-0.5,-0.5,-0.5),
        min=-0.9,
        max=1000.0
    )
    kick_rotation : BoolProperty(
        name = "Kick Rotation",
        description = "Add a random deviation to the rotation of cubes",
        default = True
    )
    join_spheres : BoolProperty(
        name = "Join Spheres",
        description = "Join spheres into one object",
        default = True
    )

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        bytool = scene.by_tool

        box = layout.box()
        box.label(text="Parameters")
        
        col = box.column()

        col.label(text="Random Seed")
        colrow = col.row(align=True)
        colrow.prop(self, "seed_value", expand = True, text="")

        colrow = col.row(align=True)
        col.label(text="Number of Spheres")
        colrow = col.row(align=True)
        colrow.prop(self, "number_of_spheres", expand=True, text="")

        colrow = col.row(align=True)
        col.label(text="Position Deviation")
        colrow = col.row(align=True)
        colrow.prop(self, "position_deviation", expand=True, text="")

        colrow = col.row(align=True)
        col.label(text="Scale Deviation Min")
        colrow = col.row(align=True)
        colrow.prop(self, "scale_min", expand=True, text="")

        colrow = col.row(align=True)
        col.label(text="Scale Deviation Max")
        colrow = col.row(align=True)
        colrow.prop(self, "scale_max", expand=True, text="")

        box = layout.box()
        box.label(text="Settings")

        column = box.column()

        row = column.row()
        row.prop(self, "uniform_scale", expand=True, text="Uniform Scale")
        row.prop(self, "kick_rotation", expand = True, text = "Kick Rotation")
        
        row = column.row()
        row.prop(self, "join_spheres", expand = True, text = "Join Spheres")
        

    def execute(self, context):
        #//////////// CONTEXT >
        scene = context.scene
        bytool = scene.by_tool
        #//////////// BEGIN GENERATION PROCEDURE >
        
        
        random.seed(self.seed_value)

        created_spheres = []

        #For number of spheres
        for x in range(self.number_of_spheres):
            #Create Sphere
            bpy.ops.mesh.primitive_uv_sphere_add()
            sO = bpy.context.active_object
            
            #Modify Sphere

            #Get Old Location
            original_location = sO.location
            #Position Diversion Values
            pos_x_diversion = random.uniform(-self.position_deviation[0], self.position_deviation[0])
            pos_y_diversion = random.uniform(-self.position_deviation[1], self.position_deviation[1])
            pos_z_diversion = random.uniform(-self.position_deviation[2], self.position_deviation[2])
            new_location = original_location
            new_location[0] = new_location[0] + pos_x_diversion
            new_location[1] = new_location[1] + pos_y_diversion
            new_location[2] = new_location[2] + pos_z_diversion
            sO.location = new_location

            #Get Old Scale
            original_scale = sO.scale
            #Scale Diversion Values
            scale_x_diversion = random.uniform(self.scale_min[0], self.scale_max[0])
            scale_y_diversion = random.uniform(self.scale_min[1], self.scale_max[1])
            scale_z_diversion = random.uniform(self.scale_max[2], self.scale_max[2])
            new_scale = original_scale
            if self.uniform_scale == True:
                new_scale[0] = new_scale[0] + scale_x_diversion
                new_scale[1] = new_scale[1] + scale_x_diversion
                new_scale[2] = new_scale[2] + scale_x_diversion
            else:
                new_scale[0] = new_scale[0] + scale_x_diversion
                new_scale[1] = new_scale[1] + scale_y_diversion
                new_scale[2] = new_scale[2] + scale_z_diversion
            sO.scale = new_scale

            if self.kick_rotation == True:
                #Get old Rotation
                original_rotation = sO.rotation_euler
                #Rotation Diversion Values
                rot_x_diversion = random.randint(-360, 360)
                rot_y_diversion = random.randint(-360, 360)
                rot_z_diversion = random.randint(-360, 360)
                new_rot = original_rotation
                new_rot[0] = new_rot[0] + rot_x_diversion
                new_rot[1] = new_rot[1] + rot_y_diversion
                new_rot[2] = new_rot[2] + rot_z_diversion
                #sO.rotation_euler = new_rot
                sO.rotation_euler = (radians(new_rot[0]), radians(new_rot[1]), radians(new_rot[2]))

            created_spheres.append(sO)
            
        if self.join_spheres:
            for x in created_spheres:
                #created_spheres[x].select_set(True)
                x.select_set(True)
            bpy.ops.object.join()
            sO = bpy.context.active_object
            #Post-Join Operations

        return {'FINISHED'}
# Generators for Modification - Requires Mesh Input
class BYGEN_OT_meta_cloud_generate(bpy.types.Operator):
    bl_idname = "object.bygen_meta_cloud_generate"
    bl_label = "Meta Cloud"
    bl_description = "Generates a meta cloud from an input mesh"
    bl_options = {'REGISTER', 'UNDO'}

    #Operator Properties
    frame_start : IntProperty(
        name = "Frame Start",
        description = "Start frame for build modifier",
        default = -60,
        min = -100,
        max = 100
    )
    particle_size : FloatProperty(
        name = "Particle Size",
        description = "Size of the particles",
        default = 3,
        min = 0,
        max = 50
    )
    particle_length : FloatProperty(
        name = "Particle Lenght",
        description = "Length of the particles",
        default = 0.15,
        min = 0,
        max = 100
    )

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        bytool = scene.by_tool

        box = layout.box()
        box.label(text="Parameters")
        
        col = box.column()

        col.label(text="Frame Start")
        colrow = col.row(align=True)
        colrow.prop(self, "frame_start", expand = True, text="")
        colrow = col.row(align=True)
        col.label(text="Particle Size")
        colrow = col.row(align=True)
        colrow.prop(self, "particle_size", expand=True, text="")
        colrow = col.row(align=True)
        col.label(text="Particle Length")
        colrow = col.row(align=True)
        colrow.prop(self, "particle_length", expand=True, text="")

    def execute(self, context):
        #//////////// CONTEXT >
        scene = context.scene
        bytool = scene.by_tool
        #//////////// BEGIN GENERATION PROCEDURE >

        sO = bpy.context.active_object
        sO_name = bpy.context.active_object.name
        mod_build = sO.modifiers.new('Build', 'BUILD')
        mod_build.use_random_order = True

        mod_build.frame_start = self.frame_start

        bpy.ops.object.bygen_apply_modifiers()

        sO.modifiers.new("Part", 'PARTICLE_SYSTEM')
        part = sO.particle_systems[0]
        part.settings.type = 'HAIR'
        part.settings.use_advanced_hair = True
        part.settings.hair_length = self.particle_length
        part.settings.render_type = 'OBJECT'

        bpy.ops.object.metaball_add(type='BALL')
        meta = bpy.context.active_object
        meta_name = bpy.context.active_object.name
        meta.scale = (0.1,0.1,0.1)
        part.settings.instance_object = meta
        part.settings.particle_size = self.particle_size
        bpy.ops.object.convert(target='MESH')

        new_name = meta_name+".001"
        meta = bpy.data.objects[new_name]

        #context.view_layer.objects.active = sO

        objs = bpy.data.objects
        objs.remove(objs[sO_name], do_unlink=True)

        old_collection = meta.users_collection
        old_collection[0].objects.unlink(meta)

        generation_result = None
        if "Generation Result" in bpy.data.collections:
            generation_result = bpy.data.collections["Generation Result"]
        else:
            bpy.data.collections.new("Generation Result")
            generation_result = bpy.data.collections["Generation Result"]
            bpy.context.scene.collection.children.link(generation_result)

        generation_result.objects.link(meta)


        #bpy.ops.object.delete()

        #context.view_layer.objects.active = meta

        #Try removing vertices here
        '''
        me = meta.data
        bm = bmesh.new()
        bm.from_mesh(me)
        bm.verts.ensure_lookup_table()
        i=0
        x = len(bm.verts)
        while i < x:
            bm.verts.ensure_lookup_table()
            if i < 192:
                v = bm.verts[i]
                bm.verts.remove(v)
            i+=1
        bm.to_mesh(me)
        '''
        return {'FINISHED'}
# Template
class BYGEN_OT_template_add(bpy.types.Operator):
    bl_idname = "object.bygen_template_add"
    bl_label = "Generate Template"
    bl_description = "Generates a Template"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        #//////////// CONTEXT >
        scene = context.scene
        bytool = scene.by_tool
        #//////////// BEGIN GENERATION PROCEDURE >
        bpy.ops.mesh.primitive_cube_add()
        sO = bpy.context.active_object
        return {'FINISHED'}
# Hard Surface
class BYGEN_OT_hard_surface_faceting_add(bpy.types.Operator):
    bl_idname = "object.bygen_hard_surface_faceting_add"
    bl_label = "Generate Hard Surface Faceting"
    bl_description = "Generates a Hard Surface Faceting Object"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        #//////////// CONTEXT >
        scene = context.scene
        bytool = scene.by_tool
        #//////////// BEGIN GENERATION PROCEDURE >
        bpy.ops.mesh.primitive_cube_add()
        sO = bpy.context.active_object
        '''
        mesh = sO.data

        for vert in mesh.vertices:
            new_location = vert.co
            rand = random.uniform(-1.0,1.0)
            vert.co = vert.co+Vector((rand,rand,rand))
        ''' 
        #////////////ADD MODIFIERS TO CREATED OBJECT >
        #RANDOM ID
        randID = random.randint(1,9999)
        #SUBSURF
        mod = sO.modifiers.new("Subsurface", 'SUBSURF')
        mod.levels = 4
        mod.render_levels = 4

        #<|<|///////// DISPLACE WITH SWITCHING
        mod_displace = sO.modifiers.new("Displace", 'DISPLACE')
        mod_displace.strength = -0.1
        tempTex = bpy.data.textures.new("ByGen_TexID_"+str(randID), 'MUSGRAVE')
        mod_displace.texture = tempTex
        tempTex = mod_displace.texture

        #DECIMATE 1
        mod_decimate1 = sO.modifiers.new('Decimate1', 'DECIMATE')
        mod_decimate1.decimate_type = 'COLLAPSE'
        mod_decimate1.ratio = 0.1
        #mod_decimate1.ratio = bytool.gen_decimate_collapse
        #DECIMATE 2
        mod_decimate2 = sO.modifiers.new('Decimate2', 'DECIMATE')
        mod_decimate2.decimate_type = 'DISSOLVE' #COLLAPSE, UNSUBDIV, DISSOLVE (PLANAR)
        #mod_decimate2.angle_limit = 0.174533 #Set radian value for planar mode as float. 30 is 0.523599 / 10 is 0.174533
        #mod_decimate2.angle_limit = bytool.gen_decimate_angle
        mod_decimate2.angle_limit = 0.698132
        #TRIANGULATE
        mod_triangulate = sO.modifiers.new('Triangulate', 'TRIANGULATE')
        #EDGE SPLIT
        mod_edgesplit = sO.modifiers.new('Edge Split', 'EDGE_SPLIT')
        mod_edgesplit.split_angle = 0.261799
        #SOLIDIFY
        mod_solidify = sO.modifiers.new('Solidify', 'SOLIDIFY')
        mod_solidify.thickness = -0.02
        #BEVEL
        mod_bevel = sO.modifiers.new('Bevel', 'BEVEL')
        mod_bevel.use_clamp_overlap = 1
        mod_bevel.limit_method = 'ANGLE' #NONE, ANGLE, WEIGHT, VGROUP
        mod_bevel.segments = 3
        #MIRROR
        mod_mirror = sO.modifiers.new('Mirror', 'MIRROR')
        mod_mirror.use_bisect_axis[0] = 1 #0=x, 1=y, 2=z || Regular Mirror is use_axis, Flip is use_bisect_flip_axis

        return {'FINISHED'}
class BYGEN_OT_hard_surface_skin_add(bpy.types.Operator):
    bl_idname = "object.bygen_hard_surface_skin_add"
    bl_label = "Generate Hard Surface Skin"
    bl_description = "Generates a Hard Surface Skin Object"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        #//////////// CONTEXT >
        scene = context.scene
        bytool = scene.by_tool
        #Set the properties

        #//////////// BEGIN GENERATION PROCEDURE >
        #sO = bpy.context.selected_objects[0]

        #Begin mesh generation procedure
        '''
        cPos = [0,0,0]
        cPos[0] = bpy.context.scene.cursor.location.x
        cPos[1] = bpy.context.scene.cursor.location.y
        cPos[2] = bpy.context.scene.cursor.location.z
        #cPos2 = cPos
        #cPos2[2] = cPos[2]+1
        #verts = [cPos2, cPos]
        '''

        verts = [(0,0,1), (0,0,0)]
        mesh = bpy.data.meshes.new("mesh")
        obj = bpy.data.objects.new("HSS_Object", mesh)
        scene = bpy.context.scene.collection
        scene.objects.link(obj)
        bpy.context.view_layer.objects.active = obj
        mesh = bpy.context.object.data
        bm = bmesh.new()
        bm.verts.new(verts[0])
        bm.verts.new(verts[1])
        bm.to_mesh(mesh)
        bm.verts.ensure_lookup_table()
        bm.edges.new((bm.verts[0],bm.verts[1]))
        bm.to_mesh(mesh)
        bm.free()

        sO = bpy.context.active_object
        
        #////////// ADDING MODIFIERS >
        #Skin
        mod_skin = sO.modifiers.new("Skin", "SKIN")
        #Remesh
        mod_remesh = sO.modifiers.new("Remesh", "REMESH")
        mod_remesh.mode = "SMOOTH"
        mod_remesh.octree_depth = 5
        #Bevel1
        mod_bevel = sO.modifiers.new("Bevel", "BEVEL")
        mod_bevel.offset_type ="PERCENT"
        mod_bevel.width_pct = 37
        mod_bevel.use_only_vertices = True
        mod_bevel.show_in_editmode = False
        #Decimate1
        mod_decimate = sO.modifiers.new("Decimate", "DECIMATE")
        mod_decimate.ratio = 0.0156
        #Decimate2
        mod_decimate2 = sO.modifiers.new("Decimate 2", "DECIMATE")
        mod_decimate2.decimate_type = "DISSOLVE"
        mod_decimate2.angle_limit = 0.087266
        #Bevel 2
        mod_bevel2 = sO.modifiers.new("Bevel 2", "BEVEL")
        mod_bevel2.offset_type = "PERCENT"
        mod_bevel2.width_pct = 33
        mod_bevel2.use_only_vertices = True
        mod_bevel2.show_in_editmode = False
        #Edge Split
        mod_edge = sO.modifiers.new("Edge Split", "EDGE_SPLIT")
        mod_edge.show_in_editmode = False
        #Solidify
        mod_solid = sO.modifiers.new("Solidify", "SOLIDIFY")
        mod_solid.thickness = -0.04
        mod_solid.use_rim_only = True
        mod_solid.show_in_editmode = False
        #Bevel 3
        mod_bevel3 = sO.modifiers.new("Bevel 3", "BEVEL")
        mod_bevel3.width = 0.053
        mod_bevel3.show_in_editmode = False
        #Mirror
        if bytool.gen_hss_allow_mirror == True:
            mod_mirror = sO.modifiers.new("Mirror", "MIRROR")
            mod_mirror.use_bisect_axis[0] = 1
            mod_mirror.show_in_editmode = False
        #Displace
        mod_displace = sO.modifiers.new("Displace", "DISPLACE")
        mod_displace.strength = 0.025
        mod_displace.show_in_editmode = False
        return {'FINISHED'}
class BYGEN_OT_hard_surface_skin_simple_add(bpy.types.Operator):
    bl_idname = "object.bygen_hard_surface_skin_simple_add"
    bl_label = "Generate Hard Surface Skin (Simple)"
    bl_description = "Generates a Hard Surface Skin (Simple) Object"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        #//////////// CONTEXT >
        scene = context.scene
        bytool = scene.by_tool
        #Set the properties

        #//////////// BEGIN GENERATION PROCEDURE >
        #sO = bpy.context.selected_objects[0]

        #Begin mesh generation procedure
        verts = [(0,0,1), (0,0,0)]
        mesh = bpy.data.meshes.new("mesh")
        obj = bpy.data.objects.new("HSS_Object", mesh)
        scene = bpy.context.scene.collection
        scene.objects.link(obj)
        bpy.context.view_layer.objects.active = obj
        mesh = bpy.context.object.data
        bm = bmesh.new()
        bm.verts.new(verts[0])
        bm.verts.new(verts[1])
        bm.to_mesh(mesh)
        bm.verts.ensure_lookup_table()
        bm.edges.new((bm.verts[0],bm.verts[1]))
        bm.to_mesh(mesh)
        bm.free()

        sO = bpy.context.active_object
        
        #////////// ADDING MODIFIERS >
        #Skin
        mod_skin = sO.modifiers.new("Skin", "SKIN")
        #Remesh
        mod_remesh = sO.modifiers.new("Remesh", "REMESH")
        mod_remesh.mode = "SMOOTH"
        mod_remesh.octree_depth = 5
        #Bevel1
        mod_bevel = sO.modifiers.new("Bevel", "BEVEL")
        mod_bevel.offset_type ="PERCENT"
        mod_bevel.width_pct = 37
        mod_bevel.use_only_vertices = True
        mod_bevel.show_in_editmode = False
        #Decimate1
        mod_decimate = sO.modifiers.new("Decimate", "DECIMATE")
        #mod_decimate.ratio = 0.0156
        mod_decimate.ratio = 0.03
        #Decimate2
        '''
        mod_decimate2 = sO.modifiers.new("Decimate 2", "DECIMATE")
        mod_decimate2.decimate_type = "DISSOLVE"
        mod_decimate2.angle_limit = 0.087266
        '''
        #Bevel 2
        mod_bevel2 = sO.modifiers.new("Bevel 2", "BEVEL")
        mod_bevel2.offset_type = "PERCENT"
        mod_bevel2.width_pct = 33
        mod_bevel2.use_only_vertices = True
        mod_bevel2.show_in_editmode = False
        #Bevel 3
        '''
        mod_bevel3 = sO.modifiers.new("Bevel 3", "BEVEL")
        mod_bevel3.width = 0.053
        mod_bevel3.show_in_editmode = False
        '''
        #Mirror
        mod_mirror = sO.modifiers.new("Mirror", "MIRROR")
        mod_mirror.use_bisect_axis[0] = 1
        mod_mirror.show_in_editmode = False
        return {'FINISHED'}
class BYGEN_OT_metal_shell_add(bpy.types.Operator):
    bl_idname = "object.bygen_metal_shell_add"
    bl_label = "Generate Metal Shell"
    bl_description = "Generates a Metal Shell Object"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        #//////////// CONTEXT >
        scene = context.scene
        bytool = scene.by_tool
        #//////////// BEGIN GENERATION PROCEDURE >
        bpy.ops.mesh.primitive_cube_add()
        sO = bpy.context.active_object

        #SUBSURF
        mod = sO.modifiers.new("Subsurface", 'SUBSURF')
        mod.levels = 3
        mod.render_levels = 3
        #TRIANGULATE
        mod_triangulate = sO.modifiers.new('Triangulate', 'TRIANGULATE')
        #WIREFRAME
        mod_wireframe = sO.modifiers.new('Wireframe', 'WIREFRAME')
        mod_wireframe.thickness = 0.03
        mod_wireframe.use_boundary = True
        #BEVEL
        mod_bevel = sO.modifiers.new('Bevel', 'BEVEL')

        return {'FINISHED'}
class BYGEN_OT_hard_padding_add(bpy.types.Operator):
    bl_idname = "object.bygen_hard_padding_add"
    bl_label = "Generate Hard Padding"
    bl_description = "Generates a Hard Padding Object"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        #//////////// CONTEXT >
        scene = context.scene
        bytool = scene.by_tool
        #//////////// BEGIN GENERATION PROCEDURE >
        bpy.ops.mesh.primitive_cube_add()
        sO = bpy.context.active_object
        #////////// ADDING MODIFIERS >
        #SUBSURF
        mod = sO.modifiers.new("Subsurface", 'SUBSURF')
        mod.levels = 3
        mod.render_levels = 3
        #Decimate
        mod_decimate = sO.modifiers.new("Decimate", "DECIMATE")
        mod_decimate.ratio = 1.0
        #Triangulate
        #mod_triangulate = sO.modifiers.new("Triangualate", "TRIANGULATE")
        #Edge Split
        mod_edge = sO.modifiers.new("Edge Split", "EDGE_SPLIT")
        mod_edge.use_edge_angle = True
        mod_edge.split_angle = 0
        mod_edge.show_in_editmode = False
        #Solidify
        mod_solid = sO.modifiers.new("Solidify", "SOLIDIFY")
        mod_solid.thickness = -0.05
        #Bevel
        mod_bevel = sO.modifiers.new("Bevel", "BEVEL")
        mod_bevel.width = 0.01
        mod_bevel.segments = 3
        mod_bevel.use_clamp_overlap = True
        mod_bevel.limit_method = "NONE"
        return {'FINISHED'}
class BYGEN_OT_midge_cell_add(bpy.types.Operator):
    bl_idname = "object.bygen_midge_cell_add"
    bl_label = "Generate Midge Cell"
    bl_description = "Generates a Midge Cell Object"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        #//////////// CONTEXT >
        scene = context.scene
        bytool = scene.by_tool
        #//////////// BEGIN GENERATION PROCEDURE >
        bpy.ops.mesh.primitive_cube_add()
        sO = bpy.context.active_object
        #RANDOM ID
        randID = random.randint(1,9999)
        #////////// ADDING MODIFIERS >
        #SUBSURF
        mod_subd = sO.modifiers.new('Subsurface', 'SUBSURF')
        mod_subd.subdivision_type = "SIMPLE"
        mod_subd.levels = 2
        mod_subd.render_levels = 2

        #EDGE SPLIT
        mod_edgesplit = sO.modifiers.new('Edge Split', 'EDGE_SPLIT')
        mod_edgesplit.split_angle = 0.261799

        #Displace
        mod_displace = sO.modifiers.new("Displace", 'DISPLACE')
        mod_displace.strength = 1.0

        #Creating texture
        tempTex = bpy.data.textures.new("ByGen_TexID_"+str(randID), "DISTORTED_NOISE")
        mod_displace.texture = tempTex
        tempTex.distortion = 1.0
        tempTex.noise_scale = 0.85
        tempTex.nabla = 0.03
        tempTex.noise_basis = "CELL_NOISE"
        tempTex.noise_distortion = "CELL_NOISE"

        #Remesh
        mod_remesh = sO.modifiers.new("Remesh", "REMESH")
        mod_remesh.mode = "BLOCKS"
        mod_remesh.octree_depth = 4
        mod_remesh.scale = 0.9

        #Decimate 1
        mod_decimate = sO.modifiers.new('Decimate1', 'DECIMATE')
        mod_decimate.decimate_type = 'DISSOLVE'
        mod_decimate.angle_limit = 0.087266

        #Wireframe
        mod_wireframe = sO.modifiers.new('Wireframe', 'WIREFRAME')
        mod_wireframe.thickness = 0.02
        mod_wireframe.use_even_offset = False
        return {'FINISHED'}
# Organic
class BYGEN_OT_organic_skin_add(bpy.types.Operator):
    bl_idname = "object.bygen_organic_skin_add"
    bl_label = "Generate Organic Skin"
    bl_description = "Generates an Organic Skin Object"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        #//////////// CONTEXT >
        scene = context.scene
        bytool = scene.by_tool

        #//////////// BEGIN GENERATION PROCEDURE >
        #sO = bpy.context.selected_objects[0]
        randID = random.randint(1,9999)
        #Begin mesh generation procedure
        verts = [(0,0,1), (0,0,0)]
        mesh = bpy.data.meshes.new("mesh")
        obj = bpy.data.objects.new("HSS_Object", mesh)
        scene = bpy.context.scene.collection
        scene.objects.link(obj)
        bpy.context.view_layer.objects.active = obj
        mesh = bpy.context.object.data
        bm = bmesh.new()
        bm.verts.new(verts[0])
        bm.verts.new(verts[1])
        bm.to_mesh(mesh)
        bm.verts.ensure_lookup_table()
        bm.edges.new((bm.verts[0],bm.verts[1]))
        bm.to_mesh(mesh)
        bm.free()

        sO = bpy.context.active_object
        bpy.ops.object.shade_smooth()
        
        #////////// ADDING MODIFIERS >
        #Skin
        mod_skin = sO.modifiers.new("Skin", "SKIN")
        #Remesh
        mod_remesh = sO.modifiers.new("Remesh", "REMESH")
        mod_remesh.mode = "SMOOTH"
        mod_remesh.octree_depth = 4
        #Displace
        mod_displace = sO.modifiers.new("Displace", 'DISPLACE')
        mod_displace.strength = 0.6
        tempTex = bpy.data.textures.new("ByGen_TexID_"+str(randID), 'MUSGRAVE')
        mod_displace.texture = tempTex
        #DECIMATE 2
        mod_decimate2 = sO.modifiers.new('Decimate2', 'DECIMATE')
        mod_decimate2.decimate_type = 'DISSOLVE' #COLLAPSE, UNSUBDIV, DISSOLVE (PLANAR)
        #mod_decimate2.angle_limit = 0.174533 #Set radian value for planar mode as float. 30 is 0.523599 / 10 is 0.174533
        mod_decimate2.angle_limit = bytool.mod_decimate_angle #0.349066 recommended
        mod_decimate2.use_dissolve_boundaries = True
        #SMOOTH
        mod_smooth = sO.modifiers.new('Smooth', 'SMOOTH')
        mod_smooth.factor = 0.5
        mod_smooth.iterations = 15
        #TRIANGULATE
        if bytool.mod_oshell_allow_triangulate:
            mod_triangulate = sO.modifiers.new('Triangulate', 'TRIANGULATE')
        #WIREFRAME
        mod_wireframe = sO.modifiers.new('Wireframe', 'WIREFRAME')
        mod_wireframe.thickness = 0.05
        #SUBD
        mod_subd = sO.modifiers.new("SubD", "SUBSURF")
        mod_subd.levels = 2
        mod_subd.render_levels = 2


        return {'FINISHED'}
class BYGEN_OT_clay_blob_add(bpy.types.Operator):
    bl_idname = "object.bygen_clay_blob_add"
    bl_label = "Generate Clay Blob"
    bl_description = "Generates a Clay Blob"
    bl_options = {'REGISTER', 'UNDO'}

    #Operator Properties
    displace_str : FloatProperty(
        name = "Displace Strength",
        description = "Strength of the displacement",
        default = -0.1,
        min = -1000,
        max = 1000.0
    )
    noise_intensity : FloatProperty(
        name = "Noise Intensity",
        description = "Intensity of the noise texture",
        default = 0.8,
        min = -1000,
        max = 1000.0
    )
    noise_scale : FloatProperty(
        name = "Noise Scale",
        description = "Scale of the noise texture",
        default = 0.4,
        min = -1000,
        max = 1000.0
    )
    use_mirror : BoolProperty(
        name = "Mirror",
        description = "Mirror the Clay Blob",
        default = True
    )

    def execute(self, context):
        #//////////// BEGIN GENERATION PROCEDURE >
        bpy.ops.mesh.primitive_cube_add()
        sO = bpy.context.active_object
        mesh = sO.data

        #////////////ADD MODIFIERS TO CREATED OBJECT >
        #RANDOM ID
        randID = random.randint(1,9999)
        #SUBSURF
        mod = sO.modifiers.new("Subsurface", 'SUBSURF')
        mod.levels = 4
        mod.render_levels = 4
        #DISPLACE
        mod_displace = sO.modifiers.new("Displace", 'DISPLACE')
        #mod_displace.strength = -0.1
        mod_displace.strength = self.displace_str
        tempTex = bpy.data.textures.new("ByGen_TexID_"+str(randID), 'VORONOI')
        mod_displace.texture = tempTex
        tempTex = mod_displace.texture
        #tempTex.noise_intensity = 0.8
        tempTex.noise_intensity = self.noise_intensity
        #tempTex.noise_scale = 0.4
        tempTex.noise_scale = self.noise_scale
        #MIRROR
        if self.use_mirror:
            mod_mirror = sO.modifiers.new('Mirror', 'MIRROR')
            mod_mirror.use_bisect_axis[0] = 1
        return {'FINISHED'}
# FX
class BYGEN_OT_point_cloud_add(bpy.types.Operator):
    bl_idname = "object.bygen_point_cloud_add"
    bl_label = "Generate Point Cloud"
    bl_description = "Generates a Point Cloud Object"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        #//////////// CONTEXT >
        scene = context.scene
        bytool = scene.by_tool
        #//////////// BEGIN GENERATION PROCEDURE >
        bpy.ops.mesh.primitive_cube_add()
        sO = bpy.context.active_object
        randID = random.randint(1,9999)

        #////////// ADDING MODIFIERS >
        #SUBSURF
        mod = sO.modifiers.new("Subsurface", 'SUBSURF')
        mod.levels = 3
        mod.render_levels = 3
        #Displace
        mod_displace = sO.modifiers.new("Displace", "DISPLACE")
        mod_displace.strength = 0.050
        mod_displace.texture_coords = "OBJECT"
        tempTex = bpy.data.textures.new("ByGen_TexID_"+str(randID), 'MUSGRAVE')
        mod_displace.texture = tempTex
        tempTex = mod_displace.texture
        #Edge Split
        mod_edge = sO.modifiers.new("Edge Split", "EDGE_SPLIT")
        mod_edge.use_edge_angle = True
        mod_edge.split_angle = 0
        #Smooth
        mod_smooth = sO.modifiers.new("Smooth", "SMOOTH")
        mod_smooth.factor = 2.15
        mod_smooth.iterations = 1
        #Bevel
        mod_bevel = sO.modifiers.new("Bevel", "BEVEL")
        mod_bevel.offset_type = "PERCENT"
        mod_bevel.width_pct = 100
        mod_bevel.use_only_vertices = True
        #Displace 2
        mod_displace2 = sO.modifiers.new("Displace", "DISPLACE")
        mod_displace2.strength = 0.1
        mod_displace2.texture_coords = "OBJECT"
        mod_displace2.texture = tempTex
        return {'FINISHED'}
class BYGEN_OT_pixelate_add(bpy.types.Operator):
    bl_idname = "object.bygen_pixelate_add"
    bl_label = "Generate Pixelate"
    bl_description = "Generates a Pixelate Object"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        #//////////// CONTEXT >
        scene = context.scene
        bytool = scene.by_tool
        #//////////// BEGIN GENERATION PROCEDURE >
        bpy.ops.mesh.primitive_cube_add()
        sO = bpy.context.active_object

        #SUBSURF
        mod = sO.modifiers.new("Subsurface", 'SUBSURF')
        mod.levels = 4
        mod.render_levels = 4
        mod.show_in_editmode = False
        #Build
        mod_build = sO.modifiers.new("Build", 'BUILD')
        mod_build.frame_start = -20
        mod_build.use_random_order = True
        #Bevel
        mod_bevel = sO.modifiers.new("Bevel", 'BEVEL')
        mod_bevel.width = 1
        mod_bevel.use_only_vertices = True
        mod_bevel.use_clamp_overlap = True
        mod_bevel.segments = 3
        #Solidify
        mod_solid = sO.modifiers.new("Solidify", 'SOLIDIFY')
        mod_solid = -0.03

        return {'FINISHED'}