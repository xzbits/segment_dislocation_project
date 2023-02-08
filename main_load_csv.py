from ovito_extract_raw_segments import DumpDirectory


if __name__ == "__main__":
    # Load wrapped segments to CSV files
    dumpfile_path = r""
    save_path = r""
    dumpfile_prefix = ""
    etl_object = DumpDirectory(dumpfile_path, save_path, dumpfile_prefix)
