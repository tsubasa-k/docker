import os

# Specify the list of folders containing Readme.txt files
folders = ["data_aug", "evasion_atk", "feature_col", "hidden_backdoor", "model_similarity"]

# Specify the output file to save the merged content
output_file = "Readme.txt"

# Open the output file in append mode, create it if it doesn't exist
with open(output_file, "a") as merged_file:
    for folder in folders:
        # Build the full path to the Readme.txt file in each folder
        readme_path = os.path.join(folder, "Readme.txt")

        # Check if the file exists
        if os.path.isfile(readme_path):
            print(f"File found: {readme_path}")
            # Open the Readme.txt file and append its content to the output file
            with open(readme_path, "r") as source_file:
                merged_file.write(f"=== Contents of {readme_path} ===\n")
                merged_file.write(source_file.read())
                merged_file.write("\n\n")
               
            # Delete the original file after merging
            os.remove(readme_path)
        else:
            print(f"File not found: {readme_path}")

print(f"Merged Readme files into {output_file} and deleted the original files")


