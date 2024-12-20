import PyMpc.Units as u
from PyMpc import *
from mpc_utils_html import *
import importlib
import opensees.utils.tcl_input as tclin

def _get_xobj_attribute(xobj, at_name):
	attribute = xobj.getAttribute(at_name)
	if attribute is None:
		raise Exception('Error: cannot find "{}" attribute'.format(at_name))
	return attribute

def makeXObjectMetaData():
	
	# beam
	at_beam = MpcAttributeMetaData()
	at_beam.type = MpcAttributeType.Index
	at_beam.name = 'Beam Element'
	at_beam.group = 'Group'
	at_beam.description = (
		html_par(html_begin()) +
		html_par(html_boldtext('Beam Element Property')+'<br/>') +
		html_par('Choose a valid Beam Element Property') +
		html_par(html_href('','')+'<br/>') +
		html_end()
		)
	at_beam.indexSource.type = MpcAttributeIndexSourceType.ElementProperty
	at_beam.indexSource.addAllowedNamespace('beam_column_elements')
	
	xom = MpcXObjectMetaData()
	xom.name = 'BeamWithShearHinge'
	xom.addAttribute(at_beam)
	
	return xom

def getNodalSpatialDim(xobj, xobj_phys_prop):
	
	# checks
	doc = App.caeDocument()
	if(doc is None):
		raise Exception('null cae document')
	
	if xobj_phys_prop.name != 'BeamWithShearHingeProperty':
		raise Exception('Wrong material type for "BeamWithShearHinge" element. Expected: "BeamWithShearHingeProperty", given: "{}"'.format(xobj_phys_prop.name))
	
	# read element properties
	xobj_ep_beam_index = _get_xobj_attribute(xobj, 'Beam Element').index
	ep_Beam = doc.elementProperties[xobj_ep_beam_index]
	ep_Beam_xobj = ep_Beam.XObject
	
	# read physical properties
	xobj_pp_beam_index = _get_xobj_attribute(xobj_phys_prop, 'Beam Property').index
	pp_Beam = doc.physicalProperties[xobj_pp_beam_index]
	pp_Beam_xobj = pp_Beam.XObject
	
	# read module and getNodalSpatialDim
	ep_Beam_module_name = 'opensees.element_properties.{}.{}'.format(ep_Beam_xobj.Xnamespace, ep_Beam_xobj.name)
	ep_Beam_module = importlib.import_module(ep_Beam_module_name)
	dim = ep_Beam_module.getNodalSpatialDim(ep_Beam_xobj, pp_Beam_xobj)
	if len(dim) != 2:
		raise Exception('BeamWithShearHinge needs an element property with 2 nodes : {}'.format(dim))
	for idim in dim:
		if idim[0] != 3 or idim[1] != 6:
			raise Exception('BeamWithShearHinge needs an element property with NDM = 3 and NDF = 6 : {}'.format(idim))
	return dim

