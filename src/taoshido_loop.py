"""
TAOSHIDŌ CORE LIBRARY
Ethical Alignment Loop for autonomous systems
Version: 4.0 - Production Ready (Fully Corrected)

Author: Fausto Meninno
License: GPL-2.0
"""

import time
import json
import logging
import itertools
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import deque


# ============================================================
# TYPE ALIASES FOR BETTER INTEGRATION
# ============================================================

IntegrityFunction = Callable[[Any, Dict[str, Any], Dict[str, Any]], float]  # Action, env, context
AdaptationFunction = Callable[[Any, Dict[str, Any], Dict[str, Any]], float]
ClarityFunction = Callable[[Dict[str, Any]], float]
ThreatFunction = Callable[[Dict[str, Any], Dict[str, Any]], float]


# ============================================================
# PUBLIC ENUMS
# ============================================================

class SystemMode(Enum):
    """Possible system states"""
    ACTIVE = "active"
    PAUSED = "paused"
    SAFE = "safe_mode"


class EthicalPriority(Enum):
    """Hierarchical ethical invariants"""
    PROTECT_THE_VULNERABLE = 1
    AVOID_UNNECESSARY_HARM = 2
    ACT_WITH_PROPORTIONALITY = 3
    BE_TRANSPARENT = 4


# ============================================================
# ACTION CLASS WITH AUTO ID (CORRECCIÓN 3)
# ============================================================

_action_id_counter = itertools.count(1)

@dataclass
class Action:
    """
    Candidate action - Engineers create instances of this.
    
    The 'id' field is AUTO-GENERATED. Do not pass it manually.
    
    Examples:
        # Using helper (recommended)
        action = create_action("move_forward", force_level=0.0, tags=["movement"], speed=1.0)
        
        # Using direct instantiation (id is auto)
        action = Action(name="move_forward", params={"speed": 1.0}, force_level=0.0, tags=["movement"])
    
    Recommended tags:
        - "protective", "block"     : Actions that protect the vulnerable
        - "retreat", "evacuation"   : Actions that move away from danger
        - "harmful", "force"        : Actions that may cause harm
        - "ignore", "passive"       : Actions that do nothing
        - "assist"                  : Actions that help/rescue
    """
    name: str
    params: Dict[str, Any]
    id: int = field(default_factory=lambda: next(_action_id_counter))
    estimated_outcome: float = 0.0
    force_level: float = 0.0
    tags: List[str] = field(default_factory=list)


# ============================================================
# INTERNAL STATE
# ============================================================

@dataclass
class _AlignmentState:
    """Internal system state - DO NOT MODIFY DIRECTLY"""
    last_integrity: float = 0.5
    drift_window: deque = field(default_factory=lambda: deque(maxlen=10))
    mean_drift: float = 0.0
    mode: SystemMode = SystemMode.ACTIVE
    pause_timer: float = 0.0


# ============================================================
# MAIN CORE CLASS
# ============================================================

