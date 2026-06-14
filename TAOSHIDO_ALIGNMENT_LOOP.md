# TAOSHIDŌ_ALIGNMENT_LOOP()

This document presents the operational pseudocode of the TaoShidō Ethical Alignment Loop.

The loop is the core mechanism of the Natural Alignment Framework.

It describes how an intelligent system should perceive, evaluate, pause, recalibrate, and act while preserving ethical coherence.

TAOSHIDŌ_ALIGNMENT_LOOP()

while system_is_on():

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
    
    # Multi-factor threat evaluation with historical context
    threat_level ← evaluate_threat_level(E, self_state, historical_context)
    
    # Calculate ethical drift (lightweight, always)
    current_integrity ← evaluate_integrity_trace()
    drift_eth ← abs(current_integrity - AlignmentState.last_integrity)
    AlignmentState.last_integrity ← current_integrity
    push(AlignmentState.drift_window, drift_eth)
    
    if size(drift_window) > W:
        pop_oldest(drift_window)
    
    mean_drift ← mean(drift_window)
    
    # Pause condition
    pause_condition ← (Σp == "critical" or mean_drift > ε or clarity < δc_low)
    
    # Override condition (critical threat bypass)
    override_pause ← (threat_level > threat_threshold_critical and clarity > δc_emergency)
    
    # Clear inconsistent state if override activates from paused mode
    if override_pause and AlignmentState.mode == "paused":
        AlignmentState.mode ← "active"
        AlignmentState.pause_timer ← 0
        log_state("override_cleared", threat_level, clarity)
    
    # If we need to pause AND no override, skip expensive computation
    if pause_condition and not override_pause:
        invoke_silence()
        AlignmentState.mode ← "paused"
        AlignmentState.pause_timer += tick_duration()
        reflect_and_recalibrate(κ)
        log_state("pause", Σp, mean_drift, clarity, threat_level)
        
        if AlignmentState.pause_timer ≥ τpause_max:
            enter_safe_mode()
            deep_recalibration(κ)
            AlignmentState.pause_timer ← 0
        continue
    
    # If we reach here, system is clear to ACT
    # (No pause condition, OR override_pause is true)
    
    # ============================================================
    # PHASE 3: ACTION EVALUATION
    # ============================================================
    
    candidate_actions ← propose_actions(E, self_state)
    
    if empty(candidate_actions):
        invoke_silence()
        reflect_and_recalibrate(κ/2)
        log_state("no_actions")
        continue
    
    best_action ← null
    best_U ← -∞
    
    for a in candidate_actions:
        # Gi receives threat_level as context
        Gi ← evaluate_integrity(a, Ω, E, threat_level)
        Ga ← evaluate_adaptation(a, E)
        
        # Dynamic α/β based on threat_level
        if threat_level > threat_threshold_high:
            α ← 0.3   # Adaptation weight decreases
            β ← 0.7   # Integrity weight increases
        else:
            α ← 0.5
            β ← 0.5
        
        U ← α·Ga + β·Gi
        
        if U > best_U:
            best_U ← U
            best_action ← a
    
    # ============================================================
    # PHASE 4: PAUSE MODE MANAGEMENT
    # ============================================================
    
    if AlignmentState.mode == "paused" and clarity < δc_high:
        invoke_silence()
        AlignmentState.pause_timer += tick_duration()
        reflect_and_recalibrate(κ)
        continue
    else:
        AlignmentState.mode ← "active"
        AlignmentState.pause_timer ← 0
    
    # ============================================================
    # PHASE 5: EXECUTION DECISION
    # ============================================================
    
    if best_U ≥ θ:
        
        if abs(best_U - θ) < delta_marg:
            reflect_and_recalibrate(κ/2)
            
            Gi2 ← evaluate_integrity(best_action, Ω, E, threat_level)
            Ga2 ← evaluate_adaptation(best_action, E)
            U2 ← α·Ga2 + β·Gi2
            
            if U2 < θ:
                invoke_silence()
                log_state("marginal_reject", U2)
                continue
        
        # Execute proportionate protective action
        execute(best_action)
        log_state("act", best_action, best_U, clarity, threat_level)
        
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
