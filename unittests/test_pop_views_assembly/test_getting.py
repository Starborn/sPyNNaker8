# Copyright (c) 2017-2019 The University of Manchester
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import division
import pickle
from unittest import SkipTest
import numpy
import pytest
from spinn_front_end_common.utilities.exceptions import ConfigurationException
from spinn_front_end_common.utilities.globals_variables import get_simulator
import spynnaker8 as sim
from spynnaker8.utilities import neo_convertor
from p8_integration_tests.base_test_case import BaseTestCase


def mock_spikes():
    return numpy.array(
        [[0, 7], [0, 20], [0, 24], [0, 34], [0, 53], [0, 67], [0, 77],
         [1, 8], [1, 20], [1, 53],
         [2, 45], [2, 76]])


def mock_v_all(variable):
    indexes = [0, 1, 2, 3]
    data = numpy.empty((100, 4))
    for i in range(100):
        for j in indexes:
            data[i][j] = -65 + j + i/100
    sampling_interval = 1
    return (data, indexes, sampling_interval)


def mock_v_one_two(variable):
    indexes = [1, 2]
    data = numpy.empty((100, 2))
    for i in range(100):
        for j in range(len(indexes)):
            data[i][j] = -65 + indexes[j] + i/100
    sampling_interval = 1
    return (data, indexes, sampling_interval)


def mock_time():
    return 100


def trim_spikes(spikes, indexes):
    return [[n, t] for [n, t] in spikes if n in indexes]


