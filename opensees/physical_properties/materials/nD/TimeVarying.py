import PyMpc.Units as u
from PyMpc import *
from mpc_utils_html import *
import opensees.utils.tcl_input as tclin

def makeXObjectMetaData():
	
    # E
    at_E = MpcAttributeMetaData()
    at_E.type = MpcAttributeType.QuantityScalar
    at_E.name = 'E'
    at_E.group = 'Elasticity'
    at_E.description = (
        html_par(html_begin()) +
        html_par(html_boldtext('E')+'<br/>') + 
        html_par('elastic Modulus') +
        html_par(html_href('http://opensees.berkeley.edu/wiki/index.php/Elastic_Isotropic_Material','Elastic Isotropic Material')+'<br/>') +
        html_end()
        )
    at_E.dimension = u.F/u.L**2

    # v
    at_v = MpcAttributeMetaData()
    at_v.type = MpcAttributeType.Real
    at_v.name = 'v'
    at_v.group = 'Elasticity'
    at_v.description = (
        html_par(html_begin()) +
        html_par(html_boldtext('v')+'<br/>') + 
        html_par('Poisson\'s ratio') +
        html_par(html_href('http://opensees.berkeley.edu/wiki/index.php/Elastic_Isotropic_Material','Elastic Isotropic Material')+'<br/>') +
        html_end()
        )

    # time_intervals (ti)
    at_ti = MpcAttributeMetaData()
    at_ti.type = MpcAttributeType.Real
    at_ti.name = 'ti'
    at_ti.group = 'Elasticity'
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
    at_it.group = 'Elasticity'
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
    at_ft.group = 'Elasticity'
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
    xom.addAttribute(at_E)
    xom.addAttribute(at_v)
    xom.addAttribute(at_ti)
    xom.addAttribute(at_it)
    xom.addAttribute(at_ft)

	
    return xom

def writeTcl(pinfo):
	
    #nDMaterial ElasticIsotropic $matTag $E $v 
    xobj = pinfo.phys_prop.XObject
    tag = xobj.parent.componentId

    # mandatory parameters
    E_at = xobj.getAttribute('E')
    if(E_at is None):
        raise Exception('Error: cannot find "E" attribute')
    E = E_at.quantityScalar

    v_at = xobj.getAttribute('v')
    if(v_at is None):
        raise Exception('Error: cannot find "v" attribute')
    v = v_at.real

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
    str_tcl = f'{pinfo.indent}nDMaterial TimeVarying {tag} 1 {int(ti)} {it} {ft} ' + ' '.join([f'{E.value}'] * int(ti)) + ' ' + ' '.join([f'{v}'] * int(ti)) + ' ' + ' '.join(['1'] * int(ti)) + f' {sopt}\n'
    
    # now write the string into the file
    pinfo.out_file.write(str_tcl)

