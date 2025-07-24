# Artifact Download Feature for Visual Diff Workflow

This document demonstrates how to use the new artifact download feature in the visual-diff workflow.

## Use Case

This feature enables workflows where images are generated on specialized hardware (e.g., GPU instances) and then compared on standard runners.

## Example Usage

### Full Workflow Example

```yaml
name: Visual Regression Testing with GPU Generation

jobs:
  generate-images:
    runs-on: [self-hosted, gpu]  # Specialized hardware
    steps:
      - name: Generate images
        run: ./generate_test_images.sh
      
      - name: Upload images  
        uses: actions/upload-artifact@v4
        with:
          name: test-images
          path: outputs/

  visual-diff:
    needs: generate-images  
    uses: owner/image-comparison-and-update/.github/workflows/visual-diff.yml@main
    with:
      outputs_directory: 'outputs'
      artifact_name: 'test-images'
```

### New Input Parameters

- `artifact_name` (optional): Name of artifact to download containing test images
  - If provided, the workflow will download the artifact before checking for images
  - If not provided, the workflow behaves as before (backward compatible)

### Backward Compatibility

The feature is fully backward compatible. Existing workflows continue to work unchanged:

```yaml
# This continues to work exactly as before
visual-diff:
  uses: owner/image-comparison-and-update/.github/workflows/visual-diff.yml@main
  with:
    outputs_directory: 'outputs'
    # No artifact_name = traditional workflow
```

## How It Works

1. **When `artifact_name` is provided:**
   - Downloads the specified artifact using `actions/download-artifact@v4`
   - Extracts contents to the specified `outputs_directory`
   - Continues with normal visual diff processing

2. **When `artifact_name` is not provided:**
   - Skips the download step entirely
   - Proceeds directly to check for existing images
   - Maintains 100% backward compatibility

## Implementation Details

The feature adds:
- New optional `artifact_name` input parameter
- Conditional download step that only runs when `artifact_name != ''`
- Uses `actions/download-artifact@v4` for reliable artifact handling
- Extracts to the user-specified `outputs_directory`

The conditional logic ensures zero impact on existing users while enabling the new use case.