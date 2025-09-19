#!/usr/bin/env python3
"""
Test script to demonstrate hierarchical prompt template functionality.
"""

def test_prompt_formatting():
    """Test how hierarchical class names are formatted with prompt templates."""
    
    # Example hierarchical class names (major;minor;specific)
    test_classes = [
        "vehicle;car;sedan",
        "vehicle;truck;pickup",
        "building;residential;house",
        "building;commercial;office",
        "vegetation;tree;oak",
        "vegetation;grass;lawn",
        "person",  # non-hierarchical example
    ]
    
    # Example prompt templates
    prompt_templates = [
        "a photo of {class}",
        "aerial view of {class}",
        "satellite image showing {class}",
        "overhead photograph of {class}",
    ]
    
    print("🧪 Testing Hierarchical Prompt Template Formatting\n")
    
    for template in prompt_templates:
        print(f"📝 Template: '{template}'")
        print("-" * 50)
        
        for class_name in test_classes:
            if '{class}' in template:
                if ';' in class_name:
                    # Convert semicolons to commas for better readability
                    formatted_class = class_name.replace(';', ', ')
                    result = template.replace('{class}', formatted_class)
                else:
                    result = template.replace('{class}', class_name)
            else:
                result = f"{template} {class_name}"
            
            print(f"  {class_name:25} → {result}")
        print()


def demonstrate_clip_benefits():
    """Explain how prompt templates help CLIP understand hierarchical classes."""
    
    print("🎯 Benefits of Prompt Templates for Hierarchical Classes\n")
    
    examples = [
        {
            "raw": "vehicle;car;sedan",
            "without_template": "vehicle;car;sedan",
            "with_template": "aerial view of vehicle, car, sedan",
            "benefit": "Provides spatial context and natural language structure"
        },
        {
            "raw": "building;residential;house",
            "without_template": "building;residential;house", 
            "with_template": "satellite image showing building, residential, house",
            "benefit": "Clarifies viewing perspective and object hierarchy"
        },
        {
            "raw": "vegetation;tree;oak",
            "without_template": "vegetation;tree;oak",
            "with_template": "overhead photograph of vegetation, tree, oak",
            "benefit": "Natural language helps CLIP understand relationships"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"Example {i}:")
        print(f"  Raw class name:    {example['raw']}")
        print(f"  Without template:  {example['without_template']}")
        print(f"  With template:     {example['with_template']}")
        print(f"  Benefit:          {example['benefit']}")
        print()


if __name__ == "__main__":
    test_prompt_formatting()
    demonstrate_clip_benefits()
    
    print("✅ To use hierarchical prompts with yoclip:")
    print("   yoclip yolotoclip /path/to/dataset output.csv --prompt-template 'aerial view of {class}'")
    print("   yoclip yolotoclip /path/to/dataset output.csv --prompt-template 'satellite image showing {class}'")
