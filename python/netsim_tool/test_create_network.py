import unittest
from shell_commands import NetsimShell
import ncs
import _ncs


def set_maapi():
    m = ncs.maapi.Maapi()
    m.start_user_session('admin', 'system', [])
    t = m.start_trans(ncs.RUNNING, ncs.READ_WRITE)
    r = ncs.maagic.get_root(t)
    return r


class TestMain(unittest.TestCase):
    def setUp(self):
        self.r = set_maapi()

    def test_non_existing_device_does_not_init_config(self):
        netsim = NetsimShell('juniper-junos', self.r.netsim.config.netsim_dir)
        success, error = netsim.init_config('this_device_shouldnt_exist')
        self.assertTrue(error)


if __name__ == '__main__':
    unittest.main()
