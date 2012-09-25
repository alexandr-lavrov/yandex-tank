from Tank.Plugins.JMeter import JMeterPlugin
from Tests.TankTests import TankTestCase
import logging
import time
import unittest

class  JMeterPluginTestCase(TankTestCase):
    def setUp(self):
        core = self.get_core()
        core.load_configs(['config/jmeter.conf'])
        self.foo = JMeterPlugin(core)

    def tearDown(self):
        del self.foo
        self.foo = None

    def test_run(self):
        self.foo.configure()
        self.foo.prepare_test()
        self.foo.start_test()
        while self.foo.is_test_finished() < 0:
            self.foo.log.debug("Not finished")
            time.sleep(1)
        self.foo.end_test(0)
        results = open(self.foo.jtl_file, 'r').read()
        logging.debug("Results: %s", results)
        self.assertNotEquals('', results.strip())
        
    def test_run_interrupt(self):
        self.foo.configure()
        self.foo.prepare_test()
        self.foo.start_test()
        time.sleep(2)
        self.foo.end_test(0)

if __name__ == '__main__':
    unittest.main()
