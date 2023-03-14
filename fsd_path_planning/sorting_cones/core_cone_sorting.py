#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
Cone sorting class.

Description: Entry point for Pathing/ConeSorting
Project: fsd_path_planning
"""
from typing import Tuple

from icecream import ic  # pylint: disable=unused-import

from fsd_path_planning.sorting_cones.trace_sorter.core_trace_sorter import \
    TraceSorter
from fsd_path_planning.sorting_cones.utils.cone_sorting_dataclasses import (
    ConeSortingInput, ConeSortingState)
from fsd_path_planning.types import FloatArray
from fsd_path_planning.utils.cone_types import ConeTypes


class ConeSorting:
    """Class that takes all Pathing/ConeSorting responsibilities."""

    def __init__(
        self,
        max_n_neighbors: int,
        max_dist: float,
        max_dist_to_first: float,
        max_length: int,
        threshold_directional_angle: float,
        threshold_absolute_angle: float,
    ):
        """
        Init method.

        Args:
            max_n_neighbors, max_dist, max_dist_to_first: Arguments for TraceSorter.
            max_length: Argument for TraceSorter. The maximum length of a
                valid trace in the sorting algorithm.
            max_length_backwards: Argument for TraceSorter. The maximum length of a
                valid trace in the sorting algorithm for the backwards direction.
            max_backwards_index: the maximum amount of cones that will be taken in the
                backwards direction
            threshold_directional_angle: The threshold for the directional angle that is
                the minimum angle for consecutive cones to be connected in the direction
                of the trace (clockwise for left cones, counterclockwise for right cones).
            threshold_absolute_angle: The threshold for the absolute angle that is the
                minimum angle for consecutive cones to be connected regardless of the
                cone type.
        """
        self.input = ConeSortingInput()

        self.state = ConeSortingState(
            max_n_neighbors=max_n_neighbors,
            max_dist=max_dist,
            max_dist_to_first=max_dist_to_first,
            max_length=max_length,
            threshold_directional_angle=threshold_directional_angle,
            threshold_absolute_angle=threshold_absolute_angle,
        )

    def set_new_input(self, slam_input: ConeSortingInput) -> None:
        """Save inputs from other software nodes in variable."""
        self.input = slam_input

    def transition_input_to_state(self) -> None:
        """Parse and save the inputs in the state variable."""
        self.state.position_global, self.state.direction_global = (
            self.input.slam_position,
            self.input.slam_direction,
        )

        self.state.cones_by_type_array = self.input.slam_cones

    def run_cone_sorting(
        self,
    ) -> Tuple[FloatArray, FloatArray]:
        """
        Calculate the sorted cones.

        Returns:
            The sorted cones. The first array contains the sorted blue (left) cones and
            the second array contains the sorted yellow (right) cones.
        """
        # make transition from set inputs to usable state variables
        self.transition_input_to_state()

        ts = TraceSorter(
            self.state.max_n_neighbors,
            self.state.max_dist,
            self.state.max_dist_to_first,
            self.state.max_length,
            self.state.threshold_directional_angle,
            self.state.threshold_absolute_angle,
        )

        left_cones, right_cones = ts.sort_left_right(
            self.state.cones_by_type_array,
            self.state.position_global,
            self.state.direction_global,
        )

        return left_cones, right_cones
