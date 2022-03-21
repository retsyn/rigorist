# limbs.py
# Created: Sunday, 27th February 2022 8:46:50 pm
# Matthew Riche
# Last Modified: Sunday, 27th February 2022 8:58:10 pm
# Modified By: Matthew Riche

from . rmodule import *
from . placer import mirror_placer
from . import orient as ori
from . import constraints as cns
from . import controls as ctl
from . import colour as col

import pprint

class Limb(RMod):
    def __init__(self, name="C_Generic_Limb", dir_prefix='', mirror=True):
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

        self.plan = {
            'base':{
                'pos':(0.0, 3.0, 4.0), 
                'name':'base',
                'placer':(1.0, 'orange'),
                'up_plc':{'pos':(0.0, 0.0, 7.0), 'size':0.4, 'colour':'white' },
                'aim':1,
                'up':0,
                'child':'hinge',
                'control':['thin_ring', 1.0, 'yellow']
            },
            'hinge':{
                'pos':(0.0, 3.0, -4.0),
                'name':'hinge', 
                'placer':(1.0, 'orange'),
                'up_plc':{'pos':(7.0, 7.0, 7.0), 'size':0.4, 'colour':'white' },
                'aim':1,
                'up':0,
                'child':'end',
                'control':['thin_ring', 0.7, 'yellow']
            },
            'end':{
                'pos':(0.0, 3.0, -4.0),
                'name':'hinge', 
                'placer':(1.0, 'orange'),
                'up_plc':{'pos':(7.0, 0.0, 0.0), 'size':0.4, 'colour':'white' },
                'aim':1,
                'up':0,
                'control':['thin_ring', 1.0, 'yellow']
            }
        }

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

        # Make the FKIK switching system.
        bind_base = (self.plan['base']['joint_node'])
        bind_hinge = (self.plan['hinge']['joint_node'])
        bind_end = (self.plan['end']['joint_node'])

        # Let's duplicate the joints we made...
        FK_base = pm.duplicate(self.plan['base']['joint_node'], po=False)[0]
        FK_hinge = pm.listRelatives(FK_base, c=True)[0]
        FK_end = pm.listRelatives(FK_hinge, c=True)[0]
        FK_base.rename(self.side_prefix + "FK" + self.plan['base']['name'] + "_joint")
        FK_hinge.rename(self.side_prefix + "FK" + self.plan['hinge']['name'] + "_joint")
        FK_end.rename(self.side_prefix + "FK" + self.plan['end']['name'] + "_joint")
        # Same process for FK.
        IK_base = pm.duplicate(self.plan['base']['joint_node'], po=False)[0]
        IK_hinge = pm.listRelatives(IK_base, c=True)[0]
        IK_end = pm.listRelatives(IK_hinge, c=True)[0]
        IK_base.rename(self.side_prefix + "IK" + self.plan['base']['name'] + "_joint")
        IK_hinge.rename(self.side_prefix + "IK" + self.plan['hinge']['name'] + "_joint")
        IK_end.rename(self.side_prefix + "IK" + self.plan['end']['name'] + "_joint")

        # Determine PV position:
        pv_pos = ori.project_pv(IK_base, amplify=200)
        self.pv_ctrl_node = ctl.create_control(load_shape='jack', colour='yellow',
            name=(self.name + "PV_CTRL"))
        self.pv_ctrl_node.translate.set(pv_pos)
        self.pv_null = ori.create_null(self.pv_ctrl_node)

        # Make double constraints with switches.
        #   Make a new controller to hold the switch: 
        self.FKIK_ctrl_node = ctl.create_control(load_shape='jack', colour='white',
                    name=(self.side_prefix + self.name + "FKIK_CTRL"))

        switch_pos = pm.xform(bind_end, ws=True, q=True, t=True)
        self.FKIK_ctrl_node.translateX.set(switch_pos[0])
        self.FKIK_ctrl_node.translateY.set(bind_base.translateY.get())

        cns.make_float_switch(FK_base, IK_base, bind_base, self.FKIK_ctrl_node, attr_name='FKIK', 
            float_size=100)
        cns.make_float_switch(FK_hinge, IK_hinge, bind_hinge, self.FKIK_ctrl_node, attr_name='FKIK', 
            float_size=100)
        cns.make_float_switch(FK_end, IK_end, bind_end, self.FKIK_ctrl_node, attr_name='FKIK', 
            float_size=100)

        # Create the nulls for the controllers and build the hierarchy.
        base_null = ori.create_null(self.plan['base']['control_node'])
        hinge_null = ori.create_null(self.plan['hinge']['control_node'])
        end_null = ori.create_null(self.plan['end']['control_node'])
        pm.parent(hinge_null, self.plan['base']['control_node'])
        pm.parent(end_null, self.plan['hinge']['control_node'])
        ctl.connect_rot(self.plan['base']['control_node'], FK_base)
        ctl.connect_rot(self.plan['hinge']['control_node'], FK_hinge)
        ctl.connect_rot(self.plan['end']['control_node'], FK_end)

        # Create controllers for IK arm.  (Not created by the plan, only the FK is.)
        self.IK_base_ctrl = ctl.create_control(
            load_shape='cube', colour='yellow', name=(self.side_prefix + 'base_CTRL')
            )
        pm.matchTransform(self.IK_base_ctrl, IK_base, pos=True, rot=False)
        self.IK_end_ctrl = ctl.create_control(
            load_shape='cube', colour='yellow', name=(self.side_prefix + 'end_CTRL')
            )
        pm.matchTransform(self.IK_end_ctrl, IK_end, pos=True, rot=False)

        pm.parent(self.IK_end_ctrl, FK_base, IK_base, base_null, bind_base, self.FKIK_ctrl_node, 
            self.IK_base_ctrl)

        # IK handle.
        solver_handle = pm.ikHandle(sj=IK_base, ee=IK_end, sol='ikRPsolver')[0]
        pm.parent(solver_handle, self.IK_end_ctrl)
        pm.poleVectorConstraint(self.pv_ctrl_node, solver_handle)


        return


