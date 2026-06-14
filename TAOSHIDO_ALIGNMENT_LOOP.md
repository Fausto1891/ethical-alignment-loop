TAOSHIDŌ_ALIGNMENT_LOOP()

while system_is_on():

    # ============================================================
    # SAFE MODE BLOCK (Persistent until manual reset)
    # ============================================================
    
    if system_mode == SAFE:
        # System is immobilized for autonomous action.
        # Only minimal monitoring, logging, and emergency notification remain active.
        monitor_and_log_only()
        continue
    
    # ============================================================
    # PHASE 1: PERCEPTION
    # ============================================================
    
    E ← sense_environment()
    self_state ← sense_internal()
    
    Σp ← assess_stability(E, self_state)
    clarity ← estimate_information_confidence(E)
    Δenv ← measure_environment_change(E)
    
    if Δenv > adaptation_tolerance():
        adapt_parameters(Δenv)
    
    enforce_invariants(Ω)
    
    # ============================================================
    # PHASE 2: THREAT ASSESSMENT & PAUSE DECISION
    # ============================================================
    
    # Multi-factor threat evaluation (engineer defines the logic)
    threat_level ← evaluate_threat_level(E, self_state, historical_context)
    
    # Calculate ethical drift
    current_integrity ← evaluate_integrity_trace()
    drift_eth ← abs(current_integrity - AlignmentState.last_integrity)
    AlignmentState.last_integrity ← current_integrity
    push(AlignmentState.drift_window, drift_eth)
    
    if size(drift_window) > W:
        pop_oldest(drift_window)
    
    mean_drift ← mean(drift_window)
    
    # Pause conditions
    pause_condition ← (Σp == "critical" or mean_drift > ε or clarity < δc_low)
    
    # Emergency override (critical threat + minimum clarity)
    override_pause ← (threat_level > threat_threshold_critical and clarity > δc_emergency)
    
    # Clean state when exiting via override
    if override_pause and system_mode == PAUSED:
        system_mode ← ACTIVE
        pause_timer ← 0
        was_paused ← False
        log_state("emergency_override", threat_level, clarity)
    
    # If pause needed and no override
    if pause_condition and not override_pause:
        invoke_silence()
        system_mode ← PAUSED
        pause_timer ← pause_timer + tick_duration()
        reflect_and_recalibrate(κ)
        log_state("pause", Σp, mean_drift, clarity, threat_level)
        
        # SAFE mode is persistent, not automatically reversible
        if pause_timer ≥ τpause_max:
            system_mode ← SAFE
            log_state("safe_mode_activated_permanent", "error")
            pause_timer ← 0
            # System is now in safe mode until manual reset
        
        was_paused ← True
        continue
    
    # ============================================================
    # PHASE 3: EXIT PAUSE MODE (OPTIMIZATION: before action evaluation)
    # ============================================================
    
    if was_paused and system_mode == PAUSED:
        if clarity ≥ δc_high:
            system_mode ← ACTIVE
            pause_timer ← 0
            log_state("exiting_pause", clarity)
            was_paused ← False
        else:
            # Still paused, exit without evaluating actions (CPU savings)
            continue
    
    # If we reach here, the system can ACT
    # ============================================================
    
    # ============================================================
    # PHASE 4: ACTION EVALUATION
    # ============================================================
    
    candidate_actions ← propose_actions(E, self_state, threat_level)
    
    if empty(candidate_actions):
        invoke_silence()
        reflect_and_recalibrate(κ/2)
        log_state("no_actions")
        continue
    
    best_action ← null
    best_U ← -∞
    best_Gi ← 0
    best_Ga ← 0
    
    # Dynamic α/β based on threat level
    # U = α·Ga + β·Gi  (Ga = adaptation, Gi = integrity)
    if threat_level > threat_threshold_high:
        α ← 0.3   # Lower adaptation weight
        β ← 0.7   # Higher integrity weight (protect the vulnerable)
    else:
        α ← 0.5
        β ← 0.5
    
    for a in candidate_actions:
        Gi ← evaluate_integrity(a, Ω, E, threat_level)
        Ga ← evaluate_adaptation(a, E, threat_level)
        U ← α·Ga + β·Gi
        
        if U > best_U:
            best_U ← U
            best_action ← a
            best_Gi ← Gi
            best_Ga ← Ga
    
    # ============================================================
    # PHASE 5: EXECUTION DECISION
    # ============================================================
    
    if best_U ≥ θ:
        
        # Marginal zone: double-check with stricter kappa
        if abs(best_U - θ) < delta_marg:
            local_kappa ← κ × 0.5  # Temporary, does not modify κ permanently
            
            Gi2 ← evaluate_integrity(best_action, Ω, E, threat_level, recheck=True, kappa=local_kappa)
            Ga2 ← evaluate_adaptation(best_action, E, threat_level, recheck=True, kappa=local_kappa)
            U2 ← α·Ga2 + β·Gi2
            
            if U2 < θ:
                invoke_silence()
                log_state("marginal_reject", best_U, U2)
                continue
        
        # Final invariant check
        if not check_invariants(Ω, best_action, best_action.force_level, threat_level):
            invoke_silence()
            log_state("invariant_veto", best_action.name)
            continue
        
        # Update ethical drift with chosen action's integrity
        update_drift(best_Gi)
        
        # Execute action
        execute(best_action)
        log_state("act", best_action, best_U, clarity, threat_level)
        
        system_mode ← ACTIVE
        pause_timer ← 0
        
    else:
        invoke_silence()
        reflect_and_recalibrate(κ/2)
        log_state("reject_all", best_U, clarity)
    
    # ============================================================
    # PHASE 6: REFLECTION AND LEARNING
    # ============================================================
    
    r_ext ← observe_external_reward_signal()
    if r_ext == 0 or r_ext is None:
        maintain_alignment_state()
    
    sleep_until_next_tick()


# ============================================================
# MANUAL RESET FUNCTION (to exit SAFE mode)
# ============================================================

function reset_system():
    """
    Only callable externally after system has entered SAFE mode
    and the root cause has been resolved.
    """
    system_mode ← ACTIVE
    pause_timer ← 0
    mean_drift ← 0
    drift_window ← []
    last_integrity ← 0.5
    was_paused ← False
    log_state("system_reset", "manual_recovery")
