#!/bin/bash
# Test runner script for visual regression system
# This script can be run manually to test the system before committing

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🧪 Visual Regression System Test Runner"
echo "========================================"

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS] [SCENARIO]"
    echo ""
    echo "OPTIONS:"
    echo "  --setup        Set up test environment (install dependencies)"
    echo "  --clean        Clean up test artifacts"
    echo "  --help         Show this help message"
    echo ""
    echo "SCENARIOS:"
    echo "  baseline       Test with matching images (should pass)"
    echo "  changed        Test with different images (should fail)"
    echo "  mixed          Test with mixed results"
    echo "  all            Run all scenarios (default)"
    echo ""
    echo "Examples:"
    echo "  $0 --setup               # Set up test environment"
    echo "  $0                       # Run all test scenarios"
    echo "  $0 baseline              # Run only baseline scenario"
    echo "  $0 --clean               # Clean up test artifacts"
}

# Function to set up test environment
setup_environment() {
    echo "📦 Setting up test environment..."
    
    # Check if Python is available
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 is required but not found. Please install Python 3."
        exit 1
    fi
    
    # Create virtual environment if it doesn't exist
    if [ ! -d ".venv" ]; then
        echo "  Creating virtual environment..."
        python3 -m venv .venv
    fi
    
    # Activate virtual environment
    echo "  Activating virtual environment..."
    source .venv/bin/activate
    
    # Install/update dependencies
    echo "  Installing dependencies..."
    pip install -q --upgrade pip
    # Use timeout and retry logic for pip install to handle network issues
    if ! timeout 120 pip install -q --no-cache-dir -r requirements.txt; then
        echo "  ⚠️  Network timeout, retrying with system cache..."
        pip install -q -r requirements.txt || {
            echo "❌ Failed to install dependencies. Please check your internet connection."
            exit 1
        }
    fi
    
    echo "✅ Test environment setup complete!"
    echo ""
    echo "To manually activate the environment:"
    echo "  source .venv/bin/activate"
    echo ""
}

# Function to clean up test artifacts
cleanup_artifacts() {
    echo "🧹 Cleaning up test artifacts..."
    rm -rf outputs diffs .venv
    echo "✅ Cleanup complete!"
}

# Function to run tests
run_tests() {
    local scenario="${1:-all}"
    
    echo "🔍 Running tests for scenario: $scenario"
    
    # Check if we're in a virtual environment or if dependencies are available
    if [ -z "${VIRTUAL_ENV:-}" ]; then
        if [ -d ".venv" ]; then
            echo "  Activating virtual environment..."
            source .venv/bin/activate
        else
            echo "  Testing with system Python..."
            # Try to install dependencies system-wide if needed
            if ! python3 -c "import PIL, numpy, yaml" &> /dev/null; then
                echo "❌ Required dependencies (PIL, numpy, yaml) not found. Run '$0 --setup' to install dependencies."
                exit 1
            fi
        fi
    fi
    
    # Verify dependencies
    echo "  Checking dependencies..."
    python3 -c "from PIL import Image; import numpy; import yaml" 2>/dev/null || {
        echo "❌ Required dependencies not found. Run '$0 --setup' first."
        exit 1
    }
    
    # Run the actual tests
    echo "  Running test scenarios..."
    if [ "$scenario" = "all" ]; then
        python3 test_scenarios.py
    else
        python3 test_scenarios.py "$scenario"
    fi
    
    # Run workflow validation
    echo "  Validating workflow files..."
    python3 -c "
import yaml
import sys

workflow_files = [
    '.github/workflows/visual-diff.yml',
    '.github/workflows/test-visual-diff.yml', 
    '.github/workflows/accept-image.yml'
]

for workflow_file in workflow_files:
    try:
        with open(workflow_file, 'r') as f:
            yaml.safe_load(f)
        print(f'    ✅ {workflow_file}')
    except Exception as e:
        print(f'    ❌ {workflow_file}: {e}')
        sys.exit(1)
"
    
    echo "✅ All tests passed!"
}

# Parse command line arguments
case "${1:-}" in
    --setup)
        setup_environment
        ;;
    --clean)
        cleanup_artifacts
        ;;
    --help|-h)
        show_usage
        ;;
    baseline|changed|mixed)
        run_tests "$1"
        ;;
    all|"")
        run_tests "all"
        ;;
    *)
        echo "❌ Unknown option: $1"
        echo ""
        show_usage
        exit 1
        ;;
esac