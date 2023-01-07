#region Imports
import bpy
from bpy.props import *
from bpy.types import (Panel,StringProperty, EnumProperty,Menu,Operator,PropertyGroup,Scene, WindowManager)
from bpy.app.handlers import persistent
import bpy.utils.previews
import os
import random
from . modules.easybpy import *
#endregion
#region Useful Variables
preview_collections = {}
#endregion
#region Useful Functions
def alistdir(directory):
    '''
    'Alternative / Avoidance List Dir'
    An alternative version of os.listdir function that ignores files beginning
    with a '.', specifically aimed at preventing .DS_Store files on MacOS from 
    disrupting the import process of content packs. Introduced with 9.1.1.
    '''
    filelist = os.listdir(directory)
    return [x for x in filelist if not (x.startswith('.'))]
#endregion

#region PREOPERATION FUNCTIONS
def generate_ambient_occlusion_group(target, group_name):
    # Set up the AO baking process.
    select_only(target)
    bpy.ops.mesh.vertex_color_add()
    vc = target.data.vertex_colors[-1]
    vc.name = group_name
    bpy.context.scene.cycles.bake_type = 'AO'
    bpy.context.scene.render.bake.target = 'VERTEX_COLORS'
    bpy.ops.object.bake(type='AO')
    # Prepare the weight group.
    bpy.ops.object.vertex_group_add()
    vertex_group = target.vertex_groups[-1]
    vertex_group.name = group_name
    vertex_colors = vc.data
    # Construct the weight group.
    colors = {}
    corners = {}
    for loop in target.data.loops:
        vi = loop.vertex_index
        if vi not in colors:
            colors[vi] = Vector(vertex_colors[loop.index].color[:3])
            corners[vi] = 1.0
        else:
            colors[vi] += Vector(vertex_colors[loop.index].color[:3])
            corners[vi]+=1.0
    for vindex in colors:
        vertex_group.add([vindex], sum(colors[vindex]/corners[vindex])/3.0, 'REPLACE')
    return vertex_group
class BYGEN_OT_groupmask_ambient_occlusion(bpy.types.Operator):
    bl_idname = "object.bygen_groupmask_ambient_occlusion"
    bl_label = "Generate AO Group Mask"
    bl_description = "Generates an AO mask group on the selected object"
    bl_options = {'REGISTER','UNDO'}

    def execute(self, context):
        generate_ambient_occlusion_group(ao(),"Ambient Occlusion")
        return{'FINISHED'}
#endregion

#region SURFACE EFFECTS 
def content_packs_se_from_directory(self, context):
    wm = context.window_manager
    enum_items = []
    if context is None:
        return enum_items

    #directory = "content_packs"
    directory = os.path.abspath(os.path.join(os.path.dirname(__file__), 'content_packs'))

    #pcoll = preview_collections["categories"]
    if directory and os.path.exists(directory):
        # Scan directory for folders
        pack_paths = alistdir(directory)
        for p in pack_paths:
            #--- Folder Check
            cpack = os.path.abspath(os.path.join(os.path.dirname(__file__), 'content_packs', p))
            folders = alistdir(cpack)
            if 'thumbnails_surface_effects' in folders:
                enum_items.append((p, p, 'Content Pack'))
            #---
    return enum_items
def get_surface_effect_thumbnails(self, context):
    enum_items = []
    #if context is None:
    #    return enum_items
    wm = context.window_manager

    #directory = wm.surface_effects_dir
    #directory = "content_packs\\"+wm.content_packs_se+"\\thumbnails_surface_effects"
    directory = os.path.abspath(os.path.join(os.path.dirname(__file__), 'content_packs', wm.content_packs_se, 'thumbnails_surface_effects'))

    # Get collection defined in register function
    pcoll = preview_collections["main"]

    if directory == pcoll.surface_effects_dir:
        print(">>> SE DIRECTORY ALREADY")
        return pcoll.surface_effects

    #print("Scanning directory %s" % directory)
    if directory and os.path.exists(directory):
        # Scan directory for jpg files
        image_paths = []
        for fn in alistdir(directory):
            if fn.lower().endswith(".jpg"):
                image_paths.append(fn)
        
        for i, name in enumerate(image_paths):
            # Generate a thumbnail preview for a file.
            filepath = os.path.join(directory, name)
            icon = pcoll.get(name)
            if not icon:
                thumb = pcoll.load(name, filepath, 'IMAGE')
            else:
                thumb = pcoll[name]
            trimname = name.split('.')
            #enum_items.append((name, name, "", thumb.icon_id, i))
            enum_items.append((trimname[0], trimname[0], "", thumb.icon_id, i))
    
    pcoll.surface_effects = enum_items
    pcoll.surface_effects_dir = directory
    return pcoll.surface_effects
class BYGEN_OT_surface_effect_import(bpy.types.Operator):
    bl_idname = "object.bygen_surface_effect_import"
    bl_label = "Import Surface Effect"
    bl_description = "Imports and adds the selected surface effect."
    bl_options = {'REGISTER','UNDO'}

    def execute(self, context):
        # Setting up context
        scene = context.scene
        bytool = scene.by_tool
        wm = context.window_manager
            
        # Beginning procedure:
        if len(bpy.context.selected_objects) > 0:
            objs = selected_objects()

            # Getting all useful directories for obtaining data (objects, node trees, etc.) from the content packs.
            directory = os.path.abspath(os.path.join(os.path.dirname(__file__), 'content_packs', wm.content_packs_se, wm.content_packs_se+'.blend'))
            colpath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'content_packs', wm.content_packs_se, wm.content_packs_se+'.blend/Collection/')) #\\Collection\\
            colname = wm.surface_effects
            treepath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'content_packs', wm.content_packs_se, wm.content_packs_se+'.blend/NodeTree/')) #\\NodeTree\\
            treename = wm.surface_effects

            # Find blend file with same name as folder (wm.content_packs_se+'.blend')
            if directory and os.path.exists(directory):
                
                # Checking to see if the surface effect is a single/simple type (no collection to import).
                if wm.surface_effects.startswith("(S)"):
                    '''
                    This is an (S) type effect, meaning there is no collection to import.
                    This means we can go straight to the importing of the geo nodes tree
                    and assign it to the object/s.
                    '''
                    for o in objs:

                            # Import geo tree from content pack
                            bpy.ops.wm.append(filename = treename, directory = treepath)

                            # Get the imported tree by name (store in surface_tree)
                            surface_tree = bpy.data.node_groups[treename]

                            # Add geonodes modifier to object (store in geomod)
                            geomod = o.modifiers.new("Geometry Nodes", "NODES")

                            # Assign new surface_effect geonode tree to new geomod
                            geomod.node_group = surface_tree

                            # Change surface_tree name to 'objname_treename_randID'
                            randID = random.randint(1,9999)
                            surface_tree.name = o.name+"_"+treename+"_"+str(randID)

                            # Open the surface tree nodes
                            nodes = surface_tree.nodes

                            # Loop through all properties and check to see if any need to be pre-calculated.
                            #  Maps need to be calculated without the geo nodes modifier
                            #get_ao = False
                            #reset = False
                            geomod.show_viewport = False
                            geomod.show_render = False
                            geomod.show_in_editmode = False
                            ginput = get_node(nodes, "Group Input")
                            for go in ginput.outputs:
                                if go.name.lower() == "(c) ambient occlusion":
                                    #get_ao = True
                                    #reset = True

                                    id = go.identifier
                                    id_prop_path = "[\""+id+"_use_attribute\"]"
                                    id_prop_name = id+"_attribute_name"

                                    # Create the ambient occlusion mask as a vertex (weight) group.
                                    ao_group = generate_ambient_occlusion_group(o, "Ambient Occlusion Group")

                                    # Toggle the property so it becomes an attribute input
                                    bpy.ops.object.geometry_nodes_input_attribute_toggle(prop_path=id_prop_path, modifier_name=geomod.name)
                                    # Give the attribute property the appropriate name
                                    geomod[id_prop_name] = "Ambient Occlusion Group"

                            geomod.show_viewport = True
                            geomod.show_render = True
                            geomod.show_in_editmode = True

                else:
                    '''
                    This is not an (S) type effect, meaning there is a collection to import.
                    Collection name should be wm.surface_effects (full path colpath).
                    We will need to import the necessary collection content before importing
                    the geometry nodes tree and assigning everything to the selected object/s.
                    '''
                    # Collection
                    col = None

                    # If the user wants to create a unique collection.
                    if bytool.se_unique_collection: 
                        # Append collection to file (store ref in col) <- (optional: link)
                        bpy.ops.wm.append(filename = colname, directory = colpath)
                        col = get_collection(wm.surface_effects)

                    # Else: The user does not want to create a unique collection.
                    else:

                        # If the collection already exists in the blend file.
                        if collection_exists(wm.surface_effects):
                            # Let's grab the collection.
                            col = get_collection(wm.surface_effects)

                        # Else: The collection does not already exist in the blend file.
                        else:
                            # Let's create the collection.
                            bpy.ops.wm.append(filename = colname, directory = colpath)
                            col = get_collection(wm.surface_effects)
                        
                    if col:
                        for o in objs:

                            # Import geo tree from content pack
                            bpy.ops.wm.append(filename = treename, directory = treepath)

                            # Get the imported tree by name (store in surface_tree)
                            surface_tree = bpy.data.node_groups[treename]

                            # Add geonodes modifier to object (store in geomod)
                            geomod = o.modifiers.new("Geometry Nodes", "NODES")

                            # Assign new surface_effect geonode tree to new geomod
                            geomod.node_group = surface_tree

                            # Change surface_tree name to 'objname_treename_randID'
                            randID = random.randint(1,9999)
                            surface_tree.name = o.name+"_"+treename+"_"+str(randID)

                            # Open surface tree nodes
                            nodes = surface_tree.nodes

                            # Put col in correct node (collection info node)
                            colinfo = get_node(nodes, "Collection Info")
                            colinfo.inputs[0].default_value = col
            else:
                print(wm.content_packs_se + " - pack file does not exist.")
        return {'FINISHED'}
