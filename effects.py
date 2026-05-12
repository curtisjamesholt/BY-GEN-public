#region Imports, Variables and Functions
import bpy
from bpy.props import *
from bpy.types import (Panel,StringProperty, EnumProperty,Menu,Operator,PropertyGroup,Scene, WindowManager)
from bpy.app.handlers import persistent
import bpy.utils.previews
import os
import platform
from datetime import datetime
import random
from . easybpy import *
from . import bl_info

addon_version = bl_info.get("version", "UNKNOWN")
if isinstance(addon_version, tuple):
    addon_version = ".".join(map(str, addon_version))

preview_collections = {}
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

#region V10+ Import Method
def import_content(name,
                   context,
                   directory):
    # Setting up context
    scene = context.scene
    bytool = scene.by_tool
    wm = context.window_manager
    geomod = None
        
    # Beginning procedure:
    objs = selected_objects()

    # Getting all useful directories for obtaining data (objects, node trees, etc.) from the content packs.
    directory = directory

    # Validity Check
    can_go = True
    if len(objs) > 0:
        for o in objs:
            if o.type!="MESH": # Not a valid object type.
                can_go = False

        if can_go == True: # Otherwise, good to go.

            '''
            Before starting, prepare debug log output (in case debug_mode and output_to_file are enabled.)
            '''
            addon_dir = ""
            log_path = ""
            if bytool.debug_mode == True and bytool.output_to_log == True:
                addon_dir = os.path.dirname(os.path.abspath(__file__))
                log_path = os.path.join(addon_dir, "log.txt")

            if directory and os.path.exists(directory):

                #region CASE (S)
                if name.startswith("(S)"):
                    '''
                    This is an (S) type effect, meaning a simple geometry node tree.
                    This means we can go straight to the importing of the geo node tree and assign it to the object/s.
                    '''
                    for o in objs:

                        if o.type == "MESH":

                            # Import geo tree from content pack
                            # (( DEBUG ))
                            if bytool.debug_mode:
                                # (( CONSOLE ))
                                print ("-------------------------------------------------")
                                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                print("Timestamp: ", timestamp)
                                print ("DEBUG: Blender version: ", bpy.app.version_string)
                                print ("DEBUG: BY-GEN version: ", addon_version)
                                print ("DEBUG: OS:", platform.system(), platform.release())
                                print ("DEBUG: Architecture:", platform.machine())
                                print ("DEBUG: Object name: " + o.name)
                                print ("DEBUG: Using import method (S). Directory seen to exist. Effect seen to start with (S).")
                                print ("DEBUG: name is: " + str(name))
                                print ("DEBUG: Directory is: " + str(directory))
                                print ("DEBUG: Does .blend file exist: ", os.path.exists(directory))
                                #  (( LOG ))
                                if bytool.output_to_log:
                                    with open(log_path, "a", encoding="utf-8") as f:
                                        f.write("-------------------------------------------------" + '\n')
                                        f.write("Timestamp: " + timestamp + '\n')
                                        f.write("DEBUG: Blender version: " + bpy.app.version_string + '\n')
                                        f.write("DEBUG: BY-GEN version: " + addon_version + '\n')
                                        f.write("DEBUG: OS:" + platform.system() + platform.release() + '\n')
                                        f.write("DEBUG: Architecture:" + platform.machine() + '\n')
                                        f.write("DEBUG: Object name: " + o.name + '\n')
                                        f.write("DEBUG: Using import method (S). Directory seen to exist. Effect seen to start with (S)." + '\n')
                                        f.write("DEBUG: name is: " + str(name) + '\n')
                                        f.write("DEBUG: Directory is: " + str(directory) + '\n')
                                        f.write("DEBUG: Does .blend file exist: " + str(os.path.exists(directory)) + '\n')

                            '''
                             Trying a new way of constructing the path.
                             Leaving separator at the end of the directory in case it is expected on macOS.
                            '''
                            tree_directory = os.path.join(directory, "NodeTree")
                            tree_directory = os.path.normpath(tree_directory)
                            tree_directory = bpy.path.native_pathsep(tree_directory) + os.path.sep
                            filepath = tree_directory + name

                            # (( DEBUG ))
                            if bytool.debug_mode:
                                # (( CONSOLE ))
                                print ("DEBUG: tree_directory is: " + tree_directory)
                                if tree_directory.endswith(os.path.sep):
                                    print ("DEBUG: End path separator DETECTED")
                                else:
                                    print ("DEBUG: End path separator NOT DETECTED")
                                print ("DEBUG: Final appending string is: " + tree_directory + name)
                                # (( LOG ))
                                if bytool.output_to_log:
                                    with open(log_path, "a", encoding="utf-8") as f:
                                        f.write("DEBUG: tree_directory is: " + tree_directory + '\n')
                                        if tree_directory.endswith(os.path.sep):
                                            f.write("DEBUG: End path separator DETECTED" + '\n')
                                        else:
                                            f.write("DEBUG: End path separator NOT DETECTED" + '\n')
                                        f.write("DEBUG: Final appending string is: " + tree_directory + name + '\n')

                            bpy.ops.wm.append(
                                filepath = filepath,
                                filename = name, 
                                directory = tree_directory)

                            # Get the imported tree by name (store in surface_tree)
                            imported_tree = bpy.data.node_groups[name]

                            # Add geonodes modifier to object (store in geomod)
                            geomod = o.modifiers.new("Geometry Nodes", "NODES")

                            # Assign new surface_effect geonode tree to new geomod
                            geomod.node_group = imported_tree

                            # Change surface_tree name to 'o.name_name_randID'
                            randID = random.randint(1,9999)
                            imported_tree.name = o.name+"_"+name+"_"+str(randID)

                            # Open the tree nodes
                            nodes = imported_tree.nodes
