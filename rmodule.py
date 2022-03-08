# rmodule.py
# Created: Tuesday, 25th January 2022 9:48:58 am
# Matthew Riche
# Last Modified: Sunday, 27th February 2022 8:58:33 pm
# Modified By: Matthew Riche

'''
rmodule.py

The intent is to have a class instance that always has two build phases, one for placers and one 
for construction.
'''

from distutils.command.build import build
import pymel.core as pm
import pymel.core.datatypes as dt
from . placer import *
from . import orient as ori

import pprint


class RMod:
    def __init__(self, name="C_Generic_RModule", dir_prefix='', mirror=False):
        '''
        Generic module.  Each one will know where it's placers should go, and have a rather 
        vanilla build-script
        '''

        self.name = name
        self.side_prefix = (self.name.split('_')[0] + '_')
        self.dir_prefix = dir_prefix

        # Using a "plan" dict, we have both placers to be made, and the joints and controls they
        # make.

        self.plan = {}

        self.dependencies = [] # Modules that must be built first.
        self.placer_nodes = {} # Placers in-scene currently as nodes.
        self.joint_nodes = {} # Joints in-scene currently as nodes.
        self.build_nodes = [] # Nodes in-scene built by this module.
        self.reverse_axis = [] # Which axis to reverse in the case of mirroring.

        # If the side chosen is 'r_' then we put in a reverse axis of x.
        if('r' in self.side_prefix.lower()):
            self.reverse_axis.append('x')

        return

    def build_placers(self):
        '''
        Run through all the placers in placer_list and create them in the scene.
        '''

        pprint.pprint (self.plan)

        for entry in self.plan:
            print("Building {}".format(self.plan[entry]['name']))
            print("Placer is {}".format(self.plan[entry]['placer']))

            build_pos = self.plan[entry]['pos']
            if('r' in self.side_prefix.lower()):
                build_pos = (-build_pos[0], build_pos[1], build_pos[2])

            new_placer = create_placer(pos=(build_pos), 
                size=self.plan[entry]['placer'][0],
                name=(self.side_prefix + self.plan[entry]['name'] + '_plc'), 
                colour=self.plan[entry]['placer'][1]
                )

            self.plan[entry]['placer_node'] = new_placer

            # Create the 'up placer' which will define the up-vector when aiming to orient the 
            # future joint.
            if(self.plan[entry]['up_plc'] is not None):
                
                plc_pos = dt.Vector(self.plan[entry]['up_plc']['pos'])

                if('r' in self.side_prefix.lower()):
                    plc_pos = dt.Vector(-plc_pos[0], plc_pos[1], plc_pos[2])

                pos_vec = (dt.Vector(build_pos) + plc_pos)
                up_placer = create_placer(pos=pos_vec, 
                    size=self.plan[entry]['up_plc']['size'],
                    colour=self.plan[entry]['up_plc']['colour'])
                self.plan[entry]['up_plc']['placer_node'] = up_placer
                create_link_vis(new_placer, up_placer, colour='grey')
    
        return

    def build_joints(self):
        '''
        Using the self.joint_plan, make joints, orient and parent them according to the data.
        '''

        for entry in self.plan:
            print("Budiling {}".format(self.plan[entry]['name']))

            new_joint = pm.joint(n=(self.side_prefix + self.plan[entry]['name']))
            pm.matchTransform(new_joint, self.plan[entry]['placer_node'])
            # Orient the joint by aiming at a target with a specified up-vector placer.
            ori.aim_at(new_joint, self.plan[self.plan[entry]['child']]['placer_node'], 
                up_object=self.plan[entry]['up_plc']['placer_node'], 
                aim_axis=self.plan[entry]['aim'], up_axis=self.plan[entry]['up'])

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
