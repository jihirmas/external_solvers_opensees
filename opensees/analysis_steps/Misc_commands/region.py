import PyMpc.Units as u
from PyMpc import *
from mpc_utils_html import *
from itertools import groupby, count
import opensees.utils.tcl_input as tclin

def ele_range_string(tagList):
	l = list(tagList)
	if len(l) > 1:
		return ' \\\n-eleRange {} {}'.format(l[0], l[-1])
	else:
		return ' \\\n-ele {}'.format(l[0])
def node_range_string(tagList):
	l = list(tagList)
	if len(l) > 1:
		return ' \\\n-nodeRange {} {}'.format(l[0], l[-1])
	else:
		return ' \\\n-node {}'.format(l[0])

def makeXObjectMetaData():
	
	at_SelectionSets = MpcAttributeMetaData()
	at_SelectionSets.type = MpcAttributeType.IndexVector
	at_SelectionSets.name = 'SelectionSets'
	at_SelectionSets.group = 'Data'
	at_SelectionSets.description = (
		html_par(html_begin()) +
		html_par(html_boldtext('region')+'<br/>') + 
		html_par(html_href('http://opensees.berkeley.edu/wiki/index.php/Region_Command','region')+'<br/>') +
		html_par('select region') +
		html_end()
		)
	at_SelectionSets.indexSource.type = MpcAttributeIndexSourceType.SelectionSet
	
	# at_type
	at_rtype = MpcAttributeMetaData()
	at_rtype.type = MpcAttributeType.String
	at_rtype.name = 'Region Type'
	at_rtype.group = 'Data'
	at_rtype.description = (
		html_par(html_begin()) +
		html_par(html_boldtext('Region Type')+'<br/>') + 
		html_par('In a region you can specify either elements or nodes, not both of them')+
		html_par(html_href('http://opensees.berkeley.edu/wiki/index.php/Region_Command','region')+'<br/>') +
		html_end()
		)
	at_rtype.sourceType = MpcAttributeSourceType.List
	at_rtype.setSourceList(['Elements', 'Nodes'])
	at_rtype.setDefault('Elements')
	
	# at_type_elements
	at_type_elements = MpcAttributeMetaData()
	at_type_elements.type = MpcAttributeType.Boolean
	at_type_elements.name = 'Elements'
	at_type_elements.group = 'Data'
	at_type_elements.editable = False
	at_type_elements.setDefault(True)
	
	# at_type_nodes
	at_type_nodes = MpcAttributeMetaData()
	at_type_nodes.type = MpcAttributeType.Boolean
	at_type_nodes.name = 'Nodes'
	at_type_nodes.group = 'Data'
	at_type_nodes.editable = False
	at_type_nodes.setDefault(False)
	
	# include_element_autogenerate
	at_include_auto_generated_elements = MpcAttributeMetaData()
	at_include_auto_generated_elements.type = MpcAttributeType.String
	at_include_auto_generated_elements.name = 'include_auto_generated_elements'
	at_include_auto_generated_elements.group = 'Data'
	at_include_auto_generated_elements.description = (
		html_par(html_begin()) +
		html_par(html_boldtext('include auto generated elements')+'<br/>') + 
		html_par('If this flag is set to True (Default) the region will also include all those elements that will be automatically generated by STKO as part of macro-elements. See for example the HingedBeam element property.')+
		html_par(html_href('http://opensees.berkeley.edu/wiki/index.php/Region_Command','region')+'<br/>') +
		html_end()
		)
	at_include_auto_generated_elements.sourceType = MpcAttributeSourceType.List
	at_include_auto_generated_elements.setSourceList(['selection', 'selection + include_auto_generated_elements', 'include_auto_generated_elements - selection'])
	at_include_auto_generated_elements.setDefault('selection + include_auto_generated_elements')
	
	# to write nodes/elements on a list
	at_write_list = MpcAttributeMetaData()
	at_write_list.type = MpcAttributeType.Boolean
	at_write_list.name = 'WriteOnList'
	at_write_list.group = 'Data'
	at_write_list.description = (
		html_par(html_begin()) +
		html_par(html_boldtext('WriteOnList')+'<br/>') + 
		html_par('If this flag is set to True (Default = False) the items (nodes or elements) in the region will be written into a TCL list')+
		html_par(html_href('http://opensees.berkeley.edu/wiki/index.php/Region_Command','region')+'<br/>') +
		html_end()
		)
	at_write_list.setDefault(False)
	
	# to write nodes/elements on a list
	at_list_name = MpcAttributeMetaData()
	at_list_name.type = MpcAttributeType.String
	at_list_name.name = 'List Name'
	at_list_name.group = 'Data'
	at_list_name.description = (
		html_par(html_begin()) +
		html_par(html_boldtext('List Name')+'<br/>') + 
		html_par('Defines how the list variable will be called in TCL')+
		html_par(html_href('http://opensees.berkeley.edu/wiki/index.php/Region_Command','region')+'<br/>') +
		html_end()
		)
	at_list_name.setDefault("Enter_a_unique_name_for_this_list")
	
	# at_rayleigh
	at_rayleigh = MpcAttributeMetaData()
	at_rayleigh.type = MpcAttributeType.Boolean
	at_rayleigh.name = 'rayleigh'
	at_rayleigh.group = 'Data'
	at_rayleigh.description = (
		html_par(html_begin()) +
		html_par(html_boldtext('rayleigh')+'<br/>') + 
		html_par(html_href('http://opensees.berkeley.edu/wiki/index.php/Rayleigh_Damping_Command','rayleigh')+'<br/>') +
		html_end()
		)
	
	# alphaM
	at_alphaM = MpcAttributeMetaData()
	at_alphaM.type = MpcAttributeType.Real
	at_alphaM.name = 'alphaM/rayleigh'
	at_alphaM.group = 'Optional'
	at_alphaM.description = (
		html_par(html_begin()) +
		html_par(html_boldtext('alphaM')+'<br/>') +
		html_par(html_href('http://opensees.berkeley.edu/wiki/index.php/Rayleigh_Damping_Command','rayleigh')+'<br/>') +
		html_end()
		)
		
	# Betak
	at_Betak = MpcAttributeMetaData()
	at_Betak.type = MpcAttributeType.Real
	at_Betak.name = 'Betak/rayleigh'
	at_Betak.group = 'Optional'
	at_Betak.description = (
		html_par(html_begin()) +
		html_par(html_boldtext('Betak')+'<br/>') +
		html_par(html_href('http://opensees.berkeley.edu/wiki/index.php/Rayleigh_Damping_Command','rayleigh')+'<br/>') +
		html_end()
		)
		
	# betaKinit
	at_betaKinit = MpcAttributeMetaData()
	at_betaKinit.type = MpcAttributeType.Real
	at_betaKinit.name = 'betaKinit/rayleigh'
	at_betaKinit.group = 'Optional'
	at_betaKinit.description = (
		html_par(html_begin()) +
		html_par(html_boldtext('betaKinit')+'<br/>') +
		html_par(html_href('http://opensees.berkeley.edu/wiki/index.php/Rayleigh_Damping_Command','rayleigh')+'<br/>') +
		html_end()
		)
	
	# betaKcomm
	at_betaKcomm = MpcAttributeMetaData()
	at_betaKcomm.type = MpcAttributeType.Real
	at_betaKcomm.name = 'betaKcomm/rayleigh'
	at_betaKcomm.group = 'Optional'
	at_betaKcomm.description = (
		html_par(html_begin()) +
		html_par(html_boldtext('betaKcomm')+'<br/>') +
		html_par(html_href('http://opensees.berkeley.edu/wiki/index.php/Rayleigh_Damping_Command','rayleigh')+'<br/>') +
		html_end()
		)
	
	
	
	xom = MpcXObjectMetaData()
	xom.name = 'region'
	xom.addAttribute(at_SelectionSets)
	xom.addAttribute(at_rtype)
	xom.addAttribute(at_type_elements)
	xom.addAttribute(at_type_nodes)
	xom.addAttribute(at_write_list)
	xom.addAttribute(at_list_name)
	xom.addAttribute(at_include_auto_generated_elements)
	xom.addAttribute(at_rayleigh)
	xom.addAttribute(at_alphaM)
	xom.addAttribute(at_Betak)
	xom.addAttribute(at_betaKinit)
	xom.addAttribute(at_betaKcomm)
	
	# VisibilityDependency
	xom.setVisibilityDependency(at_rayleigh, at_alphaM)
	xom.setVisibilityDependency(at_rayleigh, at_Betak)
	xom.setVisibilityDependency(at_rayleigh, at_betaKinit)
	xom.setVisibilityDependency(at_rayleigh, at_betaKcomm)
	
	xom.setVisibilityDependency(at_write_list, at_list_name)
	
	xom.setBooleanAutoExclusiveDependency(at_rtype, at_type_elements)
	xom.setBooleanAutoExclusiveDependency(at_rtype, at_type_nodes)
	
	xom.setVisibilityDependency(at_type_elements, at_include_auto_generated_elements)
	
	
	return xom

