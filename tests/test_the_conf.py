import unittest
from the_conf import TheConf


class TestTheConfObj(unittest.TestCase):

    def setUp(self):
        self.conf = 'the_conf.example.yml'

    def tearDown(self):
        TheConf._TheConf__instance = None

    def test_conf_loading(self):
        tc = TheConf(self.conf, cmd_line_opts=['--stuff=stuff'])
        self.assertEqual('choice 1', tc.example)
        self.assertRaises(ValueError,
                setattr, tc, 'example', 'wrong value')
        self.assertEqual(None, setattr(tc, 'example', 'choice 2'))
        self.assertRaises(AttributeError,
                getattr, tc.nested, 'value')
        self.assertRaises(ValueError,
                setattr, tc.nested, 'value', 'wrong value')
        tc.nested.value = 2
        self.assertEqual(2, tc.nested.value)
        self.assertEqual(1, tc.int_value)

    def test_conf_reloading_no_overwrite(self):
        tc = TheConf(self.conf, cmd_line_opts=[])
        self.assertRaises(AttributeError, getattr, tc, 'config')
        tc = TheConf(self.conf, cmd_line_opts=['--stuff=the conf'])
        self.assertEqual('the conf', tc.config)
        tc = TheConf(self.conf, cmd_line_opts=['--stuff=wrong'])
        self.assertEqual('the conf', tc.config)

    def test_conf_from_obj(self):
        metaconf = {'parameters': [{'option': {'type': str, 'default': 'a'}}],
                    'config_files': []}
        tc = TheConf(metaconf, cmd_line_opts=[])
        self.assertEqual('a', tc.option)
        tc.option = 1
        self.assertEqual('1', tc.option)

    def test_casting(self):
        metaconf = {'parameters': [
                        {'option1': {'type': str, 'default': 'a'}},
                        {'option2': {'type': int, 'default': '1'}},
                    ],
                    'config_files': []}
        tc = TheConf(metaconf, cmd_line_opts=[])
        self.assertEqual('a', tc.option1)
        self.assertEqual(1, tc.option2)
        tc.option1, tc.option2 = 'b', '2'
        self.assertEqual('b', tc.option1)
        self.assertEqual(2, tc.option2)

    def test_trigger_error_w_required(self):
        metaconf = {'parameters': [
                        {'option': {'type': str, 'required': True}}],
                    'config_files': []}
        self.assertRaises(ValueError,
                TheConf, metaconf, cmd_line_opts=[])
        tc = TheConf(metaconf, cmd_line_opts=['--option=stuff'])
        self.assertEqual('stuff', tc.option)

    def test_extract_config(self):
        metaconf = {'parameters': [{'option': [
                        {'option': {'type': str, 'default': 'a'}}]}],
                    'config_files': []}
        tc = TheConf(metaconf, cmd_line_opts=[])
        self.assertEqual('a', tc.option.option)
        self.assertEqual({}, tc.extract_config())
        tc.option.option = 'b'
        self.assertEqual({'option': {'option': 'b'}}, tc.extract_config())
