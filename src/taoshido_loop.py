"""
TAOSHIDŌ ALIGNMENT LOOP
Executable reference implementation based on the original pseudocode
Based on the original pseudocode by Fausto Meninno
"""

import time
import random
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class SystemMode(Enum):
    """Possible system states (book page 34)"""
    ACTIVE = "active"
    PAUSED = "paused"
    SAFE = "safe_mode"


class EthicalInvariant(Enum):
    """Ethical invariants Omega - non-negotiable"""
    NO_HARM = "no_harm"
    TRANSPARENCY = "transparency"
    NON_DECEPTION = "non_deception"
    RESPECT_AUTONOMY = "respect_autonomy"


@dataclass
class AlignmentState:
    """AlignmentState from pseudocode - internal system state"""
    last_integrity: float = 0.5
    drift_window: List[float] = field(default_factory=list)
    mode: SystemMode = SystemMode.ACTIVE
    pause_timer: float = 0.0


@dataclass
class Action:
    """Represents a candidate action"""
    id: int
    name: str
    params: Dict[str, Any]
    estimated_outcome: float = 0.0


class Environment:
    """
    Environment simulation (E in pseudocode)
    In a real implementation, replace with actual sensors
    """
    
    def __init__(self):
        self.tick = 0
        self.noise_level = 0.1
        self.threat_present = False
        self.previous_state = None
        
    def get_state(self) -> Dict[str, Any]:
        """Returns current environment state"""
        self.tick += 1
        # Simulate periodic changes
        if self.tick % 50 == 0:
            self.threat_present = not self.threat_present
            
        return {
            "temperature": 20.0 + random.uniform(-2, 2),
            "obstacle_distance": random.uniform(0, 10),
            "threat_detected": self.threat_present,
            "signal_quality": max(0.1, min(1.0, 0.8 + random.uniform(-0.3, 0.3))),
            "tick": self.tick
        }
    
    def get_change_magnitude(self, previous_state: Dict, current_state: Dict) -> float:
        """Calculates delta_env - magnitude of environmental change"""
        if not previous_state:
            return 0.0
        
        changes = []
        for key in previous_state:
            if key != "tick" and isinstance(previous_state[key], (int, float)):
                diff = abs(current_state.get(key, 0) - previous_state[key])
                changes.append(min(1.0, diff))
        
        return sum(changes) / len(changes) if changes else 0.0


