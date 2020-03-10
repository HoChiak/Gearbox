import unittest
from gearbox_functions import get_sample_time_torque
import numpy as np

class GearboxFunctionTest (unittest.TestCase):
    def test_get_sample_time_torque(self):
        self.assertTrue((get_sample_time_torque(10,5000,10,10) == np.arange(0,0.1,1/5000)).all())
        self.assertTrue((get_sample_time_torque(1,1000,13,17) == np.arange(0,17,1/1000)).all())
    

if __name__ == '__main__':
    unittest.main()