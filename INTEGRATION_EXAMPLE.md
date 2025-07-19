# Example Application CI Integration

This example shows how to integrate the visual diff system with your application's CI pipeline.

## Before (Old Approach)
The visual diff workflow generated its own test images, mixing testing logic with image generation.

## After (New Approach)
Your application CI generates images, and the visual diff workflow only compares them.

## Example Integration

### 1. Application CI Job (generates images)
```yaml
jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Build application
      run: |
        # Your build steps
        npm install
        npm run build
    
    - name: Run tests and generate screenshots
      run: |
        # Create outputs directory for visual diff
        mkdir -p outputs
        
        # Your application generates screenshots/images
        npm run test:visual
        # This should save images to outputs/
        
        # Example: Manual screenshot generation
        # your-app screenshot --output outputs/main-page.png
        # your-app screenshot --component button --output outputs/button.png
    
    - name: Commit outputs for visual diff
      run: |
        # Add generated images to git (temporary)
        git add outputs/
        git commit -m "Add generated test images" --allow-empty
    
    # The visual diff workflow will now run automatically on PR
    # and compare the images in outputs/ against golden masters

  # Visual diff runs automatically after this job
  # No changes needed - it will find images in outputs/
```

### 2. Local Development
```bash
# Generate images locally for testing
your-app screenshot --output outputs/main-page.png
your-app screenshot --component button --output outputs/button.png

# Test visual diff locally (if you have golden images)
flip -r golden/main-page.png -t outputs/main-page.png -d diffs
```

### 3. Manual Testing of Visual Diff System
Use the workflow dispatch to generate test images and verify the system works:

1. Go to Actions → Visual Diff and PR Report → Run workflow
2. Select test scenario (baseline/changed/mixed)
3. Run workflow
4. Download generated test images from artifacts
5. Use these to test the visual diff comparison logic

## Key Benefits

1. **Separation of Concerns**: Image generation is part of your application CI, not the testing framework
2. **Flexibility**: Your application can generate any type of visual output
3. **Reliability**: Visual diff only runs when images actually exist
4. **Testing**: Separate test image generation for validating the visual diff system