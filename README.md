# Visual Regression Testing with Git LFS

A robust, LFS-aware GitHub Actions workflow system for visual regression testing. This system handles multiple output images, uses NVIDIA's flip for high-fidelity comparison, and correctly stores final "golden" images using Git LFS to avoid bloating the main repository.

## Features

- **LFS-Aware Storage**: Automatically handles large image files using Git LFS
- **High-Fidelity Comparison**: Uses NVIDIA flip for precise image comparison
- **Interactive Workflow**: Accept/reject changes via PR comments
- **Embedded Image Display**: Direct image embedding in PR comments using temporary branches
- **Artifact-Based Backup**: Complete image packages for manual review when needed
- **Detailed Statistics**: FLIP-based comparison metrics and comprehensive reporting
- **Security**: Permission checks for image acceptance

## Prerequisites

The repository must be configured to use Git LFS for image file types:

```bash
# Install Git LFS
git lfs install

# Track image files (already configured in .gitattributes)
git lfs track "golden/**/*.png"
git lfs track "golden/**/*.jpg" 
git lfs track "golden/**/*.jpeg"
```

### Local Development Setup

For contributors working on this repository, tests should be run before committing changes:

```bash
# 1. Set up test environment (one-time setup)
./run_tests.sh --setup

# 2. Run tests before committing
./run_tests.sh

# 3. Alternatively, run specific test scenarios
./run_tests.sh baseline
./run_tests.sh changed
./run_tests.sh mixed
```

**Automatic Pre-commit Testing**: A pre-commit hook is installed that automatically runs tests before each commit. This ensures code quality and prevents broken changes from being committed.

## Workflow Overview

### 1. Visual Diff and PR Report (Production Use)

**Trigger**: Via `workflow_call` from external repositories

**Process**:
1. Checks for existing test images in configurable directory (default: `outputs/`)  
2. Compares each output against its golden master using NVIDIA flip
3. Generates visual diff images in `diffs/` directory  
4. Commits images temporarily to a unique branch for direct display
5. Posts comprehensive comparison report as PR comment with embedded images
6. Uploads complete artifact package as backup

**Important**: This workflow is designed for production use by external CI systems. It expects test images to already exist and only performs visual comparison. It does not generate test images.

**Usage in external repositories**:
```yaml
jobs:
  your-app-build:
    runs-on: ubuntu-latest
    steps:
      # Your application CI steps
      - name: Generate screenshots
        run: your-app screenshot --output outputs/
      
  visual-diff:
    needs: your-app-build
    uses: mpiispanen/image-comparison-and-update/.github/workflows/visual-diff.yml@main
    with:
      outputs_directory: outputs  # Optional: defaults to 'outputs'
```

### 2. Test Visual Diff System (Automated Testing)

**Trigger**: Automatically on pull requests and pushes to main, also manual workflow dispatch

**Process**:
1. Generates test images using different scenarios (baseline, changed, mixed)
2. Tests the visual diff system itself with these known test cases
3. Validates that the visual diff system correctly detects differences and matches
4. Provides automated validation that the visual diff system is working correctly

**Purpose**: This workflow tests the visual diff system itself to ensure it's working correctly. It runs automatically to catch any regressions in the visual diff functionality.

### 3. Post-Commit Visual Regression

**Trigger**: Automatically on push to main/develop branches when images are present, or manually via workflow dispatch

**Process**:
1. Checks for test images in the `outputs/` directory
2. If images are found, automatically runs visual regression testing
3. Uses the main visual-diff workflow to perform comparisons
4. Provides detailed logging and summary of results
5. Skips gracefully when no images are present (normal for code-only commits)

**Features**:
- **Automatic Detection**: Only runs when visual changes are present
- **Smart Skipping**: Skips execution for commits without visual outputs
- **Force Run**: Manual option to run even without images (generates test images)
- **Continuous Monitoring**: Provides ongoing visual regression monitoring for main branches
- **Detailed Logging**: Comprehensive reporting of post-commit visual validation

