# limbs.py
# Created: Sunday, 27th February 2022 8:46:50 pm
# Matthew Riche
# Last Modified: Sunday, 27th February 2022 8:58:10 pm
# Modified By: Matthew Riche

from . rmodule import *
from . placer import mirror_placer
from . import orient as ori

class Limb(RMod):
    def __init__(self, name="C_Generic_RModule", dir_prefix='', mirror=True):
        '''
        A generic limb as a base, hinge, and end joint.  For an arm this will be shoulder, elbow,
        and wrist, and for a leg this will be hip, knee, and ankle.
        '''
        super().__init__(name=name, dir_prefix=dir_prefix, mirror=mirror)

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
            ((0.0, 3.0, 4.0), 0.4, 'base_axis', 'white', 'base_axis'),
            ((0.0, 3.0, 0.0), 1, 'base_joint', 'orange', 'base'),
            ('link', 'white'),
            ((0.0, 2.0, 0.0), 0.8, 'hinge_joint', 'orange', 'hinge'),
            ('link', 'white'),
            ((0.0, 1.0, 0.0), 1, 'end_joint', 'orange', 'end'),
            ('link', 'white'),
            ((1.4, 1.4, 0.0), 1, 'end_axis', 'white', 'end_axis'),
            ('link', 'white'),
            ((1.4, 1.4, 0.0), 1, 'end_aim', 'white', 'end_aim'),
            ('link', 'white'),

            ((1.0, 2.0, 0.5), 0.8, 'hinge_axis', 'white', 'hinge_axis'),
        ]

        self.joint_plan = [
            {'name':'base', 
                'placer':'base_axis',
                'child_plc':'hinge_joint',
                'up_plc':'base_axis',
                'aim_ax':1,
                'up_ax':0 
                },
            {'name':'hinge', 
                'placer':'hinge_joint',
                'child_plc':'end_joint',
                'up_plc':'hinge_axis',
                'aim_ax':1,
                'up_ax':0 
                },
            {'name':'end', 
                'placer':'end_joint',
                'child_plc':'end_aim',
                'up_plc':'end_axis',
                'aim_ax':1,
                'up_ax':0 
                },
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

        # We orient the shoulder joint to the hinge axis




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
            ('link', 'white'),
            ((38.0, 115.0, 0.0), 1, 'wrist_joint', 'orange', 'end'),
            ('link', 'white'),
            ((20.0, 175.0, 30.0), 0.6, 'shoulder_axis', 'white', 'base_axis'),
            ((48.0, 154.0, 0.0), 0.6, 'elbow_axis', 'white', 'hinge_axis'),
            ('link', 'white', 'elbow_joint'),
            ((48.0, 154.0, 17.0), 0.6, 'wrist_axis', 'white', 'end_axis'),
            ('link', 'white', 'wrist_joint')
        ]

        return

    def build_module(self):
        super().build_module()

        print("Arm Module built, as child of limb module.")


class Arms:
    def __init__(self, name=""):
        '''
        A pair of Arms.
        '''

        self._left_arm = Arm("L_arm")
        self._right_arm = Arm("R_arm")

        self._left_arm.build_placers()
        self._right_arm.build_placers()

        # Now we need to build expressions to make placers mirror on X.
        for key in self._left_arm.placer_nodes.keys():
            mirror_placer(self._left_arm.placer_nodes[key], self._right_arm.placer_nodes[key])
        
    def build(self):
        '''
        Build both arm modules.
        '''

        print("Building both arms...")
        self._left_arm.build_module()
        self._right_arm.build_module()
