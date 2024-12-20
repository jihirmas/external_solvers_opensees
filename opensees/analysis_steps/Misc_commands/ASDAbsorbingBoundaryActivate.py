import PyMpc.Units as u
from PyMpc import *
from mpc_utils_html import *
import opensees.utils.tcl_input as tclin
from opensees.utils.parameter_utils import ParameterManager

def _err(msg):
	return 'Error in "ASDAbsorbingBoundaryActivate" :\n{}'.format(msg)

def makeXObjectMetaData():
	xom = MpcXObjectMetaData()
	xom.name = 'ASDAbsorbingBoundaryActivate'
	xom.Xgroup = 'absorbingBoundaries'
	return xom

def writeTcl(pinfo):
	
	from io import StringIO
	
	# check manager
	manager = pinfo.custom_data.get('ASDAbsorbingBoundary2D', None)
	if manager:
		if 'ASDAbsorbingBoundary3D' in pinfo.custom_data:
			raise Exception(_err('In the same file you cannot use both 2D and 3D ASDAbsorbingBoundary elements'))
	else:
		manager = pinfo.custom_data.get('ASDAbsorbingBoundary3D', None)
	
	# quick return
	if manager is None:
		return
	
	# make command string
	def commandstring(eles, indent):
		stream = StringIO()
		stream.write('{}parameter {}\n'.format(indent, ParameterManager.ABSORBING_STAGE))
		stream.write('{}foreach ele_id [list \\\n'.format(indent))
		count = 0
		n = len(eles)
		for i in range(n):
			count += 1
			if count == 1:
				stream.write('{}{}'.format(indent, pinfo.tabIndent))
			stream.write('{} '.format(eles[i]))
			if count == 10 and i < n-1:
				count = 0
				stream.write('\\\n')
		stream.write('] {\n')
		stream.write('{}{}addToParameter {} element $ele_id stage\n'.format(pinfo.indent, pinfo.tabIndent, ParameterManager.ABSORBING_STAGE))
		stream.write('{}}}\n'.format(pinfo.indent))
		stream.write('{}updateParameter {} 1\n'.format(pinfo.indent, ParameterManager.ABSORBING_STAGE))
		stream.write('{}remove parameter {}\n'.format(pinfo.indent, ParameterManager.ABSORBING_STAGE))
		return stream.getvalue()
	
	# comment
	for _, values in manager.elements.items():
		if len(values) > 0:
			pinfo.out_file.write('\n{}# Activate Absorbing boundaries\n'.format(pinfo.indent))
			break
	
	# check partitions
	if pinfo.process_count > 1:
		for partition_id, values in manager.elements.items():
			if(len(values) > 0):
				pinfo.out_file.write('{}if {{$STKO_VAR_process_id == {}}} {{\n'.format(pinfo.indent, partition_id))
				pinfo.out_file.write(commandstring(values, pinfo.indent+pinfo.tabIndent))
				pinfo.out_file.write('{}}}\n'.format(pinfo.indent))
	else:
		values = manager.elements[0]
		if(len(values) > 0):
			pinfo.out_file.write(commandstring(values, pinfo.indent))