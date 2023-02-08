import numpy as np


# Wrapper the dislocation back to simulation cell
class Wrapper:
    def __init__(self, segment_points, ylim):
        self.segment_points = segment_points
        self.ylim = ylim
        self.y_array = segment_points[:, 1]
        self.wrap = self.processing()

    def is_wrap_side(self):
        if np.min(self.y_array) > self.ylim[1]:
            return 2
        elif np.max(self.y_array) < self.ylim[0]:
            return 3
        elif np.max(self.y_array) > self.ylim[1] > np.min(self.y_array) > self.ylim[0]:
            # Right wrap
            return 0
        elif self.ylim[1] > np.max(self.y_array) > self.ylim[0] > np.min(self.y_array):
            # Left wrap
            return 1
        else:
            # No points out of simulation box boundaries
            return -1

    def processing(self):
        if self.is_wrap_side() == 2:
            fix_array = self.segment_points
            fix_array[:, 1] -= abs(self.y_array[-1] - self.y_array[0])
            return fix_array
        elif self.is_wrap_side() == 3:
            fix_array = self.segment_points
            fix_array[:, 1] += abs(self.y_array[-1] - self.y_array[0])
            return fix_array
        elif self.is_wrap_side() == 0:
            right_idx = np.where(self.y_array > self.ylim[1])[0]
            in_array = np.array(self.segment_points[:right_idx[0], :])
            wrap_array = self.segment_points[right_idx[0]-1:, :]
            wrap_array[:, 1] -= abs(self.y_array[-1] - self.y_array[0])
            fix_array = np.r_[wrap_array, in_array]
            return fix_array
        elif self.is_wrap_side() == 1:
            left_idx = np.where(self.y_array < self.ylim[0])[0]
            in_array = np.array(self.segment_points[left_idx[-1]+1:, :])
            wrap_array = self.segment_points[:left_idx[-1]+2, :]
            wrap_array[:, 1] += abs(self.y_array[-1] - self.y_array[0])
            fix_array = np.r_[in_array, wrap_array]
            return fix_array
        else:
            return self.segment_points
