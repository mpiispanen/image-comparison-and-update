# Visual Regression Testing with Git LFS

A robust, LFS-aware GitHub Actions workflow system for visual regression testing. This system handles multiple output images, uses NVIDIA's flip for high-fidelity comparison, and correctly stores final "golden" images using Git LFS to avoid bloating the main repository.

## Features

- **LFS-Aware Storage**: Automatically handles large image files using Git LFS
- **High-Fidelity Comparison**: Uses NVIDIA flip for precise image comparison
- **Interactive Workflow**: Accept/reject changes via PR comments
- **Consolidated Reporting**: Single PR comment with all visual changes
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
4. Posts consolidated report as PR comment
5. Uploads artifacts for the acceptance workflow

**Example Output**:
```
🔄 **Changed Image:** `ui-main-screen.png`

| Difference | New Output |
|------------|------------|
| ![Difference](./diffs/diff_ui-main-screen.png) | ![New Output](./outputs/ui-main-screen.png) |

To accept this change, comment: `/accept-image ui-main-screen.png`
```

### 2. Accept New Golden Image

**Trigger**: Comment `/accept-image <filename>` on PR

**Process**:
1. Validates commenter has write permissions
2. Downloads artifacts from visual diff workflow
3. Moves accepted image to `golden/` directory
4. Commits and pushes using Git LFS
5. Confirms acceptance via PR comment

## Usage

### Running Tests

The workflow automatically runs `generate_test_images.py` to create test outputs. Customize this script for your application:

```python
# Your test suite should populate outputs/ directory
def run_your_tests():
    # Generate screenshots, renders, etc.
    save_image("outputs/ui-component.png", your_image_data)
```

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

### Images Not Loading in PR Comments

GitHub may need time to process LFS files. Wait a moment and refresh the PR.

### Permission Denied on Accept

Ensure the user commenting has write access to the repository.

### Workflow Not Triggering

Check that:
- The PR has changes that would generate new output images
- The `generate_test_images.py` script runs successfully
- Artifacts are being uploaded correctly
