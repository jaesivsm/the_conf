import unittest
import the_conf


class TestTheConfObj(unittest.TestCase):

    def test_conf_loading(self):
        tc = the_conf.TheConf('the_conf.example.yml')
        self.assertEqual('choice 1', tc.example)
        self.assertRaises(ValueError,
                setattr, tc, 'example', 'wrong value')
        self.assertEqual(None, setattr(tc, 'example', 'choice 2'))
        self.assertRaises(AttributeError,
                getattr, the_conf.TheConf().nested, 'value')
        self.assertRaises(ValueError,
                setattr, tc.nested, 'value', 'wrong value')
        self.assertEqual(None, setattr(tc.nested, 'value', 2))
