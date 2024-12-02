import PyMpc.Units as u
import PyMpc.App
from PyMpc import *
from mpc_utils_html import *
import opensees.utils.tcl_input as tclin

def makeXObjectMetaData():
	
	at_SelectionSets = MpcAttributeMetaData()
	at_SelectionSets.type = MpcAttributeType.IndexVector
	at_SelectionSets.name = 'SelectionSets'
	at_SelectionSets.group = 'Data'
	at_SelectionSets.description = (
		html_par(html_begin()) +
		html_par(html_boldtext('switchToMechanicalAnalysis')+'<br/>') + 
		html_par(
			'Enable the Mechanical Analysis for the selected components. ')+
   
		html_end()
		)
	
	xom = MpcXObjectMetaData()
	xom.name = 'switchToMechanicalAnalysis'

	
	return xom

def writeTcl(pinfo):
	
	# write a comment
	pinfo.out_file.write('\n{}# switchToMechanicalAnalysis\n'.format(pinfo.indent))
	
	print(pinfo.inv_map)
	valor_anterior = pinfo.inv_map[(3,1)]
	pinfo.inv_map[(3,3)] = valor_anterior
	del pinfo.inv_map[(3,1)]
	print(pinfo.node_to_model_map)
	
	pinfo.out_file.write('\n')