class BYGEN_OT_surface_effect_weight_paint(bpy.types.Operator):
    bl_idname = "object.bygen_surface_effect_weight_paint"
    bl_label = "Apply (Vertex Paint)"
    bl_description = "Imports the effect and sets it up for vertex painting."
    bl_options = {'REGISTER','UNDO'}

    def execute(self, context):
        # Setting up context
        scene = context.scene
        bytool = scene.by_tool
        wm = context.window_manager
            
        # Beginning procedure:
        if bpy.context.active_object != None:
            o = ao()

            # Getting all useful directories for obtaining data (objects, node trees, etc.) from the content packs.
            directory = os.path.abspath(os.path.join(os.path.dirname(__file__), 'content_packs', wm.content_packs_se, wm.content_packs_se+'.blend'))
            colpath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'content_packs', wm.content_packs_se, wm.content_packs_se+'.blend/Collection/')) #\\Collection\\
            colname = wm.surface_effects
            treepath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'content_packs', wm.content_packs_se, wm.content_packs_se+'.blend/NodeTree/')) #\\NodeTree\\
            treename = wm.surface_effects

            # Find blend file with same name as folder (wm.content_packs_se+'.blend')
            if directory and os.path.exists(directory):
                # Checking to see if the surface effect is a single/simple type (no collection to import).
                if wm.surface_effects.startswith("(S)"):
                    '''
                    This is an (S) type effect, meaning there is no collection to import.
                    This means we can go straight to the importing of the geo nodes tree
                    and assign it to the object before setting up the weight input.
                    '''
                    # Import geo tree from content pack
                    bpy.ops.wm.append(filename = treename, directory = treepath)

                    # Get the imported tree by name (store in surface_tree)
                    surface_tree = bpy.data.node_groups[treename]

                    # Add geonodes modifier to object (store in geomod)
                    geomod = o.modifiers.new("Geometry Nodes", "NODES")

                    # Assign new surface_effect geonode tree to new geomod
                    geomod.node_group = surface_tree

                    # Open surface tree nodes
                    nodes = surface_tree.nodes

                    # Do weight paint stuff here
                    select_only(o)
                    bpy.ops.object.vertex_group_add()
                    group = o.vertex_groups[-1]
                    group.name = wm.surface_effects

                    # Get the correct input for the attribute toggle
                    id = ""
                    ginput = get_node(nodes, "Group Input")
                    for o in ginput.outputs:
                        if o.name.lower() == "weight":
                            id = o.identifier
                    id_prop_path = "[\""+id+"_use_attribute\"]"
                    id_prop_name = id+"_attribute_name"
                    bpy.ops.object.geometry_nodes_input_attribute_toggle(prop_path=id_prop_path, modifier_name=geomod.name)
                    geomod[id_prop_name] = group.name

                    # Change surface_tree name to 'objname_treename_randID'
                    randID = random.randint(1,9999)
                    surface_tree.name = o.name+"_"+treename+"_"+str(randID)

                    # Set mode to weight paint
                    bpy.ops.object.mode_set(mode="WEIGHT_PAINT")
                    
                else:
                    '''
                    This is not an (S) type effect, meaning there is a collection to import.
                    Collection name should be wm.surface_effects (full path colpath).
                    We will need to import the necessary collection content before importing
                    the geometry nodes tree and assigning everything to the selected object.
                    The weight input will be set up after this.
                    '''
                    # Collection
                    col = None

                    # If the user wants to create a unique collection.
                    if bytool.se_unique_collection:
                        # Append collection to file (store ref in col) <- (optional: link)
                        bpy.ops.wm.append(filename = colname, directory = colpath)
                        col = get_collection(wm.surface_effects)

                    # Else: The user does not want to create a unique collection.
                    else:

                        # If the collection already exists in the blend file.
                        if collection_exists(wm.surface_effects):
                            # Let's grab the collection.
                            col = get_collection(wm.surface_effects)

                        # Else: The collection does not already exist in the blend file.
                        else:
                            # Let's create the collection.
                            bpy.ops.wm.append(filename = colname, directory = colpath)
                            col = get_collection(wm.surface_effects)
                        

                    if col:
                        # Import geo tree from content pack
                        bpy.ops.wm.append(filename = treename, directory = treepath)

                        # Get the imported tree by name (store in surface_tree)
                        surface_tree = bpy.data.node_groups[treename]

                        # Add geonodes modifier to object (store in geomod)
                        geomod = o.modifiers.new("Geometry Nodes", "NODES")

                        # Assign new surface_effect geonode tree to new geomod
                        geomod.node_group = surface_tree

                        # Open surface tree nodes
                        nodes = surface_tree.nodes

                        # Do weight paint stuff here
                        select_only(o)
                        bpy.ops.object.vertex_group_add()
                        group = o.vertex_groups[-1]
                        group.name = wm.surface_effects

                        # Get the correct input for the attribute toggle
                        id = ""
                        ginput = get_node(nodes, "Group Input")
                        for o in ginput.outputs:
                            if o.name.lower() == "weight":
                                id = o.identifier
                        id_prop_path = "[\""+id+"_use_attribute\"]"
                        id_prop_name = id+"_attribute_name"
                        bpy.ops.object.geometry_nodes_input_attribute_toggle(prop_path=id_prop_path, modifier_name=geomod.name)
                        geomod[id_prop_name] = group.name

                        # Change surface_tree name to 'objname_treename_randID'
                        randID = random.randint(1,9999)
                        surface_tree.name = o.name+"_"+treename+"_"+str(randID)

                        # Put col in correct node (collection info node)
                        colinfo = get_node(nodes, "Collection Info")
                        colinfo.inputs[0].default_value = col

                        # Set mode to weight paint
                        bpy.ops.object.mode_set(mode="WEIGHT_PAINT")
            else:
                print(wm.content_packs_se + " - pack file does not exist.")
        return {'FINISHED'}   
class BYGEN_OT_refresh_effect_properties(bpy.types.Operator):
    bl_idname = "object.bygen_refresh_effect_properties"
    bl_label = "Refresh Effect Properties"
    bl_description = "Refreshes the effect properties"

    def execute(self, context):
        thumbnail_update_call(self, context)
        return {'FINISHED'}