#endregion

                #region CASE (Tr)
                elif name.startswith("(Tr)"):
                    '''
                    This is a (Tr) type effect, meaning that once an entire object has been brought in with its modifier stack,
                    the originally selected object will become a hidden source, whereas this imported object will become the host
                    for the effect. The Tr stands for Target Remote.
                    Checks for object references, looking for 'object' inputs in the geometry nodes group inputs / modifier 
                    stack inputs, will also be performed where appropriate.
                    '''
                    # Complex geo nodes stacks which require extra base referencing
                    # Assume base object is selected and make a copy.
                    base = ao()
                    new = copy_object(base)
                    select_only(new)

                    # Import from content pack
                    # (( DEBUG ))
                    if bytool.debug_mode:
                        # (( CONSOLE ))
                        print ("-------------------------------------------------")
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print("Timestamp: ", timestamp)
                        print ("DEBUG: Blender version: ", bpy.app.version_string)
                        print ("DEBUG: BY-GEN version: ", addon_version)
                        print ("DEBUG: OS:", platform.system(), platform.release())
                        print ("DEBUG: Architecture:", platform.machine())
                        print ("DEBUG: Object name: " + o.name)
                        print ("DEBUG: Using import method (Tr). Directory seen to exist. Effect seen to start with (Tr).")
                        print ("DEBUG: name is: " + str(name))
                        print ("DEBUG: Directory is: " + str(directory))
                        print ("DEBUG: Does .blend file exist: ", os.path.exists(directory))
                        #  (( LOG ))
                        if bytool.output_to_log:
                            with open(log_path, "a", encoding="utf-8") as f:
                                f.write("-------------------------------------------------" + '\n')
                                f.write("Timestamp: " + timestamp + '\n')
                                f.write("DEBUG: Blender version: " + bpy.app.version_string + '\n')
                                f.write("DEBUG: BY-GEN version: " + addon_version + '\n')
                                f.write("DEBUG: OS:" + platform.system() + platform.release() + '\n')
                                f.write("DEBUG: Architecture:" + platform.machine() + '\n')
                                f.write("DEBUG: Object name: " + o.name + '\n')
                                f.write("DEBUG: Using import method (S). Directory seen to exist. Effect seen to start with (S)." + '\n')
                                f.write("DEBUG: name is: " + str(name) + '\n')
                                f.write("DEBUG: Directory is: " + str(directory) + '\n')
                                f.write("DEBUG: Does .blend file exist: " + str(os.path.exists(directory)) + '\n')

                    # Append the template object
                    '''
                        Trying a new way of constructing the path.
                        Leaving separator at the end of the directory in case it is expected on macOS.
                    '''
                    tree_directory = os.path.join(directory, "Object")
                    tree_directory = os.path.normpath(tree_directory)
                    tree_directory = bpy.path.native_pathsep(tree_directory) + os.path.sep
                    filepath = tree_directory + name

                    # (( DEBUG ))
                    if bytool.debug_mode:
                        # (( CONSOLE ))
                        print ("DEBUG: tree_directory is: " + tree_directory)
                        if tree_directory.endswith(os.path.sep):
                            print ("DEBUG: End path separator DETECTED")
                        else:
                            print ("DEBUG: End path separator NOT DETECTED")
                        print ("DEBUG: Final appending string is: " + tree_directory + name)
                        # (( LOG ))
                        if bytool.output_to_log:
                            with open(log_path, "a", encoding="utf-8") as f:
                                f.write("DEBUG: tree_directory is: " + tree_directory + '\n')
                                if tree_directory.endswith(os.path.sep):
                                    f.write("DEBUG: End path separator DETECTED" + '\n')
                                else:
                                    f.write("DEBUG: End path separator NOT DETECTED" + '\n')
                                f.write("DEBUG: Final appending string is: " + tree_directory + name + '\n')

                    bpy.ops.wm.append(
                        filepath = filepath,
                        filename = name, 
                        directory = tree_directory)
                    template = bpy.context.selected_objects[-1]

                    # Select the object with moodifier stack.
                    select_only(new)
                    select_object(template) # <- Active selection

                    # Copy over modifiers from template.
                    bpy.ops.object.make_links_data(type='MODIFIERS')

                    # Set active back to base
                    select_only(new)

                    # Loop modifiers to find geometry nodes:
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
                    hide_in_viewport(base)
                    hide_in_render(base)
                    delete_object(template)
                    pass
