import os
import requests
import tarfile
import subprocess
import shutil
from processor import run_analysis_pipeline


def download_dataset(url, extract_path):
    """Downloads and extracts the dataset if not present."""
    archive_name = "data.tar"

    print(f"Step 0: Data Acquisition")
    print(f"Downloading 63.2 MB dataset from GitHub Releases...")

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Check for 404/500 errors

        with open(archive_name, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"Extracting files to {extract_path}...")
        with tarfile.open(archive_name, "r:gz") as tar:
            tar.extractall(path=extract_path)

        os.remove(archive_name)  # Clean up the .tar.gz
        print("Data successfully prepared.\n")

    except Exception as e:
        print(f"Critical Error during download: {e}")
        return False
    return True

def main():
    print("Starting Foci Analysis Pipeline")

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # The Direct Download URL from your GitHub Release
    DATA_URL = "https://github.com/Duelly-Baxter/automated-foci-analysis/releases/download/data/data.tar"

    # Check/Download Data
    if not os.path.exists(input_folder) or not os.listdir(input_folder):
        print(f"Data folder not found or empty.")
        success = download_dataset(DATA_URL, BASE_DIR)
        if not success:
            return
    else:
        print("Check: Data folder found. Skipping download.\n")

    # Run the Python Processor
    # Looking for 'data' in the project root
    input_folder = os.path.join(BASE_DIR, '..', 'data')
    # Saving CSV to the 'results' folder
    output_csv = os.path.join(BASE_DIR, '..', 'results', 'foci_counts.csv')

    if not os.path.exists(input_folder):
        print(f"Error: Folder '{input_folder}' not found!")
        return

    print(f"\n[1/2] Processing images in '{input_folder}'...")
    df_results = run_analysis_pipeline(input_folder, output_csv)
    print(f"Success: {len(df_results)} images processed.")

    # Run the R Statistical Validation
    print("\n[2/2] Running R Statistical Validation...")
    try:
        r_cmd = "Rscript"

        if not shutil.which(r_cmd):
            # This is local fallback; Binder will ignore this
            r_cmd = r"C:\Program Files\R\R-4.4.1\bin\Rscript.exe"

        # Point directly to analysis.R in the scripts folder
        r_script_path = os.path.join(BASE_DIR, "analysis.R")

        subprocess.run([r_cmd, r_script_path], check=True)
        print("Success: Validation plot generated in 'results' folder.")

    except Exception as e:
        print(f"R Analysis failed. Error: {e}")


if __name__ == "__main__":
    main()