class BYGEN_PT_SurfaceEffects(Panel):
    bl_idname = "BYGEN_PT_SurfaceEffects"
    bl_label = "Surface Effects"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BY-GEN"

    def draw_header(self, context):
        self.layout.label(text = "", icon = "PARTICLE_POINT")
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        bytool = scene.by_tool
        wm = context.window_manager

        column = layout.column()
        row = column.row()
        #row.scale_y = 1.2
        row.prop(wm, "content_packs_se", text = "")
        row.operator("wm.url_open", text="", icon='FILEBROWSER').url = os.path.abspath(os.path.join(os.path.dirname(__file__), 'content_packs'))
        row.operator("wm.url_open", text="", icon='URL').url = "https://curtisholt.online/by-gen"
        row.operator("object.bygen_refresh_effect_properties", text="", icon='FILE_REFRESH')

        # Displaying the thumbnail selection window:
        row = layout.row()
        row.template_icon_view(wm, "surface_effects", show_labels=True, scale=8, scale_popup=8)
        
        box = layout.box()
        col = box.column()

        #row = layout.row()
        colrow = col.row(align=True)
        colrow.operator("object.bygen_surface_effect_import", text = "Apply to Selected")
        colrow = col.row(align=True)
        colrow.operator("object.bygen_surface_effect_weight_paint", text = "Apply (Weight Paint)")#, icon = "MOD_VERTEX_WEIGHT"
        colrow = col.row(align=True)
        colrow.prop(bytool, "se_unique_collection")
class BYGEN_PT_SurfaceHelperTools(Panel):
    bl_idname = "BYGEN_PT_SurfaceHelperTools"
    bl_label = "Helper Tools"
    bl_parent_id = "BYGEN_PT_SurfaceEffects"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BY-GEN"

    def draw_header(self, context):
        self.layout.label(text = "", icon = "TOOL_SETTINGS")

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        bytool = scene.by_tool

        box = layout.box()

        col = box.column()
        colrow = col.row(align=True)
        colrow.label(text = "Vertex Group Operations")
        colrow = col.row(align=True)
        colrow.operator("object.vertex_group_assign_new", text = "Vertex Group from Selected")
        colrow = col.row(align=True)
        colrow.label(text = "Vertex Group Masks")
        colrow = col.row(align=True)
        colrow.operator("object.bygen_groupmask_ambient_occlusion", text = "Ambient Occlusion")
#endregion

#region MESH EFFECTS
#region Mesh Panel
class BYGEN_PT_MeshEffects(Panel):
    bl_idname = "BYGEN_PT_MeshEffects"
    bl_label = "Mesh Effects"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BY-GEN"

    def draw_header(self, context):
        self.layout.label(text = "", icon = "MESH_DATA")
    def draw(self, context):
        layout = self.layout
#endregion
#region Mesh Legacy
class BYGEN_PT_ModifierStyles(Panel):
    bl_idname = "BYGEN_PT_ModifierStyles"
    bl_label = "Modifier Styles"
    bl_parent_id = "BYGEN_PT_MeshEffects"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BY-GEN"

    def draw_header(self, context):
        self.layout.label(text = "", icon = "MODIFIER")

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        bytool = scene.by_tool

        box = layout.box()

        col = box.column()
        colrow = col.row(align=True)
        colrow.prop(bytool, "modAllow")
        colrow = col.row(align=True)
        colrow.label(text="Modify Mode")
        colrow = col.row(align=True)
        colrow.prop(bytool, "mode_modify", text="")

        if bytool.mode_modify == "MODE_DEST":
            colrow = col.row(align=True)
            colrow.separator()
            colrow = col.row(align=True)
            colrow.label(text="Displacement Type")
            colrow = col.row(align=True)
            colrow.prop(bytool, "mode_mod_disp", text="")

        if bytool.mode_modify == "MODE_HSFRAME":
            colrow = col.row(align = True)
            colrow.prop(bytool, "mod_hssolid_allow_mirror")
            colrow = col.row(align = True)
            colrow.operator("object.bygen_invert_solidify")

        if bytool.mode_modify == "MODE_HSF":
            colrow = col.row(align=True)
            colrow.separator()
            colrow = col.row(align=True)
            colrow.label(text="Displacement Type")
            colrow = col.row(align=True)
            colrow.prop(bytool, "mode_mod_disp", text="")
            colrow = col.row(align=True)
            colrow.prop(bytool, "mod_decimate_collapse", text="Decimate Collapse")
            colrow = col.row(align=True)
            colrow.prop(bytool, "mod_decimate_angle", text="Decimate Angle")
            colrow = col.row(align=True)
            colrow.prop(bytool, "mod_hsf_allow_mirror", text="Mirror")

        if bytool.mode_modify == "MODE_HSS":
            colrow = col.row(align=True)
            colrow.separator()
            colrow = col.row(align=True)
            colrow.prop(bytool, "mod_hss_allow_mirror", text="Mirror")

        if bytool.mode_modify == "MODE_HP":
            colrow = col.row(align=True)
            colrow.separator()
            colrow = col.row(align=True)
            colrow.prop(bytool, "mod_hp_allow_triangulate", text="Triangulate")

        if bytool.mode_modify == "MODE_MSHELL":
            colrow = col.row(align=True)
            colrow.separator()
            colrow = col.row(align=True)
            colrow.prop(bytool, "mod_mshell_allow_triangulate", text = "Triangulate")

        if bytool.mode_modify == "MODE_OSHELL":
            colrow = col.row(align=True)
            colrow.separator()
            colrow = col.row(align=True)
            colrow.prop(bytool, "mod_oshell_allow_triangulate", text="Triangulate")
            colrow = col.row(align=True)
            colrow.label(text="Displacement Type")
            colrow = col.row(align=True)
            colrow.prop(bytool, "mode_mod_disp", text="")
            colrow = col.row(align=True)
            colrow.prop(bytool, "mod_decimate_angle", text="Decimate Angle")

        if bytool.mode_modify == "MODE_PC":
            colrow = col.row(align=True)
            colrow.separator()
            colrow = col.row(align=True)
            colrow.prop(bytool, "mod_pc_create_material", text="Create Emissive Mat")

        colrow = col.row(align=True)
        colrow.separator()
        colrow = col.row(align=True)
        colrow.operator("object.bygen_modify")
        colrow = col.row(align=True)
        colrow.separator()
#endregion
#region Mesh Parametric
def content_packs_mp_from_directory(self, context):
    wm = context.window_manager
    enum_items = []
    if context is None:
        return enum_items

    directory = os.path.abspath(os.path.join(os.path.dirname(__file__), 'content_packs'))

    if directory and os.path.exists(directory):
        # Scan directory for folders
        pack_paths = alistdir(directory)
        for p in pack_paths:
            #--- Folder Check
            cpack = os.path.abspath(os.path.join(os.path.dirname(__file__), 'content_packs', p))
            folders = alistdir(cpack)
            if 'thumbnails_mesh_parametric' in folders:
                enum_items.append((p, p, 'Content Pack'))
            #---
    return enum_items
def get_mesh_parametric_thumbnails(self, context):
    enum_items = []
    wm = context.window_manager

    directory = os.path.abspath(os.path.join(os.path.dirname(__file__), 'content_packs', wm.content_packs_mp, 'thumbnails_mesh_parametric'))

    # Get collection defined in register function
    pcoll = preview_collections["main"]

    if directory == pcoll.mesh_parametric_effects_dir:
        print(">>> MD DIRECTORY ALREADY")
        return pcoll.mesh_parametric_effects

    if directory and os.path.exists(directory):
        # Scan directory for jpg files
        image_paths = []
        for fn in alistdir(directory):
            if fn.lower().endswith(".jpg"):
                image_paths.append(fn)
        
        for i, name in enumerate(image_paths):
            # Generate a thumbnail preview for a file.
            filepath = os.path.join(directory, name)
            icon = pcoll.get(name)
            if not icon:
                thumb = pcoll.load(name, filepath, 'IMAGE')
            else:
                thumb = pcoll[name]
            trimname = name.split('.')
            enum_items.append((trimname[0], trimname[0], "", thumb.icon_id, i))

    pcoll.mesh_parametric_effects = enum_items
    pcoll.mesh_parametric_effects_dir = directory
    return pcoll.mesh_parametric_effects
