# constrain.py
# Created: Monday, 14th March 2022 10:32:15 am
# Matthew Riche
# Last Modified: Monday, 14th March 2022 10:32:32 am
# Modified By: Matthew Riche

import pymel.core as pm

def make_float_switch(trans_a, trans_b, target, control_node, attr_name='switch', float_size=10.0):
    '''
    Make a parent-constraint switcher using a float.
    '''

    # Build the new constraint node...
    new_constraint = pm.parentConstraint(trans_a, trans_b, target)

    # Find the weight attribute of trans_a
    a_attr = ([a for a in pm.listAttr(new_constraint, k=True, se=True) 
        if (trans_a.name() in str(a))][0])
    b_attr = ([b for b in pm.listAttr(new_constraint, k=True, se=True) 
        if (trans_b.name() in str(b))][0])

    # Create the remap nodes.
    remap_a = pm.createNode('remapValue')
    remap_b = pm.createNode('remapValue')
    remap_a.inputMin.set(0)
    remap_a.inputMax.set(float_size)
    remap_b.inputMin.set(float_size)
    remap_b.inputMax.set(0)

    # Make the attr on the given control if it doesn't exist.  If it does, the string manipulation
    # will correctly identify it.
    if(pm.hasAttr(control_node, attr_name) == False):
        pm.addAttr(control_node, at='float', hxv=True, hnv=True, max=float_size, min=0, sn=attr_name, 
            h=False, k=True, r=True)

    # Connect the node network...
    #   ...first the new control attribute:
    pm.connectAttr((control_node.name() + '.' + attr_name), remap_a.inputValue)
    pm.connectAttr((control_node.name() + '.' + attr_name), remap_b.inputValue)
    #   ...Then the remap nodes to the constraint.
    pm.connectAttr(remap_a.outValue, (new_constraint.name() + '.' + a_attr))
    pm.connectAttr(remap_b.outValue, (new_constraint.name() + '.' + b_attr))
    
    return str(control_node.name() + '.' + attr_name)