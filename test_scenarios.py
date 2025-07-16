#!/usr/bin/env python3
"""
Helper script to test different visual regression scenarios locally.
This script helps demonstrate how the workflow handles passing and failing test cases.
"""

import os
import sys
import subprocess
import shutil

def run_scenario(scenario_name):
    """Run a specific test scenario."""
    print(f"\n{'='*50}")
    print(f"Running scenario: {scenario_name}")
    print('='*50)
    
    # Set environment variable for the scenario
    env = os.environ.copy()
    env['TEST_SCENARIO'] = scenario_name
    
    # Clean up previous outputs
    if os.path.exists('outputs'):
        shutil.rmtree('outputs')
    if os.path.exists('diffs'):
        shutil.rmtree('diffs')
    
    # Generate test images
    print("Generating test images...")
    result = subprocess.run(['python', 'generate_test_images.py'], env=env, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error generating images: {result.stderr}")
        return False
    
    print(result.stdout)
    
    # Show what was generated
    if os.path.exists('outputs'):
        output_files = os.listdir('outputs')
        print(f"Generated {len(output_files)} output files: {output_files}")
    
    return True

def main():
    """Run all test scenarios to demonstrate the workflow."""
    
    scenarios = ['baseline', 'changed', 'mixed']
    
    if len(sys.argv) > 1:
        # Run specific scenario
        scenario = sys.argv[1]
        if scenario not in scenarios:
            print(f"Invalid scenario. Choose from: {scenarios}")
            sys.exit(1)
        scenarios = [scenario]
    
    print("Visual Regression Test Scenario Runner")
    print("=====================================")
    print(f"This script demonstrates the different test scenarios:")
    print(f"  baseline: All images match golden masters (tests pass)")
    print(f"  changed:  All images differ from golden masters (tests fail)")
    print(f"  mixed:    Some images pass, some fail")
    print()
    
    success = True
    for scenario in scenarios:
        if not run_scenario(scenario):
            success = False
    
    if success:
        print(f"\n{'='*50}")
        print("All scenarios completed successfully!")
        print("You can now trigger the visual-diff workflow with different scenarios")
        print("using the workflow_dispatch event on GitHub Actions.")
        print('='*50)
    else:
        print("\nSome scenarios failed. Check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()