#endregion

                #region CASE (Ts)
                elif name.startswith("(Ts)"):
                    '''
                    This is a (Ts) type effect, meaning that once an entire object has been brought in with its modifier stack,
                    it is copied over to the originally selected object, and the imported object is deleted.
                    The Ts stands for Target Self.
                    Checks for object references, looking for 'object' inputs in the geometry nodes group inputs / modifier 
                    stack inputs, will also be performed where appropriate.
                    '''
                    # Append template object
                    base = ao()

                    # Import from content pack
                    # (( DEBUG ))
                    if bytool.debug_mode:
                        # (( CONSOLE ))
                        print ("-------------------------------------------------")
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print("Timestamp: ", timestamp)
                        print ("DEBUG: Blender version: ", bpy.app.version_string)
                        print ("DEBUG: BY-GEN version: ", addon_version)
                        print ("DEBUG: OS:", platform.system(), platform.release())
                        print ("DEBUG: Architecture:", platform.machine())
                        print ("DEBUG: Object name: " + o.name)
                        print ("DEBUG: Using import method (Ts). Directory seen to exist. Effect seen to start with (Ts).")
                        print ("DEBUG: name is: " + str(name))
                        print ("DEBUG: Directory is: " + str(directory))
                        print ("DEBUG: Does .blend file exist: ", os.path.exists(directory))
                        #  (( LOG ))
                        if bytool.output_to_log:
                            with open(log_path, "a", encoding="utf-8") as f:
                                f.write("-------------------------------------------------" + '\n')
                                f.write("Timestamp: " + timestamp + '\n')
                                f.write("DEBUG: Blender version: " + bpy.app.version_string + '\n')
                                f.write("DEBUG: BY-GEN version: " + addon_version + '\n')
                                f.write("DEBUG: OS:" + platform.system() + platform.release() + '\n')
                                f.write("DEBUG: Architecture:" + platform.machine() + '\n')
                                f.write("DEBUG: Object name: " + o.name + '\n')
                                f.write("DEBUG: Using import method (S). Directory seen to exist. Effect seen to start with (S)." + '\n')
                                f.write("DEBUG: name is: " + str(name) + '\n')
                                f.write("DEBUG: Directory is: " + str(directory) + '\n')
                                f.write("DEBUG: Does .blend file exist: " + str(os.path.exists(directory)) + '\n')
                    '''
                        Trying a new way of constructing the path.
                        Leaving separator at the end of the directory in case it is expected on macOS.
                    '''
                    tree_directory = os.path.join(directory, "Object")
                    tree_directory = os.path.normpath(tree_directory)
                    tree_directory = bpy.path.native_pathsep(tree_directory) + os.path.sep
                    filepath = tree_directory + name

                    # (( DEBUG ))
                    if bytool.debug_mode:
                        # (( CONSOLE ))
                        print ("DEBUG: tree_directory is: " + tree_directory)
                        if tree_directory.endswith(os.path.sep):
                            print ("DEBUG: End path separator DETECTED")
                        else:
                            print ("DEBUG: End path separator NOT DETECTED")
                        print ("DEBUG: Final appending string is: " + tree_directory + name)
                        # (( LOG ))
                        if bytool.output_to_log:
                            with open(log_path, "a", encoding="utf-8") as f:
                                f.write("DEBUG: tree_directory is: " + tree_directory + '\n')
                                if tree_directory.endswith(os.path.sep):
                                    f.write("DEBUG: End path separator DETECTED" + '\n')
                                else:
                                    f.write("DEBUG: End path separator NOT DETECTED" + '\n')
                                f.write("DEBUG: Final appending string is: " + tree_directory + name + '\n')

                    bpy.ops.wm.append(
                        filepath = filepath,
                        filename = name, 
                        directory = tree_directory)
                    template = bpy.context.selected_objects[-1]
                    
                    # Select the object with moodifier stack.
                    select_only(base)
                    select_object(template) # <- Active selection
                    
                    # Copy over modifiers from template.
                    bpy.ops.object.make_links_data(type='MODIFIERS')
                    
                    # Set active back to base
                    select_only(base)

                    # Loop modifiers to find geometry nodes:
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
                    pass
