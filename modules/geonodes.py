#region Information
'''
This module contains useful functions for building geometry
nodes node trees inside of Blender.
'''
#endregion
#region Imports
import bpy
from easybpy import *
#endregion
#region Main Class
class GeometryNodes:
    
    # Variables
    tree = None
    control = None
    group_input = None
    group_output = None
    
    # Class init
    def __init__(self, name = "New Node Object"):
        control = self.create_control_object(name)
    
    def create_control_object(self, name):
        o = create_object(name, "Node Objects")
        select_only(o)
        bpy.ops.node.new_geometry_nodes_modifier()
        
        # Essential variables for the class.
        self.tree = self.get_node_tree(o)
        self.group_input = self.tree.nodes["Group Input"]
        self.group_output = self.tree.nodes["Group Output"]
        return o
    
    def get_node_tree(self, object):
        return object.modifiers["GeometryNodes"].node_group
    
    def add_object(self, ref = None):
        objnode = self.tree.nodes.new(type="GeometryNodeObjectInfo")
        if ref is not None:
            objref = get_object(ref)
            objnode.inputs[0].default_value = objref
        return objnode
    
    def output_geometry(self, ref):
        node = get_node(self.tree.nodes,ref)
        index = get_index_of_output(node, "Geometry")
        create_node_link(node.outputs[index], self.group_output.inputs[0])
        
    def connect_geometry(self, first, second):
        first_index = get_index_of_output(first, "Geometry")
        second_index = get_index_of_input(second, "Geometry")
        create_node_link(first.outputs[first_index], second.inputs[second_index])
    
    def boolean(self, first, second):
        boolnode = self.tree.nodes.new(type="GeometryNodeBoolean")
        first_index = get_index_of_output(first, "Geometry")
        second_index = get_index_of_output(second, "Geometry")
        create_node_link(boolnode.inputs[0], first.outputs[first_index])
        create_node_link(boolnode.inputs[1], second.outputs[second_index])
        return boolnode
    
    def join_geometry(self, first, second):
        joinnode = self.tree.nodes.new(type="GeometryNodeJoinGeometry")
        first_index = get_index_of_output(first, "Geometry")
        second_index = get_index_of_output(second, "Geometry")
        create_node_link(joinnode.inputs[0], first.outputs[first_index])
        create_node_link(joinnode.inputs[1], second.outputs[second_index])
        return joinnode

    def transform(self, objsource):
        transformnode = self.tree.nodes.new(type="GeometryNodeTransform")
        obj_index = get_index_of_output(objsource, "Geometry")
        create_node_link(objsource.outputs[obj_index],transformnode.inputs[0])
        return transformnode
#endregion