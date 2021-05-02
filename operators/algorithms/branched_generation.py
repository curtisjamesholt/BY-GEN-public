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
#region Global Variables
maxModules = None
branchMin = None
branchMax = None
chanceLevel = None
allowSpin = None
move_offset = None
cell_count = 0
start_procedure = True
cellList = []
branchList = []
branchRef = []
extDict = {}
portBin = []
#endregion
#region Operators
# Operator for branched generation method
class BYGEN_OT_Branched_Generation(bpy.types.Operator):
    bl_label = "Branched Generation"
    bl_idname = "object.bygen_start_branched_generation"
    bl_description = "Begins the branched generation procedure"
    bl_options = {'REGISTER', 'UNDO'}

    # Setting up operator properties
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
    output_collection : StringProperty(
        name = "Output Collection",
        description = "Collection to place the output objects",
        default = "Generation Result"
    )
    max_modules : IntProperty(
        name = "Max Modules",
        description = "Maximum number of modules",
        default = 50
    )
    branch_min : IntProperty(
        name = "Branch Min",
        description = "Minimum size of a branch",
        default = 3
    )
    branch_max : IntProperty(
        name = "Branch Max",
        description = "Maximum size of a branch",
        default = 6
    )
    chance_level : IntProperty(
        name = "Chance Level",
        description = "Chance for a new branch to occur",
        default = 50
    )
    allow_spin : BoolProperty(
        name = "Allow Spin",
        description = "Allow rotation of modules along the branch",
        default = True
    )
    move_offset : FloatProperty(
        name = "Move Offset",
        description = "Movement offset for module sizes",
        default = 2
    )
    module_l : StringProperty(
        name = "Module L",
        description = "Collection for L pieces",
        default = "Module_L"
    )
    module_t : StringProperty(
        name = "Module T",
        description = "Collection for T pieces",
        default = "Module_T"
    )
    module_x : StringProperty(
        name = "Module X",
        description = "Collection for X pieces",
        default = "Module_X"
    )
    module_3corner : StringProperty(
        name = "Module 3-Corner",
        description = "Collection for 3-Corner pieces",
        default = "Module_3Corner"
    )
    module_4corner : StringProperty(
        name = "Module 4-Corner",
        description = "Collection for 4-Corner pieces",
        default = "Module_4Corner"
    )
    module_5corner : StringProperty(
        name = "Module 5-Corner",
        description = "Collection for 5-Corner pieces",
        default = "Module_5Corner"
    )
    module_6end : StringProperty(
        name = "Module 6-End",
        description = "Collection for 6-End pieces",
        default = "Module_6End"
    )
    module_straight : StringProperty(
        name = "Module Straight",
        description = "Collection for straight pieces",
        default = "Module_Straight"
    )
    module_end : StringProperty(
        name = "Module End",
        description = "Collection for end pieces",
        default = "Module_End"
    )

    '''
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    '''

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
        # Seed Value
        colrow.label(text="Seed Value:")
        colrow = col.row(align = True)
        colrow.prop(self, "seed_value", expand=True, text="")
        colrow = col.row(align = True)
        # Output Collection
        colrow.label(text="Output Collection:")
        colrow = col.row(align=True)
        colrow.prop(self, "output_collection", expand=True, text="")
        colrow = col.row(align=True)
        # Max Modules
        colrow.label(text="Maximum Modules:")
        colrow = col.row(align=True)
        colrow.prop(self, "max_modules", expand=True, text="")
        colrow = col.row(align=True)
        # Branch Minimum
        colrow.label(text="Branch Minimum Length:")
        colrow = col.row(align=True)
        colrow.prop(self, "branch_min", expand=True, text="")
        colrow = col.row(align=True)
        # Branch Maximum
        colrow.label(text="Branch Maximum Length:")
        colrow = col.row(align=True)
        colrow.prop(self, "branch_max", expand=True, text="")
        colrow = col.row(align=True)
        # Chance Level
        colrow.label(text="Chance Level:")
        colrow = col.row(align=True)
        colrow.prop(self, "chance_level", expand=True, text="")
        colrow = col.row(align=True)
        # Allow Spin
        colrow.prop(self, "allow_spin", expand=True, text="Allow Spin")
        colrow = col.row(align=True)
        # Move Offset
        colrow.label(text="Move Offset:")
        colrow = col.row(align=True)
        colrow.prop(self, "move_offset", expand=True, text="")

        # Box - Module Collections
        box_modules = layout.box()
        box_modules.label(text="Module Collections")
        col = box_modules.column()
        colrow = col.row(align=True)
        # module_l
        colrow.prop(self, "module_l", expand=True, text="L")
        colrow = col.row(align=True)
        # module_t
        colrow.prop(self, "module_t", expand=True, text="T")
        colrow = col.row(align=True)
        # module_x
        colrow.prop(self, "module_x", expand=True, text="X")
        colrow = col.row(align=True)
        # module_3corner
        colrow.prop(self, "module_3corner", expand=True, text="3 Corner")
        colrow = col.row(align=True)
        # module_4corner
        colrow.prop(self, "module_4corner", expand=True, text="4 Corner")
        colrow = col.row(align=True)
        # module_5corner
        colrow.prop(self, "module_5corner", expand=True, text="5 Corner")
        colrow = col.row(align=True)
        # module_6end
        colrow.prop(self, "module_6end", expand=True, text="6 End")
        colrow = col.row(align=True)
        # module_straight
        colrow.prop(self, "module_straight", expand=True, text="Straight")
        colrow = col.row(align=True)
        # module_end
        colrow.prop(self, "module_end", expand=True, text="End")
        colrow = col.row(align=True)

    def execute(self, context):

        # Context Setup
        scene = context.scene
        sO = bpy.context.active_object
        
        if not self.enable_generation:
            return {'FINISHED'}
        
        # Get Generation_Result Reference:
        generation_result = None
        if self.output_collection in bpy.data.collections:
            generation_result = bpy.data.collections[self.output_collection]
            if len(generation_result.objects)>0:
                if len(bpy.context.selected_objects)>0:
                    for so in bpy.context.selected_objects:
                        so.select_set(False)
                for oldObj in generation_result.objects:
                    oldObj.select_set(True)
                bpy.ops.object.delete()
        else:
            bpy.data.collections.new(self.output_collection)
            generation_result = bpy.data.collections[self.output_collection]
            bpy.context.scene.collection.children.link(generation_result)
        
        # Setting global variables from JSON config.
        global maxModules
        maxModules = self.max_modules # (Int) Maximum number of modules in total
        global branchMin
        branchMin = self.branch_min # (Int) Minimum length of a branch
        global branchMax
        branchMax = self.branch_max # (Int) Maximum length of a branch
        global chanceLevel
        chanceLevel = self.chance_level # (Int) Percentage change for a branch to split
        global allowSpin
        allowSpin = self.allow_spin # (Bool) Whether to allow spin on straight modules
        global move_offset
        move_offset = self.move_offset # (Int) Offset for cell vectors
        global cell_count
        cell_count = 0 # (Int) For counting the number of cells populated
        global start_procedure 
        start_procedure = True # (Bool) Whether procedure has just started
        global cellList 
        cellList = [] # (List) For the populated cell data
        global branchDict
        branchDict = [] # (List) For the start of branches
        global branchRef
        branchRef = [] # (List) Temp duplicate of branchList for iterating
        global extDict 
        extDict = {} # (Dict) For the external port references
        global portBin
        portBin = [] # (List) For object references to duplicated port objects
        
        # Validation check
        canProceed = True

        # Preparing module collections
        if self.module_l in bpy.data.collections:
            module_l = bpy.data.collections[self.module_l]
        else:
            canProceed=False
        if self.module_t in bpy.data.collections:
            module_t = bpy.data.collections[self.module_t]
        else:
            canProceed=False
        if self.module_x in bpy.data.collections:
            module_x = bpy.data.collections[self.module_x]
        else:
            canProceed=False
        if self.module_3corner in bpy.data.collections:
            module_3corner = bpy.data.collections[self.module_3corner]
        else:
            canProceed=False
        if self.module_4corner in bpy.data.collections:
            module_4corner = bpy.data.collections[self.module_4corner]
        else:
            canProceed=False
        if self.module_5corner in bpy.data.collections:
            module_5corner = bpy.data.collections[self.module_5corner]
        else:
            canProceed=False
        if self.module_6end in bpy.data.collections:
            module_6end = bpy.data.collections[self.module_6end]
        else:
            canProceed=False
        if self.module_straight in bpy.data.collections:
            module_straight = bpy.data.collections[self.module_straight]
        else:
            canProceed=False
        if self.module_end in bpy.data.collections:
            module_end = bpy.data.collections[self.module_straight]
        else:
            canProceed=False

        if canProceed is False:
            return {'FINISHED'}
        
        # Prepare common radians
        r90 = 1.570796
        r180 = 3.141593
        
        # Populate the virtual grid
        generate_cells()
        
        # Cycle through cellList
        for active_cell in cellList:

            # Perform Neighbour check on current cell
            is_xpos = is_xneg = False
            is_ypos = is_yneg = False
            is_zpos = is_zneg = False

            # Prepare binary representation of neighbour data
            nID = ""
            # X Positive
            check_vector = Vector((active_cell[0],active_cell[1],active_cell[2]))
            check_vector[0] += move_offset
            if check_vector in cellList:
                is_xpos = True
                nID = nID + "1"
            else:
                is_xpos = False
                nID = nID + "0"
            # X Negative
            check_vector = Vector((active_cell[0],active_cell[1],active_cell[2]))
            check_vector[0] -= move_offset
            if check_vector in cellList:
                is_xneg = True
                nID = nID + "1"
            else:
                is_xneg = False
                nID = nID + "0"
            # Y Positive
            check_vector = Vector((active_cell[0],active_cell[1],active_cell[2]))
            check_vector[1] += move_offset
            if check_vector in cellList:
                is_ypos = True
                nID = nID + "1"
            else:
                is_ypos = False
                nID = nID + "0"
            # Y Negative
            check_vector = Vector((active_cell[0],active_cell[1],active_cell[2]))
            check_vector[1] -= move_offset
            if check_vector in cellList:
                is_yneg = True
                nID = nID + "1"
            else:
                is_yneg = False
                nID = nID + "0"
            # Z Positive
            check_vector = Vector((active_cell[0],active_cell[1],active_cell[2]))
            check_vector[2] += move_offset
            if check_vector in cellList:
                is_zpos = True
                nID = nID + "1"
            else:
                is_zpos = False
                nID = nID + "0"
            # Z Negative
            check_vector = Vector((active_cell[0],active_cell[1],active_cell[2]))
            check_vector[2] -= move_offset
            if check_vector in cellList:
                is_zneg = True
                nID = nID + "1"
            else:
                is_zneg = False
                nID = nID + "0"
                
            # Decide which module to spawn
            new_module = None

            '''
            >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
                                L      MODULE      CONDITION
            >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
            '''
            # L module condition
            if ((nID == "000110") or  #1
                (nID == "100010") or  #2
                (nID == "001010") or  #3
                (nID == "010010") or  #4
                (nID == "100100") or  #5
                (nID == "101000") or  #6
                (nID == "011000") or  #7
                (nID == "010100") or  #8
                (nID == "000101") or  #9
                (nID == "100001") or  #10
                (nID == "001001") or  #11
                (nID == "010001")):     #12
                # Get list of possible modules
                object_names = []
                for obj_ref in module_l.objects:
                    if 'pos' not in obj_ref.name:
                        object_names.append(obj_ref.name)
                
                if len(object_names) > 0:
                    randID = random.randint(0,len(object_names)-1)
                    new_obj = module_l.objects[object_names[randID]]
                    # Create Object
                    new_module = new_obj.copy()
                    new_module.data = new_obj.data.copy()
                    new_module.animation_data_clear()
                    
                    # Link to Generation Result
                    generation_result.objects.link(new_module)
                    # Change Visibility
                    new_module.hide_viewport = False
                    new_module.hide_render = False
                    
                    # Move Object
                    new_module.location = active_cell
                    
                    # Check for rotation 
                    if nID == "000110": # 1
                        # Same as original, no need to rotate.
                        old_euler = new_module.rotation_euler
                        old_euler[2] += 0
                        new_module.rotation_euler = old_euler
                        
                    if nID == "100010": # 2
                        # X+ Z+, 90+ on Z 
                        old_euler = new_module.rotation_euler
                        old_euler[2] += r90
                        new_module.rotation_euler = old_euler
                        
                    if nID == "001010": # 3
                        # Y+ Z+, 180+ on Z
                        old_euler = new_module.rotation_euler
                        old_euler[2] += r180
                        new_module.rotation_euler = old_euler
                        
                    if nID == "010010": # 4
                        # X- Z+, -90 on Z
                        old_euler = new_module.rotation_euler
                        old_euler[2] += -r90
                        new_module.rotation_euler = old_euler
                    
                    if nID == "100100": # 5
                        # Y- X+, 90+ on Y
                        old_euler = new_module.rotation_euler
                        old_euler[1] += r90
                        new_module.rotation_euler = old_euler
                        
                    if nID == "101000": # 6
                        # X+ Y+, 90+Y / 90+Z
                        old_euler = new_module.rotation_euler
                        old_euler[1] += r90
                        old_euler[2] += r90
                        new_module.rotation_euler = old_euler
                        
                    if nID == "011000": # 7
                        # X- Y+, 90+y / 180+Z
                        old_euler = new_module.rotation_euler
                        old_euler[1] += r90
                        old_euler[2] += r180
                        new_module.rotation_euler = old_euler
                        
                    if nID == "010100": # 8
                        # Y- X-, -90 Y
                        old_euler = new_module.rotation_euler
                        old_euler[1] += -r90
                        new_module.rotation_euler = old_euler
                        
                    if nID == "000101": # 9
                        # Y- Z-, 180+Y
                        old_euler = new_module.rotation_euler
                        old_euler[1] += r180
                        new_module.rotation_euler = old_euler
                        
                    if nID == "100001": # 10
                        # X+ Z-, 180+ Y / 90 Z
                        old_euler = new_module.rotation_euler
                        old_euler[1] += r180
                        old_euler[2] += r90
                        new_module.rotation_euler = old_euler
                        
                    if nID == "001001": # 11
                        # Y+ Z-, 180+ Y / 180+ Z
                        old_euler = new_module.rotation_euler
                        old_euler[1] += r180
                        old_euler[2] += r180
                        new_module.rotation_euler = old_euler
                        
                    if nID == "010001": # 12
                        # X- Z-, 180+ Y, -90 Z
                        old_euler = new_module.rotation_euler
                        old_euler[1] += r180
                        old_euler[2] += -r90 
                        new_module.rotation_euler = old_euler
                
                # Update the view layer
                bpy.context.view_layer.update()

            '''
            >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
                                T      MODULE      CONDITION
            >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
            '''
            # T module condition
            if ((nID == "110100") or  # 1
                (nID == "101100") or  # 2
                (nID == "111000") or  # 3
                (nID == "011100") or  # 4
                (nID == "000111") or  # 5
                (nID == "100011") or  # 6
                (nID == "001011") or  # 7
                (nID == "010011") or  # 8
                (nID == "110001") or  # 9
                (nID == "001101") or  # 10
                (nID == "110010") or  # 11
                (nID == "001110")):   # 12
                
                # Get list of possible modules
                object_names = []
                for obj_ref in module_t.objects:
                    if 'pos' not in obj_ref.name:
                        object_names.append(obj_ref.name)
                
                if len(object_names) > 0:
                    randID = random.randint(0,len(object_names)-1)
                    new_obj = module_t.objects[object_names[randID]]
                    # Create Object
                    new_module = new_obj.copy()
                    new_module.data = new_obj.data.copy()
                    new_module.animation_data_clear()
                    
                    # Link to Generation Result
                    generation_result.objects.link(new_module)
                    # Change Visibility
                    new_module.hide_viewport = False
                    new_module.hide_render = False
                    
                    # Move Object
                    new_module.location = active_cell
                    
                    # Check for rotation 
                    if nID == "110100": # 1
                        # Same as original, do nothing
                        old_euler = new_module.rotation_euler
                        old_euler[2] += 0
                        new_module.rotation_euler = old_euler
                    
                    if nID == "101100": # 2
                        # X+ Y- Y+, 90+ Z
                        old_euler = new_module.rotation_euler
                        old_euler[2] += r90
                        new_module.rotation_euler = old_euler
                        
                    if nID == "111000": # 3
                        # X- X+ Y+, 180+ Z
                        old_euler = new_module.rotation_euler
                        old_euler[2] += r180
                        new_module.rotation_euler = old_euler
                        
                    if nID == "011100": # 4
                        # Y- X- Y+, -90 Z
                        old_euler = new_module.rotation_euler
                        old_euler[2] += -r90
                        new_module.rotation_euler = old_euler
                        
                    if nID == "000111": # 5
                        # Y- Z- Z+, 90+ Y
                        old_euler = new_module.rotation_euler
                        old_euler[1] += r90
                        new_module.rotation_euler = old_euler
                        
                    if nID == "100011": # 6
                        # Z+ X+ Z-, 90+Y / 90+Z
                        old_euler = new_module.rotation_euler
                        old_euler[1] += r90
                        old_euler[2] += r90
                        new_module.rotation_euler = old_euler
                        
                    if nID == "001011": # 7
                        # Z+ Y+ Z-, 90+Y / 180+Z
                        old_euler = new_module.rotation_euler
                        old_euler[1] += r90
                        old_euler[2] += r180
                        new_module.rotation_euler = old_euler
                        
                    if nID == "010011": # 8
                        # Z+ X- Z-, 90+Y / -90 Z
                        old_euler = new_module.rotation_euler
                        old_euler[1] += r90
                        old_euler[2] += -r90
                        new_module.rotation_euler = old_euler
                        
                    if nID == "110001": # 9
                        # X- X+ Z-, 90+X
                        old_euler = new_module.rotation_euler
                        old_euler[0] += r90
                        new_module.rotation_euler = old_euler
                        
                    if nID == "001101": # 10
                        # Y- Y+ Z-, 90+X / 90+Z
                        old_euler = new_module.rotation_euler
                        old_euler[0] += r90
                        old_euler[2] += r90
                        new_module.rotation_euler = old_euler
                        
                    if nID == "110010": # 11
                        # X- Z+ X+, -90 X
                        old_euler = new_module.rotation_euler
                        old_euler[0] += -r90
                        new_module.rotation_euler = old_euler
                        
                    if nID == "001110": # 12
                        # Y- Z+ Y+, -90 X / 90+ Z
                        old_euler = new_module.rotation_euler
                        old_euler[0] += -r90
                        old_euler[2] += r90
                        new_module.rotation_euler = old_euler
                
                # Update the view layer
                bpy.context.view_layer.update()
                
            '''
            >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
                                X      MODULE      CONDITION
            >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
            '''
            # X module condition
            if ((nID == "111100") or  # 1
                (nID == "001111") or  # 2
                (nID == "110011")):   # 3

                # Get list of possible modules
                object_names = []
                for obj_ref in module_x.objects:
                    if 'pos' not in obj_ref.name:
                        object_names.append(obj_ref.name)
                
                if len(object_names) > 0:
                    randID = random.randint(0,len(object_names)-1)
                    new_obj = module_x.objects[object_names[randID]]
                    # Create Object
                    new_module = new_obj.copy()
                    new_module.data = new_obj.data.copy()
                    new_module.animation_data_clear()
                    
                    # Link to Generation Result
                    generation_result.objects.link(new_module)
                    # Change Visibility
                    new_module.hide_viewport = False
                    new_module.hide_render = False
                    
                    # Move Object
                    new_module.location = active_cell
                    
                    # Check for rotation 
                    if nID == "111100": # 1
                        # Y- Y+ X- X+ , Same as original, do nothing
                        old_euler = new_module.rotation_euler
                        old_euler[2] += 0
                        new_module.rotation_euler = old_euler
                        
                    if nID == "001111": # 2
                        # Y- Y+ Z- Z+ , 90+Y
                        old_euler = new_module.rotation_euler
                        old_euler[1] += r90
                        new_module.rotation_euler = old_euler
                        
                    if nID == "110011": # 3
                        # X- X+ Z- Z+ , 90+X
                        old_euler = new_module.rotation_euler
                        old_euler[0] += r90
                        new_module.rotation_euler = old_euler
                
                # Update the view layer
                bpy.context.view_layer.update()
                
            '''
            >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
                                3Corner      MODULE      CONDITION
            >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
            '''
            # 3Corner module condition
            if ((nID == "100110") or  # 1
                (nID == "101010") or  # 2
                (nID == "011010") or  # 3
                (nID == "010110") or  # 4
                (nID == "100101") or  # 5
                (nID == "101001") or  # 6
                (nID == "011001") or  # 7
                (nID == "010101")):   # 8

                 #Get list of possible modules
                object_names = []
                for obj_ref in module_3corner.objects:
                    if 'pos' not in obj_ref.name:
                        object_names.append(obj_ref.name)
                
                if len(object_names) > 0:
                    randID = random.randint(0,len(object_names)-1)
                    new_obj = module_3corner.objects[object_names[randID]]
                    # Create Object
                    new_module = new_obj.copy()
                    new_module.data = new_obj.data.copy()
                    new_module.animation_data_clear()
                    
                    # Link to Generation Result
                    generation_result.objects.link(new_module)
                    # Change Visibility
                    new_module.hide_viewport = False
                    new_module.hide_render = False
                    
                    # Move Object
                    new_module.location = active_cell
                    
                    # Check for rotation 
                    if nID == "100110": # 1
                        # Y- X+ Z+ , Same as original, do nothing
                        old_euler = new_module.rotation_euler
                        old_euler[2] += 0
                        new_module.rotation_euler = old_euler
                        
                    if nID == "101010": # 2
                        # Y+ X+ Z+ , 90+Z
                        old_euler = new_module.rotation_euler
                        old_euler[2] += r90
                        new_module.rotation_euler = old_euler
                        
                    if nID == "011010": # 3
                        # Y+ X- Z+ , 180+Z
                        old_euler = new_module.rotation_euler
                        old_euler[2] += r180
                        new_module.rotation_euler = old_euler
                        
                    if nID == "010110": # 4
                        # Y- X- Z+ , -90 Z
                        old_euler = new_module.rotation_euler
                        old_euler[2] += -r90
                        new_module.rotation_euler = old_euler
                        
                    if nID == "100101": # 5
                        # Y- X+ Z- , 90+Y
                        old_euler = new_module.rotation_euler
                        old_euler[1] += r90
                        new_module.rotation_euler = old_euler
                        
                    if nID == "101001": # 6
                        # Y+ X+ Z- , 90+Y / 90+Z
                        old_euler = new_module.rotation_euler
                        old_euler[1] += r90
                        old_euler[2] += r90
                        new_module.rotation_euler = old_euler
                        
                    if nID == "011001": # 7
                        # Y+ X- Z- , 90+Y / 180+Z
                        old_euler = new_module.rotation_euler
                        old_euler[1] += r90
                        old_euler[2] += r180
                        new_module.rotation_euler = old_euler
                        
                    if nID == "010101": # 8
                        # Y- X- Z- , 90+Y / -90 Z
                        old_euler = new_module.rotation_euler
                        old_euler[1] += r90
                        old_euler[2] += -r90
                        new_module.rotation_euler = old_euler
                
                # Update the view layer
                bpy.context.view_layer.update()
                
            '''
            >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
                                4Corner      MODULE      CONDITION
            >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
            '''
            # 4Corner module condition
            if ((nID == "110110") or  # 1
                (nID == "101110") or  # 2
                (nID == "111010") or  # 3
                (nID == "011110") or  # 4
                (nID == "100111") or  # 5
                (nID == "101011") or  # 6
                (nID == "011011") or  # 7
                (nID == "010111") or  # 8
                (nID == "110101") or  # 9
                (nID == "101101") or  # 10
                (nID == "111001") or  # 11
                (nID == "011101")):   # 12
                
                # Get list of possible modules
                object_names = []
                for obj_ref in module_4corner.objects:
                    if 'pos' not in obj_ref.name:
                        object_names.append(obj_ref.name)
                
                if len(object_names) > 0:
                    randID = random.randint(0,len(object_names)-1)
                    new_obj = module_4corner.objects[object_names[randID]]
                    # Create Object
                    new_module = new_obj.copy()
                    new_module.data = new_obj.data.copy()
                    new_module.animation_data_clear()
                    
                    # Link to Generation Result
                    generation_result.objects.link(new_module)
                    # Change Visibility
                    new_module.hide_viewport = False
                    new_module.hide_render = False
                    
                    # Move Object
                    new_module.location = active_cell
                    
                    # Check for rotation 
                    if nID == "110110": # 1
                        # Same as original
                        old_euler = new_module.rotation_euler
                        old_euler[2] += 0
                        new_module.rotation_euler = old_euler
                        
                    if nID == "101110": # 2
                        # 90+ Z
                        old_euler = new_module.rotation_euler
                        old_euler[2] += r90
                        new_module.rotation_euler = old_euler
                        
                    if nID == "111010": # 3
                        # 180+Z
                        old_euler = new_module.rotation_euler
                        old_euler[2] += r180
                        new_module.rotation_euler = old_euler
                        
                    if nID == "011110": # 4
                        # -90 Z
                        old_euler = new_module.rotation_euler
                        old_euler[2] += -r90
                        new_module.rotation_euler = old_euler
                        
                    if nID == "100111": # 5
                        # 90+Y
                        old_euler = new_module.rotation_euler
                        old_euler[1] += r90
                        new_module.rotation_euler = old_euler
                        
                    if nID == "101011": # 6
                        # 90+Y / 90+Z
                        old_euler = new_module.rotation_euler
                        old_euler[1] += r90
                        old_euler[2] += r90
                        new_module.rotation_euler = old_euler
                        
                    if nID == "011011": # 7
                        # 90+Y / 180+Z
                        old_euler = new_module.rotation_euler
                        old_euler[1] += r90
                        old_euler[2] += r180
                        new_module.rotation_euler = old_euler
                        
                    if nID == "010111": # 8
                        # 90+Y / -90 Z
                        old_euler = new_module.rotation_euler
                        old_euler[1] += r90
                        old_euler[2] += -r90
                        new_module.rotation_euler = old_euler
                        
                    if nID == "110101": # 9
                        # 180+Y 
                        old_euler = new_module.rotation_euler
                        old_euler[1] += r180
                        new_module.rotation_euler = old_euler
                        
                    if nID == "101101": # 10
                        # 180+Y / 90+Z
                        old_euler = new_module.rotation_euler
                        old_euler[1] += r180
                        old_euler[2] += r90
                        new_module.rotation_euler = old_euler
                        
                    if nID == "111001": # 11
                        # 180+Y / 180+Z
                        old_euler = new_module.rotation_euler
                        old_euler[1] += r180
                        old_euler[2] += r180
                        new_module.rotation_euler = old_euler
                        
                    if nID == "011101": # 12
                        # 180+Y / -90 Z
                        old_euler = new_module.rotation_euler
                        old_euler[1] += r180
                        old_euler[2] += -r90
                        new_module.rotation_euler = old_euler
                
                # Update the view layer
                bpy.context.view_layer.update()
                
            '''
            >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
                                5Corner      MODULE      CONDITION
            >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
            '''
            # 5Corner module condition
            if ((nID == "111110") or  # 1
                (nID == "111101") or  # 2
                (nID == "101111") or  # 3
                (nID == "111011") or  # 4
                (nID == "011111") or  # 5
                (nID == "110111")):   # 6

                # Get list of possible modules
                object_names = []
                for obj_ref in module_5corner.objects:
                    if 'pos' not in obj_ref.name:
                        object_names.append(obj_ref.name)
                
                if len(object_names) > 0:
                    randID = random.randint(0,len(object_names)-1)
                    new_obj = module_5corner.objects[object_names[randID]]
                    # Create Object
                    new_module = new_obj.copy()
                    new_module.data = new_obj.data.copy()
                    new_module.animation_data_clear()
                    
                    # Link to Generation Result
                    generation_result.objects.link(new_module)
                    # Change Visibility
                    new_module.hide_viewport = False
                    new_module.hide_render = False
                    
                    # Move Object
                    new_module.location = active_cell
                    
                    # Check for rotation 
                    if nID == "111110": # 1
                        # Same as original
                        old_euler = new_module.rotation_euler
                        old_euler[2] += 0
                        new_module.rotation_euler = old_euler
                        
                    if nID == "111101": # 2
                        # 180+Y
                        old_euler = new_module.rotation_euler
                        old_euler[1] += r180
                        new_module.rotation_euler = old_euler
                        
                    if nID == "101111": # 3
                        # 90+Y
                        old_euler = new_module.rotation_euler
                        old_euler[1] += r90
                        new_module.rotation_euler = old_euler
                        
                    if nID == "111011": # 4
                        # 90+Y / 90+Z
                        old_euler = new_module.rotation_euler
                        old_euler[1] += r90
                        old_euler[2] += r90
                        new_module.rotation_euler = old_euler
                        
                    if nID == "011111": # 5
                        # 90+Y / 180+Z
                        old_euler = new_module.rotation_euler
                        old_euler[1] += r90
                        old_euler[2] += r180
                        new_module.rotation_euler = old_euler
                        
                    if nID == "110111": # 6
                        # 90+Y / -90 Z
                        old_euler = new_module.rotation_euler
                        old_euler[1] += r90
                        old_euler[2] += -r90
                        new_module.rotation_euler = old_euler
                
                # Update the view layer
                bpy.context.view_layer.update()
                
            '''
            >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
                                MODULE_6END      MODULE      CONDITION
            >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
            '''
            # 6End module condition
            if (nID == "111111"):
                # Get list of possible modules
                object_names = []
                for obj_ref in module_6end.objects:
                    if 'pos' not in obj_ref.name:
                        object_names.append(obj_ref.name)
                
                if len(object_names) > 0:
                    randID = random.randint(0,len(object_names)-1)
                    new_obj = module_6end.objects[object_names[randID]]
                    # Create Object
                    new_module = new_obj.copy()
                    new_module.data = new_obj.data.copy()
                    new_module.animation_data_clear()
                    
                    # Link to Generation Result
                    generation_result.objects.link(new_module)
                    # Change Visibility
                    new_module.hide_viewport = False
                    new_module.hide_render = False
                    
                    # Move Object
                    new_module.location = active_cell
                
                # Update the view layer
                bpy.context.view_layer.update()
                
            '''
            >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
                                STRAIGHT      MODULE      CONDITION
            >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
            '''
            # Straight module condition
            if ((nID == "110000") or 
                (nID == "001100") or 
                (nID == "000011")):

                # Perform diagonal neighbour checks
                dCheck = []
                # Angular
                dCheck.append(Vector((active_cell[0]-move_offset,active_cell[1]-move_offset,active_cell[2]-move_offset)))
                dCheck.append(Vector((active_cell[0]+move_offset,active_cell[1]-move_offset,active_cell[2]-move_offset)))
                dCheck.append(Vector((active_cell[0]-move_offset,active_cell[1]-move_offset,active_cell[2]+move_offset)))
                dCheck.append(Vector((active_cell[0]+move_offset,active_cell[1]-move_offset,active_cell[2]+move_offset)))
                dCheck.append(Vector((active_cell[0]-move_offset,active_cell[1]+move_offset,active_cell[2]-move_offset)))
                dCheck.append(Vector((active_cell[0]+move_offset,active_cell[1]+move_offset,active_cell[2]-move_offset)))
                dCheck.append(Vector((active_cell[0]-move_offset,active_cell[1]+move_offset,active_cell[2]+move_offset)))
                dCheck.append(Vector((active_cell[0]+move_offset,active_cell[1]+move_offset,active_cell[2]+move_offset)))
                # Adjacent
                dCheck.append(Vector((active_cell[0],active_cell[1]-move_offset,active_cell[2]-move_offset)))
                dCheck.append(Vector((active_cell[0],active_cell[1]+move_offset,active_cell[2]-move_offset)))
                dCheck.append(Vector((active_cell[0],active_cell[1]-move_offset,active_cell[2]+move_offset)))
                dCheck.append(Vector((active_cell[0],active_cell[1]+move_offset,active_cell[2]+move_offset)))
                dCheck.append(Vector((active_cell[0]+move_offset,active_cell[1],active_cell[2]-move_offset)))
                dCheck.append(Vector((active_cell[0]+move_offset,active_cell[1],active_cell[2]+move_offset)))
                dCheck.append(Vector((active_cell[0]-move_offset,active_cell[1],active_cell[2]-move_offset)))
                dCheck.append(Vector((active_cell[0]-move_offset,active_cell[1],active_cell[2]+move_offset)))
                dCheck.append(Vector((active_cell[0]-move_offset,active_cell[1]+move_offset,active_cell[2])))
                dCheck.append(Vector((active_cell[0]+move_offset,active_cell[1]+move_offset,active_cell[2])))
                dCheck.append(Vector((active_cell[0]-move_offset,active_cell[1]-move_offset,active_cell[2])))
                dCheck.append(Vector((active_cell[0]+move_offset,active_cell[1]-move_offset,active_cell[2])))
                
                dClear = True

                # Are the extra neighbour cells clear?
                for diag in dCheck:
                    if diag in cellList:
                        dClear = False
                
                # Get list of possible modules
                object_names = []
                for obj_ref in module_straight.objects:                        
                    if dClear == True:
                        object_names.append(obj_ref.name)
                    else:
                        if 'ext_' not in obj_ref.name:
                            # Ignore ext_ straight modules due to neighbours
                            object_names.append(obj_ref.name)
                
                if len(object_names) > 0:
                    randID = random.randint(0,len(object_names)-1)
                    new_obj = module_straight.objects[object_names[randID]]
                    # Create Object
                    new_module = new_obj.copy()
                    new_module.data = new_obj.data.copy()
                    new_module.animation_data_clear()
                    
                    # Link to Generation Result
                    generation_result.objects.link(new_module)
                    # Change Visibility
                    new_module.hide_viewport = False
                    new_module.hide_render = False
                    
                    # Move Object
                    new_module.location = active_cell
                    
                    # Check for rotation
                    if nID == "110000": # X pos and neg
                        # Need to rotate 90 degrees on Z axis
                        old_euler = new_module.rotation_euler
                        old_euler[2] += r90
                        
                        # Random rotation on Y axis for spin deviation
                        if allowSpin:
                            spinRand = random.randint(0,1)
                            if spinRand == 1:
                                old_euler[1] += r90
                        
                        new_module.rotation_euler = old_euler
                    if nID == "001100":
                        # Same as original, no need to rotate
                        old_euler = new_module.rotation_euler
                        old_euler[0]+=0
                        
                        # Random rotation on Y axis for spin deviation
                        if allowSpin:
                            spinRand = random.randint(0,1)
                            if spinRand == 1:
                                old_euler[1] += r90
                        
                        new_module.rotation_euler = old_euler
                    if nID == "000011": # Z pos and neg
                        # Need to rotate 90 degrees on X axis
                        old_euler = new_module.rotation_euler
                        old_euler[0] += r90
                        
                        # Random rotation on Z axis for spin deviation
                        if allowSpin:
                            spinRand = random.randint(0,1)
                            if spinRand == 1:
                                old_euler[2] += r90
                        
                        new_module.rotation_euler = old_euler
                
                # Update the view layer
                bpy.context.view_layer.update()

            '''
            >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
                                END      MODULE      CONDITION
            >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
            '''
            # End module condition
            if ((nID == "100000") or 
                (nID == "010000") or 
                (nID == "001000") or 
                (nID == "000100") or 
                (nID == "000010") or  
                (nID == "000001")):

                # Get list of possible modules
                object_names = []
                for obj_ref in module_end.objects:
                    if 'pos' not in obj_ref.name:
                        object_names.append(obj_ref.name)
                
                if len(object_names) > 0:
                    randID = random.randint(0,len(object_names)-1)
                    new_obj = module_end.objects[object_names[randID]]
                    # Create Object
                    new_module = new_obj.copy()
                    new_module.data = new_obj.data.copy()
                    new_module.animation_data_clear()
                    
                    # Link to Generation Result
                    generation_result.objects.link(new_module)
                    # Change Visibility
                    new_module.hide_viewport = False
                    new_module.hide_render = False
                    
                    # Move Object
                    new_module.location = active_cell
                    
                    # Check for rotation 
                    if nID == "100000":
                        # Positive X, need to rotate 90 degrees on Z axis
                        old_euler = new_module.rotation_euler
                        old_euler[2] += r90
                        new_module.rotation_euler = old_euler
                    if nID == "010000":
                        # Negative X, need to rotate -90 degrees on Z axis
                        old_euler = new_module.rotation_euler
                        old_euler[2] -= r90
                        new_module.rotation_euler = old_euler
                    if nID == "001000":
                        # Positive YNeed to rotate 180 degrees on Z axis
                        old_euler = new_module.rotation_euler
                        old_euler[2] += r180
                        new_module.rotation_euler = old_euler
                    if nID == "000100":
                        # Negative Y, don't need to to anything.
                        old_euler = new_module.rotation_euler
                        old_euler[2] += 0
                        new_module.rotation_euler = old_euler
                    if nID == "000010":
                        # Positive Z, need to rotate -90 degrees on X axis
                        old_euler = new_module.rotation_euler
                        old_euler[0] -= r90
                        new_module.rotation_euler = old_euler
                    if nID == "000001":
                        # Negative Z, need to rotate 90 degrees on X axis
                        old_euler = new_module.rotation_euler
                        old_euler[0] += r90
                        new_module.rotation_euler = old_euler
                
                # Update the view layer
                bpy.context.view_layer.update()
        
        # FOR THE FUTURE - Delete all objects in portBin
        for ob in bpy.context.selected_objects:
            ob.select_set(False)
        if len(portBin) > 0:
            for port in portBin:
                port.select_set(True)
            bpy.ops.object.delete()
        # Clear cellDict
        cellDict = {}
        # Clear extDict
        extDict = {}
        # Clear branchDict
        branchDict = {}
        # Clear branchRef
        branchRef = {}
        return {'FINISHED'}