**Usage**:
- **Automatic**: Runs automatically when you push commits containing images to `outputs/`
- **Manual**: Go to Actions → Post-Commit Visual Regression → Run workflow
- **Force Mode**: Enable "force_run" to test the system even without existing images

### 4. Accept New Golden Image

**Trigger**: Comment `/accept-image <filename>` on PR

**Process**:
1. Validates commenter has write permissions
2. Downloads artifacts from visual diff workflow
3. Moves accepted image to `golden/` directory
4. Commits and pushes using Git LFS
5. Confirms acceptance via PR comment
4. Commits and pushes using Git LFS
5. Confirms acceptance via PR comment

## Usage

### Test Scenarios

The test-visual-diff workflow supports different test scenarios to help verify both passing and failing cases:

**Available scenarios** (for testing the visual diff system):
- `baseline`: Generates consistent images that match golden masters (all tests pass)
- `changed`: Generates modified images that differ from golden masters (all tests fail)  
- `mixed`: Generates a mix where some images pass and some fail

**Running scenarios for testing**:

1. **Via GitHub Actions UI** (manual testing):
   - Go to Actions → Test Visual Diff System → Run workflow
   - Select the desired test scenario from the dropdown
   - Click "Run workflow"

2. **Via local testing**:
   ```bash
   # Run specific scenario
   python test_scenarios.py baseline
   python test_scenarios.py changed
   python test_scenarios.py mixed
   
   # Run all scenarios
   python test_scenarios.py
   ```

3. **Via environment variable**:
   ```bash
   TEST_SCENARIO=changed python generate_test_images.py
   ```

### Running Tests

**Production Integration**: The visual diff workflow expects your application's CI pipeline to generate test images in the `outputs/` directory. The workflow only performs visual comparison and does not generate test images.

**Automated Testing**: The visual diff system itself is automatically tested on every pull request and push to main using the `test-visual-diff` workflow. This ensures the visual diff functionality is working correctly.

**Manual Testing**: You can also manually test the visual diff system using workflow dispatch:

1. **Via GitHub Actions UI**:
   - Go to Actions → Test Visual Diff System → Run workflow
   - Select the desired test scenario from the dropdown (baseline, changed, mixed, or all)
   - Click "Run workflow"

2. **Via local testing**:
   ```bash
   # Run specific scenario
   python test_scenarios.py baseline
   python test_scenarios.py changed  
   python test_scenarios.py mixed
   
   # Run all scenarios
   python test_scenarios.py
   ```

**Integration with Your Application**:
Your application's CI should populate the outputs directory with screenshots, renders, or other visual outputs that need to be tested. The directory is configurable (defaults to `outputs/`). For example:

```python
# Your application's CI script
def run_your_tests():
    # Generate screenshots, renders, etc.
    save_image("outputs/ui-component.png", your_image_data)
    save_image("outputs/dashboard-view.png", dashboard_screenshot)
```

**External Repository Integration**:
```yaml
# In your external repository's .github/workflows/ci.yml
name: CI with Visual Testing

on: [pull_request, push]

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      # Your build steps...
      
      - name: Generate test images
        run: |
          mkdir -p outputs
          your-app screenshot --output outputs/
          
  # For Pull Requests: Run visual regression and comment on PR
  visual-regression-pr:
    needs: build-and-test
    if: github.event_name == 'pull_request'
    uses: mpiispanen/image-comparison-and-update/.github/workflows/visual-diff.yml@main
    with:
      outputs_directory: outputs
      pr_number: ${{ github.event.pull_request.number }}
    permissions:
      contents: write
      issues: write
      pull-requests: write

  # For Push to main: Run post-commit visual regression monitoring
  visual-regression-post-commit:
    needs: build-and-test
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    uses: mpiispanen/image-comparison-and-update/.github/workflows/post_commit_visual_regression.yml@main
    permissions:
      contents: write
      issues: write
      pull-requests: write
```

**Post-Commit Monitoring**: The post-commit workflow provides continuous monitoring of visual changes on your main branch. It automatically detects when commits contain visual outputs and runs regression testing, helping catch visual issues that may have been missed during PR review.

### Comment Behavior

The workflow now creates **new comments** for each run instead of updating existing ones. Old bot comments are automatically cleaned up to prevent confusion. This ensures:

- Each test run gets a fresh, timestamped comment
- No confusion from outdated results
- Clear history of test runs in the PR

### Accepting Changes

When the workflow detects visual changes, comment on the PR:

```
/accept-image ui-main-screen.png
```

This will:
- Move the new image to `golden/ui-main-screen.png`
- Commit it with Git LFS
- Update the PR automatically

### Directory Structure

```
├── .gitattributes          # Git LFS configuration
├── .github/workflows/
│   ├── visual-diff.yml     # Production visual comparison workflow
│   ├── test-visual-diff.yml # Automated testing of visual diff system
│   └── accept-image.yml    # Image acceptance workflow
├── generate_test_images.py # Test image generation script
├── test_scenarios.py       # Test scenario runner
├── outputs/                # Generated test images (temporary)
├── diffs/                  # Visual diff images (temporary)
└── golden/                 # Reference images (LFS tracked)
```

## Security

- Only users with write permissions can accept images
- All operations are logged and attributed
- Git LFS ensures large files don't bloat repository history

## Example Test Script

See `generate_test_images.py` for a sample implementation that creates test images with consistent, reproducible content.

## Troubleshooting

### Images Not Displaying in PR Comments

**Current Implementation**: The workflow now commits images to temporary branches to enable direct embedding in PR comments.

**Expected behavior:**
- PR comments display images directly using GitHub raw URLs
- Temporary branches are created for each test run (auto-cleaned after 7 days)
- Fallback to artifact download if branch creation fails

**If images don't display:**
1. Check if the temporary branch was created successfully in the workflow logs
2. Verify the branch name format: `visual-diff-pr-{number}-run-{id}`
3. Use the backup artifact download link provided in PR comments
4. Check repository permissions for the workflow to create branches

**Branch-based approach benefits:**
- Images display immediately in PR comments
- No authentication required for viewing
- No API rate limits
- Works consistently across public and private repositories

**Troubleshooting branch creation:**
- Ensure workflow has `contents: write` permission
- Check for branch protection rules that might block temporary branches  
- Verify git configuration in workflow steps

### No Comment Posted

**If no PR comment appears after running visual diff:**
1. Check the workflow logs for any step failures
2. Verify the workflow completed successfully
3. Look for the "Comment PR with results" or "Comment PR with success" steps
4. For private repositories, ensure the workflow has proper permissions

### Download Artifacts

**To download artifacts manually:**
1. Go to the Actions tab in your repository
2. Find the workflow run for your PR
3. Scroll to the "Artifacts" section at the bottom
4. Click the artifact name to download the ZIP file

### Permission Denied on Accept

Ensure the user commenting has write access to the repository.

**Error message:** "does not have write permissions to accept images"
- Only repository collaborators with write or admin access can accept images
- Check repository settings → Manage access

### No Test Images Found

**Error message:** "No test images found in outputs/ directory"

**Cause**: The visual diff workflow expects test images to already exist in the `outputs/` directory, generated by your application's CI pipeline.

**Solutions**:
1. **For production use**: Ensure your application's CI pipeline generates images in the `outputs/` directory before the visual diff workflow runs
2. **For testing**: Use the manual workflow dispatch "Generate Test Images" option to create test images
3. **Local testing**: Run `python generate_test_images.py` to create sample images locally

### Workflow Not Triggering

Check that:
- Your application's CI pipeline has generated test images in the `outputs/` directory
- The test images are accessible when the visual diff workflow runs
- The images are in PNG format and properly named

### Git LFS Issues

**Large repository size:**
- Ensure `.gitattributes` is configured correctly
- Verify LFS is tracking image files: `git lfs ls-files`
- Clean up old LFS objects: `git lfs prune`

**LFS file not found:**
- Run `git lfs pull` to download LFS files
- Check LFS quota in repository settings

### Debug Steps

1. **Check workflow logs** for detailed error messages
2. **Download artifacts** manually to verify image generation
3. **Test locally** by running `generate_test_images.py`
4. **Verify permissions** using repository settings
5. **Check branch protection** rules that might block automated commits
