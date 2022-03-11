# controls.py
# Created: Friday, 11th March 2022 6:47:05 am
# Matthew Riche
# Last Modified: Friday, 11th March 2022 6:47:21 am
# Modified By: Matthew Riche

import pymel.core as pm
from . import colour as cl


def create_control (target_position=None, shape_dict=None, rot=(0, 0, 0), name='Unnamed_Ctrl', 
    colour='yellow', size=1):
    '''
    Created a nurbs curve shape from a dict that contains it's knots, points, degree, and all 
    relevant attributes.
    '''

    if(shape_dict == None):
        pm.error("This function must be supplied a shape_dict.")

    new_handle = pm.curve(
        per=shape_dict['per'], 
        p=shape_dict['points'], 
        k=shape_dict['knots'],
        d=shape_dict['degree']
        )
	
    cl.change_colour(new_handle, colour=colour)

    pm.setAttr(new_handle.scaleX, size)
    pm.setAttr(new_handle.scaleY, size)
    pm.setAttr(new_handle.scaleZ, size)

    new_handle.rename(name)

	# TODO
	# Snap it to a target node...
	# Apply it's rotational offset.

    return new_handle


def learn_curve (target_curve=None):
    '''
    Collect data from a curve.
    This may never get called internally.
    If target_curve is not a pyNode, not sure what could happen.
    '''

    # Fall back on selection if no target_curve is supplied.
    if(target_curve is None):
        target_curve = pm.ls(sl=True)[0]


        
    # Can't pull knots from the curve node itself, gotta hook one of these up;
    curve_inf = pm.createNode('curveInfo')
    pm.connectAttr(target_curve.getShape().worldSpace, curve_inf.inputCurve)

    # Record the points from a curve.
    points = []
    for i in range(0, curve_inf.controlPoints.getNumElements()):
        points.append(
            (curve_inf.controlPoints[i].get()[0],
            curve_inf.controlPoints[i].get()[1],
            curve_inf.controlPoints[i].get()[2],)  
        )

    knots = pm.getAttr(curve_inf.knots)
    print("knots is {}".format(knots))

    degree = target_curve.degree()

    curve_dict = {}
    curve_dict['points'] = points
    curve_dict['knots'] = knots
    curve_dict['degree'] = degree

    # TODO this may not be evaluating correctly.  Need to dig into the enum value.
    if(target_curve.form() == 'periodic'):
        curve_dict['per'] = True

    else:
        curve_dict['per'] = False

    # Delete the temporary node we used.
    pm.delete(curve_inf)

    return curve_dict