class BYGEN_OT_mesh_parametric_import(bpy.types.Operator):
    bl_idname = "object.bygen_mesh_parametric_import"
    bl_label = "Import Parametric Mesh Effect"
    bl_description = "Imports and adds the selected parametric mesh effect"
    bl_options = {'REGISTER','UNDO'}

    def execute(self, context):
        # Setting up context
        scene = context.scene
        bytool = scene.by_tool
        wm = context.window_manager

        if bpy.context.active_object != None:
            
            # Beginning procedure:
            directory = os.path.abspath(os.path.join(os.path.dirname(__file__), 'content_packs', wm.content_packs_mp, wm.content_packs_mp+'.blend'))
            objpath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'content_packs', wm.content_packs_mp, wm.content_packs_mp+'.blend/Object/')) #\\Object\\
            objname = wm.mesh_parametric_effects
            
            if directory and os.path.exists(directory):
                if wm.mesh_parametric_effects.startswith("(G)"):
                    # Complex geo nodes stacks which require extra base referencing
                    # Assume base object is selected and make a copy.
                    base = ao()
                    new = copy_object(base)
                    select_only(new)

                    # Append the template object
                    ret = bpy.ops.wm.append(filename = objname, directory = objpath)
                    template = bpy.context.selected_objects[-1]

                    # Select the object with moodifier stack.
                    select_only(new)
                    select_object(template) # <- Active selection

                    # Copy over modifiers from template.
                    bpy.ops.object.make_links_data(type='MODIFIERS')

                    # Set active back to base
                    select_only(new)

                    # Loop modifiers to find geometry nodes:
                    #for m in template.modifiers:
                    for m in new.modifiers:
                        # Get geo node modifiers
                        if m.type == "NODES":
                            nodes = m.node_group.nodes

                            ''' - Assigning the object reference
                            for n in nodes:
                                if n.type == "OBJECT_INFO":
                                    # Set all object references to base
                                    n.inputs[0].default_value = base
                            '''
                            # Using the modifier input method.
                            id = ""
                            ginput = get_node(nodes, "Group Input")
                            for o in ginput.outputs:
                                if o.name.lower() == "object":
                                    id = o.identifier #Input_3 for example
                            m[id] = base

                            # For some reason this hack workaround is needed because
                            # bpy.context.view_layer.update() doesn't work.
                            hide_in_viewport(new)
                            show_in_viewport(new)


                        if m.type == "SKIN":
                            bpy.ops.mesh.customdata_skin_add()
                    # Clean up by deleting template and hiding base
                    #hide(base)
                    hide_in_viewport(base)
                    hide_in_render(base)
                    delete_object(template)

                else:
                    # Append template object
                    base = ao()
                    ret = bpy.ops.wm.append(filename = objname, directory = objpath)
                    template = bpy.context.selected_objects[-1]
                    
                    # Select the object with moodifier stack.
                    select_only(base)
                    select_object(template) # <- Active selection
                    
                    # Copy over modifiers from template.
                    bpy.ops.object.make_links_data(type='MODIFIERS')
                    
                    # Set active back to base
                    select_only(base)

                    # Loop modifiers to find geometry nodes:
                    #for m in template.modifiers:
                    for m in base.modifiers:
                        # Get geo node modifiers
                        if m.type == "NODES":
                            nodes = m.node_group.nodes

                            ''' - Assigning the object reference
                            for n in nodes:
                                if n.type == "OBJECT_INFO":
                                    # Set all object references to base
                                    n.inputs[0].default_value = base
                            '''
                            # Using the modifier input method.
                            id = ""
                            ginput = get_node(nodes, "Group Input")
                            for o in ginput.outputs:
                                if o.name.lower() == "object":
                                    id = o.identifier #Input_3 for example
                            m[id] = base
                            
                            # For some reason this hack workaround is needed because
                            # bpy.context.view_layer.update() doesn't work.
                            hide_in_viewport(base)
                            show_in_viewport(base)

                        if m.type == "SKIN":
                            bpy.ops.mesh.customdata_skin_add()
                    # Clean up by deleting template
                    delete_object(template)

            else:
                print(wm.content_packs_mp + " - pack file does not exist.")
        return {'FINISHED'}
class BYGEN_OT_mesh_parametric_import_template(bpy.types.Operator):
    bl_idname = "object.bygen_mesh_parametric_import_template"
    bl_label = "Import Parametric Mesh Template"
    bl_description = "Imports and adds the selected parametric mesh effect template"
    bl_options = {'REGISTER','UNDO'}

    def execute(self, context):
        # Setting up context
        scene = context.scene
        bytool = scene.by_tool
        wm = context.window_manager
            
        # Beginning procedure:
        directory = os.path.abspath(os.path.join(os.path.dirname(__file__), 'content_packs', wm.content_packs_mp, wm.content_packs_mp+'.blend'))
        objpath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'content_packs', wm.content_packs_mp, wm.content_packs_mp+'.blend/Object/')) #\\Object\\
        objname = wm.mesh_parametric_effects
        
        if directory and os.path.exists(directory):
            if wm.mesh_parametric_effects.startswith("(G)"):
                '''
                Since this is a complex geometry nodes effect requiring mesh references,
                we will look for a separate object specifically pre-prepared to be imported
                as a template object - which is separate from the object container for the
                effect.
                '''

                # Updating the filename to find the complex template.
                objname = wm.mesh_parametric_effects + " Template"

                # Duplicating the appending code in case we need to handle the importing
                # of complex templates slightly differently in the future.
                ret = bpy.ops.wm.append(filename = objname, directory = objpath)
                template = bpy.context.selected_objects[-1]
                for m in template.modifiers:
                    if m.type=='SUBSURF':
                        m.show_viewport = True
                        m.show_render = True
            else:
                '''
                Since this is not a complex (G) effect, we will just be importing the object
                that contains the modifier stack which constructs the effect.
                '''
                ret = bpy.ops.wm.append(filename = objname, directory = objpath)
                template = bpy.context.selected_objects[-1]
                for m in template.modifiers:
                    if m.type=='SUBSURF':
                        m.show_viewport = True
                        m.show_render = True
        return {'FINISHED'}
class BYGEN_PT_MeshParametric(Panel):
    bl_idname = "BYGEN_PT_MeshParametric"
    bl_label = "Parametric"
    bl_parent_id = "BYGEN_PT_MeshEffects"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BY-GEN"

    def draw_header(self, context):
        self.layout.label(text = "", icon = "OUTLINER_OB_MESH")

    def draw(self, context):
        layout = self.layout
        wm = context.window_manager
        scene = context.scene
        bytool = scene.by_tool

        column = layout.column()
        row = column.row()
        #row.scale_y = 1.2
        row.prop(wm, "content_packs_mp", text = "")
        row.operator("wm.url_open", text="", icon='FILEBROWSER').url = os.path.abspath(os.path.join(os.path.dirname(__file__), 'content_packs'))
        row.operator("wm.url_open", text="", icon='URL').url = "https://curtisholt.online/by-gen"
        row.operator("object.bygen_refresh_effect_properties", text="", icon='FILE_REFRESH')

        # Displaying the thumbnail selection window:
        row = layout.row()
        row.template_icon_view(wm, "mesh_parametric_effects", show_labels=True, scale=8, scale_popup=8)

        box = layout.box()
        col = box.column()

        colrow = col.row(align=True)
        colrow.operator("object.bygen_mesh_parametric_import", text = "Apply to Selected")
        colrow = col.row(align=True)
        colrow.operator("object.bygen_mesh_parametric_import_template", text = "Import Template")
        #colrow.prop(bytool, "mp_unique_collection")
#endregion
#region Mesh Structural
def content_packs_ms_from_directory(self, context):
    wm = context.window_manager
    enum_items = []
    if context is None:
        return enum_items

    directory = os.path.abspath(os.path.join(os.path.dirname(__file__), 'content_packs'))

    if directory and os.path.exists(directory):
        # Scan directory for folders
        pack_paths = alistdir(directory)
        for p in pack_paths:
            #--- Folder Check
            cpack = os.path.abspath(os.path.join(os.path.dirname(__file__), 'content_packs', p))
            folders = alistdir(cpack)
            if 'thumbnails_mesh_structural' in folders:
                enum_items.append((p, p, 'Content Pack'))
            #---
    return enum_items
