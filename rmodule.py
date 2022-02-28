# rmodule.py
# Created: Tuesday, 25th January 2022 9:48:58 am
# Matthew Riche
# Last Modified: Friday, 18th February 2022 9:08:08 pm
# Modified By: Matthew Riche

'''
rmodule.py

The intent is to have a class instance that always has two build phases, one for placers and one 
for construction.
'''

from sqlite3 import connect
import pymel.core as pm
from . import colour as cl

class RMod:
    def __init__(self, name="C_Generic_RModule", dir_prefix=''):
        '''
        Generic module.  Each one will know where it's placers should go, and have a rather 
        vanilla build-script
        '''

        self.name = name
        self.side_prefix = (self.name.split('_')[0] + '_')
        self.dir_prefix = dir_prefix
        self.placer_list = [] # Placers identities to be built.
        self.dependencies = [] # Modules that must be built first.
        self.placer_nodes = {} # Placers in-scene currently as nodes.
        self.build_nodes = [] # Nodes in-scene built by this module.
        self.reverse_axis = [] # Which axis to reverse in the case of mirroring.

        # If the side chosen is 'r_' then we put in a reverse axis of x.
        if('r' in self.side_prefix.lower()):
            self.reverse_axis.append('x')

        return

    def _verify_placers(self):
        '''
        Since the placer list can be user-made, verify that it's built correctly.
        '''

        print("Verifying that {} placers have complete data...".format(len(self.placer_list)))

        correct = True
        # Check for types in order:
        for placer in self.placer_list:
            if(len(placer) < 5):
                print("The placer {} is missing some data.".format(placer[2]))
                correct = False
                break
            if(type(placer[0]) is tuple and
                type(placer[1] is float) and
                type(placer[2] is str) and
                type(placer[3] is str) and
                type(placer[4] is str)):
                correct = True
            else:
                print("The placer {} has wrongly typed data.".format(placer[2]))
                correct = False
                break

        if(correct == False):
            print("Each placer definition needs four elements:\n[0] A tuple representing world"
                    "-space position\n[1] A float representing world-space scale.\n[2] A name for "
                    "the placer node that will be added to the scene.\n[3] A string naming the "
                    "colour.\n[4] A name for the key-- the key can match the name if there's no"
                    " inherited placers from a parent module, but should match the keys of the "
                    "parent module if one exists.")
            pm.error("Rigorist: The placer definitions lacked the right data.  See script-" 
                "editor for explanation.")
        else:
            return True

    def build_placers(self):
        '''
        Run through all the placers in placer_list and create them in the scene.
        '''

        self._verify_placers()

        for placer in self.placer_list:

            build_pos = placer[0]

            for axis in self.reverse_axis:
                if(axis == 'x'):
                    build_pos = (placer[0][0] * -1, placer[0][1], placer[0][2])
                elif(axis == 'y'):
                    build_pos = (placer[0][1], placer[0][1] * -1, placer[0][2])
                elif(axis == 'z'):
                    build_pos = (placer[0][1], placer[0][1], placer[0][2] * -1)
                else:
                    build_pos = placer[0]

            new_placer = create_placer(
                pos=build_pos, size=placer[1], name=(self.side_prefix + placer[2] + '_plc'), colour=placer[3]
                )
            print("Created {}.".format(new_placer))
            self.placer_nodes[placer[4]] = new_placer

        return

    def build_module(self):
        '''
        Run through all build instructions to create this module in-scene.
        '''

        # Checking that required placers are in the scene.
        failed = False
        print("Making sure all {} placers needed are in scene to build {} module."
            .format(len(self.placer_list), self.name))
        for placer in self.placer_list:
            if(pm.objExists(self.side_prefix + placer[2] + '_plc')):
                continue
            else:
                failed = True
                print("Build module failed-- returning error info.")
                break
        if(failed):
            error_msg = ("This module requires the following placers to be in the scene:")
            for placer in self.placer_list:
                error_msg.append("{}\n".format(placer[2]))
            return error_msg
        else:
            pass

    def clean_placers(self):
        '''
        Delete all in-scene placers relating to this module.
        '''

        print("Deleting placers.")
        for key in self.placer_nodes.keys():
            pm.delete(self.placer_nodes[key])

        self.placer_nodes = {}

        return
        
    def __str__(self):
        '''
        When cast as string, just print the details to console.
        '''

        return ("(Rigorist Module: {}{}{})".format(self.side_prefix, self.dir_prefix, self.name))

    def __getitem__(self, i):
        '''
        When indexed, we just send back each piece of data.
        '''
        _as_list = ([self.name, self.side_prefix, self.dir_prefix, self.placer_list, 
            self.dependencies, self.placer_nodes])

        return _as_list[i]


