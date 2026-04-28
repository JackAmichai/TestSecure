"""
Automated Experiment Runner
Runs all experiment configurations sequentially and collects results.
"""

import os
import sys
import time
import json
import subprocess
import signal
from datetime import datetime

# Configuration profiles to test
PROFILES = [
    "sha256_open",
    "sha256_lockout_rate",
    "sha256_full",
    "bcrypt_open",
    "bcrypt_lockout_rate",
    "bcrypt_full",
    "argon2_open",
    "argon2_lockout_rate",
    "argon2_full",
]

# Experiment settings
SERVER_START_DELAY = 3  # seconds to wait for server startup
SERVER_PORT = 5000
RESULTS_DIR = "experiment_results"

# Optional: Set PEPPER for all experiments
PEPPER_VALUE = "research_pepper_2025"  # Change as needed


class ExperimentRunner:
    def __init__(self):
        self.server_process = None
        self.results = []
        os.makedirs(RESULTS_DIR, exist_ok=True)
        
    def set_environment(self, profile, pepper=None):
        """Set environment variables for experiment."""
        os.environ["APP_CONFIG"] = profile
        if pepper:
            os.environ["PEPPER"] = pepper
        print(f"[ENV] APP_CONFIG={profile}")
        if pepper:
            print(f"[ENV] PEPPER={pepper}")
    
    def start_server(self):
        """Start Flask server in background."""
        print("[SERVER] Starting Flask server...")
        
        # Start server process
        self.server_process = subprocess.Popen(
            [sys.executable, "app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for server to start
        time.sleep(SERVER_START_DELAY)
        
        # Check if server started successfully
        if self.server_process.poll() is not None:
            print("[SERVER] ERROR: Server failed to start!")
            stdout, stderr = self.server_process.communicate()
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return False
        
        print(f"[SERVER] Server started (PID: {self.server_process.pid})")
        return True
    
    def stop_server(self):
        """Stop Flask server."""
        if self.server_process:
            print("[SERVER] Stopping server...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print("[SERVER] Force killing server...")
                self.server_process.kill()
                self.server_process.wait()
            print("[SERVER] Server stopped")
            self.server_process = None
    
    def generate_users(self):
        """Generate user dataset."""
        print("[SETUP] Generating user dataset...")
        result = subprocess.run(
            [sys.executable, "generate_users.py"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"[ERROR] User generation failed: {result.stderr}")
            return False
        print(result.stdout)
        return True
    
    def clear_logs(self):
        """Clear previous attempt logs."""
        log_file = "logs/attempts.log"
        if os.path.exists(log_file):
            os.remove(log_file)
            print("[CLEANUP] Cleared previous logs")
    
    def run_attack(self, attack_script, attack_name):
        """Run an attack script."""
        print(f"\n[ATTACK] Running {attack_name}...")
        start_time = time.time()
        
        result = subprocess.run(
            [sys.executable, attack_script],
            capture_output=True,
            text=True,
            timeout=7200  # 2 hour timeout
        )
        
        duration = time.time() - start_time
        
        if result.returncode != 0:
            print(f"[WARNING] {attack_name} returned error code {result.returncode}")
            print(f"STDERR: {result.stderr}")
        
        print(result.stdout)
        print(f"[ATTACK] {attack_name} completed in {duration:.2f} seconds")
        
        return {
            "attack": attack_name,
            "duration": duration,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    
    def analyze_logs(self):
        """Analyze attempt logs."""
        print("\n[ANALYSIS] Analyzing logs...")
        result = subprocess.run(
            [sys.executable, "analyze_logs_enhanced.py"],
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print(f"STDERR: {result.stderr}")
    
    def run_experiment(self, profile, use_pepper=False):
        """Run complete experiment for a profile."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        experiment_name = f"{profile}{'_pepper' if use_pepper else ''}_{timestamp}"
        
        print("\n" + "="*80)
        print(f"STARTING EXPERIMENT: {experiment_name}")
        print("="*80)
        
        # Set environment
        self.set_environment(profile, PEPPER_VALUE if use_pepper else None)
        
        # Generate users with current hash mode
        if not self.generate_users():
            print("[ERROR] Cannot continue without users")
            return None
        
        # Clear previous logs
        self.clear_logs()
        
        # Start server
        if not self.start_server():
            print("[ERROR] Cannot continue without server")
            return None
        
        experiment_result = {
            "profile": profile,
            "use_pepper": use_pepper,
            "timestamp": timestamp,
            "attacks": []
        }
        
        try:
            # Run brute-force attack
            attack_result = self.run_attack(
                "attack_bruteforce_enhanced.py",
                "Brute Force"
            )
            experiment_result["attacks"].append(attack_result)
            
            # Run password spraying attack
            attack_result = self.run_attack(
                "attack_spray_enhanced.py",
                "Password Spraying"
            )
            experiment_result["attacks"].append(attack_result)
            
            # Analyze logs
            self.analyze_logs()
            
            # Copy logs to results directory
            result_dir = os.path.join(RESULTS_DIR, experiment_name)
            os.makedirs(result_dir, exist_ok=True)
            
            # Copy attempts log
            if os.path.exists("logs/attempts.log"):
                import shutil
                shutil.copy("logs/attempts.log", 
                          os.path.join(result_dir, "attempts.log"))
            
            # Copy analysis summary
            if os.path.exists("logs/analysis_summary.json"):
                import shutil
                shutil.copy("logs/analysis_summary.json",
                          os.path.join(result_dir, "analysis_summary.json"))
            
            # Save experiment metadata
            with open(os.path.join(result_dir, "experiment_info.json"), "w") as f:
                json.dump(experiment_result, f, indent=2)
            
            print(f"\n[SUCCESS] Experiment results saved to: {result_dir}")
            
        except Exception as e:
            print(f"[ERROR] Experiment failed: {e}")
            experiment_result["error"] = str(e)
        
        finally:
            # Stop server
            self.stop_server()
        
        print("="*80)
        print(f"EXPERIMENT COMPLETED: {experiment_name}")
        print("="*80 + "\n")
        
        return experiment_result
    
    def run_all_experiments(self):
        """Run all experiments."""
        print("\n" + "="*80)
        print("AUTOMATED EXPERIMENT SUITE")
        print("="*80)
        print(f"Total profiles to test: {len(PROFILES)}")
        print(f"Testing with pepper: {'YES' if PEPPER_VALUE else 'NO'}")
        print(f"Results directory: {RESULTS_DIR}")
        print("="*80 + "\n")
        
        start_time = time.time()
        
        for i, profile in enumerate(PROFILES, 1):
            print(f"\n>>> Experiment {i}/{len(PROFILES)}: {profile}")
            
            # Run without pepper
            result = self.run_experiment(profile, use_pepper=False)
            if result:
                self.results.append(result)
            
            # Optional: Run with pepper (uncomment if needed)
            # result = self.run_experiment(profile, use_pepper=True)
            # if result:
            #     self.results.append(result)
            
            # Brief pause between experiments
            if i < len(PROFILES):
                print("\n[PAUSE] Waiting 5 seconds before next experiment...")
                time.sleep(5)
        
        total_duration = time.time() - start_time
        
        # Save summary
        summary = {
            "total_experiments": len(self.results),
            "total_duration_seconds": total_duration,
            "total_duration_hours": total_duration / 3600,
            "timestamp": datetime.now().isoformat(),
            "experiments": self.results,
        }
        
        summary_file = os.path.join(RESULTS_DIR, "experiments_summary.json")
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)
        
        print("\n" + "="*80)
        print("ALL EXPERIMENTS COMPLETED")
        print("="*80)
        print(f"Total experiments run: {len(self.results)}")
        print(f"Total duration: {total_duration/3600:.2f} hours")
        print(f"Summary saved to: {summary_file}")
        print("="*80 + "\n")


def main():
    runner = ExperimentRunner()
    
    try:
        runner.run_all_experiments()
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Experiment suite interrupted by user")
        runner.stop_server()
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] Unexpected error: {e}")
        runner.stop_server()
        sys.exit(1)


if __name__ == "__main__":
    main()
