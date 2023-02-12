import numpy as np
import os
import glob


def extract_longest_segments(raw_lst_segment, filtering_axes=1, top_length=4):
    # Extract segments from convert segments
    filter_lst_segments = list()

    for current_segment in raw_lst_segment:
        segment_len = abs(current_segment[0, filtering_axes] - current_segment[-1, filtering_axes])
        if len(filter_lst_segments) < top_length:
            filter_lst_segments.append(current_segment)
        elif segment_len > abs(filter_lst_segments[0][0, filtering_axes] - filter_lst_segments[0][-1, filtering_axes]):
            filter_lst_segments[0] = current_segment
        filter_lst_segments.sort(key=lambda x: abs(x[0, filtering_axes] - x[-1, filtering_axes]))

    if len(filter_lst_segments) == 0:
        raise ValueError("There is no segments after filtering, please check again the raw data file")

    return filter_lst_segments


def get_no_component_segment(data_convert):
    # Get number of segment in CSV file
    x_no_seg = np.where(data_convert[:, 0] == 0.0)
    y_no_seg = np.where(data_convert[:, 1] == 0.0)
    no_segment = len(np.intersect1d(x_no_seg, y_no_seg)) - 1
    no_component = np.diff(np.intersect1d(x_no_seg, y_no_seg)) - 1

    return no_segment, no_component


def get_no_component_sfw(data_convert):
    # Get number of segment in CSV file
    x_no_seg = np.where(data_convert[:] == 0.0)[0]
    no_segment = len(x_no_seg) - 1
    no_component = np.diff(x_no_seg) - 1

    return no_segment, no_component


def merging_raw_segment(data_convert, ref_avg, no_segment, no_component):
    idx_start = 1
    output = [None, None, None, None]
    for i in range(no_segment):
        idx_split = idx_start + no_component
        current_segment = data_convert[idx_start:idx_split]
        current_segment_avg = np.average(current_segment, axis=0)

        segment_idx = 0
        dist_compare = 1e6
        for j in range(len(ref_avg)):
            cur_dist_compare = abs(ref_avg[j][0] - current_segment_avg[0]) + abs(ref_avg[j][2] - current_segment_avg[2])
            if dist_compare > cur_dist_compare:
                dist_compare = cur_dist_compare
                segment_idx = j
        if output[segment_idx] is None:
            output[segment_idx] = current_segment
        else:
            np.concatenate((output[segment_idx], current_segment))

        idx_start = idx_split + 1

    for i in range(len(output)):
        output[i] = output[i][output[i][:, 1].argsort()]

    return output


def collecting_all_data(csv_filepath, get_no_func):
    """
    Get data separated by "0" array

    :param csv_filepath:
    :param get_no_func: Function to GET number of data segment AND number of component per segment based on type
    of data
    :return: List of segment data
    """
    segment_data = np.genfromtxt(csv_filepath, delimiter=",")
    no_segment, no_component = get_no_func(segment_data)
    idx_start = 1
    lst_segments = []
    for i in range(no_segment):
        idx_split = idx_start + no_component[i]
        lst_segments.append(segment_data[idx_start:idx_split])
        idx_start = idx_split + 1

    return lst_segments


def grouping_sorting(lst_segment, group_by_axes=2, no_segment_per_group=2, sort_by_axes=0):
    # Get 4 longest segments
    lst_segment = extract_longest_segments(lst_segment)

    # Grouping segments by (self.group_by_axes)-axes value
    # with 0 = x-axes, 1 = y-axes, 2 = z-axes
    grouped_segments = list()
    if lst_segment[0].shape[1] == 3:
        lst_segment.sort(key=lambda x: x[0, group_by_axes])
        no_group = len(lst_segment) // no_segment_per_group
        for i in range(no_group):
            grouped_segments.append(
                lst_segment[int(i * no_segment_per_group):int(i * no_segment_per_group + no_segment_per_group)])
    else:
        no_group = len(lst_segment) // no_segment_per_group
        for i in range(no_group):
            grouped_segments.append(
                lst_segment[int(i * no_segment_per_group):int(i * no_segment_per_group + no_segment_per_group)])
        Warning("The extract data have only 2 axes data")

    # Sorting segments by mean of (self.sort_by_axes)-axes values
    # with 0 is x-axes, 1 is y-axes, 2 is z-axes
    for i in range(len(grouped_segments)):
        grouped_segments[i].sort(key=lambda x: np.mean(x[:, sort_by_axes]))

    return grouped_segments