def get_mesh_structural_thumbnails(self, context):
    enum_items = []
    wm = context.window_manager

    directory = os.path.abspath(os.path.join(os.path.dirname(__file__), 'content_packs', wm.content_packs_ms, 'thumbnails_mesh_structural'))

    # Get collection defined in register function
    pcoll = preview_collections["main"]

    if directory == pcoll.mesh_structural_effects_dir:
        print(">>> MD DIRECTORY ALREADY")
        return pcoll.mesh_structural_effects

    if directory and os.path.exists(directory):
        # Scan directory for jpg files
        image_paths = []
        for fn in alistdir(directory):
            if fn.lower().endswith(".jpg"):
                image_paths.append(fn)
        
        for i, name in enumerate(image_paths):
            # Generate a thumbnail preview for a file.
            filepath = os.path.join(directory, name)
            icon = pcoll.get(name)
            if not icon:
                thumb = pcoll.load(name, filepath, 'IMAGE')
            else:
                thumb = pcoll[name]
            trimname = name.split('.')
            enum_items.append((trimname[0], trimname[0], "", thumb.icon_id, i))

    pcoll.mesh_structural_effects = enum_items
    pcoll.mesh_structural_effects_dir = directory
    return pcoll.mesh_structural_effects
class BYGEN_OT_mesh_structural_import(bpy.types.Operator):
    bl_idname = "object.bygen_mesh_structural_import"
    bl_label = "Import Structural Mesh Effect"
    bl_description = "Imports and adds the selected structural mesh effect"
    bl_options = {'REGISTER','UNDO'}

    def execute(self, context):
        # Setting up context
        scene = context.scene
        bytool = scene.by_tool
        wm = context.window_manager
            
        # Beginning procedure:
        if len(bpy.context.selected_objects) > 0:
            objs = selected_objects()

            # Getting all useful directories for obtaining data (objects, node trees, etc.) from the content packs.
            directory = os.path.abspath(os.path.join(os.path.dirname(__file__), 'content_packs', wm.content_packs_ms, wm.content_packs_ms+'.blend'))
            colpath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'content_packs', wm.content_packs_ms, wm.content_packs_ms+'.blend/Collection/'))
            colname = wm.mesh_structural_effects
            treepath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'content_packs', wm.content_packs_ms, wm.content_packs_ms+'.blend/NodeTree/'))
            treename = wm.mesh_structural_effects
            
            # Find blend file with same name as folder (wm.content_packs_mp+'.blend')
            if directory and os.path.exists(directory):
                for o in objs:

                    # Import geo tree from content pack
                    bpy.ops.wm.append(filename = treename, directory = treepath)

                    # Get the imported tree by name (store in surface_tree)
                    mesh_structural_tree = bpy.data.node_groups[treename]

                    # Add geonodes modifier to object (store in geomod)
                    geomod = o.modifiers.new("Geometry Nodes", "NODES")

                    # Assign new surface_effect geonode tree to new geomod
                    geomod.node_group = mesh_structural_tree

                    # Change surface_tree name to 'objname_treename_randID'
                    randID = random.randint(1,9999)
                    mesh_structural_tree.name = o.name+"_"+treename+"_"+str(randID)

            else:
                print(wm.content_packs_ms + " - pack file does not exist.")
        return {'FINISHED'}
class BYGEN_OT_mesh_structural_import_template(bpy.types.Operator):
    bl_idname = "object.bygen_mesh_structural_import_template"
    bl_label = "Import Structural Mesh Template"
    bl_description = "Imports and adds the selected structural mesh effect template"
    bl_options = {'REGISTER','UNDO'}

    def execute(self, context):
        # Setting up context
        scene = context.scene
        bytool = scene.by_tool
        wm = context.window_manager
            
        # Beginning procedure:
        directory = os.path.abspath(os.path.join(os.path.dirname(__file__), 'content_packs', wm.content_packs_ms, wm.content_packs_ms+'.blend'))
        objpath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'content_packs', wm.content_packs_ms, wm.content_packs_ms+'.blend/Object/')) #\\Object\\
        objname = wm.mesh_structural_effects
        
        if directory and os.path.exists(directory):
            ret = bpy.ops.wm.append(filename = objname, directory = objpath)
            template = bpy.context.selected_objects[-1]
            for m in template.modifiers:
                if m.type=='SUBSURF':
                    m.show_viewport = True
                    m.show_render = True
        return {'FINISHED'}
class BYGEN_PT_MeshStructural(Panel):
    bl_idname = "BYGEN_PT_MeshStructural"
    bl_label = "Structural"
    bl_parent_id = "BYGEN_PT_MeshEffects"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BY-GEN"

    def draw_header(self, context):
        self.layout.label(text = "", icon = "OUTLINER_OB_CURVE")

    def draw(self, context):
        layout = self.layout
        wm = context.window_manager
        scene = context.scene
        bytool = scene.by_tool

        column = layout.column()
        row = column.row()
        #row.scale_y = 1.2
        row.prop(wm, "content_packs_ms", text = "")
        row.operator("wm.url_open", text="", icon='FILEBROWSER').url = os.path.abspath(os.path.join(os.path.dirname(__file__), 'content_packs'))
        row.operator("wm.url_open", text="", icon='URL').url = "https://curtisholt.online/by-gen"
        row.operator("object.bygen_refresh_effect_properties", text="", icon='FILE_REFRESH')

        # Displaying the thumbnail selection window:
        row = layout.row()
        row.template_icon_view(wm, "mesh_structural_effects", show_labels=True, scale=8, scale_popup=8)

        box = layout.box()
        col = box.column()

        colrow = col.row(align=True)
        colrow.operator("object.bygen_mesh_structural_import", text = "Apply to Selected")
        colrow = col.row(align=True)
        colrow.operator("object.bygen_mesh_structural_import_template", text = "Import Template")
        #colrow = col.row(align=True)
        #colrow.prop(bytool, "ms_unique_collection")
#endregion
#region Mesh Displacement
def content_packs_md_from_directory(self, context):
    wm = context.window_manager
    enum_items = []
    if context is None:
        return enum_items

    #directory = "content_packs_md"
    directory = os.path.abspath(os.path.join(os.path.dirname(__file__), 'content_packs'))

    #pcoll = preview_collections["categories"]
    if directory and os.path.exists(directory):
        # Scan directory for folders
        pack_paths = alistdir(directory)
        for p in pack_paths:
            #--- Folder Check
            cpack = os.path.abspath(os.path.join(os.path.dirname(__file__), 'content_packs', p))
            folders = alistdir(cpack)
            if 'thumbnails_mesh_displacement' in folders:
                enum_items.append((p, p, 'Content Pack'))
            #---
    return enum_items
def get_mesh_displacement_thumbnails(self, context):
    enum_items = []
    #if context is None:
    #    return enum_items
    wm = context.window_manager

    #directory = wm.surface_effects_dir
    #directory = "content_packs\\"+wm.content_packs_md+"\\thumbnails_surface_effects"
    directory = os.path.abspath(os.path.join(os.path.dirname(__file__), 'content_packs', wm.content_packs_md, 'thumbnails_mesh_displacement'))

    # Get collection defined in register function
    pcoll = preview_collections["main"]

    if directory == pcoll.mesh_displacement_effects_dir:
        print(">>> MD DIRECTORY ALREADY")
        return pcoll.mesh_displacement_effects

    #print("Scanning directory %s" % directory)
    if directory and os.path.exists(directory):
        # Scan directory for jpg files
        image_paths = []
        for fn in alistdir(directory):
            if fn.lower().endswith(".jpg"):
                image_paths.append(fn)
        
        for i, name in enumerate(image_paths):
            # Generate a thumbnail preview for a file.
            filepath = os.path.join(directory, name)
            icon = pcoll.get(name)
            if not icon:
                thumb = pcoll.load(name, filepath, 'IMAGE')
            else:
                thumb = pcoll[name]
            trimname = name.split('.')
            #enum_items.append((name, name, "", thumb.icon_id, i))
            enum_items.append((trimname[0], trimname[0], "", thumb.icon_id, i))

    pcoll.mesh_displacement_effects = enum_items
    pcoll.mesh_displacement_effects_dir = directory
    return pcoll.mesh_displacement_effects