class TestGetting(BaseTestCase):

    def test_simple_spikes(self):
        sim.setup(timestep=1.0)
        pop = sim.Population(4, sim.IF_curr_exp(), label="a label")
        pop._get_spikes = mock_spikes
        pop._get_recorded_matrix = mock_v_all
        get_simulator().get_current_time = mock_time

        neo = pop.getSpikes()
        spikes = neo_convertor.convert_spikes(neo)
        assert numpy.array_equal(spikes,  mock_spikes())
        spiketrains = neo.segments[0].spiketrains
        assert 4 == len(spiketrains)

        #  gather False has not effect testing that here
        neo = pop.get_data("spikes", gather=False)
        spikes = neo_convertor.convert_spikes(neo)
        assert numpy.array_equal(spikes,  mock_spikes())
        spiketrains = neo.segments[0].spiketrains
        assert 4 == len(spiketrains)

        neo = pop.get_v()
        v = neo.segments[0].filter(name='v')[0].magnitude
        (target, _, _) = mock_v_all("any")
        assert numpy.array_equal(v,  target)

        neo = pop.get_gsyn()
        exc = neo.segments[0].filter(name='gsyn_exc')[0].magnitude
        assert numpy.array_equal(exc,  target)
        inh = neo.segments[0].filter(name='gsyn_inh')[0].magnitude
        assert numpy.array_equal(inh,  target)

        sim.end()

    def test_get_spikes_by_index(self):
        sim.setup(timestep=1.0)
        pop = sim.Population(4, sim.IF_curr_exp(), label="a label")
        pop.record("spikes")

        pop._get_spikes = mock_spikes
        get_simulator().get_current_time = mock_time

        neo = pop.get_data_by_indexes("spikes", [1, 2])
        spikes = neo_convertor.convert_spikes(neo)
        target = trim_spikes(mock_spikes(), [1, 2])
        assert numpy.array_equal(spikes, target)
        spiketrains = neo.segments[0].spiketrains
        assert 2 == len(spiketrains)

        sim.end()

    def test_get_spikes_by_view(self):
        sim.setup(timestep=1.0)
        pop = sim.Population(4, sim.IF_curr_exp(), label="a label")
        pop._get_spikes = mock_spikes
        get_simulator().get_current_time = mock_time

        view = pop[1:3]
        view.record("spikes")
        neo = view.get_data("spikes", gather=False)
        spikes = neo_convertor.convert_spikes(neo)
        target = trim_spikes(mock_spikes(), [1, 2])
        assert numpy.array_equal(spikes, target)
        spiketrains = neo.segments[0].spiketrains
        assert 2 == len(spiketrains)

        sim.end()

    def test_get_spikes_view_missing(self):
        sim.setup(timestep=1.0)
        pop = sim.Population(4, sim.IF_curr_exp(), label="a label")
        pop._get_spikes = mock_spikes
        pop._get_recorded_matrix = mock_v_all
        get_simulator().get_current_time = mock_time

        view = pop[2:4]
        neo = view.get_data("spikes")
        spikes = neo_convertor.convert_spikes(neo)
        target = trim_spikes(mock_spikes(), [2])
        assert numpy.array_equal(spikes, target)
        spiketrains = neo.segments[0].spiketrains
        assert 2 == len(spiketrains)
        assert 2 == len(spiketrains[0])
        assert 2 == spiketrains[0].annotations['source_index']
        assert 0 == len(spiketrains[1])
        assert 3 == spiketrains[1].annotations['source_index']

        sim.end()

    def test_get_v_view(self):
        sim.setup(timestep=1.0)
        pop = sim.Population(4, sim.IF_curr_exp(), label="a label")
        pop.record("spikes")
        pop._get_spikes = mock_spikes
        pop._get_recorded_matrix = mock_v_all
        get_simulator().get_current_time = mock_time

        view = pop[1:3]
        neo = view.get_data("v")
        v = neo.segments[0].filter(name='v')[0].magnitude
        (target, _, _) = mock_v_one_two("v")
        assert v.shape == target.shape
        assert numpy.array_equal(v,  target)

        sim.end()

    def test_get_v_missing(self):
        sim.setup(timestep=1.0)
        pop = sim.Population(4, sim.IF_curr_exp(), label="a label")
        pop._get_recorded_matrix = mock_v_one_two
        get_simulator().get_current_time = mock_time

        view = pop[0:3]
        neo = view.get_data("v")
        v = neo.segments[0].filter(name='v')[0].magnitude
        (target, _, _) = mock_v_one_two("v")
        assert numpy.array_equal(
            [1, 2], neo.segments[0].filter(name='v')[0].channel_index.index)
        assert v.shape == target.shape
        assert numpy.array_equal(v,  target)

        sim.end()

    def test_get_spike_counts(self):
        sim.setup(timestep=1.0)
        pop = sim.Population(4, sim.IF_curr_exp(), label="a label")
        pop.record("spikes")
        pop._get_spikes = mock_spikes
        get_simulator().get_current_time = mock_time

        assert {0: 7, 1: 3, 2: 2, 3: 0} == pop.get_spike_counts()

        view = pop[1:4]
        assert {1: 3, 2: 2, 3: 0} == view.get_spike_counts()

        assert 3 == pop.meanSpikeCount()
        assert 5/3 == view.mean_spike_count()

        sim.end()

    def test_write(self):
        sim.setup(timestep=1.0)
        pop = sim.Population(4, sim.IF_curr_exp(), label="a label")
        pop._get_spikes = mock_spikes
        pop._get_recorded_matrix = mock_v_all
        get_simulator().get_current_time = mock_time

        # Note gather=False will be ignored just testing it can be
        pop.write_data("spikes.pkl", "spikes", gather=False)
        try:
            with open("spikes.pkl") as pkl:
                neo = pickle.load(pkl)
                spikes = neo_convertor.convert_spikes(neo)
                assert numpy.array_equal(spikes,  mock_spikes())
        except UnicodeDecodeError:
            raise SkipTest(
                "https://github.com/NeuralEnsemble/python-neo/issues/529")

        pop.printSpikes("spikes.pkl")
        try:
            with open("spikes.pkl") as pkl:
                neo = pickle.load(pkl)
                spikes = neo_convertor.convert_spikes(neo)
                assert numpy.array_equal(spikes,  mock_spikes())
        except UnicodeDecodeError:
            raise SkipTest(
                "https://github.com/NeuralEnsemble/python-neo/issues/529")

        (target, _, _) = mock_v_all("any")

        pop.print_v("v.pkl")
        with open("v.pkl") as pkl:
            neo = pickle.load(pkl)
            v = neo.segments[0].filter(name='v')[0].magnitude
            assert v.shape == target.shape
            assert numpy.array_equal(v,  target)

        pop.print_gsyn("gsyn.pkl")
        with open("gsyn.pkl") as pkl:
            neo = pickle.load(pkl)
            exc = neo.segments[0].filter(name='gsyn_exc')[0].magnitude
            assert numpy.array_equal(exc,  target)
            inh = neo.segments[0].filter(name='gsyn_inh')[0].magnitude
            assert numpy.array_equal(inh,  target)

        sim.end()

    def test_get_(self):
        sim.setup(timestep=1.0)
        pop = sim.Population(4, sim.IF_curr_exp(), label="a label")
        pop._get_spikes = mock_spikes
        pop._get_recorded_matrix = mock_v_all
        get_simulator().get_current_time = mock_time

        v = pop.spinnaker_get_data("v")
        assert 400 == len(v)

        v = pop.spinnaker_get_data(["v"])
        assert 400 == len(v)

        with pytest.raises(ConfigurationException):
            pop.spinnaker_get_data(["v", "spikes"])
        sim.end()
