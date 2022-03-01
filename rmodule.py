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

import pymel.core as pm
from . placer import *

class RMod:
    def __init__(self, name="C_Generic_RModule", dir_prefix='', mirror=False):
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

        print("Verifying that {} entries have complete data...".format(len(self.placer_list)))

        correct = True
        # Check for types in order:
        for placer in self.placer_list:
            if(placer[0] == 'link'):
                continue
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

        # Prep place holders for link-targets
        link_targets = [None, None]

        for placer in self.placer_list:

            # If it's not a link, it's a placer.
            if(placer[0] != 'link'):
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
                    pos=build_pos, size=placer[1], name=(self.side_prefix + placer[2] + '_plc'), 
                    colour=placer[3])

                # Make it such that the last two placers are always the link targets.
                link_targets.pop(0)
                link_targets.append(new_placer)

                print("Created {}.".format(new_placer))
                self.placer_nodes[placer[4]] = new_placer

            elif(placer[0] == 'link'):
                create_link_vis(link_targets[0], link_targets[1], colour=placer[1])

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