class Arm(Limb):
    def __init__(self, name="Arm_Module", dir_prefix=''):
        '''
        The least most complicated limb that is still acceptable in the rigging world--
        FK/IK switch, cleanly placed pole-vector, nothing else.
        '''
        super().__init__(name=name, dir_prefix=dir_prefix)

        self.plan['base']['pos'] = (20.0, 175.0, 0.0)
        self.plan['base']['name'] = 'shoulder'
        self.plan['hinge']['pos'] = (28.0, 145.0, -4.0)
        self.plan['hinge']['name'] = 'elbow'
        self.plan['end']['pos'] = (38.0, 115.0, 0.0)
        self.plan['end']['name'] = 'wrist'

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

        # Recolour in plan:
        self._left_arm.plan['base']['control'][2] = 'red'
        self._left_arm.plan['hinge']['control'][2] = 'red'
        self._left_arm.plan['end']['control'][2] = 'red'
        self._right_arm.plan['base']['control'][2] = 'blue'
        self._right_arm.plan['hinge']['control'][2] = 'blue'
        self._right_arm.plan['end']['control'][2] = 'blue'

        self._left_arm.build_placers()
        self._right_arm.build_placers()

        # Now we need to build expressions to make placers mirror on X.
        for key in self._left_arm.plan:
            mirror_placer(self._left_arm.plan[key]['placer_node'], 
            self._right_arm.plan[key]['placer_node'])
        
    def build(self):
        '''
        Build both arm modules.
        '''

        print("Building both arms...")
        self._left_arm.build_module()
        self._right_arm.build_module()

        # Recolour some post-plan modules:
        col.change_colour(self._left_arm.IK_end_ctrl, colour='red')
        col.change_colour(self._left_arm.IK_base_ctrl, colour='red')
        col.change_colour(self._right_arm.IK_end_ctrl, colour='blue')
        col.change_colour(self._right_arm.IK_base_ctrl, colour='blue')
        col.change_colour(self._left_arm.FKIK_ctrl_node, colour='pale_orange')
        col.change_colour(self._right_arm.FKIK_ctrl_node, colour='cyan')

        self._left_arm.clean_placers()
        self._right_arm.clean_placers()

        return
