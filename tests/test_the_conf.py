import unittest
import the_conf


class TestTheConfObj(unittest.TestCase):

    def tearDown(self):
        the_conf.TheConf._TheConf__instance = None

    def test_conf_loading(self):
        tc = the_conf.TheConf('the_conf.example.yml',
                cmd_line_opts=['--stuff=stuff'])
        self.assertEqual('choice 1', tc.example)
        self.assertRaises(ValueError,
                setattr, tc, 'example', 'wrong value')
        self.assertEqual(None, setattr(tc, 'example', 'choice 2'))
        self.assertRaises(AttributeError,
                getattr, tc.nested, 'value')
        self.assertRaises(ValueError,
                setattr, tc.nested, 'value', 'wrong value')
        self.assertEqual(None, setattr(tc.nested, 'value', 2))
        self.assertEqual(1, tc.int_value)

    def test_conf_reloading_no_overwrite(self):
        tc = the_conf.TheConf('the_conf.example.yml', cmd_line_opts=[])
        self.assertRaises(AttributeError, getattr, tc, 'config')
        tc = the_conf.TheConf('the_conf.example.yml',
                cmd_line_opts=['--stuff=the conf'])
        self.assertEqual('the conf', tc.config)
        tc = the_conf.TheConf('the_conf.example.yml',
                cmd_line_opts=['--stuff=wrong'])
        self.assertEqual('the conf', tc.config)
