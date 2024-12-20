# ======================================================================================
# ADAPTIVE TRANSIENT ANALYSIS
# ======================================================================================

# ======================================================================================
# USER INPUT DATA 
# ======================================================================================

# duration and initial time step
set total_duration __total_time__
set initial_num_incr __initial_num_incr__

# parameters for adaptive time step
set max_factor __max_factor__
set min_factor __min_factor__
set max_factor_increment __max_factor_incr__
set min_factor_increment __min_factor__
set max_iter __max_iter__
set desired_iter __des_iter__

set STKO_VAR_increment 1
set factor 1.0
set old_factor $factor
set STKO_VAR_time 0.0
set initial_time_increment [expr $total_duration / $initial_num_incr]
set time_tolerance [expr abs($initial_time_increment) * 1.0e-8]

set STKO_VAR_initial_time_increment $initial_time_increment

while 1 {
	
	# check end of analysis
	if {[expr abs($STKO_VAR_time)] >= [expr abs($total_duration)]} {
		if {$STKO_VAR_process_id == 0} {
			puts "Target time has been reached. Current time = $STKO_VAR_time"
			puts "SUCCESS."
		}
		break
	}
	
	# compute new adapted time increment
	set STKO_VAR_time_increment [expr $initial_time_increment * $factor]
	if {[expr abs($STKO_VAR_time + $STKO_VAR_time_increment)] > [expr abs($total_duration) - $time_tolerance]} {
		set STKO_VAR_time_increment [expr $total_duration - $STKO_VAR_time]
	}
	
	# update integrator
	integrator __integrator_type__ __more_int_data__
	
	# before analyze
	STKO_CALL_OnBeforeAnalyze
	
	# perform this step
	set STKO_VAR_analyze_done [analyze 1 $STKO_VAR_time_increment]
	
	# update common variables
	if {$STKO_VAR_analyze_done == 0} {
		set STKO_VAR_num_iter [testIter]
		set STKO_VAR_time [expr $STKO_VAR_time + $STKO_VAR_time_increment]
		set STKO_VAR_percentage [expr $STKO_VAR_time/$total_duration]
		set norms [testNorms]
		if {$STKO_VAR_num_iter > 0} {set STKO_VAR_error_norm [lindex $norms [expr $STKO_VAR_num_iter-1]]} else {set STKO_VAR_error_norm 0.0}
	}
	
	# after analyze
	set STKO_VAR_afterAnalyze_done 0
	STKO_CALL_OnAfterAnalyze
	
	# check convergence
	if {$STKO_VAR_analyze_done == 0} {
		
		# print statistics
		if {$STKO_VAR_process_id == 0} {
			puts [format "Increment: %6d | Iterations: %4d | Norm: %8.3e | Progress: %7.3f %%" $STKO_VAR_increment $STKO_VAR_num_iter  $STKO_VAR_error_norm [expr $STKO_VAR_percentage*100.0]]
		}
		
		# update adaptive factor
		set factor_increment [expr min($max_factor_increment, [expr double($desired_iter) / double($STKO_VAR_num_iter)])]
		
		# check STKO_VAR_afterAnalyze_done. Simulate a reduction similar to non-convergence
		if {$STKO_VAR_afterAnalyze_done != 0} {
			set factor_increment [expr max($min_factor_increment, [expr double($desired_iter) / double($max_iter)])]
			if {$STKO_VAR_process_id == 0} {
				puts "Reducing increment factor due to custom error controls. Factor = $factor"
			}
		}
		
		set factor [expr $factor * $factor_increment]
		if {$factor > $max_factor} {
			set factor $max_factor
		}
		if {$STKO_VAR_process_id == 0} {
			if {$factor > $old_factor} {
				puts "Increasing increment factor due to faster convergence. Factor = $factor"
			}
		}
		set old_factor $factor
		
		# increment time step
		incr STKO_VAR_increment
		
	} else {
		
		# update adaptive factor
		set STKO_VAR_num_iter $max_iter
		set factor_increment [expr max($min_factor_increment, [expr double($desired_iter) / double($STKO_VAR_num_iter)])]
		set factor [expr $factor * $factor_increment]
		if {$STKO_VAR_process_id == 0} {
			puts "Reducing increment factor due to non convergence. Factor = $factor"
		}
		if {$factor < $min_factor} {
			if {$STKO_VAR_process_id == 0} {
				puts "ERROR: current factor is less then the minimum allowed ($factor < $min_factor)"
				puts "Giving up"
			}
			error "ERROR: the analysis did not converge"
		}
	}
	
}
