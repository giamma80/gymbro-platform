#!/usr/bin/env python3
"""
GymBro Platform - Master Test Runner
===================================
Executes comprehensive tests across all services in the platform.

Usage:
    python run-all-tests.py [local|prod]
    
    local: Test against localhost (default)
    prod:  Test against production URLs
    
Features:
- Parallel test execution for speed
- Consolidated reporting across all services
- Environment management (local/prod)
- Color-coded output with service identification
- Summary statistics and failure analysis
"""

import sys
import subprocess
import asyncio
import time
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import concurrent.futures


class TestColors:
    """ANSI color codes for test output."""
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    END = "\033[0m"


class MasterTestRunner:
    """Master test runner for all GymBro Platform services."""
    
    def __init__(self, environment: str = "local"):
        self.environment = environment
        self.start_time = time.time()
        self.services_with_tests = [
            "calorie-balance", 
            "user-management"
        ]
        self.results = {}
        
    def log_header(self, message: str):
        """Print a main header."""
        print(f"\n{TestColors.BOLD}{TestColors.BLUE}{'='*80}")
        print(f"🚀 {message}")
        print(f"{'='*80}{TestColors.END}")
        
    def log_service(self, service: str, message: str):
        """Print service-specific message."""
        color = TestColors.CYAN if "PASS" in message else TestColors.RED if "FAIL" in message else TestColors.YELLOW
        print(f"{color}📋 [{service.upper()}] {message}{TestColors.END}")
        
    def log_summary(self, message: str):
        """Print summary message."""
        print(f"{TestColors.PURPLE}{TestColors.BOLD}📊 {message}{TestColors.END}")
    
    def run_service_tests(self, service: str) -> Tuple[str, Dict]:
        """Run tests for a specific service."""
        service_path = Path(f"/Users/giamma/workspace/gymbro-platform/services/{service}")
        
        if not service_path.exists():
            return service, {
                "success": False, 
                "error": "Service directory not found",
                "total": 0,
                "passed": 0,
                "failed": 0,
                "duration": 0
            }
            
        test_file = service_path / "test_comprehensive.py"
        if not test_file.exists():
            return service, {
                "success": False,
                "error": "test_comprehensive.py not found", 
                "total": 0,
                "passed": 0,
                "failed": 0,
                "duration": 0
            }
            
        self.log_service(service, f"Starting tests ({self.environment})...")
        
        try:
            # Run the test with poetry
            cmd = ["poetry", "run", "python", "test_comprehensive.py", self.environment]
            result = subprocess.run(
                cmd,
                cwd=service_path,
                capture_output=True,
                text=True,
                timeout=120  # 2 minutes timeout
            )
            
            # Parse output to extract statistics
            output = result.stdout
            stats = self._parse_test_output(output)
            stats["success"] = result.returncode == 0
            stats["output"] = output
            stats["error_output"] = result.stderr
            
            # Debug output for troubleshooting
            if stats["total"] == 0 and output:
                # Look for the summary section more carefully
                summary_lines = []
                in_summary = False
                for line in output.split('\n'):
                    if "Test Summary" in line:
                        in_summary = True
                    if in_summary:
                        summary_lines.append(line.strip())
                        if line.startswith("Duration:") or "seconds" in line:
                            break
                
                print(f"DEBUG [{service}]: Searching in summary section:")
                for line in summary_lines:
                    print(f"  {line}")
                    
                # Try parsing the summary section specifically
                for line in summary_lines:
                    if "Total Tests:" in line:
                        try:
                            stats["total"] = int(line.split("Total Tests:")[-1].strip())
                        except Exception as e:
                            print(f"  Failed to parse total: {e}")
                    elif line.startswith("Passed:"):
                        try:
                            stats["passed"] = int(line.split("Passed:")[-1].strip())
                        except Exception as e:
                            print(f"  Failed to parse passed: {e}")
                    elif line.startswith("Failed:"):
                        try:
                            stats["failed"] = int(line.split("Failed:")[-1].strip())
                        except Exception as e:
                            print(f"  Failed to parse failed: {e}")
                    elif "Success Rate:" in line:
                        try:
                            rate_str = line.split("Success Rate:")[-1].strip().replace("%", "")
                            stats["success_rate"] = float(rate_str)
                        except Exception as e:
                            print(f"  Failed to parse success rate: {e}")
                    elif "Duration:" in line:
                        try:
                            duration_str = line.split("Duration:")[-1].strip().replace("seconds", "").strip()
                            stats["duration"] = float(duration_str)
                        except Exception as e:
                            print(f"  Failed to parse duration: {e}")
            
            if stats["success"]:
                self.log_service(service, f"✅ COMPLETED - {stats['passed']}/{stats['total']} tests passed ({stats['success_rate']:.1f}%)")
            else:
                self.log_service(service, f"❌ FAILED - {stats['passed']}/{stats['total']} tests passed ({stats['success_rate']:.1f}%)")
                
            return service, stats
            
        except subprocess.TimeoutExpired:
            return service, {
                "success": False,
                "error": "Test execution timeout (120s)",
                "total": 0,
                "passed": 0, 
                "failed": 0,
                "duration": 120
            }
        except Exception as e:
            return service, {
                "success": False,
                "error": str(e),
                "total": 0,
                "passed": 0,
                "failed": 0,
                "duration": 0
            }
    
    def _parse_test_output(self, output: str) -> Dict:
        """Parse test output to extract statistics - strips ANSI color codes."""
        # Remove ANSI escape sequences (color codes)
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        clean_output = ansi_escape.sub('', output)
        
        stats = {
            "total": 0,
            "passed": 0, 
            "failed": 0,
            "success_rate": 0.0,
            "duration": 0.0
        }
        
        lines = clean_output.split('\n')
        for line in lines:
            line = line.strip()
            if "Total Tests:" in line:
                try:
                    stats["total"] = int(line.split("Total Tests:")[-1].strip())
                except:
                    pass
            elif line.startswith("Passed:"):
                try:
                    stats["passed"] = int(line.split("Passed:")[-1].strip())
                except:
                    pass
            elif line.startswith("Failed:"):
                try:
                    stats["failed"] = int(line.split("Failed:")[-1].strip())
                except:
                    pass
            elif "Success Rate:" in line:
                try:
                    rate_str = line.split("Success Rate:")[-1].strip().replace("%", "")
                    stats["success_rate"] = float(rate_str)
                except:
                    pass
            elif "Duration:" in line:
                try:
                    duration_str = line.split("Duration:")[-1].strip().replace("seconds", "").strip()
                    stats["duration"] = float(duration_str)
                except:
                    pass
                    
        return stats
    
    def run_all_tests(self):
        """Run tests for all services."""
        self.log_header(f"GymBro Platform - Master Test Runner ({self.environment.upper()})")
        
        print(f"{TestColors.CYAN}Environment: {self.environment}{TestColors.END}")
        print(f"{TestColors.CYAN}Services: {', '.join(self.services_with_tests)}{TestColors.END}")
        print(f"{TestColors.CYAN}Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{TestColors.END}")
        
        # Run tests in parallel for speed
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.services_with_tests)) as executor:
            future_to_service = {
                executor.submit(self.run_service_tests, service): service 
                for service in self.services_with_tests
            }
            
            for future in concurrent.futures.as_completed(future_to_service):
                service, result = future.result()
                self.results[service] = result
        
        self._generate_master_summary()
    
    def _generate_master_summary(self):
        """Generate comprehensive summary across all services."""
        total_duration = time.time() - self.start_time
        
        self.log_header("MASTER TEST SUMMARY")
        
        # Service-by-service breakdown
        total_tests = 0
        total_passed = 0
        total_failed = 0
        services_success = 0
        
        for service, result in self.results.items():
            total_tests += result.get("total", 0)
            total_passed += result.get("passed", 0)
            total_failed += result.get("failed", 0)
            
            if result.get("success", False):
                services_success += 1
                status = f"{TestColors.GREEN}✅ SUCCESS{TestColors.END}"
            else:
                status = f"{TestColors.RED}❌ FAILED{TestColors.END}"
                
            print(f"{status} {service:<20} | {result.get('passed', 0):>3}/{result.get('total', 0):<3} tests | "
                  f"{result.get('success_rate', 0):>5.1f}% | {result.get('duration', 0):>5.1f}s")
            
            if not result.get("success", False) and "error" in result:
                print(f"       {TestColors.RED}└─ Error: {result['error']}{TestColors.END}")
        
        # Overall statistics
        overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        platform_success = services_success == len(self.services_with_tests)
        
        print(f"\n{TestColors.BOLD}📊 PLATFORM STATISTICS{TestColors.END}")
        print(f"Services:      {services_success}/{len(self.services_with_tests)} successful")
        print(f"Total Tests:   {total_tests}")
        print(f"Passed:        {TestColors.GREEN}{total_passed}{TestColors.END}")
        print(f"Failed:        {TestColors.RED}{total_failed}{TestColors.END}")
        print(f"Success Rate:  {TestColors.CYAN}{overall_success_rate:.1f}%{TestColors.END}")
        print(f"Duration:      {TestColors.YELLOW}{total_duration:.1f}s{TestColors.END}")
        
        # Final verdict
        if platform_success:
            print(f"\n{TestColors.GREEN}{TestColors.BOLD}🎉 ALL SERVICES PASSED!{TestColors.END}")
        else:
            print(f"\n{TestColors.RED}{TestColors.BOLD}⚠️  SOME SERVICES FAILED - CHECK LOGS ABOVE{TestColors.END}")
            
        return platform_success


def main():
    """Main execution function."""
    # Environment handling
    environments = ["local", "prod"]
    
    if len(sys.argv) > 1:
        env_profile = sys.argv[1].lower()
        if env_profile not in environments:
            print(f"❌ Invalid profile: {env_profile}")
            print(f"Available profiles: {', '.join(environments)}")
            sys.exit(1)
    else:
        env_profile = "local"
    
    runner = MasterTestRunner(env_profile)
    success = runner.run_all_tests()
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)