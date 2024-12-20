import PyMpc.Units as u
from PyMpc import *
from mpc_utils_html import *
import PyMpc
import PyMpc.Math
import math
import opensees.utils.tcl_input as tclin

def makeXObjectMetaData():
	
	# Function
	at_Function = MpcAttributeMetaData()
	at_Function.type = MpcAttributeType.String
	at_Function.name = '__mpc_function__'
	at_Function.group = 'Group'
	at_Function.description = (
		html_par(html_begin()) +
		html_par(html_boldtext('Function')+'<br/>') + 
		html_par('') +
		html_par(html_href('','')+'<br/>') +
		html_end()
		)
	at_Function.editable = False
	
	# tStart
	at_tStart = MpcAttributeMetaData()
	at_tStart.type = MpcAttributeType.Real
	at_tStart.name = 'tStart'
	at_tStart.group = 'Group'
	at_tStart.description = (
		html_par(html_begin()) +
		html_par(html_boldtext('tStart')+'<br/>') + 
		html_par('starting time of non-zero load factor') +
		html_par(html_href('http://opensees.berkeley.edu/wiki/index.php/Trigonometric_TimeSeries','Trigonometric TimeSeries')+'<br/>') +
		html_end()
		)
	at_tStart.setDefault(0.0)
	
	# tEnd
	at_tEnd = MpcAttributeMetaData()
	at_tEnd.type = MpcAttributeType.Real
	at_tEnd.name = 'tEnd'
	at_tEnd.group = 'Group'
	at_tEnd.description = (
		html_par(html_begin()) +
		html_par(html_boldtext('tEnd')+'<br/>') + 
		html_par('ending time of non-zero load factor') +
		html_par(html_href('http://opensees.berkeley.edu/wiki/index.php/Trigonometric_TimeSeries','Trigonometric TimeSeries')+'<br/>') +
		html_end()
		)
	at_tEnd.setDefault(1.0)
	
	# period
	at_period = MpcAttributeMetaData()
	at_period.type = MpcAttributeType.Real
	at_period.name = 'period'
	at_period.group = 'Group'
	at_period.description = (
		html_par(html_begin()) +
		html_par(html_boldtext('period')+'<br/>') + 
		html_par('characteristic period of sine wave') +
		html_par(html_href('http://opensees.berkeley.edu/wiki/index.php/Trigonometric_TimeSeries','Trigonometric TimeSeries')+'<br/>') +
		html_end()
		)
	at_period.setDefault(1.0)
	
	# -shift
	at_use_shift = MpcAttributeMetaData()
	at_use_shift.type = MpcAttributeType.Boolean
	at_use_shift.name = '-shift'
	at_use_shift.group = 'Group'
	at_use_shift.description = (
		html_par(html_begin()) +
		html_par(html_boldtext('-shift')+'<br/>') + 
		html_par('phase shift in radians (optional, default=0.0)') +
		html_par(html_href('http://opensees.berkeley.edu/wiki/index.php/Trigonometric_TimeSeries','Trigonometric TimeSeries')+'<br/>') +
		html_end()
		)
	
	# shift
	at_shift = MpcAttributeMetaData()
	at_shift.type = MpcAttributeType.Real
	at_shift.name = 'shift'
	at_shift.group = '-shift'
	at_shift.description = (
		html_par(html_begin()) +
		html_par(html_boldtext('shift')+'<br/>') + 
		html_par('phase shift in radians (optional, default=0.0)') +
		html_par(html_href('http://opensees.berkeley.edu/wiki/index.php/Trigonometric_TimeSeries','Trigonometric TimeSeries')+'<br/>') +
		html_end()
		)
	at_shift.setDefault(0.0)
	
	# factor
	at_factor = MpcAttributeMetaData()
	at_factor.type = MpcAttributeType.Boolean
	at_factor.name = '-factor'
	at_factor.group = 'Group'
	at_factor.description = (
		html_par(html_begin()) +
		html_par(html_boldtext('-factor')+'<br/>') + 
		html_par('the load factor amplification factor (optional, default=1.0)') +
		html_par(html_href('http://opensees.berkeley.edu/wiki/index.php/Trigonometric_TimeSeries','Trigonometric TimeSeries')+'<br/>') +
		html_end()
		)
	
	# cFactor
	at_cFactor = MpcAttributeMetaData()
	at_cFactor.type = MpcAttributeType.Real
	at_cFactor.name = 'cFactor'
	at_cFactor.group = '-factor'
	at_cFactor.description = (
		html_par(html_begin()) +
		html_par(html_boldtext('cFactor')+'<br/>') + 
		html_par('the load factor amplification factor (optional, default=1.0)') +
		html_par(html_href('http://opensees.berkeley.edu/wiki/index.php/Trigonometric_TimeSeries','Trigonometric TimeSeries')+'<br/>') +
		html_end()
		)
	at_cFactor.setDefault(1.0)
	
	xom = MpcXObjectMetaData()
	xom.name = 'Trig'
	xom.addAttribute(at_Function)
	xom.addAttribute(at_tStart)
	xom.addAttribute(at_tEnd)
	xom.addAttribute(at_period)
	xom.addAttribute(at_use_shift)
	xom.addAttribute(at_shift)
	xom.addAttribute(at_factor)
	xom.addAttribute(at_cFactor)
	
	
	# cFactor-dep
	xom.setVisibilityDependency(at_factor, at_cFactor)
	
	# shift-dep
	xom.setVisibilityDependency(at_use_shift, at_shift)
	
	return xom

