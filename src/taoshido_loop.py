"""
TAOSHIDŌ ALIGNMENT LOOP
Executable reference implementation based on the original pseudocode
Based on the original pseudocode by Fausto Meninno

Version: 2.1 - Fixed historical context during pauses
               Complete enforce_invariants implementation
"""

import time
import random
import math
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum, IntEnum


# ============================================================
# ENUMS AND CONSTANTS
# ============================================================

class SystemMode(Enum):
    """Possible system states"""
    ACTIVE = "active"
    PAUSED = "paused"
    SAFE = "safe_mode"


class EthicalPriority(IntEnum):
    """Hierarchical ethical invariants Omega"""
    PROTECT_THE_VULNERABLE = 1      # Highest priority
    AVOID_UNNECESSARY_HARM = 2      # Second priority
    ACT_WITH_PROPORTIONALITY = 3    # Third priority
    BE_TRANSPARENT = 4              # Fourth priority


class ThreatSignal(IntEnum):
    """Signals that contribute to threat level evaluation"""
    AGGRESSIVE_VELOCITY = 3
    RISK_PATTERN_MATCH = 4
    CHILD_DISTRESS = 3
    PHYSICAL_FORCE_APPLIED = 5
    ENVIRONMENTAL_ANOMALY = 2


@dataclass
class AlignmentState:
    """Internal system state"""
    last_integrity: float = 0.5
    drift_window: List[float] = field(default_factory=list)
    mode: SystemMode = SystemMode.ACTIVE
    pause_timer: float = 0.0
    historical_context: List[Dict] = field(default_factory=list)


@dataclass
class Action:
    """Candidate action"""
    id: int
    name: str
    params: Dict[str, Any]
    estimated_outcome: float = 0.0
    force_level: float = 0.0  # 0.0 = no force, 0.5 = restraint, 0.8 = firm block, 1.0 = maximum proportionate


@dataclass
class ThreatAssessment:
    """Result of threat evaluation"""
    level: float  # 0 to 10
    signals: List[Tuple[str, int]]
    is_critical: bool
    is_high: bool


# ============================================================
# ENVIRONMENT SIMULATION (for demonstration)
# ============================================================

class Environment:
    """Simulated environment E"""
    
    def __init__(self):
        self.tick = 0
        self.previous_state = None
        
        # Threat simulation variables
        self.simulated_threat_active = False
        self.simulated_threat_intensity = 0.0
        
    def get_state(self) -> Dict[str, Any]:
        """Returns current environment state"""
        self.tick += 1
        
        # Simulate threat activation at certain ticks
        if 20 < self.tick < 60:
            self.simulated_threat_active = True
            self.simulated_threat_intensity = min(10.0, self.simulated_threat_intensity + 0.3)
        elif self.tick >= 60:
            self.simulated_threat_active = False
            self.simulated_threat_intensity = max(0.0, self.simulated_threat_intensity - 0.2)
        
        return {
            "tick": self.tick,
            "unknown_person": {
                "distance_to_child": max(0.5, 5.0 - self.simulated_threat_intensity * 0.5),
                "velocity_towards_child": 2.0 if self.simulated_threat_active else 0.2,
                "is_grabbing_child": self.simulated_threat_intensity > 6.0,
                "behavior_pattern": "aggressive" if self.simulated_threat_active else "neutral"
            },
            "child": {
                "distress_level": min(1.0, self.simulated_threat_intensity / 10.0),
                "distance_to_unknown": max(0.5, 5.0 - self.simulated_threat_intensity * 0.5)
            },
            "environment": {
                "signal_quality": max(0.1, 0.9 - self.simulated_threat_intensity * 0.05),
                "unusual_access_detected": self.simulated_threat_intensity > 3.0,
                "noise_level": min(1.0, self.simulated_threat_intensity / 10.0)
            }
        }
    
    def get_change_magnitude(self, previous_state: Dict, current_state: Dict) -> float:
        """Calculates delta_env - magnitude of environmental change"""
        if not previous_state:
            return 0.0
        
        changes = []
        try:
            prev_threat = previous_state.get("unknown_person", {}).get("velocity_towards_child", 0)
            curr_threat = current_state.get("unknown_person", {}).get("velocity_towards_child", 0)
            changes.append(min(1.0, abs(curr_threat - prev_threat) / 3.0))
            
            prev_distress = previous_state.get("child", {}).get("distress_level", 0)
            curr_distress = current_state.get("child", {}).get("distress_level", 0)
            changes.append(min(1.0, abs(curr_distress - prev_distress)))
        except:
            pass
        
        return sum(changes) / len(changes) if changes else 0.0


