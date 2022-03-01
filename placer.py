# placer.py
# Created: Monday, 28th February 2022 8:40:59 am
# Matthew Riche
# Last Modified: Monday, 28th February 2022 8:42:11 am
# Modified By: Matthew Riche

import pymel.core as pm
from . import colour as cl


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


def mirror_placer(live_placer, matched_placer, mirror_axis='x'):
    '''
    Takes two placers, one being live and placeable in the scene, and the other being the intended
    mirror-match.  The trans node are connected to make the position of the latter constantly
    mirrored.
    '''

    available_axis = ['x','y','z']
    available_axis.remove(mirror_axis)

    # Built the regular non-mirrored connections.
    for axis in available_axis:
        if(axis == 'x'):
            live_placer.translateX >> matched_placer.translateX
        elif(axis == 'y'):
            live_placer.translateY >> matched_placer.translateY
        elif(axis == 'z'):
            live_placer.translateZ >> matched_placer.translateZ
        
    # Build the mirror!
    multi_div = pm.createNode('multiplyDivide', 
        n=('{}_mirror_multDiv'.format(live_placer.name().split('_')[1])))
    multi_div.input2X.set(-1)

    if(mirror_axis == 'x'):
        live_placer.translateX >> multi_div.input1X
        multi_div.outputX >> matched_placer.translateX
    if(mirror_axis == 'y'):
        live_placer.translateY >> multi_div.input1Y
        multi_div.outputY >> matched_placer.translateY
    if(mirror_axis == 'z'):
        live_placer.translateZ >> multi_div.input1Z
        multi_div.outputZ >> matched_placer.translateZ

    return


def create_link_vis(target_a, target_b, colour='white'):
    '''
	Create a one-degree curve between two placers to visualize connection before the binding phase.
    '''

    new_link = pm.curve(d=1, p=[(1, 0, 0,), (-1,0,0)])
	# Take the two CVs of that, attach them by matrix/transform to the targets
    pm.connectAttr(target_a.translate, new_link.getShape().controlPoints[0])
    pm.connectAttr(target_b.translate, new_link.getShape().controlPoints[1])

    cl.change_colour(new_link, colour=colour)
    
    return new_link