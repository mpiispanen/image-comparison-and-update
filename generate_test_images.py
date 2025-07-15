#!/usr/bin/env python3
"""
Sample test script that generates test images for visual regression testing.
This script creates simple test images that can be used to demonstrate
the visual diff workflow.
"""

import os
from PIL import Image, ImageDraw, ImageFont
import random

def create_test_image(filename, text, width=400, height=300, color_scheme=None):
    """Create a simple test image with text and shapes."""
    
    # Create image with background color
    if color_scheme is None:
        bg_color = (255, 255, 255)  # White background
        text_color = (0, 0, 0)      # Black text
        shape_color = (100, 150, 200)  # Blue shapes
    else:
        bg_color, text_color, shape_color = color_scheme
    
    image = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(image)
    
    # Draw some simple shapes
    draw.rectangle([50, 50, width-50, height-50], outline=shape_color, width=3)
    draw.ellipse([100, 100, width-100, height-100], outline=shape_color, width=2)
    
    # Add text
    try:
        # Try to use a default font
        font = ImageFont.load_default()
    except:
        font = None
    
    # Calculate text position (center)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    draw.text((x, y), text, fill=text_color, font=font)
    
    # Add some random elements to make changes more visible
    for i in range(5):
        x1, y1 = random.randint(0, width), random.randint(0, height)
        x2, y2 = x1 + random.randint(10, 50), y1 + random.randint(10, 50)
        draw.rectangle([x1, y1, x2, y2], fill=shape_color)
    
    return image

def main():
    """Generate sample test images."""
    
    # Ensure outputs directory exists
    os.makedirs('outputs', exist_ok=True)
    
    # Check if we should generate test scenario with changes
    test_scenario = os.environ.get('TEST_SCENARIO', 'baseline')
    print(f"Generating images for scenario: {test_scenario}")
    
    # Set seed for reproducible random elements - different seeds for different scenarios
    if test_scenario == 'changed':
        random.seed(123)  # Different seed to create changes
        print("Using changed seed to create visual differences")
    else:
        random.seed(42)   # Original baseline seed
        print("Using baseline seed for consistent images")
    
    # Generate test images
    test_cases = [
        {
            'filename': 'ui-main-screen.png',
            'text': 'Main Screen UI',
            'color_scheme': ((255, 255, 255), (0, 0, 0), (100, 150, 200))
        },
        {
            'filename': 'ui-settings-dialog.png', 
            'text': 'Settings Dialog',
            'color_scheme': ((240, 240, 240), (50, 50, 50), (200, 100, 100))
        },
        {
            'filename': 'ui-dashboard.png',
            'text': 'Dashboard View',
            'color_scheme': ((250, 250, 250), (30, 30, 30), (150, 200, 100))
        }
    ]
    
    # Modify test cases based on scenario
    if test_scenario == 'changed':
        # Modify all test cases to create detectable differences
        test_cases[0]['text'] = 'Main Screen UI - UPDATED'  # Text change
        test_cases[0]['color_scheme'] = ((255, 255, 255), (0, 0, 0), (150, 100, 200))  # Color change
        test_cases[1]['color_scheme'] = ((220, 220, 220), (50, 50, 50), (200, 150, 100))  # Background change
        test_cases[2]['text'] = 'Dashboard View - MODIFIED'  # Text change for third image
        test_cases[2]['color_scheme'] = ((240, 240, 240), (40, 40, 40), (100, 150, 200))  # Color change for third image
        print("Applied changes to create visual differences")
    elif test_scenario == 'mixed':
        # Mix of changed and unchanged - only modify the first image
        test_cases[0]['text'] = 'Main Screen UI - CHANGED'
        test_cases[0]['color_scheme'] = ((255, 255, 255), (0, 0, 0), (200, 100, 150))
        print("Applied mixed changes - some images will pass, some will fail")
    
    for test_case in test_cases:
        print(f"Generating {test_case['filename']}...")
        image = create_test_image(
            test_case['filename'],
            test_case['text'],
            color_scheme=test_case['color_scheme']
        )
        
        output_path = os.path.join('outputs', test_case['filename'])
        image.save(output_path)
        print(f"Saved {output_path}")
    
    print(f"Test image generation completed for scenario: {test_scenario}!")

if __name__ == "__main__":
    main()