class BYGEN_OT_mesh_displacement_import(bpy.types.Operator):
    bl_idname = "object.bygen_mesh_displacement_import"
    bl_label = "Import Mesh Displacement"
    bl_description = "Imports and adds the selected mesh displacement effect"
    bl_options = {'REGISTER','UNDO'}

    def execute(self, context):
        # Setting up context
        scene = context.scene
        bytool = scene.by_tool
        wm = context.window_manager
            
        # Beginning procedure:
        if len(bpy.context.selected_objects) > 0:
            objs = selected_objects()
            # Search directory content_packs os.path.abspath(os.path.join(os.path.dirname(__file__), 'content_packs', wm.content_packs_md))
            directory = os.path.abspath(os.path.join(os.path.dirname(__file__), 'content_packs', wm.content_packs_md, wm.content_packs_md+'.blend'))
            treepath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'content_packs', wm.content_packs_md, wm.content_packs_md+'.blend/NodeTree/')) #\\NodeTree\\
            treename = wm.mesh_displacement_effects
            # Find blend file with same name as folder (wm.content_packs_md+'.blend')
            if directory and os.path.exists(directory):
                for o in objs:

                    # Import geo tree from content pack
                    bpy.ops.wm.append(filename = treename, directory = treepath)

                    # Get the imported tree by name (store in surface_tree)
                    mesh_tree = bpy.data.node_groups[treename]

                    # Add geonodes modifier to object (store in geomod)
                    geomod = o.modifiers.new("Geometry Nodes", "NODES")

                    # Assign new surface_effect geonode tree to new geomod
                    geomod.node_group = mesh_tree

                    # Change mesh_tree name to 'objname_treename_randID'
                    randID = random.randint(1,9999)
                    mesh_tree.name = o.name+"_"+treename+"_"+str(randID)

                    # Selected object should already be the input mesh
            else:
                print(wm.content_packs_md + " - pack file does not exist.")
        return {'FINISHED'}
class BYGEN_PT_Displacement(Panel):
    bl_idname = "BYGEN_PT_Displacement"
    bl_label = "Displacement"
    bl_parent_id = "BYGEN_PT_MeshEffects"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BY-GEN"
    
    def draw_header(self, context):
        self.layout.label(text = "", icon = "MOD_DISPLACE")

    def draw(self, context):
        layout = self.layout
        wm = context.window_manager

        column = layout.column()
        row = column.row()
        #row.scale_y = 1.2
        row.prop(wm, "content_packs_md", text = "")
        row.operator("wm.url_open", text="", icon='FILEBROWSER').url = os.path.abspath(os.path.join(os.path.dirname(__file__), 'content_packs'))
        row.operator("wm.url_open", text="", icon='URL').url = "https://curtisholt.online/by-gen"
        row.operator("object.bygen_refresh_effect_properties", text="", icon='FILE_REFRESH')

        # Displaying the thumbnail selection window:
        row = layout.row()
        row.template_icon_view(wm, "mesh_displacement_effects", show_labels=True, scale=8, scale_popup=8)

        box = layout.box()
        col = box.column()

        colrow = col.row(align=True)
        colrow.operator("object.bygen_mesh_displacement_import", text = "Apply to Selected")
        colrow = col.row(align=True)
        colrow.label(text="Requires high geometry density.")
#endregion
#region Mesh Helper Tools
class BYGEN_PT_MeshHelperTools(Panel):
    bl_idname = "BYGEN_PT_MeshHelperTools"
    bl_label = "Helper Tools"
    bl_parent_id = "BYGEN_PT_MeshEffects"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BY-GEN"
    def draw_header(self, context):
        self.layout.label(text = "", icon = "TOOL_SETTINGS")
    def draw(self, context):
        layout = self.layout

        box = layout.box()

        col = box.column()
        colrow = col.row(align=True)
        #colrow.operator("object.bygen_open_depth_tool", text="Open Depth Tool Folder")
        colrow.operator("wm.url_open", text="Open Depth Tool Folder").url = os.path.abspath(os.path.join(os.path.dirname(__file__), 'tools')) #icon='FILEBROWSER'
        colrow = col.row(align=True)
        colrow.operator("object.bygen_single_vertex_object")
        colrow = col.row(align=True)
        colrow.operator("object.bygen_add_skin_subsurf")
class BYGEN_OT_SingleVertexObject(bpy.types.Operator):
    bl_idname = "object.bygen_single_vertex_object"
    bl_label = "Create Vertex Object"
    bl_description = "Creates an object with a single vertex on the 3D Cursor"
    bl_options = {'REGISTER','UNDO'}

    def execute(self, context):
        # Setting up context
        scene = context.scene
        bytool = scene.by_tool
        wm = context.window_manager

        obj = create_object()
        obj.location = get_cursor_location()
        mesh = bpy.data.meshes.new("New Mesh")
        mesh.vertices.add(1)
        obj.data = mesh
        select_only(obj)

        return {'FINISHED'}
class BYGEN_OT_AddSkinSubsurf(bpy.types.Operator):
    bl_idname = "object.bygen_add_skin_subsurf"
    bl_label = "Add Skin and Subsurf"
    bl_description = "Adds the Skin and Subsurf modifiers"
    bl_options = {'REGISTER','UNDO'}

    def execute(self, context):
        # Setting up context
        scene = context.scene
        bytool = scene.by_tool
        wm = context.window_manager

        for o in so():
            mod_skin = add_skin(o, "Skin")
            mod_skin.use_smooth_shade = True
            mod_sub = add_subsurf(o, "Subsurf")
            mod_sub.levels = 2
            mod_sub.render_levels = 2

        return {'FINISHED'}
class BYGEN_OT_OpenDepthTool(bpy.types.Operator):
    bl_idname = "object.bygen_open_depth_tool"
    bl_label = "Open Depth Tool"
    bl_description = "Opens the depth tool file"
    bl_options = {'REGISTER','UNDO'}

    def execute(self, context):
        # Setting up context
        scene = context.scene
        bytool = scene.by_tool
        wm = context.window_manager

        depth_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'tools', 'depth_tool.blend'))
        #bpy.ops.wm.save_mainfile('INVOKE_AREA')
        bpy.ops.wm.open_mainfile(filepath=depth_file)

        return {'FINISHED'}
#endregion
#endregion

#region VOLUME EFFECTS
def content_packs_ve_from_directory(self, context):
    wm = context.window_manager
    enum_items = []
    if context is None:
        return enum_items

    #directory = "content_packs_md"
    directory = os.path.abspath(os.path.join(os.path.dirname(__file__), 'content_packs'))

    #pcoll = preview_collections["categories"]
    if directory and os.path.exists(directory):
        # Scan directory for folders
        pack_paths = alistdir(directory)
        for p in pack_paths:
            #--- Folder Check
            cpack = os.path.abspath(os.path.join(os.path.dirname(__file__), 'content_packs', p))
            folders = alistdir(cpack)
            if 'thumbnails_volume_effects' in folders:
                enum_items.append((p, p, 'Content Pack'))
            #---
    return enum_items
def get_volume_effect_thumbnails(self, context):
    enum_items = []
    #if context is None:
    #    return enum_items
    wm = context.window_manager

    #directory = wm.surface_effects_dir
    #directory = "content_packs\\"+wm.content_packs_md+"\\thumbnails_surface_effects"
    directory = os.path.abspath(os.path.join(os.path.dirname(__file__), 'content_packs', wm.content_packs_ve, 'thumbnails_volume_effects'))

    # Get collection defined in register function
    pcoll = preview_collections["main"]

    if directory == pcoll.volume_effects_dir:
        print(">>> MD DIRECTORY ALREADY")
        return pcoll.volume_effects

    #print("Scanning directory %s" % directory)
    if directory and os.path.exists(directory):
        # Scan directory for jpg files
        image_paths = []
        for fn in alistdir(directory):
            if fn.lower().endswith(".jpg"):
                image_paths.append(fn)
        
        for i, name in enumerate(image_paths):
            # Generate a thumbnail preview for a file.
            filepath = os.path.join(directory, name)
            icon = pcoll.get(name)
            if not icon:
                thumb = pcoll.load(name, filepath, 'IMAGE')
            else:
                thumb = pcoll[name]
            trimname = name.split('.')
            #enum_items.append((name, name, "", thumb.icon_id, i))
            enum_items.append((trimname[0], trimname[0], "", thumb.icon_id, i))

    pcoll.volume_effects = enum_items
    #pcoll.volume_effects_dir = directory
    return pcoll.volume_effects
