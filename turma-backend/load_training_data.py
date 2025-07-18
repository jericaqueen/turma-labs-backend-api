import pandas as pd
import json
import os

def load_training_materials_from_excel(excel_file_path):
    """
    Load training materials from Excel file and return as list of dictionaries
    """
    try:
        # Read the Excel file
        df = pd.read_excel(excel_file_path)
        
        # Convert DataFrame to list of dictionaries
        training_materials = []
        for _, row in df.iterrows():
            material = {
                "Tutorial Title": str(row.get('Tutorial Title', '')),
                "Article Link": str(row.get('Article Link', '')),
                "Video": str(row.get('Video', '')),
                "Categories": str(row.get('Categories', '')),
                "Tags": str(row.get('Tags', ''))
            }
            training_materials.append(material)
        
        print(f"Successfully loaded {len(training_materials)} training materials from Excel file")
        return training_materials
        
    except Exception as e:
        print(f"Error loading training materials from Excel: {str(e)}")
        return []

def save_training_materials_to_json(training_materials, json_file_path):
    """
    Save training materials to JSON file for backup
    """
    try:
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(training_materials, f, indent=2, ensure_ascii=False)
        print(f"Training materials saved to {json_file_path}")
    except Exception as e:
        print(f"Error saving training materials to JSON: {str(e)}")

if __name__ == "__main__":
    # Load from Excel
    excel_path = "/home/ubuntu/HowToLibrary.xlsx"
    training_materials = load_training_materials_from_excel(excel_path)
    
    # Save to JSON for backup
    json_path = "/home/ubuntu/turma-backend/training_materials.json"
    save_training_materials_to_json(training_materials, json_path)
    
    print(f"Total materials loaded: {len(training_materials)}")
    if training_materials:
        print("Sample material:")
        print(json.dumps(training_materials[0], indent=2))

