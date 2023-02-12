import os.path

from transform_raw_segment import process_sfw_data, process_average_sfw_data
import argparse

if __name__ == "__main__":
    intro_sfw_calculation = """
    Calculating SFW data from segments CSV files and load SFW data per frame into CSV data
    """

    parser_sfw_calculation = argparse.ArgumentParser(description=intro_sfw_calculation)
    parser_sfw_calculation.add_argument('-c', '--csv_file_path',
                                        required=True,
                                        metavar='',
                                        type=str,
                                        help='Path pointing to segment CSV files')

    parser_sfw_calculation.add_argument('-cp', '--csv_file_prefix',
                                        required=True,
                                        metavar='',
                                        type=str,
                                        help='Segment CSV files prefix')

    parser_sfw_calculation.add_argument('-sp', '--sfw_file_prefix',
                                        required=False,
                                        default="sfw_frame_",
                                        metavar='',
                                        type=str,
                                        help='Prefix of saved SFW CSV files. Default: sfw_frame_')

    parser_sfw_calculation.add_argument('-af', '--sfw_average_flag',
                                        required=False,
                                        default=False,
                                        metavar='',
                                        type=bool,
                                        help='Flag to calculate SFW average with 0 - False, 1 - True. Default: 0')

    parser_sfw_calculation.add_argument('-sf', '--sfw_average_filename',
                                        required=False,
                                        default="sfw_average.csv",
                                        metavar='',
                                        type=str,
                                        help='SFW average files name. Default: sfw_average.csv')

    args = parser_sfw_calculation.parse_args()
    process_sfw_data(args.csv_file_path,
                     args.csv_file_prefix,
                     args.sfw_file_prefix)
    print("Finish SFW calculation!!!!")
    print()

    if args.sfw_average_flag:
        process_average_sfw_data(args.csv_file_path,
                                 args.sfw_file_prefix,
                                 args.sfw_average_filename)

        print("Finish SFW average calculation, "
              "please refer file: %s!!!!" % os.path.join(args.csv_file_path,
                                                         args.sfw_average_filename))