class BYGEN_OT_volume_effect_import(bpy.types.Operator):
    bl_idname = "object.bygen_volume_effect_import"
    bl_label = "Import Volume Effect"
    bl_description = "Imports and adds the selected volume effect."
    bl_options = {'REGISTER','UNDO'}

    def execute(self, context):
        # Setting up context
        scene = context.scene
        bytool = scene.by_tool
        wm = context.window_manager
            
        # Beginning procedure:
        if len(bpy.context.selected_objects) > 0:
            objs = selected_objects()

            # Getting all useful directories for obtaining data (objects, node trees, etc.) from the content packs.
            directory = os.path.abspath(os.path.join(os.path.dirname(__file__), 'content_packs', wm.content_packs_ve, wm.content_packs_ve+'.blend'))
            colpath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'content_packs', wm.content_packs_ve, wm.content_packs_ve+'.blend/Collection/')) #\\Collection\\
            colname = wm.volume_effects
            treepath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'content_packs', wm.content_packs_ve, wm.content_packs_ve+'.blend/NodeTree/')) #\\NodeTree\\
            treename = wm.volume_effects

            # Find blend file with same name as folder (wm.content_packs_ve+'.blend')
            if directory and os.path.exists(directory):

                if wm.volume_effects.startswith("(S)"):
                    '''
                    This is an (S) type effect, meaning there is no collection to import.
                    This means we can go straight to the importing of the geo nodes tree
                    and assign it to the object/s.
                    '''
                    for o in objs:

                        # Import geo tree from content pack
                        bpy.ops.wm.append(filename = treename, directory = treepath)

                        # Get the imported tree by name (store in surface_tree)
                        volume_tree = bpy.data.node_groups[treename]

                        # Add geonodes modifier to object (store in geomod)
                        geomod = o.modifiers.new("Geometry Nodes", "NODES")

                        # Assign new surface_effect geonode tree to new geomod
                        geomod.node_group = volume_tree

                        # Change surface_tree name to 'objname_treename_randID'
                        randID = random.randint(1,9999)
                        volume_tree.name = o.name+"_"+treename+"_"+str(randID)

                else:
                    '''
                    This is not an (S) type effect, meaning there is a collection to import.
                    Collection name should be wm.surface_effects (full path colpath).
                    We will need to import the necessary collection content before importing
                    the geometry nodes tree and assigning everything to the selected object/s.
                    '''
                    # Collection
                    col = None

                    # If the user wants to create a unique collection.
                    if bytool.ve_unique_collection:
                        # Append collection to file (store ref in col) <- (optional: link)
                        bpy.ops.wm.append(filename = colname, directory = colpath)
                        col = get_collection(wm.volume_effects)
                    
                    # Else: The user does not want to create a unique collection.
                    else:

                        # If the collection already exists in the blend file.
                        if collection_exists(wm.volume_effects):
                            # Let's grab the collection.
                            col = get_collection(wm.volume_effects)
                        
                        # Else: The collection does not already exist in the blend file.
                        else:
                            # Let's create the collection.
                            bpy.ops.wm.append(filename = colname, directory = colpath)
                            col = get_collection(wm.volume_effects)
                        
                    # if col:
                    if col:
                        for o in objs:

                            # Import geo tree from content pack
                            bpy.ops.wm.append(filename = treename, directory = treepath)

                            # Get the imported tree by name (store in surface_tree)
                            volume_tree = bpy.data.node_groups[treename]

                            # Add geonodes modifier to object (store in geomod)
                            geomod = o.modifiers.new("Geometry Nodes", "NODES")

                            # Assign new surface_effect geonode tree to new geomod
                            geomod.node_group = volume_tree

                            # Change surface_tree name to 'objname_treename_randID'
                            randID = random.randint(1,9999)
                            volume_tree.name = o.name+"_"+treename+"_"+str(randID)

                            # Open surface tree nodes
                            nodes = volume_tree.nodes

                            # Put col in correct node (collection info node)
                            colinfo = get_node(nodes, "Collection Info")
                            colinfo.inputs[0].default_value = col
            else:
                print(wm.content_packs_ve + " - pack file does not exist.")
        return {'FINISHED'}
class BYGEN_PT_VolumeEffects(Panel):
    bl_idname = "BYGEN_PT_VolumeEffects"
    bl_label = "Volume Effects"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BY-GEN"

    def draw_header(self, context):
        self.layout.label(text = "", icon = "SNAP_VOLUME")

    def draw(self, context):
        layout = self.layout
        wm = context.window_manager
        scene = context.scene
        bytool = scene.by_tool

        column = layout.column()
        row = column.row()
        #row.scale_y = 1.2
        row.prop(wm, "content_packs_ve", text = "")
        row.operator("wm.url_open", text="", icon='FILEBROWSER').url = os.path.abspath(os.path.join(os.path.dirname(__file__), 'content_packs'))
        row.operator("wm.url_open", text="", icon='URL').url = "https://curtisholt.online/by-gen"
        row.operator("object.bygen_refresh_effect_properties", text="", icon='FILE_REFRESH')

        # Displaying the thumbnail selection window:
        row = layout.row()
        row.template_icon_view(wm, "volume_effects", show_labels=True, scale=8, scale_popup=8)

        box = layout.box()
        col = box.column()

        colrow = col.row(align=True)
        colrow.operator("object.bygen_volume_effect_import", text = "Apply to Selected")
        colrow = col.row(align=True)
        colrow.prop(bytool, "ve_unique_collection")
#endregion

#region App Handling
def thumbnail_update_call(self, context):
    # Flush and Reconstruct Thumbnails with new selection
    register_props()
    return None
'''
The following app handler makes sure that the catgories
and thumbnails are recalculated every time a blend file is
loaded. This prevents a bug where the thumbnails would not
represent the category shown in the selection, meaning that
when the user goes to apply the mode, it fails, as the mode
does not exist in the selected content pack.
'''
@persistent
def load_reset(temp):
    thumbnail_update_call(None, bpy.context)
