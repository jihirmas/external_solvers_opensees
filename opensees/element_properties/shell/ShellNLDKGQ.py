import PyMpc.Units as u
from PyMpc import *
from mpc_utils_html import *
import opensees.utils.tcl_input as tclin

def makeXObjectMetaData():
	
	xom = MpcXObjectMetaData()
	xom.name = 'ShellNLDKGQ'
	
	return xom

def getNodalSpatialDim(xobj, xobj_phys_prop):

	return [(3,6),(3,6),(3,6),(3,6)]

def writeTcl(pinfo):
	import opensees.element_properties.shell.shell_utils as shelu
	
	# element ShellNLDKGQ $eleTag $iNode $jNode $kNode $lNode $secTag
	
	elem = pinfo.elem
	phys_prop = pinfo.phys_prop
	elem_prop = pinfo.elem_prop
	
	tag = elem.id
	secTag = phys_prop.id
	xobj = elem_prop.XObject
	
	ClassName = xobj.name
	if pinfo.currentDescription != ClassName:
		pinfo.out_file.write('\n{}# {} {}\n'.format(pinfo.indent, xobj.Xnamespace, ClassName))
		pinfo.currentDescription = ClassName
	
	namePh = phys_prop.XObject.Xnamespace
	if namePh != 'sections':
		raise Exception('Error: physical property must be "sections" and not: "{}"'.format(namePh))
	
	# NODE
	nstr = shelu.getNodeString(elem)
	
	if (elem.geometryFamilyType() != MpcElementGeometryFamilyType.Quadrilateral or len(elem.nodes)!=4):
		raise Exception('Error: invalid type of element or number of nodes')
	
	str_tcl = '{}element ShellNLDKGQ {} {} {}\n'.format(pinfo.indent, tag, nstr, secTag)
	
	# now write the string into the file
	pinfo.out_file.write(str_tcl)