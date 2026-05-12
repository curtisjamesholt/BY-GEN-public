'''
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

bl_info = {
    "name" : "BY-GEN",
    "author" : "Curtis Holt",
    "description" : "A generative modeling toolkit by Curtis Holt.",
    "blender" : (5, 0, 1),
    "version" : (10,0,0),
    "location" : "View3D",
    "warning" : "",
    "category" : "Generic"
}

import bpy
import bmesh
import random
import bpy.utils.previews
import os
from mathutils import Vector, Matrix
from bpy.props import *
from bpy.types import (Panel,Menu,Operator,PropertyGroup,)

from . import effects

custom_icons = None
class BGProperties(PropertyGroup):
    secret_string: StringProperty(
        name="Super secret boy band.",
        description="I don't wanna join your super secret boy band.",
        default="Proof that Tony Stark has a heart."
    )

    unique_collection: BoolProperty(
        name="Make Collections Unique",
        description="Make imported collections unique",
        default = False
        )
    debug_mode : BoolProperty(
        name="Debug Mode",
        description="Outputs information to the console for debugging.",
        default=False
    )
    output_to_log : BoolProperty(
        name="Output to Log",
        description="Outputs debug information to a text file.",
        default=False
    )

classes = (
    BGProperties,
)
keys = []


def register():
    from bpy.utils import register_class

    effects.register()

    for cls in classes:
        register_class(cls)

    bpy.types.Scene.by_tool = PointerProperty(type=BGProperties)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)

    effects.unregister()

    del bpy.types.Scene.by_tool

if __name__ == "__main__":
    register()