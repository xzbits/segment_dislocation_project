"""This script is using to:
- Extract dislocation lines using DXA which is implemented in Ovito
- Wrap dislocation lines back to simulation cell
- Interpolating the dislocation points to achieve equispaced data point
"""
from ovito.io import import_file, export_file
from ovito.modifiers import DislocationAnalysisModifier
from ovito.modifiers import AffineTransformationModifier
from ovito.modifiers import WrapPeriodicImagesModifier
from wrapper import Wrapper
import os
import re
import numpy as np


class DumpDirectory:
    def __init__(self, path, save_path, dumpfile_prefix, temperature_desire=None):
        """
        IMPORTANT NOTE: An dump folder must have one type of file name.
        :param path: Dump files path
        """
        self.temperature_desire = temperature_desire
        self.path = path
        self.save_path = save_path
        self.dumpfile_prefix = dumpfile_prefix
        self.files_list = os.listdir(self.path)
        self.file_name_type = self.classify_file_name(self.files_list[0])
        if self.file_name_type == -1:
            raise ValueError(self.files_list[0])
        self.re_term = self.get_re_term(self.files_list[0])
        if self.file_name_type == 0:
            self.temperature_list = self.extract_temperature_list()
        else:
            pass

    @staticmethod
    def classify_file_name(file_name):
        """
        Classify file name based on HEADislocation project
        :param file_name: File name.
        :return: 3 type of files name (file name with Temperature and Time, file name with Time, others)
        """
        re_file_name = re.findall(r"_(\d+)_(\d+).cfg", file_name)
        if re_file_name.__len__() == 1:
            # File name with Temperature and Time
            return 0
        elif re_file_name.__len__() == 0:
            # File name with Time
            return 1
        else:
            # Others
            return -1

    @staticmethod
    def get_re_term(file_name):
        re_file_name = re.findall(r"_(\d+)_(\d+).cfg", file_name)
        if re_file_name.__len__() == 1:
            # File name with Temperature and Time
            return r"_(\d+)_(\d+).cfg"
        elif re_file_name.__len__() == 0:
            # File name with Time
            return r"_(\d+).cfg"
        else:
            raise RuntimeError("Cannot identify regular expresion term for this {} file".format(file_name))

    def extract_temperature_list(self):
        output_list = list()
        for file_name in self.files_list:
            if self.classify_file_name(file_name) != self.file_name_type:
                raise RuntimeError("There are more than 2 type of file names existing in the directory: {} and {}"
                                   .format(self.files_list[0], file_name))
            else:
                re_name = re.findall(self.re_term, file_name)
                if int(re_name[0][0]) in self.temperature_desire:
                    pass
                else:
                    output_list.append(int(re_name[0][0]))
        return output_list

    @staticmethod
    def get_simulation_box(data):
        cell = data.cell[...]  # cell contains the original dislocation coordinate

        origin = cell[:, 3]
        p0 = np.zeros((1, 3), dtype=float) + origin
        p4 = p0 + cell[:, 2]
        p5 = p4 + cell[:, 0]
        p6 = p5 + cell[:, 1]

        xlim = (origin[0], p6[0, 0])
        ylim = (origin[1], p6[0, 1])
        zlim = (origin[2], p6[0, 2])

        return xlim, ylim, zlim

    @staticmethod
    def extract_pipeline_data(dumpfile_path):
        """
        Using OVITO package for extracting the segment data from dump files with default configuration
            + DislocationAnalysisModifier with line_point_separation=0 and line_smoothing_level=0
            + DislocationAnalysisModifier.Lattice.FCC
            + AffineTransformationModifier
            + WrapPeriodicImagesModifier

        :param dumpfile_path: The path lead to LAMMPS dump files
        :return: All Segment data in frame which is clarified in dumpfile_path
        """
        pipeline = import_file(dumpfile_path)
        modifier = DislocationAnalysisModifier(line_point_separation=0, line_smoothing_level=0)
        modifier.input_crystal_structure = DislocationAnalysisModifier.Lattice.FCC
        pipeline.modifiers.append(modifier)
        pipeline.modifiers.append(AffineTransformationModifier(relative_mode=False,
                                                               target_cell=pipeline.compute().cell[...],
                                                               only_selected=True))
        pipeline.modifiers.append(WrapPeriodicImagesModifier())
        all_frame_data = pipeline.compute()

        return all_frame_data, pipeline

    def get_dump_file_time_steps(self, dumpfile_list):
        output = []
        for file_name in dumpfile_list:
            time_steps = int(re.findall(r"{}(\d+)_(\d+)".format(self.dumpfile_prefix), file_name)[0][1])
            output.append(time_steps)
        output.sort()
        return output

    def extract_segment_raw(self, pipeline_path, save_path, start=None, stop=None):
        data, pipeline = self.extract_pipeline_data(pipeline_path)

        start_frame = 0 if start is None else start
        end_frame = pipeline.source.num_frames if start is None else stop

        for i in range(start_frame, end_frame):
            print("Frame: {}".format(i))
            data = pipeline.compute(i)
            segments_per_frame = np.array([[0, 0, 0]])
            for segment in data.dislocations.segments:
                segments_per_frame = np.r_[segments_per_frame, segment.points]
                segments_per_frame = np.r_[segments_per_frame, np.array([[0, 0, 0]])]
            np.savetxt(os.path.join(save_path, "segment_points_raw_frame_{}.csv".format(i)),
                       segments_per_frame, delimiter=",")

    def extract_segment_wrapped(self, pipeline_path, save_path, start=None, stop=None):
        data, pipeline = self.extract_pipeline_data(pipeline_path)
        xlimit, ylimit, zlimit = self.get_simulation_box(data)

        start_frame = 0 if start is None else start
        end_frame = pipeline.source.num_frames if start is None else stop

        for i in range(start_frame, end_frame):
            print("Frame: {}".format(i))
            data = pipeline.compute(i)
            segments_per_frame = np.array([[0, 0, 0]])
            for segment in data.dislocations.segments:
                aa = Wrapper(segment.points, ylimit)
                segments_per_frame = np.r_[segments_per_frame, aa.wrap]
                segments_per_frame = np.r_[segments_per_frame, np.array([[0, 0, 0]])]
            np.savetxt(os.path.join(save_path, "segment_points_raw_frame_{}.csv".format(i)),
                       segments_per_frame, delimiter=",")

    def load_wrapped_segment_csv(self):
        if self.temperature_desire is None:
            if self.file_name_type == 0:
                for temp in self.temperature_list:
                    print("Temperature: {}".format(temp))
                    pipelines_path = os.path.join(self.path, self.dumpfile_prefix + "{}_*.cfg".format(temp))
                    save_path = os.path.join(self.save_path, "extracted_data", "t_{}".format(temp))
                    self.extract_segment_wrapped(pipelines_path, save_path)
            elif self.file_name_type == 1:
                pipelines_path = os.path.join(self.path, self.dumpfile_prefix + "*.cfg")
                save_path = os.path.join(self.save_path, "extracted_data")
                self.extract_segment_wrapped(pipelines_path, save_path)
            else:
                pass
        else:
            if isinstance(self.temperature_desire, list):
                for temp in self.temperature_desire:
                    print("Temperature: {}".format(temp))
                    pipelines_path = os.path.join(self.path, self.dumpfile_prefix + "{}_*.cfg".format(temp))
                    save_path = os.path.join(self.save_path, "extracted_data", "t_{}".format(temp))
                    self.extract_segment_wrapped(pipelines_path, save_path)
            else:
                raise ValueError("Please set temperature_desire type is list object")

    def load_raw_segment_csv(self):
        if self.temperature_desire is None:
            if self.file_name_type == 0:
                for temp in self.temperature_list:
                    print("Temperature: {}".format(temp))
                    pipelines_path = os.path.join(self.path, self.dumpfile_prefix + "{}_*.cfg".format(temp))
                    save_path = os.path.join(self.save_path, "extracted_data", "t_{}".format(temp))
                    self.extract_segment_raw(pipelines_path, save_path)
            elif self.file_name_type == 1:
                pipelines_path = os.path.join(self.path, self.dumpfile_prefix + "*.cfg")
                save_path = os.path.join(self.save_path, "extracted_data")
                self.extract_segment_raw(pipelines_path, save_path)
            else:
                pass
        else:
            if isinstance(self.temperature_desire, list):
                for temp in self.temperature_desire:
                    print("Temperature: {}".format(temp))
                    pipelines_path = os.path.join(self.path, self.dumpfile_prefix + "{}_*.cfg".format(temp))
                    save_path = os.path.join(self.save_path, "extracted_data", "t_{}".format(temp))
                    self.extract_segment_raw(pipelines_path, save_path)
            else:
                raise ValueError("Please set temperature_desire type is list object")

    def create_dir(self):
        # Create extracted_data directory
        path_extract = os.path.join(self.save_path, "extracted_data")
        try:
            os.mkdir(path_extract)
        except OSError:
            print("Creation of the temperature with time directory %s failed" % path_extract)
        else:
            print("Successfully created the  temperature with time directory %s" % path_extract)
        if self.temperature_desire is None:
            # Create extracted_data sub-directory
            if self.file_name_type == 0:
                for one_temperature in self.extract_temperature_list():
                    path = os.path.join(self.save_path, "extracted_data", "t_{}".format(one_temperature))
                    try:
                        os.mkdir(path)
                    except OSError:
                        print("Creation of the temperature with time directory %s failed" % path)
                    else:
                        print("Successfully created the  temperature with time directory %s" % path)
            elif self.file_name_type == 1:
                pass
            else:
                raise ValueError("Cannot recognize the type of dump file names!!!!!!!")
        else:
            # Create extracted_data sub-directory
            if self.file_name_type == 0:
                for one_temperature in self.temperature_desire:
                    path = os.path.join(self.save_path, "extracted_data", "t_{}".format(one_temperature))
                    try:
                        os.mkdir(path)
                    except OSError:
                        print("Creation of the temperature with time directory %s failed" % path)
                    else:
                        print("Successfully created the  temperature with time directory %s" % path)
            elif self.file_name_type == 1:
                pass
            else:
                raise ValueError("Cannot recognize the type of dump file names!!!!!!!")