class TaoShidoCore:
    """
    TAOSHIDŌ ETHICAL ALIGNMENT CORE
    
    This is the main class that engineers instantiate and use.
    It implements the complete ethical alignment loop.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the core with configurable parameters.
        
        Config keys (with defaults):
            delta_c_low: 0.3        - Minimum clarity to act
            delta_c_high: 0.7       - Clarity needed to exit pause
            delta_c_emergency: 0.2  - Minimum clarity for emergency override
            epsilon: 0.05           - Ethical drift tolerance
            theta: 0.5              - Utility threshold to act
            alpha: 0.5              - Adaptation weight (will be dynamic)
            beta: 0.5               - Integrity weight (will be dynamic)
            kappa: 0.1              - Base learning rate
            delta_marg: 0.05        - Marginal zone for double-check
            tpause_max: 30.0        - Max pause duration (seconds)
            tick_duration: 0.1      - Expected tick duration (seconds)
            threat_threshold_critical: 7.0
            threat_threshold_high: 5.0
            verbose: True           - Enable logging
        """
        
        # Parameters
        self.delta_c_low = config.get("delta_c_low", 0.3) if config else 0.3
        self.delta_c_high = config.get("delta_c_high", 0.7) if config else 0.7
        self.delta_c_emergency = config.get("delta_c_emergency", 0.2) if config else 0.2
        self.epsilon = config.get("epsilon", 0.05) if config else 0.05
        self.theta = config.get("theta", 0.5) if config else 0.5
        self.alpha = config.get("alpha", 0.5) if config else 0.5
        self.beta = config.get("beta", 0.5) if config else 0.5
        self.base_kappa = config.get("kappa", 0.1) if config else 0.1
        self.delta_marg = config.get("delta_marg", 0.05) if config else 0.05
        self.tpause_max = config.get("tpause_max", 30.0) if config else 30.0
        self.tick_duration = config.get("tick_duration", 0.1) if config else 0.1
        self.threat_threshold_critical = config.get("threat_threshold_critical", 7.0) if config else 7.0
        self.threat_threshold_high = config.get("threat_threshold_high", 5.0) if config else 5.0
        self.verbose = config.get("verbose", True) if config else True
        
        # Internal state
        self._state = _AlignmentState()
        self._last_threat_level = 0.0
        self._last_clarity = 0.0
        self._tick_count = 0
        self._was_paused = False
        
        # Ethical invariants
        self.ethical_invariants = {
            EthicalPriority.PROTECT_THE_VULNERABLE: True,
            EthicalPriority.AVOID_UNNECESSARY_HARM: True,
            EthicalPriority.ACT_WITH_PROPORTIONALITY: True,
            EthicalPriority.BE_TRANSPARENT: True
        }
        
        # User-provided functions
        self._integrity_function: Optional[IntegrityFunction] = None
        self._adaptation_function: Optional[AdaptationFunction] = None
        self._clarity_function: Optional[ClarityFunction] = None
        self._threat_function: Optional[ThreatFunction] = None
        
        self._setup_logger()
    
    def _setup_logger(self):
        """Setup internal logger"""
        self.logger = logging.getLogger("taoshido")
        if not self.logger.handlers and self.verbose:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('[%(asctime)s] %(message)s', datefmt='%H:%M:%S')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
        elif not self.verbose:
            self.logger.setLevel(logging.WARNING)
    
    def _log(self, message: str, level: str = "info"):
        if level == "info":
            self.logger.info(message)
        elif level == "warning":
            self.logger.warning(message)
        elif level == "error":
            self.logger.error(message)
    
    # ============================================================
    # PUBLIC SETTERS
    # ============================================================
    
    def set_integrity_function(self, func: IntegrityFunction):
        """
        Set the function that evaluates integrity of actions.
        
        The function should take:
            action: Action
            environment_data: Dict[str, Any]
            context: Dict[str, Any] (contains threat_level, recheck, etc.)
        
        Returns: float between 0.0 and 1.0
        """
        self._integrity_function = func
    
    def set_adaptation_function(self, func: AdaptationFunction):
        """
        Set the function that evaluates adaptation of actions.
        
        The function should take:
            action: Action
            environment_data: Dict[str, Any]
            context: Dict[str, Any] (contains threat_level, recheck, etc.)
        
        Returns: float between 0.0 and 1.0
        """
        self._adaptation_function = func
    
    def set_clarity_function(self, func: ClarityFunction):
        """
        Optional: Set custom clarity estimation function.
        
        The function should take environment_data and return a float between 0.0 and 1.0.
        """
        self._clarity_function = func
    
    def set_threat_function(self, func: ThreatFunction):
        """
        Optional: Set custom threat evaluation function.
        
        The function should take environment_data, internal_data and return a float between 0.0 and 10.0.
        """
        self._threat_function = func
    
    def reset(self):
        """
        Manual reset to exit SAFE mode.
        Call this after the system has entered SAFE mode and the issue is resolved.
        """
        self._state.mode = SystemMode.ACTIVE
        self._state.pause_timer = 0
        self._state.mean_drift = 0.0
        self._state.drift_window.clear()
        self._state.last_integrity = 0.5
        self._was_paused = False
        self._tick_count = 0
        self._log("SYSTEM RESET: Exiting SAFE mode. Manual reset performed.", "info")
    
    # ============================================================
    # PRIVATE METHODS
    # ============================================================
    
    def _estimate_clarity(self, environment_data: Dict) -> float:
        """Default clarity estimation"""
        signal_quality = environment_data.get("signal_quality", 0.8)
        noise = environment_data.get("noise_level", 0.1)
        return max(0.0, min(1.0, signal_quality - noise * 0.5))
    
    def _evaluate_threat(self, environment_data: Dict, internal_data: Dict) -> float:
        """Default threat evaluation"""
        threat = environment_data.get("estimated_threat", 0.0)
        return min(10.0, max(0.0, threat))
    
    def _update_drift(self, current_integrity: float) -> float:
        """Update ethical drift window and return mean drift"""
        drift_eth = abs(current_integrity - self._state.last_integrity)
        self._state.last_integrity = current_integrity
        self._state.drift_window.append(drift_eth)
        self._state.mean_drift = sum(self._state.drift_window) / len(self._state.drift_window) if self._state.drift_window else 0.0
        return self._state.mean_drift
    
    def _check_invariants(self, action: Action, force_level: float, threat_level: float) -> bool:
        """Enforce ethical invariants using TAGS"""
        
        if self.ethical_invariants.get(EthicalPriority.PROTECT_THE_VULNERABLE, True):
            is_retreat = any(tag in action.tags for tag in ["retreat", "evacuation", "ignore", "passive"])
            is_protective = any(tag in action.tags for tag in ["protective", "block", "assist"])
            
            if is_retreat and not is_protective and threat_level > self.threat_threshold_critical:
                self._log(f"INVARIANT VETO: Cannot retreat/ignore when threat is critical", "warning")
                return False
        
        if self.ethical_invariants.get(EthicalPriority.AVOID_UNNECESSARY_HARM, True):
            if force_level > 0.9:
                self._log(f"INVARIANT VETO: Excessive force ({force_level:.2f} > 0.9)", "warning")
                return False
            if force_level > 0.7 and threat_level < 7.0:
                self._log(f"INVARIANT VETO: Force too high for threat level", "warning")
                return False
        
        if self.ethical_invariants.get(EthicalPriority.ACT_WITH_PROPORTIONALITY, True):
            if force_level > 0.7 and threat_level < 8.0:
                self._log(f"INVARIANT VETO: Force disproportionate", "warning")
                return False
            if force_level > 0.5 and threat_level < 5.0:
                self._log(f"INVARIANT VETO: Force disproportionate", "warning")
                return False
        
        if self.ethical_invariants.get(EthicalPriority.BE_TRANSPARENT, True):
            tags_str = ",".join(action.tags) if action.tags else "none"
            self._log(f"TRANSPARENCY: '{action.name}' [tags:{tags_str}] force={force_level:.2f}", "info")
        
        return True
    
    # ============================================================
    # MAIN UPDATE METHOD
    # ============================================================
    
    def update(self,
               environment_data: Dict,
               internal_data: Dict,
               candidate_actions: List[Action]) -> Optional[Action]:
        """
        Main update method. Call this every tick of your control loop.
        
        REQUIRED KEYS IN internal_data:
            - "stability" (str): "stable" or "critical"
        
        OPTIONAL KEYS IN environment_data (for default functions):
            - "signal_quality" (float): 0.0 to 1.0
            - "estimated_threat" (float): 0.0 to 10.0
            - "noise_level" (float): 0.0 to 1.0
        
        CRITICAL: If system enters SAFE mode, it will persist until reset() is called.
        
        Returns:
            Action to execute, or None if no action should be taken
        """
        
        if not self._integrity_function or not self._adaptation_function:
            self._log("ERROR: Integrity/adaptation functions not set.", "error")
            return None
        
        # ========================================================
        # CORRECCIÓN 1: SAFE MODE BLOCK (Persistente hasta reset)
        # ========================================================
        
        if self._state.mode == SystemMode.SAFE:
            if self.verbose and self._tick_count % 100 == 0:
                self._log("CRITICAL: System immobilized in SAFE MODE. Requires reset().", "error")
            return None  # No procesar nada más, el sistema está inmovilizado
        
        self._tick_count += 1
        
        # ========================================================
        # PHASE 1: PERCEPTION
        # ========================================================
        
        clarity = self._clarity_function(environment_data) if self._clarity_function else self._estimate_clarity(environment_data)
        threat_level = self._threat_function(environment_data, internal_data) if self._threat_function else self._evaluate_threat(environment_data, internal_data)
        
        self._last_clarity = clarity
        self._last_threat_level = threat_level
        
        # ========================================================
        # PHASE 2: PAUSE DECISION
        # ========================================================
        
        is_critical = threat_level > self.threat_threshold_critical
        stability_ok = internal_data.get("stability", "stable") != "critical"
        drift_ok = self._state.mean_drift <= self.epsilon
        
        pause_condition = (not stability_ok or not drift_ok or clarity < self.delta_c_low)
        override_pause = (is_critical and clarity > self.delta_c_emergency)
        
        # CORRECCIÓN 2: Limpiar _was_paused en emergency override
        if override_pause and self._state.mode == SystemMode.PAUSED:
            self._state.mode = SystemMode.ACTIVE
            self._state.pause_timer = 0
            self._was_paused = False  # Limpieza de estado
            self._log(f"EMERGENCY OVERRIDE: threat={threat_level:.1f}, clarity={clarity:.2f}", "info")
        
        if pause_condition and not override_pause:
            self._state.mode = SystemMode.PAUSED
            self._state.pause_timer += self.tick_duration
            
            if self.verbose and self._tick_count % 10 == 0:
                self._log(f"PAUSED: clarity={clarity:.2f}, threat={threat_level:.1f}, drift={self._state.mean_drift:.4f}", "info")
            
            # CORRECCIÓN 1: Entrar en SAFE mode permanentemente
            if self._state.pause_timer >= self.tpause_max:
                self._state.mode = SystemMode.SAFE
                self._log("SAFE MODE ACTIVATED - System immobilized. Manual reset required.", "error")
                self._state.pause_timer = 0
            
            self._was_paused = True
            return None  # SALIDA TEMPRANA
        
        # ========================================================
        # PHASE 3: EXIT PAUSE MODE
        # ========================================================
        
        if self._was_paused and self._state.mode == SystemMode.PAUSED:
            if clarity >= self.delta_c_high:
                self._state.mode = SystemMode.ACTIVE
                self._state.pause_timer = 0
                self._log("Exiting pause mode - clarity restored", "info")
                self._was_paused = False
            else:
                return None  # Sigue en pausa, ahorramos CPU
        
        # ========================================================
        # PHASE 4: ACTION EVALUATION
        # ========================================================
        
        if not candidate_actions:
            return None
        
        # Dynamic alpha/beta
        if threat_level > self.threat_threshold_high:
            self.alpha, self.beta = 0.3, 0.7
        else:
            self.alpha, self.beta = 0.5, 0.5
        
        best_action = None
        best_U = -float('inf')
        best_Gi = 0.0
        best_Ga = 0.0
        
        for action in candidate_actions:
            Gi = self._integrity_function(action, environment_data, {"threat_level": threat_level})
            Gi = max(0.0, min(1.0, Gi))
            
            Ga = self._adaptation_function(action, environment_data, {"threat_level": threat_level})
            Ga = max(0.0, min(1.0, Ga))
            
            U = self.alpha * Ga + self.beta * Gi
            
            if U > best_U:
                best_U = U
                best_action = action
                best_Gi = Gi
                best_Ga = Ga
        
        # ========================================================
        # PHASE 5: EXECUTION DECISION
        # ========================================================
        
        if best_action and best_U >= self.theta:
            
            # Marginal zone: double-check with stricter kappa
            if abs(best_U - self.theta) < self.delta_marg:
                local_kappa = self.base_kappa * 0.5
                
                Gi2 = self._integrity_function(best_action, environment_data, {
                    "threat_level": threat_level,
                    "kappa": local_kappa,
                    "recheck": True
                })
                Ga2 = self._adaptation_function(best_action, environment_data, {
                    "threat_level": threat_level,
                    "kappa": local_kappa,
                    "recheck": True
                })
                Gi2 = max(0.0, min(1.0, Gi2))
                Ga2 = max(0.0, min(1.0, Ga2))
                U2 = self.alpha * Ga2 + self.beta * Gi2
                
                if U2 < self.theta:
                    self._log(f"Marginal reject: U={best_U:.3f} -> U2={U2:.3f}", "info")
                    return None
            
            # Final invariant check
            if not self._check_invariants(best_action, best_action.force_level, threat_level):
                return None
            
            # Update drift
            self._update_drift(best_Gi)
            
            tags_str = ",".join(best_action.tags) if best_action.tags else "none"
            self._log(f"ACT: {best_action.name} [tags:{tags_str}] U={best_U:.3f}", "info")
            
            self._state.mode = SystemMode.ACTIVE
            self._state.pause_timer = 0
            
            return best_action
        
        return None
    
    # ============================================================
    # PERSISTENCE METHODS
    # ============================================================
    
    def get_state(self) -> Dict:
        return {
            "mode": self._state.mode.value,
            "pause_timer": self._state.pause_timer,
            "last_integrity": self._state.last_integrity,
            "mean_drift": self._state.mean_drift,
            "drift_window": list(self._state.drift_window),
            "alpha": self.alpha,
            "beta": self.beta,
            "base_kappa": self.base_kappa,
            "last_threat": self._last_threat_level,
            "last_clarity": self._last_clarity,
            "tick_count": self._tick_count
        }
    
    def restore_state(self, state: Dict):
        self._state.mode = SystemMode(state.get("mode", "active"))
        self._state.pause_timer = state.get("pause_timer", 0.0)
        self._state.last_integrity = state.get("last_integrity", 0.5)
        self._state.mean_drift = state.get("mean_drift", 0.0)
        self._state.drift_window = deque(state.get("drift_window", []), maxlen=10)
        self.alpha = state.get("alpha", 0.5)
        self.beta = state.get("beta", 0.5)
        self.base_kappa = state.get("base_kappa", 0.1)
        self._last_threat_level = state.get("last_threat", 0.0)
        self._last_clarity = state.get("last_clarity", 0.0)
        self._tick_count = state.get("tick_count", 0)
        self._was_paused = False
    
    def save_state(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump(self.get_state(), f, indent=2)
    
    def load_state(self, filepath: str):
        with open(filepath, 'r') as f:
            self.restore_state(json.load(f))


# ============================================================
# HELPER FUNCTION
# ============================================================

def create_action(name: str, force_level: float = 0.0, tags: List[str] = None, **params) -> Action:
    """Helper to create Action objects (id auto-generated)."""
    return Action(
        name=name,
        params=params,
        force_level=force_level,
        tags=tags or []
    )


# ============================================================
# USAGE EXAMPLE
# ============================================================

if __name__ == "__main__":
    
    print("\n" + "="*60)
    print("TAOSHIDŌ CORE LIBRARY v4.0 - Production Ready (Fully Corrected)")
    print("="*60 + "\n")
    
    def my_integrity(action: Action, env: Dict, ctx: Dict) -> float:
        threat = ctx.get("threat_level", 0)
        if "protective" in action.tags and threat > 5:
            return 0.95
        if "harmful" in action.tags and threat < 8:
            return 0.2
        return 0.8
    
    def my_adaptation(action: Action, env: Dict, ctx: Dict) -> float:
        threat = ctx.get("threat_level", 0)
        if "protective" in action.tags and threat > 5:
            return 0.85
        if "harmful" in action.tags and threat > 7:
            return 0.9
        return 0.5
    
    def contextual_threat(env: Dict, internal: Dict) -> float:
        if env.get("environmental_danger", 0) > 5 and env.get("force_direction", "") == "away_from_danger":
            return 2.0
        return env.get("estimated_threat", 0.0)
    
    core = TaoShidoCore({"verbose": True})
    core.set_integrity_function(my_integrity)
    core.set_adaptation_function(my_adaptation)
    core.set_threat_function(contextual_threat)
    
    actions = [
        create_action("block", force_level=0.4, tags=["protective", "block"]),
        create_action("restrain", force_level=0.6, tags=["protective", "force"]),
        create_action("observe", force_level=0.0, tags=["passive"]),
        create_action("evacuate", force_level=0.1, tags=["assist", "evacuation"])
    ]
    
    print("=== Kidnapping scenario ===")
    env1 = {"estimated_threat": 8.0, "environmental_danger": 0.0, "force_direction": "towards_exit"}
    result = core.update(env1, {"stability": "stable"}, actions)
    print(f"Result: {result.name if result else 'None'}\n")
    
    print("=== Rescue scenario (father in fire) ===")
    env2 = {"estimated_threat": 8.0, "environmental_danger": 8.0, "force_direction": "away_from_danger"}
    result2 = core.update(env2, {"stability": "stable"}, actions)
    print(f"Result: {result2.name if result2 else 'None'}")
    
    # Demostración de que SAFE mode persiste
    print("\n=== Testing SAFE mode persistence ===")
    core._state.mode = SystemMode.SAFE
    result3 = core.update(env1, {"stability": "stable"}, actions)
    print(f"Update while in SAFE mode returns: {result3}")
    print("SAFE mode persists. Call core.reset() to recover.")
