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

## How It Works

This system provides comprehensive visual regression testing through two complementary workflows that work together to catch visual issues at different stages of development:

### 🔄 Complete Workflow Flow

```
Development Process:
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Development   │    │   Pull Request   │    │   Main Branch   │
│                 │    │                  │    │                 │
│ 1. Code Changes │───▶│ 2. PR Workflow   │───▶│ 3. Post-Commit  │
│ 2. Generate     │    │    - Visual Diff │    │    - Monitoring │
│    Screenshots  │    │    - PR Comment  │    │    - Validation │
│                 │    │    - Accept/Deny │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### 1. 🔍 PR Visual Testing (Pull Request Workflow)

**When it runs**: Automatically on pull requests when visual outputs are detected

**Purpose**: Catches visual regressions before they reach the main branch

**Process**:
1. Your application CI generates screenshots/renders in `outputs/` directory
2. **Visual Diff Workflow** automatically compares outputs against golden masters
3. Creates visual diff images showing exact pixel differences
4. Posts comprehensive report as PR comment with embedded images
5. Provides `/accept-image` commands for approving legitimate changes

**Key Benefits**:
- 🛡️ **Prevention**: Stops visual regressions before merge
- 👀 **Visibility**: Clear diff images show exactly what changed
- ⚡ **Interactive**: Accept/reject changes directly in PR comments
- 📊 **Detailed**: FLIP-based comparison with precise metrics

**Example PR Integration**:
```yaml
# In your repository's .github/workflows/ci.yml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Generate screenshots
        run: your-app screenshot --output outputs/
      
  visual-testing:
    needs: build
    if: github.event_name == 'pull_request'
    uses: mpiispanen/image-comparison-and-update/.github/workflows/visual-diff.yml@main
    with:
      outputs_directory: outputs
```

### 2. 🚨 Post-Commit Monitoring (Main Branch Workflow)

**When it runs**: Automatically after commits are pushed to main/develop branches

**Purpose**: Continuous monitoring to catch issues that may have slipped through

**Process**:
1. **Smart Detection**: Automatically detects when commits contain visual outputs
2. **Conditional Execution**: Only runs when `outputs/` directory has images
3. **Validation**: Runs same visual comparison as PR workflow
4. **Enhanced Reporting**: Creates workflow summary with detailed results
5. **Graceful Skipping**: Skips cleanly for code-only commits

**Key Benefits**:
- 🔄 **Continuous**: Ongoing monitoring of main branch health
- 🎯 **Smart**: Only runs when visual changes are present
- 📈 **Comprehensive**: Detailed logging and artifact generation
- ⚙️ **Zero Config**: Works automatically without additional setup

**Automatic Execution Example**:
```bash
# Your development workflow
mkdir -p outputs
your-app generate-screenshots --output outputs/
git add outputs/ src/
git commit -m "feat: update UI components"
git push origin main
# ✅ Post-commit workflow runs automatically
```

### 3. 🎯 Image Acceptance System

**When it runs**: Via PR comments using `/accept-image` commands

**Purpose**: Allows approved changes to become new golden master references

**Process**:
1. User reviews visual diff results in PR comment
2. Comments `/accept-image filename.png` to approve changes
3. **Accept Image Workflow** validates user permissions
4. Moves accepted image to `golden/` directory with Git LFS
5. Updates PR automatically to reflect acceptance

**Security Features**:
- 🔒 **Permission Checking**: Only users with write access can accept images
- 📝 **Audit Trail**: All acceptances are logged and attributed
- 🏪 **LFS Storage**: Large images stored efficiently without bloating repository

### 4. 🧪 System Testing (Internal)

**When it runs**: Automatically on changes to the visual diff system itself

**Purpose**: Validates that the visual comparison system is working correctly

**Process**:
1. Generates known test scenarios (passing, failing, mixed results)
2. Tests the visual diff system with controlled inputs
3. Validates proper detection of differences and matches
4. Ensures system reliability and catches regressions in testing logic

## Workflow Integration Patterns

### Pattern A: Complete Integration (Recommended)
```yaml
# Full PR and post-commit coverage
name: CI with Visual Testing

