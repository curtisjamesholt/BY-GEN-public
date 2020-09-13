import bpy
import random
from math import sqrt, radians
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

# For measuring distance between vectors
def measure (first,second):
    locx = second[0] - first[0]
    locy = second[1] - first[1]
    locz = second[2] - first[2]
    distance = sqrt( (locx)**2 + (locy)**2 + (locz)**2  )
    return distance

# For getting a random point within a radius (XY)
# Thanks to nbogie
def get_point_in_circle(max_radius):
    # Take vector pointing along X axis with random length less than radius
    radius = random.uniform(0, max_radius)
    vec = Vector((radius, 0.0, 0.0))
    # Rotate it random amount (0-360 degrees) along Z axis
    angle_degrees = random.uniform(0,360)
    rot = Matrix.Rotation(radians(angle_degrees), 3, "Z")
    vec.rotate(rot)
    return vec

# For getting a random point within a spherical radius
def get_point_in_sphere(max_radius):
    # Take vector pointing along X axis with random length less than radius
    radius = random.uniform(o, max_radius)
    vec = Vector((radius, 0.0, 0.0))
    # Rotate it random amount (0-360) along all axes
    angle_deg_x = random.uniform(0,360)
    angle_deg_y = random.uniform(0,360)
    angle_deg_z = random.uniform(0.360)
    rot = Matrix.Rotation(radians(angle_deg_x), 3, "X")
    vec.rotate(rot)
    rot = Matrix.Rotation(radians(angle_deg_y), 3, "Y")
    vec.rotate(rot)
    rot = Matrix.Rotation(radians(angle_deg_z), 3, "Z")
    vec.rotate(rot)
    return vec

# For getting a random point within a cubic space
def get_point_in_cube(origin, max_distance):
    # Position Diversion Values
    pos_x_deviation = random.uniform(-max_distance, max_distance)
    pos_y_deviation = random.uniform(-max_distance, max_distance)
    pos_z_deviation = random.uniform(-max_distance, max_distance)
    new_location = origin
    new_location[0] = new_location[0] + pos_x_deviation
    new_location[1] = new_location[1] + pos_y_deviation
    new_location[2] = new_location[2] + pos_z_deviation
    return new_location

# For detecting if point is inside object (object space)
# https://blog.michelanders.nl/2016/03/performance-of-ray-casting-in-blender_81.html
def is_inside_object(ob, point_in_object_space):
    direction = Vector((1,0,0))
    epsilon = direction * 1e-6
    count = 0
    result, point_in_object_space, normal, index = ob.ray_cast(point_in_object_space, direction)
    while result:
        count += 1
        result, point_in_object_space, normal, index = ob.ray_cast(point_in_object_space + epsilon, direction)
    return (count % 2) == 1