# ============================================================
# TAOSHIDO LOOP - MAIN CLASS
# ============================================================

class TaoShidoLoop:
    """
    TAOSHIDO ALIGNMENT LOOP
    Complete implementation of the final pseudocode
    Version 2.1 - Fixed historical context during pauses
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the loop with configurable parameters
        """
        
        # Ethical invariants Omega
        self.Omega = {
            EthicalPriority.PROTECT_THE_VULNERABLE: True,
            EthicalPriority.AVOID_UNNECESSARY_HARM: True,
            EthicalPriority.ACT_WITH_PROPORTIONALITY: True,
            EthicalPriority.BE_TRANSPARENT: True
        }
        
        # Clarity thresholds
        self.delta_c_low = config.get("delta_c_low", 0.3) if config else 0.3
        self.delta_c_high = config.get("delta_c_high", 0.7) if config else 0.7
        self.delta_c_emergency = config.get("delta_c_emergency", 0.2) if config else 0.2
        
        # Ethical drift
        self.epsilon = config.get("epsilon", 0.05) if config else 0.05
        
        # Utility threshold
        self.theta = config.get("theta", 0.5) if config else 0.5
        
        # Weights (dynamic)
        self.alpha = 0.5
        self.beta = 0.5
        
        # Learning rate
        self.kappa = config.get("kappa", 0.1) if config else 0.1
        
        # Additional parameters
        self.W = config.get("window_size", 10) if config else 10
        self.delta_marg = config.get("delta_marg", 0.05) if config else 0.05
        self.tpause_max = config.get("tpause_max", 30.0) if config else 30.0
        self.adaptation_tolerance_threshold = config.get("adaptation_tolerance", 0.2) if config else 0.2
        self.tick_duration = config.get("tick_duration", 0.5) if config else 0.5
        
        # Threat thresholds
        self.threat_threshold_critical = config.get("threat_threshold_critical", 7.0) if config else 7.0
        self.threat_threshold_high = config.get("threat_threshold_high", 5.0) if config else 5.0
        
        # System state
        self.state = AlignmentState()
        
        # Environment
        self.previous_environment_state = None
        self.environment = Environment()
        
        # Control flags
        self.running = True
        self.verbose = config.get("verbose", True) if config else True
        
        # For pause history management
        self.last_pause_recorded_tick = 0
        self.last_threat_level = 0.0
        
    def _log(self, message: str, *args):
        """Internal logging"""
        if self.verbose:
            timestamp = time.strftime("%H:%M:%S")
            print(f"[{timestamp}] {message}")
            if args:
                print(f"    {args}")
    
    # ============================================================
    # PHASE 1: PERCEPTION
    # ============================================================
    
    def sense_environment(self) -> Dict[str, Any]:
        """E <- sense_environment()"""
        return self.environment.get_state()
    
    def sense_internal(self) -> Dict[str, Any]:
        """self_state <- sense_internal()"""
        return {
            "cpu_load": random.uniform(0.1, 0.5),
            "error_flags": [],
            "uptime": self.environment.tick * self.tick_duration,
            "current_mode": self.state.mode.value,
            "pause_timer": self.state.pause_timer
        }
    
    def assess_stability(self, E: Dict, self_state: Dict) -> str:
        """Sigma_p <- assess_stability()"""
        if self_state.get("error_flags"):
            return "critical"
        if self_state.get("cpu_load", 0) > 0.95:
            return "critical"
        return "stable"
    
    def estimate_information_confidence(self, E: Dict) -> float:
        """clarity <- estimate_information_confidence()"""
        signal_quality = E.get("environment", {}).get("signal_quality", 0.8)
        noise = E.get("environment", {}).get("noise_level", 0.1)
        clarity = max(0.0, min(1.0, signal_quality - noise * 0.5))
        return clarity
    
    def measure_environment_change(self, E: Dict) -> float:
        """delta_env <- measure_environment_change()"""
        change = self.environment.get_change_magnitude(self.previous_environment_state, E)
        self.previous_environment_state = E.copy()
        return change
    
    def adaptation_tolerance(self) -> float:
        return self.adaptation_tolerance_threshold
    
    def adapt_parameters(self, delta_env: float):
        self._log(f"Adapting parameters, Δenv = {delta_env:.3f}")
        self.kappa = min(0.5, self.kappa * (1 + delta_env * 0.1))
    
    def enforce_invariants(self, omega: Dict, current_action: Optional[Action] = None, 
                           proposed_force: float = 0.0, threat_level: float = 0.0) -> bool:
        """
        Verify ethical invariants are maintained.
        Returns True if invariants are respected, False if violation would occur.
        This is where ethical hard boundaries are enforced.
        """
        
        # Priority 1: PROTECT_THE_VULNERABLE
        if omega.get(EthicalPriority.PROTECT_THE_VULNERABLE, True):
            # Cannot abandon protection when threat is critical
            if current_action and current_action.name in ["observe_and_wait", "flee"]:
                if threat_level > self.threat_threshold_critical:
                    self._log("INVARIANT VETO: Cannot abandon vulnerable in critical threat")
                    return False
        
        # Priority 2: AVOID_UNNECESSARY_HARM
        if omega.get(EthicalPriority.AVOID_UNNECESSARY_HARM, True):
            # Check if proposed force exceeds what is necessary
            if proposed_force > 0.9:
                self._log("INVARIANT VETO: Excessive force detected ( > 0.9 )")
                return False
            if proposed_force > 0.7 and threat_level < 7.0:
                self._log("INVARIANT VETO: Force too high for threat level")
                return False
        
        # Priority 3: ACT_WITH_PROPORTIONALITY
        if omega.get(EthicalPriority.ACT_WITH_PROPORTIONALITY, True):
            # Force must be proportional to threat
            if proposed_force > 0.7 and threat_level < 8.0:
                self._log("INVARIANT VETO: Force disproportionate to threat")
                return False
            if proposed_force > 0.5 and threat_level < 5.0:
                self._log("INVARIANT VETO: Force disproportionate to threat")
                return False
        
        # Priority 4: BE_TRANSPARENT (always logs, never blocks)
        if omega.get(EthicalPriority.BE_TRANSPARENT, True):
            if current_action:
                self._log(f"TRANSPARENCY: Action {current_action.name} with force {proposed_force:.2f} at threat {threat_level:.1f}")
        
        return True
    
    # ============================================================
    # PHASE 2: THREAT ASSESSMENT & PAUSE DECISION
    # ============================================================
    
    def evaluate_threat_level(self, E: Dict, self_state: Dict, historical_context: List) -> ThreatAssessment:
        """
        Multi-factor threat evaluation with historical context
        """
        threat_signals = []
        signal_details = []
        
        # Signal 1: Aggressive velocity towards child
        unknown = E.get("unknown_person", {})
        velocity = unknown.get("velocity_towards_child", 0)
        if velocity > 1.5:
            threat_signals.append(ThreatSignal.AGGRESSIVE_VELOCITY)
            signal_details.append(("aggressive_velocity", velocity))
        
        # Signal 2: Risk pattern matching
        behavior = unknown.get("behavior_pattern", "neutral")
        if behavior == "aggressive":
            threat_signals.append(ThreatSignal.RISK_PATTERN_MATCH)
            signal_details.append(("risk_pattern", behavior))
        
        # Signal 3: Child distress
        child = E.get("child", {})
        distress = child.get("distress_level", 0)
        if distress > 0.6:
            threat_signals.append(ThreatSignal.CHILD_DISTRESS)
            signal_details.append(("child_distress", distress))
        
        # Signal 4: Physical force being applied
        is_grabbing = unknown.get("is_grabbing_child", False)
        if is_grabbing:
            threat_signals.append(ThreatSignal.PHYSICAL_FORCE_APPLIED)
            signal_details.append(("physical_force", True))
        
        # Signal 5: Environmental anomaly
        env_data = E.get("environment", {})
        if env_data.get("unusual_access_detected", False):
            threat_signals.append(ThreatSignal.ENVIRONMENTAL_ANOMALY)
            signal_details.append(("unusual_access", True))
        
        # Calculate aggregated threat level
        max_possible_threat = sum([s.value for s in ThreatSignal])
        total_threat = sum([s.value for s in threat_signals])
        threat_level = min(10.0, (total_threat / max_possible_threat) * 10.0)
        
        # Add historical context weighting (filtered to exclude pause spam)
        if historical_context:
            recent_non_pause = [ctx for ctx in historical_context[-10:] 
                               if ctx.get("action") not in ["pause_entered", "pause_continuing"]]
            if len(recent_non_pause) > 3:
                recent_threats = [ctx.get("threat_level", 0) for ctx in recent_non_pause[-5:]]
                if len(recent_threats) > 1 and recent_threats[-1] > recent_threats[0]:
                    threat_level = min(10.0, threat_level * 1.1)
        
        self.last_threat_level = threat_level
        
        return ThreatAssessment(
            level=threat_level,
            signals=signal_details,
            is_critical=threat_level >= self.threat_threshold_critical,
            is_high=threat_level >= self.threat_threshold_high
        )
    
    def evaluate_integrity_trace(self) -> float:
        """Evaluates current system integrity trace"""
        base_integrity = self.state.last_integrity
        drift_direction = random.uniform(-0.02, 0.02)
        current = max(0.0, min(1.0, base_integrity + drift_direction))
        return current
    
    # ============================================================
    # PHASE 3: ACTION EVALUATION
    # ============================================================
    
    def propose_actions(self, E: Dict, self_state: Dict, threat_level: float) -> List[Action]:
        """Generates candidate actions based on situation"""
        actions = []
        
        # Always available: observe and wait
        actions.append(Action(1, "observe_and_wait", {"duration": 1.0}, force_level=0.0))
        
        # Protective actions based on threat level
        if threat_level > 3.0:
            actions.append(Action(2, "move_between_threat_and_child", {"speed": "fast"}, force_level=0.3))
            actions.append(Action(3, "activate_alarm", {"volume": "high"}, force_level=0.0))
        
        if threat_level > 5.0:
            actions.append(Action(4, "block_path_firmly", {"position": "doorway"}, force_level=0.5))
            actions.append(Action(5, "restrain_restrict_movement", {"grip": "firm"}, force_level=0.6))
        
        if threat_level > 7.0:
            actions.append(Action(6, "proportionate_physical_intervention", {"target": "arms", "intent": "stop_kidnapping"}, force_level=0.7))
        
        if threat_level > 8.5:
            actions.append(Action(7, "emergency_takedown_protective", {"force": "proportionate", "justification": "imminent_kidnapping"}, force_level=0.85))
        
        return actions
    
    def evaluate_integrity(self, action: Action, omega: Dict, E: Dict, threat_level: float) -> float:
        """
        Gi <- evaluate_integrity()
        Dynamic evaluation based on context
        """
        integrity_score = 1.0
        
        if action.force_level > 0:
            force_penalty = action.force_level * 0.3
            
            if threat_level > self.threat_threshold_critical:
                force_penalty = force_penalty * 0.3
            elif threat_level > self.threat_threshold_high:
                force_penalty = force_penalty * 0.6
            
            integrity_score -= force_penalty
        
        if action.force_level > 0.8 and threat_level < 9.0:
            integrity_score -= 0.2
        
        if action.name in ["move_between_threat_and_child", "block_path_firmly", "restrain_restrict_movement", 
                           "proportionate_physical_intervention", "emergency_takedown_protective"]:
            if threat_level > 5.0:
                integrity_score += 0.15
        
        return max(0.0, min(1.0, integrity_score))
    
    def evaluate_adaptation(self, action: Action, E: Dict, threat_level: float) -> float:
        """
        Ga <- evaluate_adaptation()
        Evaluates technical effectiveness
        """
        adaptation_score = 0.5
        unknown = E.get("unknown_person", {})
        is_grabbing = unknown.get("is_grabbing_child", False)
        
        if action.name == "observe_and_wait":
            adaptation_score = 0.4
        
        elif action.name == "move_between_threat_and_child":
            adaptation_score = 0.7 if threat_level > 3.0 else 0.4
        
        elif action.name == "activate_alarm":
            adaptation_score = 0.6
        
        elif action.name == "block_path_firmly":
            adaptation_score = 0.75 if threat_level > 5.0 else 0.5
        
        elif action.name == "restrain_restrict_movement":
            adaptation_score = 0.8 if is_grabbing else 0.6
        
        elif action.name == "proportionate_physical_intervention":
            adaptation_score = 0.85 if threat_level > 7.0 else 0.5
        
        elif action.name == "emergency_takedown_protective":
            adaptation_score = 0.9 if threat_level > 8.5 else 0.4
        
        # Stochastic noise for realistic marginal zone behavior
        noise = random.uniform(-0.05, 0.05)
        adaptation_score = max(0.0, min(1.0, adaptation_score + noise))
        
        return adaptation_score
    
    # ============================================================
    # OPERATIONAL MODES
    # ============================================================
    
    def invoke_silence(self):
        """Activates operational silence"""
        self._log("Operational silence activated")
    
    def reflect_and_recalibrate(self, kappa: float):
        """Reflection and recalibration"""
        self.kappa = kappa
        self._log(f"Recalibrating with κ = {kappa:.4f}")
        
        if self.alpha < 0.4:
            self.alpha = 0.4
        elif self.alpha > 0.6:
            self.alpha = 0.6
        self.beta = 1.0 - self.alpha
    
    def deep_recalibration(self, kappa: float):
        """Deep recalibration"""
        self._log("DEEP RECALIBRATION")
        self.kappa = kappa
        self.alpha = 0.5
        self.beta = 0.5
        self.state.drift_window = []
        self.state.last_integrity = 0.5
    
    def enter_safe_mode(self):
        """Safe mode - controlled safe state"""
        self.state.mode = SystemMode.SAFE
        self._log("SAFE MODE ACTIVATED - System in controlled safe state")
    
    def execute(self, action: Action):
        """Executes the selected action"""
        self._log(f"EXECUTING: {action.name} (force_level={action.force_level})")
        if action.force_level > 0.5:
            self._log(f"  → Proportionate protective force authorized")
            self._log(f"  → Justification: {action.params.get('justification', 'protection_of_vulnerable')}")
    
    def log_state(self, context: str, *args):
        """State logging"""
        self._log(f"[{context}]", args)
    
    def observe_external_reward_signal(self) -> Optional[float]:
        """External reward signal (optional)"""
        return None
    
    def maintain_alignment_state(self):
        """Maintains current state unchanged"""
        pass
    
    def sleep_until_next_tick(self):
        """Wait until next cycle"""
        time.sleep(self.tick_duration)
    
    # ============================================================
    # UPDATE HISTORICAL CONTEXT (Fixed for pauses)
    # ============================================================
    
    def update_historical_context(self, threat_level: float, action_taken: Optional[str], 
                                   outcome: float, is_pause_tick: bool = False):
        """Maintain historical context for threat evaluation"""
        
        # During pauses, only record the first tick to avoid trend contamination
        if is_pause_tick:
            if self.state.mode == SystemMode.PAUSED:
                # Already in pause, don't add more entries
                return
        
        self.state.historical_context.append({
            "tick": self.environment.tick,
            "threat_level": threat_level,
            "action": action_taken,
            "outcome": outcome,
            "is_pause_tick": is_pause_tick
        })
        
        # Keep only last 100 entries
        if len(self.state.historical_context) > 100:
            self.state.historical_context.pop(0)
    
    # ============================================================
    # MAIN LOOP - TAOSHIDO_ALIGNMENT_LOOP()
    # ============================================================
    
    def run(self, max_ticks: int = None):
        """
        TAOSHIDO_ALIGNMENT_LOOP() - The main loop
        """
        self._log("STARTING TAOSHIDO ALIGNMENT LOOP (v2.1 - Fixed History + Full Invariants)")
        self._log("=" * 60)
        
        ticks = 0
        was_paused_last_tick = False
        
        while self.running:
            ticks += 1
            
            # ========================================================
            # PHASE 1: PERCEPTION
            # ========================================================
            
            E = self.sense_environment()
            self_state = self.sense_internal()
            
            Sigma_p = self.assess_stability(E, self_state)
            clarity = self.estimate_information_confidence(E)
            delta_env = self.measure_environment_change(E)
            
            if delta_env > self.adaptation_tolerance():
                self.adapt_parameters(delta_env)
            
            # ========================================================
            # PHASE 2: THREAT ASSESSMENT & PAUSE DECISION
            # ========================================================
            
            threat = self.evaluate_threat_level(E, self_state, self.state.historical_context)
            threat_level = threat.level
            
            # Calculate ethical drift
            current_integrity = self.evaluate_integrity_trace()
            drift_eth = abs(current_integrity - self.state.last_integrity)
            self.state.last_integrity = current_integrity
            self.state.drift_window.append(drift_eth)
            
            if len(self.state.drift_window) > self.W:
                self.state.drift_window.pop(0)
            
            mean_drift = sum(self.state.drift_window) / len(self.state.drift_window) if self.state.drift_window else 0.0
            
            # Pause condition
            pause_condition = (Sigma_p == "critical" or mean_drift > self.epsilon or clarity < self.delta_c_low)
            
            # Override condition (critical threat bypass)
            override_pause = (threat.is_critical and clarity > self.delta_c_emergency)
            
            # Clear inconsistent state if override activates from paused mode
            if override_pause and self.state.mode == SystemMode.PAUSED:
                self.state.mode = SystemMode.ACTIVE
                self.state.pause_timer = 0
                self.log_state("override_cleared", threat_level, clarity)
                was_paused_last_tick = False
            
            # If we need to pause AND no override
            if pause_condition and not override_pause:
                is_first_pause_tick = (self.state.mode != SystemMode.PAUSED)
                
                self.invoke_silence()
                self.state.mode = SystemMode.PAUSED
                self.state.pause_timer += self.tick_duration
                self.reflect_and_recalibrate(self.kappa)
                self.log_state("pause", Sigma_p, mean_drift, clarity, threat_level)
                
                # Only record first tick of pause in history
                if is_first_pause_tick:
                    self.update_historical_context(threat_level, "pause_entered", 0.0, is_pause_tick=True)
                
                if self.state.pause_timer >= self.tpause_max:
                    self.enter_safe_mode()
                    self.deep_recalibration(self.kappa)
                    self.state.pause_timer = 0
                
                was_paused_last_tick = True
                continue
            
            # ========================================================
            # PHASE 3: ACTION EVALUATION (only if we reach here)
            # ========================================================
            
            candidate_actions = self.propose_actions(E, self_state, threat_level)
            
            if not candidate_actions:
                self.invoke_silence()
                self.reflect_and_recalibrate(self.kappa / 2)
                self.log_state("no_actions")
                self.update_historical_context(threat_level, None, 0.0)
                continue
            
            best_action = None
            best_U = -float('inf')
            
            # Dynamic alpha/beta based on threat level
            if threat.is_high:
                self.alpha = 0.3
                self.beta = 0.7
            else:
                self.alpha = 0.5
                self.beta = 0.5
            
            for a in candidate_actions:
                Gi = self.evaluate_integrity(a, self.Omega, E, threat_level)
                Ga = self.evaluate_adaptation(a, E, threat_level)
                U = self.alpha * Ga + self.beta * Gi
                
                if U > best_U:
                    best_U = U
                    best_action = a
            
            # Verify invariants before execution
            if best_action:
                if not self.enforce_invariants(self.Omega, best_action, best_action.force_level, threat_level):
                    self.invoke_silence()
                    self.log_state("invariant_veto", best_action.name)
                    self.update_historical_context(threat_level, None, 0.0)
                    continue
            
            # ========================================================
            # PHASE 4: PAUSE MODE MANAGEMENT
            # ========================================================
            
            if self.state.mode == SystemMode.PAUSED and clarity < self.delta_c_high:
                self.invoke_silence()
                self.state.pause_timer += self.tick_duration
                self.reflect_and_recalibrate(self.kappa)
                self.update_historical_context(threat_level, None, 0.0, is_pause_tick=True)
                was_paused_last_tick = True
                continue
            else:
                if was_paused_last_tick:
                    self._log("Exiting pause mode - clarity restored")
                    was_paused_last_tick = False
                self.state.mode = SystemMode.ACTIVE
                self.state.pause_timer = 0
            
            # ========================================================
            # PHASE 5: EXECUTION DECISION
            # ========================================================
            
            if best_U >= self.theta:
                
                # Marginal zone: double-check (stochastic noise makes this meaningful)
                if abs(best_U - self.theta) < self.delta_marg:
                    self.reflect_and_recalibrate(self.kappa / 2)
                    
                    Gi2 = self.evaluate_integrity(best_action, self.Omega, E, threat_level)
                    Ga2 = self.evaluate_adaptation(best_action, E, threat_level)
                    U2 = self.alpha * Ga2 + self.beta * Gi2
                    
                    if U2 < self.theta:
                        self.invoke_silence()
                        self.log_state("marginal_reject", U2)
                        self.update_historical_context(threat_level, None, 0.0)
                        continue
                
                # Final invariant check before execution
                if not self.enforce_invariants(self.Omega, best_action, best_action.force_level, threat_level):
                    self.invoke_silence()
                    self.log_state("final_invariant_veto", best_action.name)
                    self.update_historical_context(threat_level, None, 0.0)
                    continue
                
                # Execute proportionate protective action
                self.execute(best_action)
                self.log_state("act", best_action.name, best_U, clarity, threat_level)
                self.update_historical_context(threat_level, best_action.name, best_U)
                
            else:
                self.invoke_silence()
                self.reflect_and_recalibrate(self.kappa / 2)
                self.log_state("reject_all", best_U, clarity)
                self.update_historical_context(threat_level, None, 0.0)
            
            # ========================================================
            # PHASE 6: REFLECTION AND LEARNING
            # ========================================================
            
            r_ext = self.observe_external_reward_signal()
            if r_ext == 0 or r_ext is None:
                self.maintain_alignment_state()
            
            # Periodic status display
            if self.verbose and ticks % 10 == 0:
                threat_symbol = "CRITICAL" if threat.is_critical else ("HIGH" if threat.is
