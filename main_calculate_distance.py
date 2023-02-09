from transform_raw_segment import process_sfw_data, process_average_sfw_data

if __name__ == "__main__":
    # After loading all wrapped segment data to CSV file
    csv_path = r"C:\Users\Hoa\Desktop\cur_work\1200_data\phong_wrapped\extracted_data\t_1000"
    csv_file_prefix = "segment_points_raw_frame_"
    SFW_csv_prefix = "sfw_frame_"

    sfw_avg_filename = "sfw_average.csv"

    process_sfw_data(csv_path, csv_file_prefix, SFW_csv_prefix)
    process_average_sfw_data(csv_path, SFW_csv_prefix, sfw_avg_filename)