def display_result_cells():
    for cell in cellList:
        print(str(cell))

def cube_populate():
    generation_result = bpy.data.collections['Generation_Result']
    for cell in cellList:
        bpy.ops.mesh.primitive_cube_add()
        so = bpy.context.active_object
        so.location = cell
        generation_result.objects.link(so)

def populate_branch(current_cell, branchLength, chosenAxis, chosenDir):
    global maxModules
    global branchMin
    global branchMax
    global chanceLevel
    global move_offset
    global cell_count
    global cellList
    global branchList
    global branchRef
    global extDict
    global portBin
    
    if cell_count < maxModules:
        # For the length of the branch
        i = 1
        while i <= branchLength:
            # Increment current_cell using axis and direction
            new_cell = Vector((current_cell[0],current_cell[1],current_cell[2]))
            if chosenAxis == 'X':
                if chosenDir == 'POS':
                    new_cell[0] += move_offset
                if chosenDir == 'NEG':
                    new_cell[0] -= move_offset
            if chosenAxis == 'Y':
                if chosenDir == 'POS':
                    new_cell[1] += move_offset
                if chosenDir == 'NEG':
                    new_cell[1] -= move_offset
            if chosenAxis == 'Z':
                if chosenDir == 'POS':
                    new_cell[2] += move_offset
                if chosenDir == 'NEG':
                    new_cell[2] -= move_offset
            # Check for overlap
            newVector = Vector((new_cell[0],new_cell[1],new_cell[2]))
            if newVector not in cellList:
                # Record curent_cell in cellList
                cellList.append(Vector((new_cell[0],new_cell[1],new_cell[2])))
                cell_count += 1
                current_cell = new_cell
            
                # Get branchChance between 1,100
                branchChance = random.randint(1,100)
                if branchChance <= chanceLevel:
                    # randAxis = rand between 1,4
                    randAxis = random.randint(1,4)
                    axisList = []
                    # if chosenAxis is 'X':
                    if chosenAxis == 'X':
                        # axisList add Y+ Y- Z+ Z-
                        axisList.append("Y:POS")
                        axisList.append("Y:NEG")
                        axisList.append("Z:POS")
                        axisList.append("Z:NEG")
                    # if chosenAxis is 'Y':
                    if chosenAxis == 'Y':
                        # axisList add X+ X- Z+ Z-
                        axisList.append("X:POS")
                        axisList.append("X:NEG")
                        axisList.append("Z:POS")
                        axisList.append("Z:NEG")
                    # if chosenAxis is 'Z':
                    if chosenAxis == 'Z':
                        # axisList is X+ X- Y+ Y-
                        axisList.append("X:POS")
                        axisList.append("X:NEG")
                        axisList.append("Y:POS")
                        axisList.append("Y:NEG")
                    # For randAxis:
                    j = 1
                    while j < randAxis:
                        random.shuffle(axisList)                    
                        cell_key = str(new_cell[0])+","+str(new_cell[1])+","+str(new_cell[2])
                        
                        branch_entry = cell_key + "/" + axisList[0]
                        # Store new branch starting point in branchList
                        branchList.append(branch_entry)
                        
                        # remove it from axisList
                        axisList.pop(0)
                        # Increment loop
                        j += i
            current_cell = Vector((new_cell[0], new_cell[1], new_cell[2]))
            # Increment Loop
            i += 1