#endregion

#region Ending Import
            else:
                print("Pack file does not exist.")
            return {'FINISHED'}
pass
#endregion
#endregion

#region SURFACE EFFECTS
def content_packs_se_from_directory(self, context):
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
            if 'thumbnails_surface_effects' in folders:
                enum_items.append((p, p, 'Content Pack'))
            #---
    return enum_items
def get_surface_effect_thumbnails(self, context):
    enum_items = []
    wm = context.window_manager

    directory = os.path.abspath(os.path.join(os.path.dirname(__file__), 'content_packs', wm.content_packs_se, 'thumbnails_surface_effects'))

    # Get collection defined in register function
    pcoll = preview_collections["main"]

    if directory == pcoll.surface_effects_dir:
        return pcoll.surface_effects

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

        # Getting all useful directories for obtaining data (objects, node trees, etc.) from the content packs.
        directory = os.path.abspath(os.path.join(os.path.dirname(__file__), 'content_packs', wm.content_packs_se, wm.content_packs_se+'.blend'))
        
        import_content(
            name = wm.surface_effects,
            context = context,
            directory = directory
        )
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
    bl_label = "Surface"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BY-GEN"

    def draw_header(self, context):
        self.layout.label(text = "", icon = "OUTLINER_OB_SURFACE")
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        bytool = scene.by_tool
        wm = context.window_manager

        column = layout.column()
        row = column.row()
        #row.scale_y = 1.2
        row.prop(wm, "content_packs_se", text = "")
        #row.operator("wm.url_open", text="", icon='FILEBROWSER').url = os.path.abspath(os.path.join(os.path.dirname(__file__), 'content_packs'))
        #row.operator("wm.url_open", text="", icon='URL').url = "https://curtisholt.online/by-gen"
        row.operator("object.bygen_refresh_effect_properties", text="", icon='FILE_REFRESH')

        # Displaying the thumbnail selection window:
        row = layout.row()
        row.template_icon_view(wm, "surface_effects", show_labels=True, scale=8, scale_popup=8)
        
        box = layout.box()
        col = box.column()

        #row = layout.row()
        colrow = col.row(align=True)
        colrow.operator("object.bygen_surface_effect_import", text = "Apply")
        '''
        colrow = col.row(align=True)
        colrow.operator("object.bygen_surface_effect_weight_paint", text = "Apply (Weight Paint)")#, icon = "MOD_VERTEX_WEIGHT"
        '''
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
#endregion

#region MESH EFFECTS
def content_packs_me_from_directory(self, context):
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
            if 'thumbnails_mesh_effects' in folders:
                enum_items.append((p, p, 'Content Pack'))
            #---
    return enum_items
