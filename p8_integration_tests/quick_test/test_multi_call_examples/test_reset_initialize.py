import spynnaker8 as sim
from p8_integration_tests.base_test_case import BaseTestCase


class TestResetInitialize(BaseTestCase):
    # Test that resets and initialises, checking that membrane voltages
    # are reset and initialised correctly

    def do_run(self):
        sim.setup(1.0)
        pop = sim.Population(1, sim.IF_curr_exp, {}, label="pop")
        pop.set(i_offset=1.0)
        pop.record(["v"])
        initial1 = -64.0
        initial2 = -62.0
        initial3 = -63.0
        initial4 = -61.0
        runtime = 10

        pop.initialize(v=initial1)
        sim.run(runtime)

        sim.reset()
        pop.initialize(v=initial2)
        sim.run(runtime)

        sim.reset()
        pop.initialize(v=initial3)
        pop.set(i_offset=2.0)
        sim.run(runtime)

        pop.initialize(v=initial4)  # this should do nothing
        pop.set(i_offset=2.5)
        sim.run(runtime)

        v = pop.get_data('v')

        sim.end()

        # test values at start of each run() call above
        self.assertEqual(v.segments[0].filter(name='v')[0][0], initial1)
        self.assertEqual(v.segments[1].filter(name='v')[0][0], initial2)
        self.assertEqual(v.segments[2].filter(name='v')[0][0], initial3)
        self.assertNotEqual(v.segments[2].filter(name='v')[0][runtime],
                            initial4)

        # test the lengths of each segment are correct
        self.assertEqual(len(v.segments[0].filter(name='v')[0]), runtime)
        self.assertEqual(len(v.segments[0].filter(name='v')[0]),
                         len(v.segments[1].filter(name='v')[0]))
        self.assertEqual(len(v.segments[2].filter(name='v')[0]), 2 * runtime)

    def test_do_run(self):
        self.runsafe(self.do_run)
