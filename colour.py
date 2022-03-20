# colour.py
# Created: Tuesday, 25th January 2022 9:54:52 am
# Matthew Riche
# Last Modified: Sunday, 27th February 2022 8:58:53 pm
# Modified By: Matthew Riche

'''
Utils for changing the colour of things in viewport.
'''

import pymel.core as pm

colour_enum = { 'grey':0, 'black':1, 'dark_grey':2, 'light_grey':3, 'dark_red':4, 'navy':5, 'blue':6, 
    'dark_green':7, 'dark_purple':8, 'purple':9, 'brown':10, 'dark_brown':11, 'dark_orange':12, 
    'red':13, 'bright_green':14, 'pale_blue':15, 'white':16, 'yellow':17, 'cyan':18, 
    'select_green':19, 'pink':20, 'pale_orange':21, 'pale_yellow':22, 'paleGreen':23, 'orange':24, 
    'dark_yellow':25, 'ugly_green':26, 'blue_green':27, 'dark_cyan':28, 'dark_blue':29, 
    'pale_purple':30, 'violet':31 }


def change_colour(node, colour='red', shape=True ):
    '''
    Given a node, and a string entry for the colour_enum dict, change the drawing override colour.
    If shape=True, the shape node will receive colour override in addition to the trans-node.
    '''

    node.getShape().overrideEnabled.set(True)
    node.getShape().overrideColor.set(colour_enum[colour])

    return