import patoolib

def extract_7z(archive_path, extract_path):
    try:
        patoolib.extract_archive(archive_path, outdir=extract_path)

        print(f"Successfully extracted {archive_path} to {extract_path}")
    except Exception as e:
        print(f"An error occurred: {e}")