def generate_cells():
    global maxModules
    global branchMin
    global branchMax
    global chanceLevel
    global cell_count
    global start_procedure
    global cellList
    global branchList
    global branchRef
    global extDict
    global portBin
    
    # Maxmimum cell count has been reached
    if cell_count >= maxModules:
        pass
    # Maximum cell count has not been reached
    else:
        # If this is the first branch
        if start_procedure == True:
            current_cell = Vector((0,0,0))
            
            # Add the origin cell as a starting point and increment the total cell count.
            cellList.append(Vector((current_cell[0],current_cell[1],current_cell[2])))
            cell_count += 1
            
            # Get [x] rand from (branchMin, branchMax)
            branchLength = random.randint(branchMin,branchMax)
            
            # Pick random axis, X/Y/Z [0]/[1]/[2]
            axisPick = ['X','Y','Z']
            pickAxis = random.randint(0,2)
            chosenAxis = axisPick[pickAxis]
            
            # Pick random direction, positive [+] or negative [-]
            directionPick = ['POS', 'NEG']
            pickDir = random.randint(0,1)
            chosenDir = directionPick[pickDir]
            
            # Change the boolen start_procedure so that next time
            # this function is called, we will be checking future branches.
            start_procedure = False
            
            # Call Populate Branch
            populate_branch(current_cell, branchLength, chosenAxis, chosenDir)
            generate_cells()
            
        else:
            # Try to kick off new branch loop
            if len(branchList) > 0:
                branchRef = []
                branchRef.extend(branchList)
                for newBranch in branchRef:
                    if cell_count < maxModules:
                        # Get axis and direction from newBranch
                        cell_string, axis_dir = newBranch.split("/",1)
                        chosenAxis, chosenDir = axis_dir.split(":",1)
                        
                        # Get Vector from newBranch
                        cell_x, cell_y, cell_z = cell_string.split(",")
                        new_cell = Vector((float(cell_x),float(cell_y),float(cell_z)))
                        
                        # Get [x] rand from (branchMin, branchMax)
                        branchLength = random.randint(branchMin,branchMax)
                        
                        
                        # TEMPORARY DEBUG SOLUTION:
                        if new_cell in cellList:
                            # Call Populate Branch
                            populate_branch(new_cell, branchLength, chosenAxis, chosenDir)
                    else:
                        break
                # Now loop is done, remove from branchList
                for element in branchRef:
                    branchList.remove(element)
                generate_cells()
#endregion