class Limb(RMod):
    def __init__(self, name="C_Generic_RModule", dir_prefix=''):
        '''
        A generic limb as a base, hinge, and end joint.  For an arm this will be shoulder, elbow,
        and wrist, and for a leg this will be hip, knee, and ankle.
        '''
        super().__init__(name=name, dir_prefix=dir_prefix)

        # The anatomy of these tuples is:
        #   [0] World Space Position
        #   [1] World Space Scale.
        #   [2] The name in the scene.
        #   [3] The colour (string that matches our colour dict.)
        #   [4] The key name.
        # The key name and the scene name being diffent allows for modules that inherit something 
        # generic like 'limb' and still reference placers correctly while displaying more accurate
        # names in the viewport.

        self.placer_list = [
            ((0.0, 3.0, 0.0), 1, 'base_joint', 'orange', 'base'),
            ((0.0, 2.0, 0.0), 0.8, 'hinge_joint', 'orange', 'hinge'),
            ((0.0, 1.0, 0.0), 1, 'end_joint', 'orange', 'end'),
        ]

        # Get membership for the essential joints of a parent joint.
        self.base_joint = None
        self.hinge_joint = None
        self.end_joint = None

        return

    def build_module(self):
        '''
        Based upon placers in the scene, begin construction
        '''
        super().build_module()

        # Select clear to disallow any automatic parenting
        pm.select(cl=True)

        self.base_joint = pm.joint(n=(self.side_prefix + self.placer_list[0][2]))
        self.hinge_joint = pm.joint(n=(self.side_prefix + self.placer_list[1][2]))
        self.end_joint = pm.joint(n=(self.side_prefix + self.placer_list[2][2]))

        pm.matchTransform(self.base_joint, self.placer_nodes['base'])
        pm.matchTransform(self.hinge_joint, self.placer_nodes['hinge'])
        pm.matchTransform(self.end_joint, self.placer_nodes['end'])


class Arm(Limb):
    def __init__(self, name="C_Generic_RModule", dir_prefix=''):
        '''
        The least most complicated limb that is still acceptable in the rigging world--
        FK/IK switch, cleanly placed pole-vector, nothing else.
        '''
        super().__init__(name=name, dir_prefix=dir_prefix)

        self.placer_list = [
            ((20.0, 175.0, 0.0), 1, 'shoulder_joint', 'orange', 'base'),
            ((28.0, 145.0, 0.0), 0.8, 'elbow_joint', 'orange', 'hinge'),
            ((38.0, 115, 0.0), 1, 'wrist_joint', 'orange', 'end'),
        ]

        return

    def build_module(self):
        super().build_module()

        print("Arm Module built, as child of limb module.")


def create_placer( pos=(0.0, 0.0, 0.0), size=1, name='RigoristPlacer', colour='blue'):
    '''
    create_placer
    Makes a nice way to visualize a placer that stands out.
    
    USAGE:
    create_placer( pos, size, name, colour)
    Arguments taken are the three vectors of the worlds space xform, the 
    visualized size, a name and a colour. Xform vectors are separate so that the
    use has the option of leaving one or two out.
    '''

    # Nurbs sphere placer is created and moved to the coords passed.
    new_placer = pm.sphere(polygon=0, radius=size, name=name)[0]
    pm.move(new_placer, pos)

    # Disconnect the initial Shader
    initial_shader_grp = pm.PyNode('initialShadingGroup')
    pm.disconnectAttr(new_placer.getShape().instObjGroups[0], 
        initial_shader_grp.dagSetMembers, na=True)

    # Set up colour override
    cl.change_colour(new_placer, colour)

    return new_placer