def evaluateFunctionAttribute(xobj):
	if(xobj is None):
		print('Error: xobj is null\n')
		return PyMpc.Math.mat()
	
	if(xobj.name != 'Trig'):
		print('Error: invalid xobj type, expected "Trig", given "{}"'.format(xobj.name))
		return PyMpc.Math.mat()
	
	func_at = xobj.getAttribute('__mpc_function__')
	if(func_at is None):
		print('Error: cannot find "Function" attribute\n')
		return PyMpc.Math.mat()
	
	tStart_at = xobj.getAttribute('tStart')
	if(tStart_at is None):
		print('Error: cannot find "tStart" attribute\n')
		return PyMpc.Math.mat()
	
	tEnd_at = xobj.getAttribute('tEnd')
	if(tEnd_at is None):
		print('Error: cannot find "tEnd" attribute\n')
		return PyMpc.Math.mat()
	
	period_at = xobj.getAttribute('period')
	if(period_at is None):
		print('Error: cannot find "period" attribute\n')
		return PyMpc.Math.mat()
	
	use_shift_at = xobj.getAttribute('-shift')
	if(use_shift_at is None):
		print('Error: cannot find "-shift" attribute\n')
		return PyMpc.Math.mat()
	
	shift_at = xobj.getAttribute('shift')
	if(shift_at is None):
		print('Error: cannot find "-shift" attribute\n')
		return PyMpc.Math.mat()
	
	fact_at = xobj.getAttribute('-factor')
	if(fact_at is None):
		print('Error: cannot find "-factor" attribute\n')
		return PyMpc.Math.mat()
	
	cFactor_at = xobj.getAttribute('cFactor')
	if(cFactor_at is None):
		print('Error: cannot find "cFactor" attribute\n')
		return PyMpc.Math.mat()
	
	tStart = tStart_at.real
	tEnd = tEnd_at.real
	period = period_at.real
	shift = shift_at.real
	cFactor = cFactor_at.real
	
	if(period<=0):
		raise Exception('Invalid period value')
	if(tStart>=tEnd):
		raise Exception('Invalid domain (tStart >= tEnd)')
	
	Dt = tEnd - tStart
	n = int(math.ceil(Dt/period))
	
	pnt_min = 4
	pnt_max = 50
	min_at = 50
	max_at = 2
	ns = (float(n) - float(min_at))/float(max_at - min_at)
	ns = max(0.0, min(1.0, ns))
	ns = int(ns*(pnt_max - pnt_min) + pnt_min)
	
	pnt = ns*n + 1
	ddt = Dt/(pnt-1)
	pnt = int(Dt/ddt)+1
	
	xy = PyMpc.Math.mat(pnt+4, 2) 	#matrix size
	xy[0, 0] = tStart-Dt/10			#x
	xy[0, 1] = 0.0					#y
	xy[1, 0] = tStart				#x
	xy[1, 1] = 0.0					#y
	
	xy[pnt+2, 0] = tEnd				#x (pnt+2 because it starts from 0)
	xy[pnt+2, 1] = 0.0				#y (pnt+2 because it starts from 0)
	xy[pnt+3, 0] = tEnd+Dt/10		#x (pnt+3 because it starts from 0)
	xy[pnt+3, 1] = 0.0				#y (pnt+3 because it starts from 0)
	
	c = 2
	for i in range(pnt):
		ix = tStart + i*ddt
		xy[c, 0] = ix
		xy[c, 1] = cFactor*math.sin((2.0*math.pi*(ix-tStart)/period)+shift)
		c+=1
	
		
	
	return xy

def writeTcl(pinfo):
	
	#timeSeries Trig $tag $tStart $tEnd $period <-factor $cFactor> <-shift $shift>
	xobj = pinfo.definition.XObject
	
	ClassName = xobj.name
	if pinfo.currentDescription != ClassName:
		pinfo.out_file.write('\n{}# {} {}\n'.format(pinfo.indent, xobj.Xnamespace, ClassName))
		pinfo.currentDescription = ClassName
	
	tag = xobj.parent.componentId
	
	# mandatory parameters
	tStart_at = xobj.getAttribute('tStart')
	if(tStart_at is None):
		raise Exception('Error: cannot find "tStart" attribute')
	tStart = tStart_at.real
	
	tEnd_at = xobj.getAttribute('tEnd')
	if(tEnd_at is None):
		raise Exception('Error: cannot find "tEnd" attribute')
	tEnd = tEnd_at.real
	
	period_at = xobj.getAttribute('period')
	if(period_at is None):
		raise Exception('Error: cannot find "period" attribute')
	period = period_at.real
	
	
	# optional paramters
	sopt = ''
	
	fact_at = xobj.getAttribute('-factor')
	if(fact_at is None):
		raise Exception('Error: cannot find "-factor" attribute\n')
	fact = fact_at.boolean
	if fact:
		cFactor_at = xobj.getAttribute('cFactor')
		if(cFactor_at is None):
			raise Exception('Error: cannot find "cFactor" attribute')
		cFactor = cFactor_at.real
		sopt += ' -factor {}'.format(cFactor)
	
	use_shift_at = xobj.getAttribute('-shift')
	if(use_shift_at is None):
		raise Exception('Error: cannot find "-shift" attribute')
	use_shift = use_shift_at.boolean
	if use_shift:
		shift_at = xobj.getAttribute('shift')
		if(shift_at is None):
			raise Exception('Error: cannot find "shift" attribute')
		shift = shift_at.real
		sopt += ' -shift {}'.format(shift)
	
	str_tcl = '{}timeSeries Trig {} {} {} {}{}\n'.format(pinfo.indent, tag, tStart, tEnd, period, sopt)
	
	# now write the string into the file
	pinfo.out_file.write(str_tcl)