def writeTcl(pinfo):
	
	# get document
	doc = App.caeDocument()
	if(doc is None):
		raise Exception('null cae document')
	
	# get element and check it
	elem = pinfo.elem
	if elem.topologyType() != MpcElementTopologyType.Edge:
		raise Exception('Error: element must be "Edge" and not "{}"'.format(elem.topologyType().name))
	if len(elem.nodes) != 2:
		raise Exception('Error: internal element for "BeamWithShearHinge" beam must have 2 nodes')
	tag = elem.id
	
	# get physical and element properties
	phys_prop = pinfo.phys_prop
	elem_prop = pinfo.elem_prop
	if(phys_prop is None):
		raise Exception('Error: Null physical property. Please assign a physical property of type "BeamWithShearHingeProperty"')
	if(elem_prop is None):
		raise Exception('Error: Null element property. Please assign an element property of type "BeamWithShearHinge"')
	
	# get element properties
	xobj_ep_beam_index = _get_xobj_attribute(elem_prop.XObject, 'Beam Element').index
	
	# get physical properties
	if phys_prop.XObject.name != 'BeamWithShearHingeProperty':
		raise Exception('Wrong material type for "BeamWithShearHinge" element. Expected: "BeamWithShearHingeProperty", given: "{}"'.format(phys_prop.XObject.name))
	xobj_pp_beam_index = _get_xobj_attribute(phys_prop.XObject, 'Beam Property').index
	
	# get or create the custom data for this element property.
	# A map
	# Key = tuple(geom_id, edge_id)
	# Value = boolean
	# Note for Value: now we just need to see if a key is present or not,
	#   but for future usage, we may need to map other values.
	gemap_name = 'BeamWithShearHinge'
	if gemap_name in pinfo.custom_data:
		gemap = pinfo.custom_data[gemap_name]
	else:
		gemap = dict()
		pinfo.custom_data[gemap_name] = gemap
	
	# compute hinge position if necessary
	def check_hinge():
		center = 0.5-1.0e-6
		for geom_id, mog in doc.mesh.meshedGeometries.items():
			for edge_id in range(len(mog.edges)):
				domain = mog.edges[edge_id]
				for i in range(len(domain.elements)):
					trial = domain.elements[i]
					if trial.id == elem.id:
						# Found the Edge domain this element belongs to
						#print('Found element {} in Geometry: {} - Edge: {}'.format(elem.id, geom_id, edge_id))
						
						# let's see if we already put a hinge in this edge
						gemap_key = (geom_id, edge_id)
						if gemap_key in gemap:
							return None
						
						# find bounds of the whole edge
						pmin = None
						pmax = None
						for ieinfo in domain.elementGeomInfos:
							for iuv in ieinfo.uv:
								if pmin is None:
									pmin = iuv.x
									pmax = iuv.x
								else:
									pmin = min(pmin, iuv.x)
									pmax = max(pmax, iuv.x)
						# parametric beam location in the middle of the edge
						pmiddle = (pmin+pmax)/2.0
						
						# sort element nodes with parameters, sort also local node position
						elem_param = domain.elementGeomInfos[i]
						Ui = elem_param.uv[0].x
						Uj = elem_param.uv[1].x
						Pi = elem.nodes[0].position
						Pj = elem.nodes[1].position
						Li = 0
						Lj = 1
						if Ui > Uj:
							Ui, Uj = Uj, Ui
							Pi, Pj = Pj, Pi
							Li, Lj = Lj, Li
						
						# check whether pmiddle is within the element parameters (or on the boundaries)
						tolerance = 1.0e-3*(Uj-Ui)
						if pmiddle < Ui-tolerance or pmiddle > Uj+tolerance:
							return None
						
						# normalize element parameters
						Uspan = Uj-Ui
						Uc = (pmiddle-Ui)/Uspan
						Uj = (Uj-Ui)/Uspan
						Ui = 0.0
						Lc = None
						# to avoid very small elements...
						Usmall = 0.1
						if Uc < Usmall:
							Uc = 0.0
							Lc = Li
						elif Uc > 1.0-Usmall:
							Uc = 1.0
							Lc = Lj
						
						# compute hinge point
						Pc = Pi + (Pj - Pi)*Uc
						
						# store as already processed and return
						gemap[gemap_key] = True
						return (Pc, Uc, Lc)
		return None
	hp = check_hinge()
	
	# save original nodes' ids, they are going to be changed for processing inner elements
	# and then set back to the original ones
	# why? because the nodes generated by STKO are put into the model map
	# moreover, since they are created here, they are not in the node_to_model_map
	# just add their ndm/ndf pair to the node_to_model_map copying from the exterior ones
	exterior_node_i = pinfo.elem.nodes[0].id
	exterior_node_j = pinfo.elem.nodes[1].id
	# since we are going to change them (probably) with the joint model ...
	# save a copy to be used in the finally statement
	exterior_node_i_copy = exterior_node_i
	exterior_node_j_copy = exterior_node_j
	
	# prepare common data for writing
	ndm_ndf = pinfo.node_to_model_map[pinfo.elem.nodes[0].id]
	pinfo.updateModelBuilder(ndm_ndf[0], ndm_ndf[1])
	FMT = pinfo.get_double_formatter()
	ep_Beam = doc.elementProperties[xobj_ep_beam_index]
	ep_Beam_xobj = ep_Beam.XObject
	
	# write and extra node
	def define_node(pos, mass = None):
		node_aux = pinfo.next_node_id
		pinfo.next_node_id += 1
		pinfo.node_to_model_map[node_aux] = pinfo.node_to_model_map[exterior_node_i_copy] # i and j dims are the same
		pinfo.out_file.write('{}# extra node for shear hinge\n'.format(pinfo.indent))
		if mass is not None:
			pinfo.out_file.write('{}node {}  {} {} {}  -mass {} {} {} {} {} {}\n'.format(
				pinfo.indent, node_aux, 
				FMT(pos.x), FMT(pos.y), FMT(pos.z),
				FMT(mass[0]), FMT(mass[1]), FMT(mass[2]), 
				FMT(mass[3]), FMT(mass[4]), FMT(mass[5]),
				))
		else:
			pinfo.out_file.write('{}node {}  {} {} {}\n'.format(pinfo.indent, node_aux, FMT(pos.x), FMT(pos.y), FMT(pos.z)))
		return node_aux
	
	# get the mass of a node
	def get_node_mass(node_id):
		mass = pinfo.mass_to_node_map.get(node_id, [0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
		if len(mass) != 6:
			raise Exception('Nodal mass, if defined, at node {} should have 6 components'.format(node_id))
		return mass[:] # return a copy
	
	# scales a mass
	def scale_mass(mass, scale):
		for i in range(len(mass)):
			mass[i] *= scale
	
	# avg of masses
	def mass_avg(m1, m2):
		return [(m1[i]+m2[i])/2.0 for i in range(len(m1))]
	
	# difference of 2 masses
	def mass_diff(m1, m2):
		return [(m1[i] - m2[i]) for i in range(len(m1))]
	
	# update a mass in OpenSees
	def update_mass(node_id, mass):
		pinfo.out_file.write('{}mass {}   {} {} {} {} {} {}\n'.format(
			pinfo.indent, node_id,
			FMT(mass[0]), FMT(mass[1]), FMT(mass[2]), 
			FMT(mass[3]), FMT(mass[4]), FMT(mass[5])))
	
	# generate new element id
	def gen_ele_id():
		tag = pinfo.next_elem_id
		pinfo.next_elem_id += 1
		if elem.id in pinfo.auto_generated_element_data_map:
			auto_gen_data = pinfo.auto_generated_element_data_map[elem.id]
		else:
			auto_gen_data = tclin.auto_generated_element_data()
			pinfo.auto_generated_element_data_map[elem.id] = auto_gen_data
		auto_gen_data.elements.append(tag)
		return tag
	
	# get vector global direction index (1, 2, 3, or 0 if not alligned)
	def get_vec_gdir(v):
		for i in range(3):
			if abs(v[i]) > 0.99:
				return i+1
		return 0
	
	# write the shear hinge
	def define_hinge(n1, n2):
		tag = gen_ele_id()
		# orientation vectors
		orientation = elem.orientation.computeOrientation()
		vx = orientation.col(0)
		vy = orientation.col(1)
		pinfo.out_file.write('{}# Shear hinge definition\n'.format(pinfo.indent))
		mat_Vy = _get_xobj_attribute(phys_prop.XObject, 'Vy Material').index
		mat_Vz = _get_xobj_attribute(phys_prop.XObject, 'Vz Material').index
		vx_gdir = get_vec_gdir(vx)
		if vx_gdir > 0:
			# equal dofs
			pinfo.out_file.write('{}equalDOF {} {} {} 4 5 6\n'.format(
				pinfo.indent, n1, n2, vx_gdir)
				)
			# write zerolength
			pinfo.out_file.write(
				'{0}element zeroLength {1} {2} {3} -mat {4} {5} -dir 2 3 -orient {6} {7} {8} {9} {10} {11}\n'.format(
					pinfo.indent, tag, n1, n2, 
					mat_Vy, mat_Vz,
					vx.x, vx.y, vx.z, vy.x, vy.y, vy.z)
				)
		else:
			# materials
			mat_K = pinfo.next_physicalProperties_id
			pinfo.next_physicalProperties_id += 1
			K = _get_xobj_attribute(phys_prop.XObject, 'K').real
			pinfo.out_file.write('{}uniaxialMaterial Elastic {} {}\n'.format(pinfo.indent, mat_K, K))
			# write zerolength
			pinfo.out_file.write(
				'{0}element zeroLength {1} {2} {3} -mat {4} {5} {6} {4} {4} {4} -dir 1 2 3 4 5 6 -orient {7} {8} {9} {10} {11} {12}\n'.format(
					pinfo.indent, tag, n1, n2, 
					mat_K, mat_Vy, mat_Vz,
					vx.x, vx.y, vx.z, vy.x, vy.y, vy.z)
				)
	# write the beam
	def define_beam():
		ep_Beam_module_name = 'opensees.element_properties.{}.{}'.format(ep_Beam_xobj.Xnamespace, ep_Beam_xobj.name)
		ep_Beam_module = importlib.import_module(ep_Beam_module_name)
		ep_Beam_module.writeTcl(pinfo)
	
	# Put the following code into a try-catch block, due to hacks...
	try:
		
		# if no hinge should be generated, write the beam and go on
		if hp is None:
			# hack properties !!
			pinfo.phys_prop = doc.physicalProperties[xobj_pp_beam_index]
			pinfo.elem_prop = doc.elementProperties[xobj_ep_beam_index]
			# beam
			define_beam()
			# done
			return
		
		# we have to crete an hinge
		hpos = hp[0]
		hparam = hp[1]
		hloc = hp[2]
		#print('Creating shear hinge at position ({}, {}, {}) [param {}]'.format(hpos.x, hpos.y, hpos.z, hparam))
		
		# apply correction for joints (2D)??
		node_vect = [exterior_node_i, exterior_node_j]
		if 'RCJointModel3D' in pinfo.custom_data:
			joint_manager = pinfo.custom_data['RCJointModel3D']
			node_pos = joint_manager.adjustBeamConnectivity(pinfo, elem, node_vect)
		else:
			node_pos = [elem.nodes[0].position, elem.nodes[1].position]
		exterior_node_i = node_vect[0]
		exterior_node_j = node_vect[1]
		
		# case 1: hinge at first position
		if hloc == 0:
			
			# create an extra node at start
			M1 = get_node_mass(exterior_node_i)
			scale_mass(M1, 0.5)
			update_mass(exterior_node_i, M1)
			N2 = define_node(node_pos[0], mass = M1)
			
			# hinge at start
			define_hinge(exterior_node_i, N2)
			
			# beam from N2 to exterior_node_j
			# hack properties !!
			pinfo.phys_prop = doc.physicalProperties[xobj_pp_beam_index]
			pinfo.elem_prop = doc.elementProperties[xobj_ep_beam_index]
			# hack elem nodal id!!!!
			pinfo.elem.nodes[0].id = N2
			define_beam()
		
		# case 2: hinge at last position
		elif hloc == 1:
			
			# create an extra node at end
			M2 = get_node_mass(exterior_node_j)
			scale_mass(M2, 0.5)
			update_mass(exterior_node_j, M2)
			N2 = define_node(node_pos[1], mass = M2)
			
			# beam from exterior_node_i to N2
			# hack properties !!
			pinfo.phys_prop = doc.physicalProperties[xobj_pp_beam_index]
			pinfo.elem_prop = doc.elementProperties[xobj_ep_beam_index]
			# hack elem nodal id!!!!
			pinfo.elem.nodes[1].id = N2
			define_beam()
			
			# hinge at end
			define_hinge(N2, exterior_node_j)
			
		# case 3: hinge within 2 beams
		else:
			
			# check masses
			M1 = get_node_mass(exterior_node_i)
			M2 = get_node_mass(exterior_node_j)
			# we assume half of the source mass at each node comes from this element
			M1_source = M1[:]
			M2_source = M2[:]
			scale_mass(M1, 0.5)
			scale_mass(M2, 0.5)
			# compute an avg
			MA = mass_avg(M1, M2)
			scale_mass(MA, 0.5) # split in 2 equal parts
			# update previous nodes
			update_mass(exterior_node_i, mass_diff(M1_source, MA))
			update_mass(exterior_node_j, mass_diff(M2_source, MA))
			# create an 2 extra nodes at hpos
			N1 = define_node(hpos, mass = MA)
			N2 = define_node(hpos, mass = MA)
			
			# beam from exterior_node_i to N1
			# hack properties !!
			pinfo.phys_prop = doc.physicalProperties[xobj_pp_beam_index]
			pinfo.elem_prop = doc.elementProperties[xobj_ep_beam_index]
			# hack elem nodal id!!!!
			pinfo.elem.nodes[0].id = exterior_node_i
			pinfo.elem.nodes[1].id = N1
			define_beam()
			
			# hinge at hpos
			define_hinge(N1, N2)
			
			# beam from N2 to exterior_node_j (extra)
			aux_tag = gen_ele_id()
			pinfo.mpco_cdata_utils.mapElement(elem.id, aux_tag)
			# hack elements id
			pinfo.elem.id = aux_tag
			# hack elem nodal id!!!!
			pinfo.elem.nodes[0].id = N2
			pinfo.elem.nodes[1].id = exterior_node_j
			define_beam()
			
	except Exception as the_exception:
		raise the_exception
	
	finally:
		# get rid of the hack
		pinfo.elem.nodes[0].id = exterior_node_i_copy
		pinfo.elem.nodes[1].id = exterior_node_j_copy
		pinfo.elem.id = tag
		pinfo.phys_prop = phys_prop
		pinfo.elem_prop = elem_prop