def get_mesh_effect_thumbnails(self, context):
    enum_items = []
    wm = context.window_manager

    directory = os.path.abspath(os.path.join(os.path.dirname(__file__), 'content_packs', wm.content_packs_me, 'thumbnails_mesh_effects'))

    # Get collection defined in register function
    pcoll = preview_collections["main"]

    if directory == pcoll.mesh_effects_dir:
        return pcoll.mesh_effects

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

    pcoll.mesh_effects = enum_items
    return pcoll.mesh_effects
class BYGEN_OT_mesh_effect_import(bpy.types.Operator):
    bl_idname = "object.bygen_mesh_effect_import"
    bl_label = "Import Mesh Effect"
    bl_description = "Imports and adds the selected mesh effect."
    bl_options = {'REGISTER','UNDO'}

    def execute(self, context):
        # Setting up context
        scene = context.scene
        bytool = scene.by_tool
        wm = context.window_manager

        # Getting all useful directories for obtaining data (objects, node trees, etc.) from the content packs.
        directory = os.path.abspath(os.path.join(os.path.dirname(__file__), 'content_packs', wm.content_packs_me, wm.content_packs_me+'.blend'))

        import_content(
            name = wm.mesh_effects,
            context = context,
            directory = directory
        )
        return {'FINISHED'}
class BYGEN_PT_MeshEffects(Panel):
    bl_idname = "BYGEN_PT_MeshEffects"
    bl_label = "Mesh"
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
        row.prop(wm, "content_packs_me", text = "")
        #row.operator("wm.url_open", text="", icon='FILEBROWSER').url = os.path.abspath(os.path.join(os.path.dirname(__file__), 'content_packs'))
        #row.operator("wm.url_open", text="", icon='URL').url = "https://curtisholt.online/by-gen"
        row.operator("object.bygen_refresh_effect_properties", text="", icon='FILE_REFRESH')

        # Displaying the thumbnail selection window:
        row = layout.row()
        row.template_icon_view(wm, "mesh_effects", show_labels=True, scale=8, scale_popup=8)

        box = layout.box()
        col = box.column()

        colrow = col.row(align=True)
        colrow.operator("object.bygen_mesh_effect_import", text = "Apply")
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
        return pcoll.volume_effects

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

        # Getting all useful directories for obtaining data (objects, node trees, etc.) from the content packs.
        directory = os.path.abspath(os.path.join(os.path.dirname(__file__), 'content_packs', wm.content_packs_ve, wm.content_packs_ve+'.blend'))
        
        import_content(
            name = wm.volume_effects,
            context = context,
            directory = directory
        )
        return {'FINISHED'}
class BYGEN_PT_VolumeEffects(Panel):
    bl_idname = "BYGEN_PT_VolumeEffects"
    bl_label = "Volume"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BY-GEN"

    def draw_header(self, context):
        self.layout.label(text = "", icon = "OUTLINER_OB_VOLUME")

    def draw(self, context):
        layout = self.layout
        wm = context.window_manager
        scene = context.scene
        bytool = scene.by_tool

        column = layout.column()
        row = column.row()
        #row.scale_y = 1.2
        row.prop(wm, "content_packs_ve", text = "")
        #row.operator("wm.url_open", text="", icon='FILEBROWSER').url = os.path.abspath(os.path.join(os.path.dirname(__file__), 'content_packs'))
        #row.operator("wm.url_open", text="", icon='URL').url = "https://curtisholt.online/by-gen"
        row.operator("object.bygen_refresh_effect_properties", text="", icon='FILE_REFRESH')

        # Displaying the thumbnail selection window:
        row = layout.row()
        row.template_icon_view(wm, "volume_effects", show_labels=True, scale=8, scale_popup=8)

        box = layout.box()
        col = box.column()

        colrow = col.row(align=True)
        colrow.operator("object.bygen_volume_effect_import", text = "Apply")
#endregion