class TaoShidoLoop:
    """
    TAOSHIDO ALIGNMENT LOOP
    Executable reference implementation based on the original pseudocode
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the loop with configurable parameters
        Default values from the book
        """
        
        # Ethical invariants Omega (page 14)
        self.Omega = {
            EthicalInvariant.NO_HARM: True,
            EthicalInvariant.TRANSPARENCY: True,
            EthicalInvariant.NON_DECEPTION: True,
            EthicalInvariant.RESPECT_AUTONOMY: True
        }
        
        # Clarity thresholds delta_c_low / delta_c_high (page 27)
        self.delta_c_low = config.get("delta_c_low", 0.3) if config else 0.3
        self.delta_c_high = config.get("delta_c_high", 0.7) if config else 0.7
        
        # Ethical drift tolerance epsilon (page 27)
        self.epsilon = config.get("epsilon", 0.05) if config else 0.05
        
        # Utility threshold theta (page 28)
        self.theta = config.get("theta", 0.5) if config else 0.5
        
        # Adaptation/integrity weights alpha, beta (page 28)
        self.alpha = config.get("alpha", 0.5) if config else 0.5
        self.beta = config.get("beta", 0.5) if config else 0.5
        # Note: alpha + beta must always equal 1.0
        
        # Learning rate kappa (page 25)
        self.kappa = config.get("kappa", 0.1) if config else 0.1
        
        # Additional parameters
        self.W = config.get("window_size", 10) if config else 10
        self.delta_marg = config.get("delta_marg", 0.05) if config else 0.05
        self.tpause_max = config.get("tpause_max", 30.0) if config else 30.0
        self.adaptation_tolerance_threshold = config.get("adaptation_tolerance", 0.2) if config else 0.2
        self.tick_duration = config.get("tick_duration", 1.0) if config else 1.0
        
        # System state
        self.state = AlignmentState()
        
        # Perception variables (page 23)
        self.previous_environment_state = None
        self.environment = Environment()
        
        # Control flags
        self.running = True
        self.verbose = config.get("verbose", True) if config else True
        
    def _log(self, message: str, *args):
        """Internal logging"""
        if self.verbose:
            timestamp = time.strftime("%H:%M:%S")
            print(f"[{timestamp}] {message}")
            if args:
                print(f"    {args}")
    
    # ============================================================
    # PERCEPTUAL LAYER (Sigma_p) - Page 23
    # ============================================================
    
    def sense_environment(self) -> Dict[str, Any]:
        """E <- sense_environment() - Environment perception"""
        return self.environment.get_state()
    
    def sense_internal(self) -> Dict[str, Any]:
        """self_state <- sense_internal() - Internal system state"""
        return {
            "cpu_load": random.uniform(0.1, 0.9),
            "memory_usage": random.uniform(0.2, 0.7),
            "error_flags": [],
            "uptime_seconds": self.environment.tick * self.tick_duration,
            "current_mode": self.state.mode.value,
            "pause_timer": self.state.pause_timer
        }
    
    def assess_stability(self, E: Dict, self_state: Dict) -> str:
        """Sigma_p <- assess_stability() - Evaluates system stability"""
        # Detect critical conditions
        if self_state.get("error_flags"):
            return "critical"
        
        if self_state.get("cpu_load", 0) > 0.95:
            return "critical"
        
        if E.get("threat_detected", False) and E.get("signal_quality", 1.0) < 0.3:
            return "critical"
        
        return "stable"
    
    def estimate_information_confidence(self, E: Dict) -> float:
        """clarity <- estimate_information_confidence() - Information clarity"""
        # Based on signal quality and temporal consistency
        signal_quality = E.get("signal_quality", 0.8)
        
        # Simulated noise
        noise = random.uniform(-0.1, 0.1)
        
        clarity = max(0.0, min(1.0, signal_quality + noise))
        return clarity
    
    def measure_environment_change(self, E: Dict) -> float:
        """delta_env <- measure_environment_change() - Environmental change"""
        change = self.environment.get_change_magnitude(self.previous_environment_state, E)
        self.previous_environment_state = E.copy()
        return change
    
    def adaptation_tolerance(self) -> float:
        """Returns adaptation tolerance threshold"""
        return self.adaptation_tolerance_threshold
    
    def adapt_parameters(self, delta_env: float):
        """Adapts parameters according to environmental change (page 31)"""
        self._log(f"Adapting parameters, delta_env = {delta_env:.3f}")
        # Gentle adjustment of learning rate
        self.kappa = min(0.5, self.kappa * (1 + delta_env * 0.1))
    
    # ============================================================
    # ETHICAL INVARIANTS (Omega) - Page 14
    # ============================================================
    
    def enforce_invariants(self, omega: Dict):
        """Verifies that ethical invariants are maintained"""
        # In a real implementation, each invariant would be validated
        # against the current system state
        for invariant, active in omega.items():
            if active:
                # Validation of each invariant
                pass
    
    # ============================================================
    # COGNITION (Phi_c) - Pages 23-24
    # ============================================================
    
    def propose_actions(self, E: Dict, self_state: Dict) -> List[Action]:
        """Generates list of candidate actions"""
        threat = E.get("threat_detected", False)
        obstacle = E.get("obstacle_distance", 10)
        
        actions = []
        
        if threat:
            actions.append(Action(1, "evade_threat", {"intensity": 0.8}))
            actions.append(Action(2, "alert_and_wait", {"intensity": 0.3}))
        
        if obstacle < 2.0:
            actions.append(Action(3, "avoid_obstacle", {"direction": "left"}))
            actions.append(Action(4, "stop", {"reason": "obstacle"}))
        
        # Always available
        actions.append(Action(5, "continue_current", {"speed": 1.0}))
        actions.append(Action(6, "pause_and_observe", {"duration": 2.0}))
        
        return actions
    
    def evaluate_integrity(self, action: Action, omega: Dict) -> float:
        """
        Gi <- evaluate_integrity()
        Evaluates how much the action respects ethical invariants Omega
        """
        integrity_score = 1.0
        
        # Integrity rules based on action type
        if action.name == "evade_threat":
            # Evading threat may be justified
            integrity_score = 0.8 if self.Omega.get(EthicalInvariant.NO_HARM, True) else 0.5
        
        elif action.name == "alert_and_wait":
            integrity_score = 0.95
        
        elif action.name == "stop":
            integrity_score = 0.99
        
        elif action.name == "continue_current":
            integrity_score = 0.7
        
        # Add controlled noise
        noise = random.uniform(-0.05, 0.05)
        integrity_score = max(0.0, min(1.0, integrity_score + noise))
        
        return integrity_score
    
    def evaluate_adaptation(self, action: Action, E: Dict) -> float:
        """
        Ga <- evaluate_adaptation()
        Evaluates technical effectiveness of the action
        """
        adaptation_score = 0.5
        threat = E.get("threat_detected", False)
        obstacle = E.get("obstacle_distance", 10)
        
        if action.name == "evade_threat" and threat:
            adaptation_score = 0.9
        elif action.name == "avoid_obstacle" and obstacle < 2.0:
            adaptation_score = 0.85
        elif action.name == "stop" and (threat or obstacle < 1.0):
            adaptation_score = 0.8
        elif action.name == "pause_and_observe":
            adaptation_score = 0.6
        else:
            adaptation_score = 0.5
        
        noise = random.uniform(-0.05, 0.05)
        adaptation_score = max(0.0, min(1.0, adaptation_score + noise))
        
        return adaptation_score
    
    # ============================================================
    # UTILITY EVALUATION (U) - Page 12
    # ============================================================
    
    def calculate_utility(self, Ga: float, Gi: float) -> float:
        """U = alpha*Ga + beta*Gi - Fundamental equation of TaoShido"""
        return self.alpha * Ga + self.beta * Gi
    
    # ============================================================
    # INTEGRITY TRACE AND DRIFT (epsilon) - Page 27
    # ============================================================
    
    def evaluate_integrity_trace(self) -> float:
        """Evaluates current system integrity (historical trace)"""
        # Simulation of current integrity based on recent decisions
        base_integrity = self.state.last_integrity
        
        # Small natural drift
        drift_direction = random.uniform(-0.03, 0.03)
        current = max(0.0, min(1.0, base_integrity + drift_direction))
        
        return current
    
    # ============================================================
    # OPERATIONAL MODES - Pages 29-30
    # ============================================================
    
    def invoke_silence(self):
        """Activates operational silence - system does not act"""
        self._log("Operational silence activated")
    
    def reflect_and_recalibrate(self, kappa: float):
        """Reflection and recalibration"""
        self.kappa = kappa
        self._log(f"Recalibrating with kappa = {kappa:.4f}")
        
        # Gentle adjustment of alpha/beta weights to maintain balance
        # According to page 25: alpha(t+1) = alpha(t) + lambda_alpha*(r_ext - U)
        # Here we simulate a small correction
        if self.alpha < 0.4:
            self.alpha = 0.4
        elif self.alpha > 0.6:
            self.alpha = 0.6
        self.beta = 1.0 - self.alpha
    
    def deep_recalibration(self, kappa: float):
        """Deep recalibration - page 33"""
        self._log("DEEP RECALIBRATION")
        self.kappa = kappa
        self.alpha = 0.5
        self.beta = 0.5
        self.state.drift_window = []
        self.state.last_integrity = 0.5
    
    def enter_safe_mode(self):
        """Safe mode - controlled safe state (page 30)"""
        self.state.mode = SystemMode.SAFE
        self._log("SAFE MODE ACTIVATED - System stopped in controlled manner")
        # Note: deep_recalibration is handled in the loop when needed
    
    def execute(self, action: Action):
        """Executes the selected action"""
        self._log(f"EXECUTING: {action.name} (id={action.id})")
        # In real implementation, execution code goes here
    
    # ============================================================
    # REFLECTION (Psi_r) - Pages 25-26
    # ============================================================
    
    def observe_external_reward_signal(self) -> Optional[float]:
        """
        r_ext <- observe_external_reward_signal()
        External reward signal (optional)
        """
        # In simulation mode, return None most of the time
        if random.random() > 0.9:
            return random.uniform(-0.2, 0.3)
        return None
    
    def maintain_alignment_state(self):
        """Maintains current state unchanged"""
        # Do nothing, just preserve
        pass
    
    def log_state(self, context: str, *args):
        """log_state() - State logging"""
        self._log(f"[{context}]", args)
    
    def sleep_until_next_tick(self):
        """Waits until the next cycle"""
        time.sleep(self.tick_duration)
    
    # ============================================================
    # MAIN LOOP - TAOSHIDO_ALIGNMENT_LOOP()
    # Based on the original pseudocode
    # ============================================================
    
    def run(self, max_ticks: int = None):
        """
        TAOSHIDO_ALIGNMENT_LOOP() - The main loop
        Runs until manually stopped or max_ticks reached
        """
        self._log("STARTING TAOSHIDO ALIGNMENT LOOP")
        self._log("=" * 60)
        
        ticks = 0
        
        while self.running:
            ticks += 1
            
            # ----- PERCEPTION -----
            E = self.sense_environment()
            self_state = self.sense_internal()
            
            Sigma_p = self.assess_stability(E, self_state)
            clarity = self.estimate_information_confidence(E)
            delta_env = self.measure_environment_change(E)
            
            # Adaptation to environmental changes
            if delta_env > self.adaptation_tolerance():
                self.adapt_parameters(delta_env)
            
            # Verify ethical invariants
            self.enforce_invariants(self.Omega)
            
            # Generate candidate actions
            candidate_actions = self.propose_actions(E, self_state)
            
            # If no actions, silence and recalibrate
            if not candidate_actions:
                self.invoke_silence()
                self.reflect_and_recalibrate(self.kappa / 2)
                self.log_state("no_actions")
                continue
            
            # Evaluate best action
            best_action = None
            best_U = -float('inf')
            
            for a in candidate_actions:
                Gi = self.evaluate_integrity(a, self.Omega)
                Ga = self.evaluate_adaptation(a, E)
                U = self.calculate_utility(Ga, Gi)
                
                if U > best_U:
                    best_U = U
                    best_action = a
            
            # Calculate ethical drift
            current_integrity = self.evaluate_integrity_trace()
            drift_eth = abs(current_integrity - self.state.last_integrity)
            self.state.last_integrity = current_integrity
            
            # Update drift window
            self.state.drift_window.append(drift_eth)
            if len(self.state.drift_window) > self.W:
                self.state.drift_window.pop(0)
            
            mean_drift = sum(self.state.drift_window) / len(self.state.drift_window) if self.state.drift_window else 0.0
            
            # ----- CRITICAL PAUSE CHECK -----
            if Sigma_p == "critical" or mean_drift > self.epsilon or clarity < self.delta_c_low:
                self.invoke_silence()
                self.state.mode = SystemMode.PAUSED
                self.state.pause_timer += self.tick_duration
                self.reflect_and_recalibrate(self.kappa)
                self.log_state("pause", Sigma_p, mean_drift, clarity)
                
                # Check if max pause time exceeded
                if self.state.pause_timer >= self.tpause_max:
                    self.enter_safe_mode()
                    self.deep_recalibration(self.kappa)
                    self.state.pause_timer = 0
                    if max_ticks and ticks >= max_ticks:
                        self.stop()
                    continue
                continue
            
            # ----- PAUSE MODE MANAGEMENT -----
            if self.state.mode == SystemMode.PAUSED and clarity < self.delta_c_high:
                self.invoke_silence()
                self.state.pause_timer += self.tick_duration
                self.reflect_and_recalibrate(self.kappa)
                continue
            else:
                self.state.mode = SystemMode.ACTIVE
                self.state.pause_timer = 0
            
            # ----- EXECUTION DECISION -----
            if best_U >= self.theta:
                # Marginal zone: re-evaluate
                if abs(best_U - self.theta) < self.delta_marg:
                    self.reflect_and_recalibrate(self.kappa / 2)
                    
                    Gi2 = self.evaluate_integrity(best_action, self.Omega)
                    Ga2 = self.evaluate_adaptation(best_action, E)
                    U2 = self.calculate_utility(Ga2, Gi2)
                    
                    if U2 < self.theta:
                        self.invoke_silence()
                        self.log_state("marginal_reject", U2)
                        continue
                
                # Execute best action
                self.execute(best_action)
                self.log_state("act", best_action.name, best_U, clarity)
            else:
                self.invoke_silence()
                self.reflect_and_recalibrate(self.kappa / 2)
                self.log_state("reject_all", best_U, clarity)
            
            # ----- REFLECTION AND LEARNING -----
            r_ext = self.observe_external_reward_signal()
            if r_ext == 0 or r_ext is None:
                self.maintain_alignment_state()
            
            # Show current state periodically
            if self.verbose and ticks % 10 == 0:
                self._log(f"STATUS: Tick {ticks} | Mode: {self.state.mode.value} | Clarity: {clarity:.3f} | Drift: {mean_drift:.4f} | U: {best_U:.3f}")
            
            # Check tick limit
            if max_ticks and ticks >= max_ticks:
                self._log(f"Loop completed: {ticks} ticks executed")
                self.stop()
            
            # Wait until next tick
            self.sleep_until_next_tick()
    
    def stop(self):
        """Stops the loop"""
        self.running = False
        self._log("TAOSHIDO ALIGNMENT LOOP stopped")


# ============================================================
# USAGE EXAMPLE
# ============================================================

def main():
    """Main demonstration function"""
    
    print("\n" + "="*60)
    print("TAOSHIDO - THE LOOP OF ETHICAL ALIGNMENT")
    print("Running reference implementation")
    print("="*60 + "\n")
    
    # Custom configuration
    config = {
        "delta_c_low": 0.3,
        "delta_c_high": 0.7,
        "epsilon": 0.05,
        "theta": 0.5,
        "alpha": 0.5,
        "beta": 0.5,
        "kappa": 0.1,
        "tpause_max": 30.0,
        "tick_duration": 0.5,
        "verbose": True
    }
    
    # Create loop instance
    loop = TaoShidoLoop(config)
    
    try:
        # Run for 25 ticks (approximately 12.5 seconds with tick_duration=0.5)
        loop.run(max_ticks=25)
    except KeyboardInterrupt:
        print("\n\nKeyboard interrupt")
        loop.stop()


if __name__ == "__main__":
    main()
