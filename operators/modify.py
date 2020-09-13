import bpy
import bmesh
import random
from mathutils import Vector, Matrix
from bpy.props import *
from bpy.types import (Panel,Menu,Operator,PropertyGroup)
# //====================================================================//
#    < Operators >
# //====================================================================//
# Operator for modifying mesh from UI panel
class BYGEN_OT_Modify(bpy.types.Operator):
    bl_idname = "object.bygen_modify"
    bl_label = "Apply Style"
    bl_description = "Activate BY-GEN Modify"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):

        # Setting up context
        scene = context.scene
        bytool = scene.by_tool

        # Modification mode switching
        # Destructor mode
        if bytool.mode_modify=="MODE_DEST":
            # Begin modification procedure
            if len(bpy.context.selected_objects) > 0:
                sO = bpy.context.selected_objects[0]
                canGo = False

                if bytool.modAllow == True:
                    canGo = True
                else:
                    if len(sO.modifiers)==0:
                        canGo=True

                if canGo == True:
                    randID = random.randint(1,9999)
                    # Displacement
                    mod_displace = sO.modifiers.new("Displace", 'DISPLACE')
                    mod_displace.strength = 0.2 # 0.5
                    tempTex = bpy.data.textures.new("ByGen_TexID_"+str(randID), 'DISTORTED_NOISE')
                    mod_displace.texture = tempTex
                    tempTex = mod_displace.texture

                    # Clouds
                    if bytool.mode_mod_disp == "MODE_MD_CLOUDS":
                        tempTex.type="CLOUDS"
                    
                    # Distorted Noise
                    if bytool.mode_mod_disp == "MODE_MD_DISTNOISE":
                        tempTex.type="DISTORTED_NOISE"
                    
                    # Noise
                    if bytool.mode_mod_disp == "MODE_MD_NOISE":
                        tempTex.type="NOISE"
                    
                    # Marble
                    if bytool.mode_mod_disp == "MODE_MD_MARBLE":
                        tempTex.type="MARBLE"
                    
                    # Musgrave
                    if bytool.mode_mod_disp == "MODE_MD_MUSGRAVE":
                        tempTex.type='MUSGRAVE'
                    
                    # Stucci
                    if bytool.mode_mod_disp == "MODE_MD_STUCCI":
                        tempTex.type='STUCCI'
                    
                    # Voronoi
                    if bytool.mode_mod_disp == "MODE_MD_VORONOI":
                        tempTex.type='VORONOI'
                    
                    # Wood
                    if bytool.mode_mod_disp == "MODE_MD_WOOD":
                        tempTex.type='WOOD'

                    # Build
                    mod_build = sO.modifiers.new("Build", 'BUILD')
                    mod_build.use_random_order = True
                    mod_build.frame_start = 18

                    # Triangulate
                    # mod_triangulate = sO.modifiers.new("Triangulate", 'TRIANGULATE')

                    # Edge Split
                    mod_triangulate = sO.modifiers.new("Edge Split", 'EDGE_SPLIT')

                    # Maybe Subsurf
                    # mod_subsurf = sO.modifiers.new("Subsurf", 'SUBSURF')

                    # Smooth
                    mod_smooth = sO.modifiers.new("Smooth", 'SMOOTH')
                    mod_smooth.factor = 1.643

                    # Solidify
                    mod_solidify = sO.modifiers.new("Solidify", 'SOLIDIFY')
                    mod_solidify.thickness = 0.036
        
        # Hard Surface Faceted
        if bytool.mode_modify=="MODE_HSF":

            # Begin modification procedure
            if len(bpy.context.selected_objects) > 0:
                sO = bpy.context.selected_objects[0]
                canGo = False

                if bytool.modAllow == True:
                    canGo = True
                else:
                    if len(sO.modifiers)==0:
                        canGo=True

                if canGo == True:
                    
                    # Random ID
                    randID = random.randint(1,9999)

                    # We do not apply Subsurf to existing object as it should already have shape definition.
                    # Subsurf
                    # mod = sO.modifiers.new("Subsurface", 'SUBSURF')
                    # mod.levels = 4
                    # mod.render_levels = 4

                # Displace with switching
                    mod_displace = sO.modifiers.new("Displace", 'DISPLACE')
                    mod_displace.strength = -0.1
                    tempTex = bpy.data.textures.new("ByGen_TexID_"+str(randID), 'DISTORTED_NOISE')
                    mod_displace.texture = tempTex
                    tempTex = mod_displace.texture

                    # Clouds
                    if bytool.mode_mod_disp == "MODE_MD_CLOUDS":
                        tempTex.type="CLOUDS"
                    
                    # Distorted Noise
                    if bytool.mode_mod_disp == "MODE_MD_DISTNOISE":
                        tempTex.type="DISTORTED_NOISE"
                    
                    # Noise
                    if bytool.mode_mod_disp == "MODE_MD_NOISE":
                        tempTex.type="NOISE"
                    
                    # Marble
                    if bytool.mode_mod_disp == "MODE_MD_MARBLE":
                        tempTex.type="MARBLE"
                    
                    # Musgrave
                    if bytool.mode_mod_disp == "MODE_MD_MUSGRAVE":
                        tempTex.type='MUSGRAVE'
                    
                    # Stucci
                    if bytool.mode_mod_disp == "MODE_MD_STUCCI":
                        tempTex.type='STUCCI'
                    
                    # Voronoi
                    if bytool.mode_mod_disp == "MODE_MD_VORONOI":
                        tempTex.type='VORONOI'
                    
                    # Wood
                    if bytool.mode_mod_disp == "MODE_MD_WOOD":
                        tempTex.type='WOOD'
            
                    # Decimate 1
                    mod_decimate1 = sO.modifiers.new('Decimate1', 'DECIMATE')
                    mod_decimate1.decimate_type = 'COLLAPSE'
                    # mod_decimate1.ratio = 0.2
                    mod_decimate1.ratio = bytool.mod_decimate_collapse

                    # Decimate 2
                    mod_decimate2 = sO.modifiers.new('Decimate1', 'DECIMATE')
                    mod_decimate2.decimate_type = 'DISSOLVE' # COLLAPSE, UNSUBDIV, DISSOLVE (PLANAR)
                    # Set radian value for planar mode as float. 30 is 0.523599 / 10 is 0.174533
                    # mod_decimate2.angle_limit = 0.174533 
                    mod_decimate2.angle_limit = bytool.mod_decimate_angle
                    
                    # Triangulate
                    mod_triangulate = sO.modifiers.new('Triangulate', 'TRIANGULATE')

                    # Edge Split
                    mod_edgesplit = sO.modifiers.new('Edge Split', 'EDGE_SPLIT')
                    mod_edgesplit.split_angle = 0.261799

                    # Solidify
                    mod_solidify = sO.modifiers.new('Solidify', 'SOLIDIFY')
                    mod_solidify.thickness = -0.02

                    # Bevel
                    mod_bevel = sO.modifiers.new('Bevel', 'BEVEL')
                    mod_bevel.use_clamp_overlap = 1
                    mod_bevel.limit_method = 'ANGLE' # NONE, ANGLE, WEIGHT, VGROUP
                    mod_bevel.segments = 3

                    # Mirror
                    if bytool.mod_hsf_allow_mirror == True:
                        mod_mirror = sO.modifiers.new('Mirror', 'MIRROR')
                        mod_mirror.use_bisect_axis[0] = 1 # [0] is x, [1] is y, [2] is z || Regular Mirror is use_axis, Flip is use_bisect_flip_axis
        
        # Hard Surface Skin
        if bytool.mode_modify=="MODE_HSS":
            # Begin generation procedure
            if len(bpy.context.selected_objects) > 0:
                sO = bpy.context.selected_objects[0]
                canGo = False

                if bytool.modAllow == True:
                    canGo = True
                else:
                    if len(sO.modifiers)==0:
                        canGo=True

                if canGo == True:
                    # Adding modifiers
                    # Skin
                    mod_skin = sO.modifiers.new("Skin", "SKIN")
                    # Remesh
                    mod_remesh = sO.modifiers.new("Remesh", "REMESH")
                    mod_remesh.mode = "SMOOTH"
                    mod_remesh.octree_depth = 5
                    # Bevel1
                    mod_bevel = sO.modifiers.new("Bevel", "BEVEL")
                    mod_bevel.offset_type ="PERCENT"
                    mod_bevel.width_pct = 37
                    mod_bevel.affect = "VERTICES"
                    mod_bevel.show_in_editmode = False
                    # Decimate1
                    mod_decimate = sO.modifiers.new("Decimate", "DECIMATE")
                    mod_decimate.ratio = 0.0156
                    # Decimate2
                    mod_decimate2 = sO.modifiers.new("Decimate 2", "DECIMATE")
                    mod_decimate2.decimate_type = "DISSOLVE"
                    mod_decimate2.angle_limit = 0.087266
                    # Bevel 2
                    mod_bevel2 = sO.modifiers.new("Bevel 2", "BEVEL")
                    mod_bevel2.offset_type = "PERCENT"
                    mod_bevel2.width_pct = 33
                    mod_bevel2.affect = "VERTICES"
                    mod_bevel2.show_in_editmode = False
                    # Edge Split
                    mod_edge = sO.modifiers.new("Edge Split", "EDGE_SPLIT")
                    mod_edge.show_in_editmode = False
                    # Solidify
                    mod_solid = sO.modifiers.new("Solidify", "SOLIDIFY")
                    mod_solid.thickness = -0.04
                    mod_solid.use_rim_only = True
                    mod_solid.show_in_editmode = False
                    # Bevel 3
                    mod_bevel3 = sO.modifiers.new("Bevel 3", "BEVEL")
                    mod_bevel3.width = 0.053
                    mod_bevel3.show_in_editmode = False
                    # Mirror
                    if bytool.mod_hss_allow_mirror == True:
                        mod_mirror = sO.modifiers.new("Mirror", "MIRROR")
                        mod_mirror.use_bisect_axis[0] = 1
                        mod_mirror.show_in_editmode = False
                    # Displace
                    mod_displace = sO.modifiers.new("Displace", "DISPLACE")
                    mod_displace.strength = 0.025
                    mod_displace.show_in_editmode = False

        # Hard Padding
        if bytool.mode_modify=="MODE_HP":
            if len(bpy.context.selected_objects) > 0:
                sO = bpy.context.selected_objects[0]
                canGo = False

                if bytool.modAllow == True:
                    canGo = True
                else:
                    if len(sO.modifiers)==0:
                        canGo=True

                if canGo == True:
                    # Adding Modifiers
                    # Decimate
                    mod_decimate = sO.modifiers.new("Decimate", "DECIMATE")
                    mod_decimate.ratio = 1.0
                    # Triangulate
                    if bytool.mod_hp_allow_triangulate == True:
                        mod_triangulate = sO.modifiers.new("Triangualate", "TRIANGULATE")
                    # Edge Split
                    mod_edge = sO.modifiers.new("Edge Split", "EDGE_SPLIT")
                    mod_edge.use_edge_angle = True
                    mod_edge.split_angle = 0
                    # Solidify
                    mod_solid = sO.modifiers.new("Solidify", "SOLIDIFY")
                    mod_solid.thickness = -0.05
                    # Bevel
                    mod_bevel = sO.modifiers.new("Bevel", "BEVEL")
                    mod_bevel.width = 0.01
                    mod_bevel.segments = 3
                    mod_bevel.use_clamp_overlap = True
                    mod_bevel.limit_method = "NONE"

        # Metal Shell
        if bytool.mode_modify=="MODE_MSHELL":
            # Beginning modification procedure
            if len(bpy.context.selected_objects) > 0:
                sO = bpy.context.selected_objects[0]
                canGo = False

                if bytool.modAllow == True:
                    canGo = True
                else:
                    if len(sO.modifiers)==0:
                        canGo=True

                if canGo == True:
                    randID = random.randint(1,9999)
                    # Triangulate
                    if bytool.mod_mshell_allow_triangulate:
                        mod_triangulate = sO.modifiers.new('Triangulate', 'TRIANGULATE')
                    # Wireframe
                    mod_wireframe = sO.modifiers.new('Wireframe', 'WIREFRAME')
                    mod_wireframe.thickness = 0.03
                    mod_wireframe.use_boundary = True
                    # Bevel
                    mod_bevel = sO.modifiers.new('Bevel', 'BEVEL')
        
        # Organic Shell
        if bytool.mode_modify=="MODE_OSHELL":
            # Beginning modification procedure
            if len(bpy.context.selected_objects) > 0:
                sO = bpy.context.selected_objects[0]
                canGo = False

                if bytool.modAllow == True:
                    canGo = True
                else:
                    if len(sO.modifiers)==0:
                        canGo=True

                if canGo == True:
                    # Random ID
                    randID = random.randint(1,9999)
                    # We do not apply Subsurf to existing object as it should already have shape definition.
                    # Subsurf
                    # mod = sO.modifiers.new("Subsurface", 'SUBSURF')
                    # mod.levels = 4
                    # mod.render_levels = 4
                    bpy.ops.object.shade_smooth()

                # Displace with switching
                    mod_displace = sO.modifiers.new("Displace", 'DISPLACE')
                    mod_displace.strength = 0.6
                    tempTex = bpy.data.textures.new("ByGen_TexID_"+str(randID), 'DISTORTED_NOISE')
                    mod_displace.texture = tempTex
                    tempTex = mod_displace.texture

                    # Clouds
                    if bytool.mode_mod_disp == "MODE_MD_CLOUDS":
                        tempTex.type="CLOUDS"
                    
                    # Distorted Noise
                    if bytool.mode_mod_disp == "MODE_MD_DISTNOISE":
                        tempTex.type="DISTORTED_NOISE"
                    
                    # Noise
                    if bytool.mode_mod_disp == "MODE_MD_NOISE":
                        tempTex.type="NOISE"
                    
                    # Marble
                    if bytool.mode_mod_disp == "MODE_MD_MARBLE":
                        tempTex.type="MARBLE"
                    
                    # Musgrave
                    if bytool.mode_mod_disp == "MODE_MD_MUSGRAVE":
                        tempTex.type='MUSGRAVE'
                    
                    # Stucci
                    if bytool.mode_mod_disp == "MODE_MD_STUCCI":
                        tempTex.type='STUCCI'
                    
                    # Voronoi
                    if bytool.mode_mod_disp == "MODE_MD_VORONOI":
                        tempTex.type='VORONOI'
                    
                    # Wood
                    if bytool.mode_mod_disp == "MODE_MD_WOOD":
                        tempTex.type='WOOD'
            
                    # Decimate 2
                    mod_decimate2 = sO.modifiers.new('Decimate2', 'DECIMATE')
                    mod_decimate2.decimate_type = 'DISSOLVE' # COLLAPSE, UNSUBDIV, DISSOLVE (PLANAR)
                    # Set radian value for planar mode as float. 30 is 0.523599 / 10 is 0.174533
                    # mod_decimate2.angle_limit = 0.174533 
                    mod_decimate2.angle_limit = bytool.mod_decimate_angle #0.349066 recommended
                    mod_decimate2.use_dissolve_boundaries = True
                    
                    # Smooth
                    mod_smooth = sO.modifiers.new('Smooth', 'SMOOTH')
                    mod_smooth.factor = 0.5
                    mod_smooth.iterations = 15
                    
                    # Triangulate
                    if bytool.mod_oshell_allow_triangulate:
                        mod_triangulate = sO.modifiers.new('Triangulate', 'TRIANGULATE')
                    
                    # Wireframe
                    mod_wireframe = sO.modifiers.new('Wireframe', 'WIREFRAME')
                    mod_wireframe.thickness = 0.05
                    
                    # Subsurf
                    mod_subd = sO.modifiers.new("SubD", "SUBSURF")
                    mod_subd.levels = 2
                    mod_subd.render_levels = 2

        # Midge Cell
        if bytool.mode_modify=="MODE_MIDGE_CELL":
            # Begin modification procedure
            if len(bpy.context.selected_objects) > 0:
                sO = bpy.context.selected_objects[0]
                canGo = False

                if bytool.modAllow == True:
                    canGo = True
                else:
                    if len(sO.modifiers)==0:
                        canGo=True

                if canGo == True:
                    # Random ID
                    randID = random.randint(1,9999)

                    # Subsurf
                    # mod = sO.modifiers.new("Subsurface", 'SUBSURF')
                    # mod.levels = 5
                    # mod.render_levels = 5

                    # Subsurf
                    mod_subd = sO.modifiers.new('Subsurface', 'SUBSURF')
                    mod_subd.subdivision_type = "SIMPLE"
                    mod_subd.levels = 2
                    mod_subd.render_levels = 2

                    # Edge Split
                    mod_edgesplit = sO.modifiers.new('Edge Split', 'EDGE_SPLIT')
                    mod_edgesplit.split_angle = 0.261799

                    # Displace
                    mod_displace = sO.modifiers.new("Displace", 'DISPLACE')
                    mod_displace.strength = 1.0

                    # Creating texture
                    tempTex = bpy.data.textures.new("ByGen_TexID_"+str(randID), "DISTORTED_NOISE")
                    mod_displace.texture = tempTex
                    tempTex.distortion = 1.0
                    tempTex.noise_scale = 0.85
                    tempTex.nabla = 0.03
                    tempTex.noise_basis = "CELL_NOISE"
                    tempTex.noise_distortion = "CELL_NOISE"
            
                    # Remesh
                    mod_remesh = sO.modifiers.new("Remesh", "REMESH")
                    mod_remesh.mode = "BLOCKS"
                    mod_remesh.octree_depth = 4
                    mod_remesh.scale = 0.9

                    # Decimate 1
                    mod_decimate = sO.modifiers.new('Decimate1', 'DECIMATE')
                    mod_decimate.decimate_type = 'DISSOLVE'
                    mod_decimate.angle_limit = 0.087266

                    # Wireframe
                    mod_wireframe = sO.modifiers.new('Wireframe', 'WIREFRAME')
                    mod_wireframe.thickness = 0.02
                    mod_wireframe.use_even_offset = False

        # Point Cloud
        if bytool.mode_modify=="MODE_PC":
            if len(bpy.context.selected_objects) > 0:
                sO = bpy.context.selected_objects[0]
                canGo = False

                if bytool.modAllow == True:
                    canGo = True
                else:
                    if len(sO.modifiers)==0:
                        canGo=True

                if canGo == True:
                    randID = random.randint(1,9999)

                    # Creating emissive material
                    if bytool.mod_pc_create_material == True:
                        mat = bpy.data.materials.new(name = "PointEmis_"+str(randID))
                        sO.data.materials.append(mat)
                        mat.use_nodes = True
                        nodes = mat.node_tree.nodes
                        material_output = nodes.get("Material Output")
                        node_emission = nodes.new(type='ShaderNodeEmission')
                        node_emission.inputs[0].default_value = (0.0,0.3,1.0,1) # color
                        node_emission.inputs[1].default_value = 1000.0 # strength
                        links = mat.node_tree.links
                        link = links.new(node_emission.outputs[0], material_output.inputs[0])

                    # Adding Modifiers
                    # Displace
                    mod_displace = sO.modifiers.new("Displace", "DISPLACE")
                    mod_displace.strength = 0.050
                    mod_displace.texture_coords = "OBJECT"
                    tempTex = bpy.data.textures.new("ByGen_TexID_"+str(randID), 'MUSGRAVE')
                    mod_displace.texture = tempTex
                    tempTex = mod_displace.texture
                    
                    # Edge Split
                    mod_edge = sO.modifiers.new("Edge Split", "EDGE_SPLIT")
                    mod_edge.use_edge_angle = True
                    mod_edge.split_angle = 0
                    
                    # Smooth
                    mod_smooth = sO.modifiers.new("Smooth", "SMOOTH")
                    mod_smooth.factor = 2.15
                    mod_smooth.iterations = 1
                    
                    # Bevel
                    mod_bevel = sO.modifiers.new("Bevel", "BEVEL")
                    mod_bevel.offset_type = "PERCENT"
                    mod_bevel.width_pct = 100
                    mod_bevel.use_only_vertices = True
                    
                    # Displace 2
                    mod_displace2 = sO.modifiers.new("Displace", "DISPLACE")
                    mod_displace2.strength = 0.1
                    mod_displace2.texture_coords = "OBJECT"
                    mod_displace2.texture = tempTex

        # Pixelate
        if bytool.mode_modify=="MODE_PIX":
            if len(bpy.context.selected_objects) > 0:
                sO = bpy.context.selected_objects[0]
                canGo = False

                if bytool.modAllow == True:
                    canGo = True
                else:
                    if len(sO.modifiers)==0:
                        canGo=True

                if canGo == True:
                    randID = random.randint(1,9999)
                    
                    # Subsurf
                    '''
                    mod = sO.modifiers.new("Subsurface", 'SUBSURF')
                    mod.levels = 4
                    mod.render_levels = 4
                    mod.show_in_editmode = False
                    '''

                    # Build
                    mod_build = sO.modifiers.new("Build", 'BUILD')
                    mod_build.frame_start = -20
                    mod_build.use_random_order = True
                    
                    # Bevel
                    mod_bevel = sO.modifiers.new("Bevel", 'BEVEL')
                    mod_bevel.width = 1
                    mod_bevel.use_only_vertices = True
                    mod_bevel.use_clamp_overlap = True
                    mod_bevel.segments = 3
                    
                    # Solidify
                    mod_solid = sO.modifiers.new("Solidify", 'SOLIDIFY')
                    mod_solid = -0.03

        return {'FINISHED'}