#region SETTINGS PANEL
class BYGEN_PT_Settings(Panel):
    bl_idname = "BYGEN_PT_Settings"
    bl_label = "Settings"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BY-GEN"

    def draw_header(self, context):
        self.layout.label(text = "", icon = "SETTINGS")

    def draw(self, context):
        layout = self.layout
        wm = context.window_manager
        scene = context.scene
        bytool = scene.by_tool

        box = layout.box()
        col = box.column()

        colrow = col.row(align=True)
        colrow.prop(bytool, "unique_collection")
        colrow = col.row(align=True)
        colrow.prop(bytool, "debug_mode")
        colrow = col.row(align=True)
        if bytool.debug_mode == True:
            colrow.prop(bytool, "output_to_log")
            colrow = col.row(align=True)
        colrow.operator("wm.url_open", text="Local Content Packs", icon='FILEBROWSER').url = os.path.abspath(os.path.join(os.path.dirname(__file__), 'content_packs'))
#endregion

#region INFO PANEL
class OBJECT_PT_ByGenInfo(Panel):
    bl_idname = "OBJECT_PT_ByGenInfo"
    bl_label = "Info"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BY-GEN"

    def draw_header(self, context):
        self.layout.label(text = "", icon = "INFO")

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        bytool = scene.by_tool

        #Operations Layout
        box = layout.box()
        box.operator("wm.url_open", text="Created by Curtis Holt", icon='FILE_SCRIPT').url = "https://www.curtisholt.online"
        box.operator("wm.url_open", text="Additional Work by Charan", icon='FILE_SCRIPT').url = "https://x.com/sai_charan_md"
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

    # Surface Effects
    BYGEN_PT_SurfaceEffects,
    BYGEN_OT_surface_effect_import,
    BYGEN_OT_refresh_effect_properties,

    # Mesh Effects
    #BYGEN_OT_mesh_structural_import,
    BYGEN_OT_mesh_effect_import,
    BYGEN_PT_MeshEffects,
    
    # Volume Effects
    BYGEN_OT_volume_effect_import,
    BYGEN_PT_VolumeEffects,

    # Settings
    BYGEN_PT_Settings,

    # Info
    OBJECT_PT_ByGenInfo,
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
    del WindowManager.surface_effects
    del WindowManager.content_packs_se # Surface Effects
    del WindowManager.content_packs_me # Mesh Effects
    del WindowManager.content_packs_ve # Volume Effects

    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()
    #endregion
    #region Creating pcoll Properties
    # Reconstruct Props
    pcoll = bpy.utils.previews.new()
    pcoll.surface_effects_dir = ""
    pcoll.mesh_effects_dir = ""
    pcoll.volume_effects_dir = ""
    pcoll.surface_effects = ()
    pcoll.mesh_effects = ()
    pcoll.volume_effects = ()
    preview_collections["main"] = pcoll
    #endregion
    #region Creating WindowManager Properties
    WindowManager.content_packs_se = EnumProperty( # Surface Effects
        items = content_packs_se_from_directory(None, bpy.context),
        update = thumbnail_update_call,
    )
    WindowManager.content_packs_me = EnumProperty( # Mesh Displacement
        items = content_packs_me_from_directory(None, bpy.context),
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
    WindowManager.mesh_effects_dir = StringProperty( # Mesh Displacement
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
    WindowManager.mesh_effects = EnumProperty( # Surface Effects
        items = get_mesh_effect_thumbnails(None, bpy.context),
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
    pcoll.mesh_effects_dir = ""
    pcoll.volume_effects_dir = ""
    pcoll.surface_effects = ()
    pcoll.mesh_effects = ()
    pcoll.volume_effects = ()
    preview_collections["main"] = pcoll
    #endregion
    #region Creating WindowManager Properties
    WindowManager.content_packs_se = EnumProperty( # Surface Effects
        items = content_packs_se_from_directory(None, bpy.context),
        update = thumbnail_update_call,
    )
    WindowManager.content_packs_me = EnumProperty( # Mesh Displacement
        items = content_packs_me_from_directory(None, bpy.context),
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
    WindowManager.mesh_effects_dir = StringProperty( # Mesh Displacement
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
    WindowManager.mesh_effects = EnumProperty( # Mesh Displacement
        items = get_mesh_effect_thumbnails(None, bpy.context),
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
    del WindowManager.mesh_effects
    del WindowManager.surface_effects
    del WindowManager.volume_effects_dir
    del WindowManager.mesh_effects_dir
    del WindowManager.surface_effects_dir
    del WindowManager.content_packs_ve
    del WindowManager.content_packs_me
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