def extract_tags(pinfo, domain, tag, xobj, is_ele):
	if is_ele:
		include_auto_generated_elements_at = xobj.getAttribute('include_auto_generated_elements')
		if(include_auto_generated_elements_at is None):
			raise Exception('Error: cannot find "include_auto_generated_elements" attribute')
		include_auto_generated_elements = include_auto_generated_elements_at.string
		if include_auto_generated_elements == 'selection':
			for elem in domain.elements:
				tag.append(elem.id) # include source
		elif include_auto_generated_elements == 'selection + include_auto_generated_elements':
			for elem in domain.elements:
				tag.append(elem.id) # include source
				if elem.id in pinfo.auto_generated_element_data_map:
					ele_map = pinfo.auto_generated_element_data_map[elem.id]
					if (ele_map is not None):
						for id_elem_auto_generated in ele_map.elements:
							tag.append(id_elem_auto_generated) # include also auto-gen
		elif include_auto_generated_elements == 'include_auto_generated_elements - selection':
			for elem in domain.elements:
				if elem.id in pinfo.auto_generated_element_data_map:
					ele_map = pinfo.auto_generated_element_data_map[elem.id]
					if (ele_map is not None):
						for id_elem_auto_generated in ele_map.elements:
							tag.append(id_elem_auto_generated) # include only auto-gen
	else:
		for elem in domain.elements:
			for node in elem.nodes:
				tag.append(node.id)