bpy.app.handlers.load_post.append(load_reset)
#endregion
#region Registration
classes = (
    # Preoperation Functions / Classes
    BYGEN_OT_groupmask_ambient_occlusion,
    # Surface Effects
    BYGEN_PT_SurfaceEffects,
    BYGEN_PT_SurfaceHelperTools,
    BYGEN_OT_surface_effect_import,
    BYGEN_OT_surface_effect_weight_paint,
    BYGEN_OT_refresh_effect_properties,
    # Mesh Effects
    BYGEN_PT_MeshEffects,
    #BYGEN_PT_ModifierStyles,
    BYGEN_PT_MeshParametric,
    BYGEN_OT_mesh_parametric_import,
    BYGEN_OT_mesh_parametric_import_template,
    BYGEN_OT_mesh_structural_import,
    BYGEN_OT_mesh_structural_import_template,
    BYGEN_PT_MeshStructural,
    BYGEN_PT_Displacement,
    BYGEN_OT_mesh_displacement_import,
    BYGEN_PT_MeshHelperTools,
    BYGEN_OT_SingleVertexObject,
    BYGEN_OT_AddSkinSubsurf,
    BYGEN_OT_OpenDepthTool,
    # Volume Effects
    BYGEN_OT_volume_effect_import,
    BYGEN_PT_VolumeEffects,
)
def register_props():
    #region Info and Imports
    '''
    Here we destroy the original props for the interface and reconstruct them
    using the new selection for the content_packs property.
    Realistically we only need to reconstruct the thumbnails in this phase, but
    I have left it so content_packs also updates because this would allow
    people to install and select new packs while Blender is running.
    (New content packs will only display when the user has selected a different
    pre-existing content pack in the interface, causing the value to update and
    run the directory search again.)
    '''
    import bpy
    from bpy.utils import register_class
    from bpy.types import WindowManager
    from bpy.props import (
        StringProperty,
        EnumProperty,
        BoolProperty,
    )
    import bpy.utils.previews
    #endregion
    #region Deleting Window Manager Properties
    # Flush Original Props
    del WindowManager.volume_effects
    del WindowManager.mesh_displacement_effects
    del WindowManager.surface_effects
    del WindowManager.content_packs_se # Surface Effects
    del WindowManager.content_packs_md # Mesh Displacement
    del WindowManager.content_packs_mp # Mesh Parametric
    del WindowManager.content_packs_ms # Mesh Structural
    del WindowManager.content_packs_ve # Volume Effects

    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()
    #endregion
    #region Creating pcoll Properties
    # Reconstruct Props
    pcoll = bpy.utils.previews.new()
    pcoll.surface_effects_dir = ""
    pcoll.mesh_displacement_effects_dir = ""
    pcoll.mesh_parametric_effects_dir = ""
    pcoll.mesh_structural_effects_dir = ""
    pcoll.volume_effects_dir = ""
    pcoll.surface_effects = ()
    pcoll.mesh_displacement_effects = ()
    pcoll.mesh_parametric_effects = ()
    pcoll.mesh_structural_effects = ()
    pcoll.volume_effects = ()
    preview_collections["main"] = pcoll
    #endregion
    #region Creating WindowManager Properties
    WindowManager.content_packs_se = EnumProperty( # Surface Effects
        items = content_packs_se_from_directory(None, bpy.context),
        update = thumbnail_update_call,
    )
    WindowManager.content_packs_md = EnumProperty( # Mesh Displacement
        items = content_packs_md_from_directory(None, bpy.context),
        update = thumbnail_update_call,
    )
    WindowManager.content_packs_mp = EnumProperty( # Mesh Parametric
        items = content_packs_mp_from_directory(None, bpy.context),
        update = thumbnail_update_call,
    )
    WindowManager.content_packs_ms = EnumProperty( # Mesh Structural
        items = content_packs_ms_from_directory(None, bpy.context),
        update = thumbnail_update_call,
    )
    WindowManager.content_packs_ve = EnumProperty( # Volume Effects
        items = content_packs_ve_from_directory(None, bpy.context),
        update = thumbnail_update_call,
    )
    WindowManager.surface_effects_dir = StringProperty( # Surface Effects
        name = "Folder Path",
        subtype = 'DIR_PATH',
        default="images"
    )
    WindowManager.mesh_displacement_effects_dir = StringProperty( # Mesh Displacement
        name = "Folder Path",
        subtype = 'DIR_PATH',
        default="images"
    )
    WindowManager.mesh_parametric_effects_dir = StringProperty( # Mesh Parametric
        name = "Folder Path",
        subtype = 'DIR_PATH',
        default="images"
    )
    WindowManager.mesh_structural_effects_dir = StringProperty( # Mesh Structural
        name = "Folder Path",
        subtype = 'DIR_PATH',
        default="images"
    )
    WindowManager.volume_effects_dir = StringProperty( # Volume Effects
        name = "Folder Path",
        subtype = 'DIR_PATH',
        default="images"
    )
    WindowManager.surface_effects = EnumProperty( # Surface Effects
        items = get_surface_effect_thumbnails(None, bpy.context),
    )
    WindowManager.mesh_displacement_effects = EnumProperty( # Mesh Displacement
        items = get_mesh_displacement_thumbnails(None, bpy.context),
    )
    WindowManager.mesh_parametric_effects = EnumProperty( # Mesh Parametric
        items = get_mesh_parametric_thumbnails(None, bpy.context),
    )
    WindowManager.mesh_structural_effects = EnumProperty( # Mesh Structural
        items = get_mesh_structural_thumbnails(None, bpy.context),
    )
    WindowManager.volume_effects = EnumProperty( # Volume Effects
        items = get_volume_effect_thumbnails(None, bpy.context),
    )
    #endregion
def register():
    #region Info and Imports
    import bpy
    from bpy.utils import register_class
    from bpy.types import WindowManager
    from bpy.props import (
        StringProperty,
        EnumProperty,
        BoolProperty,
    )
    import bpy.utils.previews
    #endregion
    #region Creating pcoll Properties
    pcoll = bpy.utils.previews.new()
    pcoll.surface_effects_dir = ""
    pcoll.mesh_displacement_effects_dir = ""
    pcoll.mesh_parametric_effects_dir = ""
    pcoll.mesh_structural_effects_dir = ""
    pcoll.volume_effects_dir = ""
    pcoll.surface_effects = ()
    pcoll.mesh_displacement_effects = ()
    pcoll.mesh_parametric_effects = ()
    pcoll.mesh_structural_effects = ()
    pcoll.volume_effects = ()
    preview_collections["main"] = pcoll
    #endregion
    #region Creating WindowManager Properties
    WindowManager.content_packs_se = EnumProperty( # Surface Effects
        items = content_packs_se_from_directory(None, bpy.context),
        update = thumbnail_update_call,
    )
    WindowManager.content_packs_md = EnumProperty( # Mesh Displacement
        items = content_packs_md_from_directory(None, bpy.context),
        update = thumbnail_update_call,
    )
    WindowManager.content_packs_mp = EnumProperty( # Mesh Parametric
        items = content_packs_mp_from_directory(None, bpy.context),
        update = thumbnail_update_call,
    )
    WindowManager.content_packs_ms = EnumProperty( # Mesh Structural
        items = content_packs_ms_from_directory(None, bpy.context),
        update = thumbnail_update_call,
    )
    WindowManager.content_packs_ve = EnumProperty( # Volume Effects
        items = content_packs_ve_from_directory(None, bpy.context),
        update = thumbnail_update_call,
    )
    WindowManager.surface_effects_dir = StringProperty( # Surface Effects
        name = "Folder Path",
        subtype = 'DIR_PATH',
        default="images"
    )
    WindowManager.mesh_displacement_effects_dir = StringProperty( # Mesh Displacement
        name = "Folder Path",
        subtype = 'DIR_PATH',
        default="images"
    )
    WindowManager.mesh_parametric_effects_dir = StringProperty( # Mesh Parametric
        name = "Folder Path",
        subtype = 'DIR_PATH',
        default="images"
    )
    WindowManager.mesh_structural_effects_dir = StringProperty( # Mesh Structural
        name = "Folder Path",
        subtype = 'DIR_PATH',
        default="images"
    )
    WindowManager.volume_effects_dir = StringProperty( # Volume Effects
        name = "Folder Path",
        subtype = 'DIR_PATH',
        default="images"
    )
    WindowManager.surface_effects = EnumProperty( # Surface Effects
        items = get_surface_effect_thumbnails(None, bpy.context),
    )
    WindowManager.mesh_displacement_effects = EnumProperty( # Mesh Displacement
        items = get_mesh_displacement_thumbnails(None, bpy.context),
    )
    WindowManager.mesh_parametric_effects = EnumProperty( # Mesh Parametric
        items = get_mesh_parametric_thumbnails(None, bpy.context),
    )
    WindowManager.mesh_structural_effects = EnumProperty( # Mesh Structural
        items = get_mesh_structural_thumbnails(None, bpy.context),
    )
    WindowManager.volume_effects = EnumProperty( # Volume Effects
        items = get_volume_effect_thumbnails(None, bpy.context),
    )
    #endregion
    #region Registering Classes
    for cls in classes:
        register_class(cls)
    #endregion
def unregister():
    #region Info and Imports
    from bpy.utils import unregister_class
    #endregion
    #region Deleting WindowManager Properties
    del WindowManager.volume_effects
    del WindowManager.mesh_structural_effects
    del WindowManager.mesh_parametric_effects
    del WindowManager.mesh_displacement_effects
    del WindowManager.surface_effects
    del WindowManager.volume_effects_dir
    del WindowManager.mesh_structural_effects_dir
    del WindowManager.mesh_parametric_effects_dir
    del WindowManager.mesh_displacement_effects_dir
    del WindowManager.surface_effects_dir
    del WindowManager.content_packs_ve
    del WindowManager.content_packs_ms
    del WindowManager.content_packs_mp
    del WindowManager.content_packs_md
    del WindowManager.content_packs_se
    #endregion
    #region Deleting pcoll Properties
    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()
    #endregion
    #region Unregistering Classes
    for cls in reversed(classes):
        unregister_class(cls)
    #endregion
#endregion