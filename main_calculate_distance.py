from transform_raw_segment import process_data

if __name__ == "__main__":
    # After loading all wrapped segment data to CSV file
    csv_path = r"~\extracted_data\t_1000"
    csv_file_prefix = ""
    SFW_csv_prefix = "sfw_frame_"
    process_data(csv_path, csv_file_prefix, SFW_csv_prefix)
