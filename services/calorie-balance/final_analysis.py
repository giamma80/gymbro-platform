#!/usr/bin/env python3
"""
Final Test Results Summary
"""
import subprocess
import sys
import os

os.chdir('/Users/giamma/workspace/gymbro-platform/services/calorie-balance')

print("🔍 FINAL TEST RESULTS ANALYSIS")
print("=" * 70)

# Run the full test suite
try:
    result = subprocess.run([
        sys.executable, '-m', 'pytest', 'test_comprehensive.py', 
        '--tb=no', '-q', '--disable-warnings'
    ], capture_output=True, text=True, timeout=180)
    
    output_lines = result.stdout.split('\n')
    error_lines = result.stderr.split('\n')
    
    # Parse results
    passed = 0
    failed = 0
    errors = 0
    
    for line in output_lines:
        if ' passed' in line and ' failed' in line:
            # Parse line like "25 passed, 21 failed in 45.67s"
            parts = line.split()
            for i, part in enumerate(parts):
                if part == 'passed' and i > 0:
                    passed = int(parts[i-1])
                elif part == 'failed' and i > 0:
                    failed = int(parts[i-1])
        elif ' passed' in line and 'failed' not in line:
            # Parse line like "46 passed in 45.67s"  
            parts = line.split()
            for i, part in enumerate(parts):
                if part == 'passed' and i > 0:
                    passed = int(parts[i-1])
                    
    total = passed + failed + errors
    
    print(f"📊 TEST RESULTS SUMMARY:")
    print(f"   ✅ PASSED:  {passed}")
    print(f"   ❌ FAILED:  {failed}")
    print(f"   🚫 ERRORS:  {errors}")
    print(f"   📋 TOTAL:   {total}")
    
    if total > 0:
        success_rate = (passed / total) * 100
        print(f"   🎯 SUCCESS RATE: {success_rate:.1f}%")
        
        print("\n📈 COMPARISON:")
        print("   BEFORE Fix: 25 passed, 21 failed (54.3%)")
        print(f"   AFTER  Fix: {passed} passed, {failed} failed ({success_rate:.1f}%)")
        
        improvement = success_rate - 54.3
        if improvement > 0:
            print(f"   📈 IMPROVEMENT: +{improvement:.1f}% success rate!")
        
        if success_rate >= 90:
            print("\n🎉 EXCELLENT! Target >90% success rate ACHIEVED!")
        elif success_rate >= 80:
            print("\n✅ GOOD! >80% success rate achieved!")
        elif improvement >= 10:
            print("\n📈 SIGNIFICANT IMPROVEMENT! +10%+ success rate!")
        else:
            print("\n⚠️  Limited improvement - may need additional fixes")
    
    # Show any remaining failures for analysis
    if failed > 0:
        print(f"\n🔍 ANALYZING REMAINING {failed} FAILURES...")
        # Run with more details on failures
        detail_result = subprocess.run([
            sys.executable, '-m', 'pytest', 'test_comprehensive.py',
            '--tb=line', '-q', '--disable-warnings'
        ], capture_output=True, text=True, timeout=60)
        
        detail_lines = detail_result.stdout.split('\n')
        failures = [line for line in detail_lines if 'FAILED' in line]
        
        print("   Top failing tests:")
        for i, failure in enumerate(failures[:5]):  # Show first 5
            print(f"   {i+1}. {failure}")
        
        if len(failures) > 5:
            print(f"   ... and {len(failures) - 5} more")

    print("\n" + "=" * 70)
    print("🏁 SCHEMA ALIGNMENT FIX ANALYSIS COMPLETE")
    
except subprocess.TimeoutExpired:
    print("❌ Test execution timeout")
except Exception as e:
    print(f"❌ Error executing tests: {e}")