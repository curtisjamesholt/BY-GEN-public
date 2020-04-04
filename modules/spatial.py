import bpy
from math import sqrt

#For measuring distance between vectors
def measure (first,second):
    locx = second[0] - first[0]
    locy = second[1] - first[1]
    locz = second[2] - first[2]
    distance = sqrt( (locx)**2 + (locy)**2 + (locz)**2  )
    return distance