def writeTcl(pinfo):
	# region $regTag <-ele ($ele1 $ele2 ...)> <-eleOnly ($ele1 $ele2 ...)> <-eleRange $startEle $endEle>
	# <-eleOnlyRange $startEle $endEle> <-node ($node1 $node2 ...)> <-nodeOnly ($node1 $node2 ...)>
	# <-nodeRange $startNode $endNode> <-nodeOnlyRange $startNode $endNode> <-node all> 
	# <-rayleigh $alphaM $betaK $betaKinit $betaKcomm>
	
	xobj = pinfo.analysis_step.XObject
	regTag = xobj.parent.componentId
	
	ClassName = xobj.name
	if pinfo.currentDescription != ClassName:
		pinfo.out_file.write('\n{}# {} {}\n'.format(pinfo.indent, xobj.Xnamespace, ClassName))
		pinfo.currentDescription = ClassName
	
	SelectionSets_at = xobj.getAttribute('SelectionSets')
	if(SelectionSets_at is None):
		raise Exception('Error: cannot find "SelectionSets" attribute')
	SelectionSets = SelectionSets_at.indexVector
	
	rtype_at = xobj.getAttribute('Region Type')
	if(rtype_at is None):
		raise Exception('Error: cannot find "Region Type" attribute')
	rtype = rtype_at.string
	is_ele = (rtype == 'Elements')
	
	doc = App.caeDocument()
	
	# get element and node tags
	tags = []
	for selection_set_id in SelectionSets:
		if not selection_set_id in doc.selectionSets: 
			continue
		selection_set = doc.selectionSets[selection_set_id]
		for geometry_id, geometry_subset in selection_set.geometries.items():
			mesh_of_geom = doc.mesh.meshedGeometries[geometry_id]
			for domain_id in geometry_subset.edges:
				domain = mesh_of_geom.edges[domain_id]
				extract_tags(pinfo, domain, tags, xobj, is_ele)
			for domain_id in geometry_subset.faces:
				domain = mesh_of_geom.faces[domain_id]
				extract_tags(pinfo, domain, tags, xobj, is_ele)
			for domain_id in geometry_subset.solids:
				domain = mesh_of_geom.solids[domain_id]
				extract_tags(pinfo, domain, tags, xobj, is_ele)
			if not is_ele:
				for domain_id in geometry_subset.vertices:
					domain = mesh_of_geom.vertices[domain_id]
					tags.append(domain.id)
		for interaction_id in selection_set.interactions:
			domain = doc.mesh.meshedInteractions[interaction_id]
			extract_tags(pinfo, domain, tags, xobj, is_ele)
	
	# quick return
	if len(tags) == 0:
		return
	
	# write on a list
	at_write_list = xobj.getAttribute('WriteOnList')
	if at_write_list is None:
		raise Exception('Error: Cannot find "WriteOnList" attribute')
	if at_write_list.boolean:
		at_list_name = xobj.getAttribute('List Name')
		if at_list_name is None:
			raise Exception('Error: Cannot find "List Name" attribute')
		list_name = at_list_name.string
		str_list = '\n{0}# List generated from region command.\n{0}set {1} {{\\\n{0}'.format(pinfo.indent, list_name)
		# update region data
		region_data = pinfo.regions_data
		region_data[regTag] = {
			'name': list_name,
		}
		counter = 0
		for i in tags:
			counter += 1
			if counter > 10:
				str_list += '\\\n'
				counter = 1
			str_list += '{} '.format(i)
		str_list += '}\n'
		pinfo.out_file.write(str_list)
	
	sopt =''
	rayleigh_at = xobj.getAttribute('rayleigh')
	if (rayleigh_at is None):
		raise Exception('Error: cannot find "rayleigh" attribute')
	if rayleigh_at.boolean:
		alphaM_at = xobj.getAttribute('alphaM/rayleigh')
		if(alphaM_at is None):
			raise Exception('Error: cannot find "alphaM" attribute')
		sopt += ' {}'.format(alphaM_at.real)
		
		Betak_at = xobj.getAttribute('Betak/rayleigh')
		if(Betak_at is None):
			raise Exception('Error: cannot find "Betak" attribute')
		sopt += ' {}'.format(Betak_at.real)
		
		betaKinit_at = xobj.getAttribute('betaKinit/rayleigh')
		if(betaKinit_at is None):
			raise Exception('Error: cannot find "betaKinit" attribute')
		sopt += ' {}'.format(betaKinit_at.real)
	
		betaKcomm_at = xobj.getAttribute('betaKcomm/rayleigh')
		if(betaKcomm_at is None):
			raise Exception('Error: cannot find "betaKcomm" attribute')
		sopt += ' {}'.format(betaKcomm_at.real)
	
	# process
	tags = list(set(tags))
	tags.sort()
	range_fun = ele_range_string if is_ele else node_range_string
	pinfo.out_file.write('\n{}region {}'.format(pinfo.indent, regTag))
	pinfo.out_file.write(''.join(range_fun(g) for _, g in groupby(tags, key=lambda n, c=count(): n-next(c))))
	if rayleigh_at.boolean:
		pinfo.out_file.write(' \\\n{}-rayleigh{}'.format(pinfo.indent, sopt))
	pinfo.out_file.write('\n')
 
