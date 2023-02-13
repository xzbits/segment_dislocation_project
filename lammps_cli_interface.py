from ovito_extract_raw_segments import DumpDirectory
import argparse


if __name__ == "__main__":
    intro_lammmps_extract = """
    Extracting segments data from LAMMPS dump files and load all segment data into CSV files
    """

    parser_lammps_extract = argparse.ArgumentParser(description=intro_lammmps_extract)
    parser_lammps_extract.add_argument('-d', '--dumpfile_path',
                                       required=True,
                                       metavar='',
                                       type=str,
                                       help='Path pointing to LAMMPS dump files')

    parser_lammps_extract.add_argument('-s', '--save_path',
                                       required=True,
                                       metavar='',
                                       type=str,
                                       help='Path pointing to a saved directory')

    parser_lammps_extract.add_argument('-p', '--dumpfile_prefix',
                                       required=False,
                                       default='dump.dislocation_',
                                       type=str,
                                       help='LAMMPS dump files prefix. Default: dump.dislocation_')

    parser_lammps_extract.add_argument('-t', '--temperature_list',
                                       required=False,
                                       default=[10, 200, 400, 600, 800, 1000],
                                       nargs='*',
                                       type=int,
                                       help='Dump files temperature that need extracting segments. '
                                            'Default: [10, 200, 400, 600, 800, 1000]')
    args = parser_lammps_extract.parse_args()

    etl_object = DumpDirectory(args.dumpfile_path, args.save_path, args.dumpfile_prefix)