on: [pull_request, push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Generate visual outputs
        run: your-app screenshot --output outputs/

  # PR Testing: Catch issues before merge  
  visual-regression-pr:
    needs: build
    if: github.event_name == 'pull_request'
    uses: mpiispanen/image-comparison-and-update/.github/workflows/visual-diff.yml@main
    
  # Post-Commit: Continuous monitoring
  visual-regression-monitoring:
    needs: build
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    uses: mpiispanen/image-comparison-and-update/.github/workflows/post_commit_visual_regression.yml@main
```

### Pattern B: PR-Only Testing
```yaml
# Only test on pull requests
visual-diff:
  if: github.event_name == 'pull_request'
  uses: mpiispanen/image-comparison-and-update/.github/workflows/visual-diff.yml@main
```

### Pattern C: Post-Commit Only
```yaml
# Only monitor main branch changes
post-commit:
  if: github.event_name == 'push' && github.ref == 'refs/heads/main'
  uses: mpiispanen/image-comparison-and-update/.github/workflows/post_commit_visual_regression.yml@main
```

## Key Differences: PR vs Post-Commit

| Aspect | PR Workflow | Post-Commit Workflow |
|--------|-------------|----------------------|
| **Timing** | Before merge | After merge |
| **Purpose** | Prevention | Detection |
| **Interaction** | Interactive (accept/reject) | Automated monitoring |
| **Reporting** | PR comments with images | Workflow summary + artifacts |
| **Failure Impact** | Blocks merge (if required) | Alerts to existing issue |
| **User Action** | Review and approve changes | Investigate and fix |

## Advanced Features

### 🎛️ Manual Testing
- **Force Run**: Test post-commit workflow even without images
- **Test Scenarios**: Generate controlled test cases for validation
- **Workflow Dispatch**: Run workflows manually for debugging

### 📊 Enhanced Reporting
- **GitHub Actions Summary**: Prominent workflow results with status indicators
- **Downloadable Artifacts**: Complete test reports for offline analysis
- **Embedded Images**: Direct image display in PR comments
- **Detailed Metrics**: FLIP-based comparison statistics

## Usage

### Quick Start Guide

#### 1. 🚀 Set Up Your Repository

**Add to your CI workflow**:
```yaml
# .github/workflows/ci.yml
name: CI with Visual Testing
on: [pull_request, push]

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build your application
        run: |
          npm install && npm run build
      
      - name: Generate visual outputs
        run: |
          mkdir -p outputs
          your-app screenshot --output outputs/
          # Example outputs:
          # outputs/homepage.png
          # outputs/dashboard.png
          # outputs/login-form.png

  # 🔍 PR Visual Testing - Catches issues before merge
  visual-diff-pr:
    needs: build-and-test
    if: github.event_name == 'pull_request'
    uses: mpiispanen/image-comparison-and-update/.github/workflows/visual-diff.yml@main
    with:
      outputs_directory: outputs
    permissions:
      contents: write
      issues: write
      pull-requests: write

  # 🚨 Post-Commit Monitoring - Continuous validation on main
  post-commit-monitoring:
    needs: build-and-test  
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    uses: mpiispanen/image-comparison-and-update/.github/workflows/post_commit_visual_regression.yml@main
    permissions:
      contents: write
      issues: write
      pull-requests: write
```

#### 2. 🎯 Working with Pull Requests

**When you create a PR with visual changes**:

1. **Automatic Detection**: The workflow automatically runs when it detects images in `outputs/`
2. **Review Results**: Check the PR comment for visual diff results:
   ```
   ## 🔍 Visual Regression Test Results
   
   ### 📊 Summary
   - ✅ 2 images passed (no changes)
   - ⚠️ 1 image changed: homepage.png
   
   ### 🖼️ Changed Images
   
   #### homepage.png
   [Visual diff image showing changes]
   
   **FLIP Score**: 0.23 (changes detected)
   
   ### 🔧 Accept New Images
   Copy and paste to accept changes:
   ```
   /accept-image homepage.png
   ```
   ```

3. **Accept Changes**: If the visual changes are intentional, use the provided command:
   ```
   /accept-image homepage.png
   ```

4. **Automatic Update**: The accepted image becomes the new golden master

#### 3. 🔄 Post-Commit Monitoring

**After merging to main**:

1. **Automatic Execution**: Workflow runs automatically when commits contain visual outputs
2. **Smart Detection**: Skips when no images are present (normal for code-only commits)
3. **Results Access**: Check workflow summary or download artifacts for detailed results

**Manual Testing**:
```bash
# Go to Actions → Post-Commit Visual Regression → Run workflow
# Options:
# - Branch: main (or target branch)
# - Force run: true (generates test images for testing)
```

### Common Scenarios

#### Scenario A: New Feature with UI Changes
```bash
# 1. Develop feature with visual changes
git checkout -b feature/new-dashboard
# ... make code changes ...

# 2. Generate screenshots in CI
mkdir -p outputs
your-app screenshot --page dashboard --output outputs/dashboard.png

# 3. Create PR
git add . && git commit -m "feat: new dashboard layout"
git push origin feature/new-dashboard
# → Creates PR, visual diff workflow runs automatically

# 4. Review visual changes in PR comment
# 5. Accept changes if intentional: /accept-image dashboard.png
# 6. Merge PR
# → Post-commit workflow validates on main branch
```

#### Scenario B: Bug Fix (No Visual Changes Expected)
```bash
# 1. Fix bug
git checkout -b fix/calculation-error
# ... fix code without UI changes ...

# 2. Create PR (no visual outputs generated)
git add . && git commit -m "fix: calculation error"
git push origin fix/calculation-error
# → Visual diff workflow skips (no images to test)

# 3. Merge PR
# → Post-commit workflow also skips (no visual changes)
```

#### Scenario C: Investigating Regression on Main
```bash
# Post-commit workflow detected regression
# 1. Check workflow artifacts for visual differences
# 2. Compare current vs expected images
# 3. Create hotfix if needed
git checkout -b hotfix/visual-regression
# ... fix visual issue ...
# → Follow Scenario A process
```

### Advanced Usage

#### 🧪 Testing the Visual Diff System

**Test Scenarios Available**:
- `baseline`: Generates images that match golden masters (all tests pass)
- `changed`: Generates modified images that differ from golden masters (all tests fail)  
- `mixed`: Generates a mix where some images pass and some fail

**Running Test Scenarios**:

1. **Via GitHub Actions UI**:
   - Go to Actions → Test Visual Diff System → Run workflow
   - Select desired test scenario from dropdown
   - Click "Run workflow"

2. **Via Local Testing**:
   ```bash
   # Run specific scenario
   python test_scenarios.py baseline
   python test_scenarios.py changed
   python test_scenarios.py mixed
   
   # Run all scenarios
   python test_scenarios.py
   ```

3. **Force Run Post-Commit Testing**:
   - Go to Actions → Post-Commit Visual Regression → Run workflow
   - Enable "Force run" to test without existing images
   - Select target branch

#### 🔧 Manual Image Generation

**For Local Development**:
```bash
# Generate test images locally
mkdir -p outputs
your-app screenshot --page homepage --output outputs/homepage.png
your-app screenshot --component button --output outputs/button.png

# Test comparison locally (requires FLIP)
pip install flip-evaluator
flip -r golden/homepage.png -t outputs/homepage.png -d diffs/
```

**Integration in Your Application**:
```python
# Example: Selenium screenshot generation
def generate_test_screenshots():
    driver = webdriver.Chrome()
    
    # Homepage screenshot
    driver.get("http://localhost:3000")
    driver.save_screenshot("outputs/homepage.png")
    
    # Component screenshots  
    driver.get("http://localhost:3000/components")
    button = driver.find_element(By.CLASS_NAME, "primary-button")
    button.screenshot("outputs/button.png")
    
    driver.quit()
```

#### 📊 Understanding Results

**FLIP Comparison Metrics**:
- **Score < 0.1**: Likely no visible difference
- **Score 0.1-0.3**: Minor differences, may be acceptable
- **Score > 0.3**: Significant visual changes

**Artifact Contents**:
- `outputs/`: Your generated test images
- `diffs/`: Visual difference images (red highlights show changes)
- `golden/`: Reference images for comparison
- `summary.md`: Detailed test results and statistics

#### 🔍 Debugging Common Issues

**Workflow Not Running**:
```bash
# Check trigger conditions
git log --oneline -5  # Verify recent commits
ls -la outputs/       # Verify images exist
git status            # Check working directory
```

**Images Not Matching**:
```bash
# Download artifacts and compare manually
# Check image dimensions and format
file outputs/*.png golden/*.png

# Verify image content
flip -r golden/image.png -t outputs/image.png -d debug/
```

**Permission Issues**:
```yaml
# Ensure workflows have proper permissions
permissions:
  contents: write      # For committing golden images
  issues: write        # For creating issues (if enabled)
  pull-requests: write # For PR comments
  actions: read        # For artifact access
```

### 🎯 Accepting Visual Changes

#### When Changes Are Detected

When the PR workflow detects visual differences, you'll see a comment like:
```markdown
## 🔍 Visual Regression Test Results

### 📊 Summary
- ⚠️ 1 image changed: homepage.png
- FLIP Score: 0.25 (visual changes detected)

### 🖼️ Changed Images

#### homepage.png
[Embedded visual diff image showing before/after]

### 🔧 Accept New Images
Copy and paste to accept changes:
```
/accept-image homepage.png
```
```

#### Accepting Changes

1. **Review the visual diff** to ensure changes are intentional
2. **Copy the accept command** from the PR comment
3. **Paste as a new comment** on the PR:
   ```
   /accept-image homepage.png
   ```
4. **Automatic processing**: The system will:
   - Validate you have write permissions to the repository
   - Download the new image from workflow artifacts
   - Move it to `golden/homepage.png` (replacing the old reference)
   - Commit the change using Git LFS
   - Post confirmation comment on the PR

#### Comment Behavior

- **Fresh Comments**: Each workflow run creates a new comment with latest results
- **Clean History**: Old bot comments are automatically cleaned up
- **Timestamped**: Each comment shows when the test was run
- **Clear Status**: Easy to see current state vs historical runs

#### Security Features

- **Permission Validation**: Only users with write access can accept images
- **Audit Trail**: All acceptances are logged with user attribution
- **Safe Storage**: Accepted images are stored with Git LFS to avoid repository bloat

## Repository Structure

```
├── .gitattributes              # Git LFS configuration for image files
├── .github/workflows/
│   ├── visual-diff.yml         # 🔍 Main visual comparison workflow (PR testing)
│   ├── post_commit_visual_regression.yml  # 🚨 Post-commit monitoring workflow
│   ├── test-visual-diff.yml    # 🧪 System testing workflow
│   └── accept-image.yml        # 🎯 Image acceptance workflow
├── generate_test_images.py     # Test image generation script
├── test_scenarios.py           # Test scenario runner for validation
├── outputs/                    # 📁 Generated test images (temporary)
├── diffs/                      # 📁 Visual diff images (temporary)
├── golden/                     # 📁 Reference "golden master" images (LFS tracked)
├── README.md                   # 📖 Complete documentation (this file)
├── POST_COMMIT_USAGE.md        # 📋 Post-commit workflow examples
└── INTEGRATION_EXAMPLE.md      # 🔗 CI integration examples
```

### Key Directories

- **`outputs/`**: Where your application generates test images for comparison
- **`golden/`**: Reference images that represent the "correct" visual state (Git LFS tracked)
- **`diffs/`**: Generated visual difference images showing pixel-level changes
- **`.github/workflows/`**: The workflow files that power the visual regression system

## Security

- **Permission-Based Access**: Only users with write permissions can accept images
- **Automated Validation**: All operations are logged and attributed to users
- **LFS Storage**: Large image files stored efficiently without bloating repository history
- **Secure Workflows**: Workflows operate with minimal required permissions

## Example Test Script

See `generate_test_images.py` for a sample implementation that creates test images with consistent, reproducible content suitable for visual regression testing.

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
