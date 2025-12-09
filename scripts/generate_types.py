import os
import subprocess
import sys

def main():
    """
    Generate TypeScript interfaces from Pydantic models using datamodel-code-generator.
    """
    try:
        # Check if datamodel-code-generator is installed
        subprocess.run(["datamodel-code-generator", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("datamodel-code-generator not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "datamodel-code-generator"])

    # Define paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_dir = os.path.join(base_dir, "src", "models")
    output_file = os.path.join(base_dir, "frontend", "src", "types", "schema.ts")

    # Run generator
    # We explicitly target the models directory to avoid crawling everything
    cmd = [
        "datamodel-code-generator",
        "--input", input_dir,
        "--output", output_file,
        "--output-model-type", "typescript",
        "--input-file-type", "auto",
        "--use-annotated",
        "--strict-nullable",
        "--enum-field-as-literal", "all" # Better for TS unions
    ]

    print(f"Generating types from {input_dir} to {output_file}...")
    try:
        subprocess.run(cmd, check=True)
        print("✅ TypeScript generation successful!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Type generation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
