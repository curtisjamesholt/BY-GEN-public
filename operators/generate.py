import bpy
import bmesh
import random
import json
from mathutils import Vector, Matrix
from bpy.props import *
from bpy.types import (Panel,Menu,Operator,PropertyGroup)
# //====================================================================//
#    < Operators >
# //====================================================================//
#////////// OPERATOR FOR MESH GENERATION >
class BYGEN_OT_Generate(bpy.types.Operator):
    bl_idname = "object.bygen_generate"
    bl_label = "Generate Mesh"
    bl_description = "Activate BY-GEN Generate"
    bl_options = {'REGISTER', 'UNDO'}
    
    '''
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        bytool = scene.by_tool
        
        col = layout.column()
        col.label(text="Property Change Test")
        colrow = col.row(align=True)
        #colrow.prop(bytool, "gen_mc_framestart", expand=True)
        colrow.prop(self, "gen_frame_start", expand=True)
    '''
    '''
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    '''
    def execute(self, context):
        
        #//////////// CONTEXT >
        scene = context.scene
        bytool = scene.by_tool

    #<|<|<|<|<|<|<| GENERATION MODE SWITCHING >

        #//////////MODE: HARD SURFACE FACETED >
        if bytool.mode_generate=="MODE_HSF":

            #//////////// BEGIN GENERATION PROCEDURE >
            bpy.ops.mesh.primitive_cube_add()
            sO = bpy.context.active_object
            mesh = sO.data

            for vert in mesh.vertices:
                new_location = vert.co
                rand = random.uniform(-1.0,1.0)
                vert.co = vert.co+Vector((rand,rand,rand))
                
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
            tempTex = bpy.data.textures.new("ByGen_TexID_"+str(randID), 'DISTORTED_NOISE')
            mod_displace.texture = tempTex
            tempTex = mod_displace.texture

            if bytool.mode_gen_disp == "MODE_GD_CLOUDS":
                tempTex.type="CLOUDS"
                #---
            if bytool.mode_gen_disp == "MODE_GD_DISTNOISE":
                tempTex.type="DISTORTED_NOISE"
                #---
            if bytool.mode_gen_disp == "MODE_GD_MARBLE":
                tempTex.type="MARBLE"
                #---
            if bytool.mode_gen_disp == "MODE_GD_MUSGRAVE":
                tempTex.type='MUSGRAVE'
                #---
            if bytool.mode_gen_disp == "MODE_GD_STUCCI":
                tempTex.type='STUCCI'
                #---
            if bytool.mode_gen_disp == "MODE_GD_VORONOI":
                tempTex.type='VORONOI'
                #---
            if bytool.mode_gen_disp == "MODE_GD_WOOD":
                tempTex.type='WOOD'
                #---
            
            
            #DECIMATE 1
            mod_decimate1 = sO.modifiers.new('Decimate1', 'DECIMATE')
            mod_decimate1.decimate_type = 'COLLAPSE'
            #mod_decimate1.ratio = 0.2
            mod_decimate1.ratio = bytool.gen_decimate_collapse
            #DECIMATE 2
            mod_decimate2 = sO.modifiers.new('Decimate1', 'DECIMATE')
            mod_decimate2.decimate_type = 'DISSOLVE' #COLLAPSE, UNSUBDIV, DISSOLVE (PLANAR)
            #mod_decimate2.angle_limit = 0.174533 #Set radian value for planar mode as float. 30 is 0.523599 / 10 is 0.174533
            mod_decimate2.angle_limit = bytool.gen_decimate_angle
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
        #//////////MODE: HARD SURFACE SKIN >
        if bytool.mode_generate=="MODE_HSS":

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
        #//////////MODE: CLAY BLOB >
        if bytool.mode_generate=="MODE_BLOB":
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
            mod_displace.strength = -0.1
            tempTex = bpy.data.textures.new("ByGen_TexID_"+str(randID), 'VORONOI')
            mod_displace.texture = tempTex
            tempTex = mod_displace.texture
            tempTex.noise_intensity = 0.8
            tempTex.noise_scale = 0.4
            #MIRROR
            mod_mirror = sO.modifiers.new('Mirror', 'MIRROR')
            mod_mirror.use_bisect_axis[0] = 1
        #//////////GEN_META_CLOUD >
        if bytool.mode_generate=="GEN_META_CLOUD":
            bpy.ops.object.bygen_meta_cloud_generate()
            '''
            sO = bpy.context.active_object
            sO_name = bpy.context.active_object.name
            mod_build = sO.modifiers.new('Build', 'BUILD')
            mod_build.use_random_order = True

            #mod_build.frame_start = 60
            #mod_build.frame_start = self.gen_frame_start
            mod_build.frame_start = -60

            bpy.ops.object.bygen_apply_modifiers()

            sO.modifiers.new("Part", 'PARTICLE_SYSTEM')
            part = sO.particle_systems[0]
            part.settings.type = 'HAIR'
            part.settings.use_advanced_hair = True
            part.settings.hair_length = 0.15
            part.settings.render_type = 'OBJECT'

            bpy.ops.object.metaball_add(type='BALL')
            meta = bpy.context.active_object
            meta_name = bpy.context.active_object.name
            meta.scale = (0.1,0.1,0.1)
            part.settings.instance_object = meta
            part.settings.particle_size = 3
            bpy.ops.object.convert(target='MESH')

            new_name = meta_name+".001"
            meta = bpy.data.objects[new_name]

            #context.view_layer.objects.active = sO

            objs = bpy.data.objects
            objs.remove(objs[sO_name], do_unlink=True)

            #bpy.ops.object.delete()

            #context.view_layer.objects.active = meta

            #Try removing vertices here
            '''
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