def calculate_distance_of_2segments(segment1_data, segment2_data):
    x1_array = segment1_data[:, 0]
    y1_array = segment1_data[:, 1]

    x_array = segment2_data[:, 0]
    y_array = segment2_data[:, 1]

    equal_segments = y1_array

    temp_array = np.array([])
    idx_temp_array = np.array([], dtype=int)
    first_idx = None

    for j in range(0, y_array.shape[0] - 1):
        in_segment_idx = np.where((y_array[j] <= equal_segments) & (equal_segments <= y_array[j + 1]))[0]
        if in_segment_idx.shape[0] != 0:
            if first_idx is None:
                first_idx = in_segment_idx[0]
            for idd in in_segment_idx:
                if idd not in idx_temp_array:
                    y_hat = equal_segments[idd]
                    x_i = x_array[j]
                    y_i = y_array[j]
                    x_i1 = x_array[j + 1]
                    y_i1 = y_array[j + 1]
                    x_hat = x_i + (((x_i1 - x_i) * (y_hat - y_i)) / (y_i1 - y_i))
                    temp_array = np.append(temp_array, x_hat)
                else:
                    continue
        else:
            continue
        idx_temp_array = np.append(idx_temp_array, in_segment_idx)
    distance_array = abs(x1_array[first_idx:temp_array.shape[0] + first_idx] - temp_array)
    return distance_array


def calculate_sfw(csv_filepath):
    list_segments = collecting_all_data(csv_filepath, get_no_func=get_no_component_segment)
    group_segments = grouping_sorting(list_segments)

    sfw_array = np.array([[0]])
    for one_group in group_segments:
        sfw = calculate_distance_of_2segments(one_group[0], one_group[1]).reshape(-1, 1)
        sfw_array = np.concatenate((sfw_array, sfw))
        sfw_array = np.concatenate((sfw_array, np.array([[0]])))

    return sfw_array


def calculate_average_sfw(csv_filepath):
    list_segments = collecting_all_data(csv_filepath, get_no_func=get_no_component_sfw)
    sfw_average = []
    for one_segment in list_segments:
        sfw_average.append(np.average(one_segment))

    if len(sfw_average) == 0:
        raise ValueError("SFW average cannot be empty")

    return sfw_average


def create_directory(save_path, sub_dir_name):
    save_path = os.path.join(save_path, sub_dir_name)
    try:
        os.mkdir(save_path)
    except OSError:
        print("Creation of the directory %s failed" % save_path)
    else:
        print("Successfully created the directory %s" % save_path)


def process_sfw_data(filepath, csv_file_prefix, save_file_prefix):
    """
    Finding all files and processing all files in filepath

    :param filepath: File path to job_offer and job_details files
    :param csv_file_prefix: CSV files prefix
    :param save_file_prefix: saved CSV files prefix
    :return: None
    """
    # Get all files from directory
    all_files = []
    for root, dirs, files in os.walk(filepath):
        files = glob.glob(os.path.join(root, csv_file_prefix + "*[0-9].csv"))
        for f in files:
            all_files.append(os.path.abspath(f))

    # Number of files in directory
    num_files = len(all_files)
    all_files = sorted(all_files, key=lambda x: int(os.path.splitext(os.path.basename(x))[0].split("_")[-1]))

    # Iterating over files and process
    for num, datafile in enumerate(all_files, 1):
        filename = os.path.splitext(os.path.basename(datafile))[0]
        frame = filename.split("_")[-1]
        print("Extracting SFW from file: {}".format(filename))
        sfw = calculate_sfw(datafile)
        np.savetxt(os.path.join(filepath, save_file_prefix + "{}.csv".format(frame)), sfw, delimiter=",")
        print('{}/{} files processed'.format(num, num_files))


def process_average_sfw_data(filepath, sfw_csv_file_prefix, saved_file_name="sfw_average.csv"):
    """
    Calculate average SFW data based on SFW CSV files

    :param filepath: Path to SFW CSV files
    :param sfw_csv_file_prefix: SFW CSV files prefix
    :param saved_file_name: SFW average CSV file name
    :return: None
    """
    # Processing all SFW files
    # Get all SFW CSV files from directory
    all_SFW_files = []
    for root, dirs, files in os.walk(filepath):
        files = glob.glob(os.path.join(root, sfw_csv_file_prefix + "*[0-9].csv"))
        for f in files:
            all_SFW_files.append(os.path.abspath(f))

    # Number of files in directory
    num_SFW_files = len(all_SFW_files)
    all_SFW_files = sorted(all_SFW_files, key=lambda x: int(os.path.splitext(os.path.basename(x))[0].split("_")[-1]))

    # Iterating over files and process
    average_sfw = []
    for datafile in all_SFW_files:
        filename = os.path.splitext(os.path.basename(datafile))[0]
        frame = int(filename.split("_")[-1]) + 1
        print("Calculating average SFW from file: {}".format(filename))
        add_data = calculate_average_sfw(datafile)
        if len(add_data) > 2:
            raise ValueError(
                "There are more than 2 pair of segments in frame {}. Please check again!!".format(frame - 1))
        average_sfw.append(add_data)
        print('{}/{} files processed'.format(frame, num_SFW_files))
    np.savetxt(os.path.join(filepath, saved_file_name), np.array(average_sfw), delimiter=",")

