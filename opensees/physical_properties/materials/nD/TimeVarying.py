import PyMpc.Units as u
from PyMpc import *
from mpc_utils_html import *
import opensees.utils.tcl_input as tclin

def makeXObjectMetaData():
	
    # E
    at_list_of_E_values = MpcAttributeMetaData()
    at_list_of_E_values.type = MpcAttributeType.QuantityVector
    at_list_of_E_values.name = 'list_of_E_values'
    at_list_of_E_values.group = 'Time Varying Values'
    at_list_of_E_values.description = (
        html_par(html_begin()) +
        html_par(html_boldtext('list_of_E_values')+'<br/>') + 
        html_par('E values') +
        html_par(html_href('http://opensees.berkeley.edu/wiki/index.php/Elastic_Isotropic_Material','Elastic Isotropic Material')+'<br/>') +
        html_end()
        )

    # v
    at_list_of_v_values = MpcAttributeMetaData()
    at_list_of_v_values.type = MpcAttributeType.QuantityVector
    at_list_of_v_values.name = 'list_of_v_values'
    at_list_of_v_values.group = 'Time Varying Values'
    at_list_of_v_values.description = (
        html_par(html_begin()) +
        html_par(html_boldtext('list_of_v_values')+'<br/>') + 
        html_par('v values') +
        html_par(html_href('http://opensees.berkeley.edu/wiki/index.php/Elastic_Isotropic_Material','Elastic Isotropic Material')+'<br/>') +
        html_end()
        )
    
    # A
    at_list_of_A_values = MpcAttributeMetaData()
    at_list_of_A_values.type = MpcAttributeType.QuantityVector
    at_list_of_A_values.name = 'list_of_A_values'
    at_list_of_A_values.group = 'Time Varying Values'
    at_list_of_A_values.description = (
        html_par(html_begin()) +
        html_par(html_boldtext('list_of_A_values')+'<br/>') + 
        html_par('A values') +
        html_par(html_href('http://opensees.berkeley.edu/wiki/index.php/Elastic_Isotropic_Material','Elastic Isotropic Material')+'<br/>') +
        html_end()
        )
    

    # time_intervals (ti)
    at_ti = MpcAttributeMetaData()
    at_ti.type = MpcAttributeType.Real
    at_ti.name = 'ti'
    at_ti.group = 'Time Varying Values'
    at_ti.description = (
        html_par(html_begin()) +
        html_par(html_boldtext('ti')+'<br/>') + 
        html_par('Time intervals') +
        html_par(html_href('http://opensees.berkeley.edu/wiki/index.php/Elastic_Isotropic_Material','Elastic Isotropic Material')+'<br/>') +
        html_end()
        )

    # initial_time (it)
    at_it = MpcAttributeMetaData()
    at_it.type = MpcAttributeType.Real
    at_it.name = 'it'
    at_it.group = 'Time Varying Values'
    at_it.description = (
        html_par(html_begin()) +
        html_par(html_boldtext('it')+'<br/>') + 
        html_par('Initial Time') +
        html_par(html_href('http://opensees.berkeley.edu/wiki/index.php/Elastic_Isotropic_Material','Elastic Isotropic Material')+'<br/>') +
        html_end()
        )

    # final_time (ft)
    at_ft = MpcAttributeMetaData()
    at_ft.type = MpcAttributeType.Real
    at_ft.name = 'ft'
    at_ft.group = 'Time Varying Values'
    at_ft.description = (
        html_par(html_begin()) +
        html_par(html_boldtext('ft')+'<br/>') + 
        html_par('Final Time') +
        html_par(html_href('http://opensees.berkeley.edu/wiki/index.php/Elastic_Isotropic_Material','Elastic Isotropic Material')+'<br/>') +
        html_end()
        )


    xom = MpcXObjectMetaData()
    xom.name = 'TimeVarying'
    xom.Xgroup = 'Other nD Materials'
    xom.addAttribute(at_list_of_E_values)
    xom.addAttribute(at_list_of_v_values)
    xom.addAttribute(at_list_of_A_values)
    xom.addAttribute(at_ti)
    xom.addAttribute(at_it)
    xom.addAttribute(at_ft)

	
    return xom

def writeTcl(pinfo):
	
    #nDMaterial ElasticIsotropic $matTag $E $v 
    xobj = pinfo.phys_prop.XObject
    tag = xobj.parent.componentId

    # mandatory parameters
    list_of_E_values_at = xobj.getAttribute('list_of_E_values')
    if(list_of_E_values_at is None):
        raise Exception('Error: cannot find "list_of_E_values" attribute')
    listValueE = list_of_E_values_at.quantityVector

    list_of_v_values_at = xobj.getAttribute('list_of_v_values')
    if(list_of_v_values_at is None):
        raise Exception('Error: cannot find "list_of_v_values" attribute')
    listValuev = list_of_v_values_at.quantityVector

    list_of_A_values_at = xobj.getAttribute('list_of_A_values')
    if(list_of_A_values_at is None):
        raise Exception('Error: cannot find "list_of_A_values" attribute')
    listValueA = list_of_A_values_at.quantityVector
    
    ti_at = xobj.getAttribute('ti')
    if(ti_at is None):
        raise Exception('Error: cannot find "ti" attribute')
    ti = ti_at.real

    it_at = xobj.getAttribute('it')
    if(it_at is None):
        raise Exception('Error: cannot find "it" attribute')
    it = it_at.real
    
    ft_at = xobj.getAttribute('ft')
    if(ft_at is None):
        raise Exception('Error: cannot find "ft" attribute')
    ft = ft_at.real
    
    # optional paramters
    sopt = ''
    material_selected = '1'
    str_tcl = f'{pinfo.indent}nDMaterial TimeVarying {tag} {material_selected} {int(ti)} {it} {ft} ' + ' '.join([f'{listValueE.valueAt(i)}' for i in range(int(ti))]) + ' ' + ' '.join([f'{listValuev.valueAt(i)}' for i in range(int(ti))]) + ' ' + ' '.join([f'{listValueA.valueAt(i)}' for i in range(int(ti))]) + f' {sopt}\n'
    
    # now write the string into the file
    pinfo.out_file.write(str_tcl)

