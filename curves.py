# curves.py
# Created: Wednesday, 9th March 2022 10:49:09 am
# Matthew Riche
# Last Modified: Wednesday, 9th March 2022 10:49:16 am
# Modified By: Matthew Riche


from . rmodule import *

import pymel.core as pm
import pymel.core.datatypes as dt

class Curve(RMod):
    def __init__(self, name="C_Generic_RModule", dir_prefix='', mirror=True):
        '''
        A curve defining class.
        '''
        super().__init__(name=name, dir_prefix=dir_prefix, mirror=mirror)

        self.curve_node = None

        self.plan = {
            'start':{
                'pos':(0.0, 3.0, 0.0), 
                'name':'curve_base',
                'placer':(1.0, 'blue'),
                'child':None
            },
            'mid':{
                'pos':(0.0, 6.0, 0.0),
                'name':'curve_mid', 
                'placer':(1.0, 'blue'),
                'child':None
            },
            'end':{
                'pos':(0.0, 9.0, 0.0),
                'name':'curve_end', 
                'placer':(1.0, 'blue'),
                'child':None
            }
        }

        return

    def build_curve(self):
        ''' 
        Given placers, construct a curve defined by them.
        '''

        point_list = []

        for entry in self.plan:
            point_list.append(
                dt.Vector(self.plan[entry]['placer_node'].getTranslation(space='world'))
                )
            
        print("The point list xforms {}".format(point_list))
        degree = (len(point_list) - 1)

        new_curve = pm.curve(per=False, p=point_list, d=degree)

        self.curve_node = new_curve

    def build_spline(self, rebuild=False, count=5):
        '''
        Makes the self.curve into a spline_IK with joints
        '''

        pm.select(cl=True)

        if(rebuild):
            old_curve_node = self.curve_node
            old_curve_name = self.curve_node.name()
            self.curve_node = rebuild_curve(self.curve_node, 
                new_curve_name=self.curve_node.name(), 
                cv_count = count)
            pm.delete(old_curve_node)
            self.curve_node.rename(old_curve_name)

        
        joint_array = make_joint_array(self.curve_node)

        self.joints = joint_array['all']
        self.base_joint = joint_array['base']

        print(self.joints)
        print(self.joints[-1])

        pm.ikHandle(ccv = False, c=self.curve_node, ee=self.joints[-1], sj=self.base_joint)

        return
        

def make_joint_array(target_curve, name="spline"):
    '''
    Make a joint for every CV on a high-res curve.
    ''' 

    joints_built = []
    base_joint = None

    pm.select(cl=True)

    count = 0
    for point in target_curve.cv:
        count += 1
        tip_joint = pm.joint(
            p=(pm.pointPosition(point)), name=(name + str(count).zfill(2) + '_joint'))
        joints_built.append(tip_joint)
        if(base_joint is None):
            base_joint = tip_joint

    return {'base':base_joint, 'all':joints_built}


def rebuild_curve(target_curve, new_curve_name='new_curve', cv_count=5):
	'''
	Rebuild curve with evenly spaced CVs
    Not the same as Maya rebuild curve-- New CVs will be placed along old curve,
    Instead of in position that perfectly reform the old curve.
	'''

	# Get this vars using Pymel.
	length = target_curve.length()
	degree = target_curve.degree()

	ncvs = max(cv_count, 2)           # Number of CVs
	spans = ncvs - degree            # Number of spans
	nknots = spans + 2 * degree - 1  # Number of knots
	
	knots = []
	knots.append(0.0)
	knots.append(0.0)

	for k in range(nknots - 5):
		knots.append(float(k))

	knots.append(float(nknots-5))
	knots.append(float(nknots-5))
	knots.append(float(nknots-5))
	new_cvs = []

	# PyMel point data class required	
	cv_point = dt.Point
	cv_point.x = 0
	cv_point.y = 0
	cv_point.z = 0

	for k in range(ncvs):
		step_length = ( length / (ncvs - 1) ) * k
		param = target_curve.findParamFromLength(step_length)
		cv_point = target_curve.getPointAtParam( param, 'world' )
		new_cvs.append(cv_point)

	new_curve = pm.curve(
		name=new_curve_name,
	    degree=degree, 
	    worldSpace=True, 
	    point=new_cvs, 
	    knot=knots
	    )

	return new_curve
