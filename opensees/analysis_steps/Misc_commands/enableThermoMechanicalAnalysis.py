import os
from PyMpc import *
from mpc_utils_html import *
from itertools import groupby, count
import opensees.utils.tcl_input as tclin
import opensees.utils.write_element as write_element
import opensees.utils.write_node as write_node

def makeXObjectMetaData():
	
	at_SelectionSets = MpcAttributeMetaData()
	at_SelectionSets.type = MpcAttributeType.IndexVector
	at_SelectionSets.name = 'SelectionSets'
	at_SelectionSets.group = 'Data'
	at_SelectionSets.description = (
		html_par(html_begin()) +
		html_par(html_boldtext('Enable ThermoMechanical Analysis')+'<br/>') + 
		html_par(
			'Enable the ThermoMechanical Analysis for the selected components. ')+
   
		html_end()
		)
	
	xom = MpcXObjectMetaData()
	xom.name = 'StartThermoMechanicalAnalysis'

	
	return xom



def writeTcl(pinfo):
	
	# get xobject and its parent component id
	xobj = pinfo.analysis_step.XObject
	id = xobj.parent.componentId
	
	# write a comment
	pinfo.out_file.write('\n{}# StartThermoMechanicalAnalysis [{}] {}\n'.format(pinfo.indent, id, xobj.parent.componentName))
	
	pinfo.out_file.write('\n')