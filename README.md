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

## Workflow Overview

### 1. Visual Diff and PR Report

**Trigger**: On every pull request

**Process**:
1. Runs your test suite to generate output images in `outputs/` directory
2. Compares each output against its golden master using NVIDIA flip
3. Generates visual diff images in `diffs/` directory  
4. Commits images temporarily to a unique branch for direct display
5. Posts comprehensive comparison report as PR comment with embedded images
6. Uploads complete artifact package as backup

**Image Display**:
Images are now directly embedded in PR comments using temporary GitHub branches:

```markdown
## 🖼️ Visual Comparison Results

### Changed Images

#### ui-main-screen.png

**Golden Master (Expected):**
![Golden Master](https://raw.githubusercontent.com/owner/repo/visual-diff-pr-123-run-456/golden/ui-main-screen.png)

**New Output (Actual):**
![New Output](https://raw.githubusercontent.com/owner/repo/visual-diff-pr-123-run-456/outputs/ui-main-screen.png)

**Visual Difference (Highlighted Changes):**
![Difference](https://raw.githubusercontent.com/owner/repo/visual-diff-pr-123-run-456/diffs/diff_ui-main-screen.png)

### 📦 Backup Download
If images don't load above, download the complete results: [Visual Test Results](https://github.com/owner/repo/actions/runs/456)

> 🧹 The temporary branch `visual-diff-pr-123-run-456` will be automatically cleaned up after 7 days.
```

**Temporary Branch Cleanup**:
- Creates unique branches like `visual-diff-pr-{number}-run-{id}` for each test run
- Branches are automatically cleaned up after 7 days
- Images are immediately accessible via GitHub raw URLs
- No API rate limits or authentication issues

**Fallback to Artifacts**:
If branch creation fails, the workflow falls back to the previous artifact-based approach.

### 2. Accept New Golden Image

**Trigger**: Comment `/accept-image <filename>` on PR

**Process**:
1. Validates commenter has write permissions
2. Downloads artifacts from visual diff workflow
3. Moves accepted image to `golden/` directory
4. Commits and pushes using Git LFS
5. Confirms acceptance via PR comment

## Usage

### Test Scenarios

The workflow supports different test scenarios to help verify both passing and failing cases:

**Available scenarios:**
- `baseline`: Generates consistent images that match golden masters (all tests pass)
- `changed`: Generates modified images that differ from golden masters (all tests fail)  
- `mixed`: Generates a mix where some images pass and some fail

**Running scenarios:**

1. **Via GitHub Actions UI** (recommended):
   - Go to Actions → Visual Diff and PR Report → Run workflow
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

The workflow automatically runs `generate_test_images.py` to create test outputs. Customize this script for your application:

```python
# Your test suite should populate outputs/ directory
def run_your_tests():
    # Generate screenshots, renders, etc.
    save_image("outputs/ui-component.png", your_image_data)
```

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
│   ├── visual-diff.yml     # Main comparison workflow
│   └── accept-image.yml    # Image acceptance workflow
├── generate_test_images.py # Sample test script
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

### Workflow Not Triggering

Check that:
- The PR has changes that would generate new output images
- The `generate_test_images.py` script runs successfully
- Artifacts are being uploaded correctly

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
