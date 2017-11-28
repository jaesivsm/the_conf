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
        self.assertRaises(ValueError, setattr, tc, 'example', 'wrong value')
        tc.example = 'choice 2'
        self.assertEqual('choice 2', tc.example)
        self.assertRaises(AttributeError, getattr, tc.nested, 'value')
        self.assertRaises(ValueError, setattr, tc.nested, 'value', 'wrong val')
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

    def test_loading_from_env(self):
        metaconf = {'parameters': [{'option': {'type': str}}],
                    'source_order': ['env'],
                    'config_files': []}
        tc = TheConf(metaconf, environ={'STUFF': 'true', 'OPTION': 'value'})
        self.assertEqual('value', tc.option)

    def test_loading_nested_from_env(self):
        metaconf = {'parameters': [{'option': [{'option': {'type': str}}]}],
                    'source_order': ['env']}
        tc = TheConf(metaconf,
                environ={'OPTION_OPTION': 'value', 'OPTION': 'stuff'})
        self.assertEqual('value', tc.option.option)

    def test_conf_from_obj(self):
        metaconf = {'parameters': [{'option': {'type': str, 'default': 'a'}}],
                    'config_files': []}
        tc = TheConf(metaconf, cmd_line_opts=[])
        self.assertEqual('a', tc.option)
        tc.option = 1
        self.assertEqual('1', tc.option)

    def test_casting(self):
        metaconf = {'parameters': [{'option1': {'type': str, 'default': 'a'}},
                                   {'option2': {'type': int, 'default': '1'}}],
                    'config_files': []}
        tc = TheConf(metaconf, cmd_line_opts=[])
        self.assertEqual('a', tc.option1)
        self.assertEqual(1, tc.option2)
        tc.option1, tc.option2 = 'b', '2'
        self.assertEqual('b', tc.option1)
        self.assertEqual(2, tc.option2)

    def test_read_only(self):
        tc = TheConf({'parameters': [
                            {'option1': {'default': 'a', 'read_only': True}},
                            {'option2': {'read_only': True}},
                      ],
                      'config_files': []}, cmd_line_opts=['--option2=stuff'])
        self.assertEqual('a', tc.option1)
        self.assertEqual('stuff', tc.option2)
        self.assertRaises(AttributeError, setattr, tc, 'option1', 'read only')
        self.assertRaises(AttributeError, setattr, tc, 'option2', 'read only')

    def test_trigger_error_w_required(self):
        metaconf = {'parameters': [
                        {'option': {'type': str, 'required': True}}],
                    'config_files': []}
        self.assertRaises(ValueError, TheConf, metaconf, cmd_line_opts=[])
        tc = TheConf(metaconf, cmd_line_opts=['--option=stuff'])
        self.assertEqual('stuff', tc.option)

    def test_extract_config(self):
        metaconf = {'parameters': [{'option': [
                        {'option': {'type': str, 'default': 'a'}}]}],
                    'config_files': []}
        tc = TheConf(metaconf, cmd_line_opts=[])
        self.assertEqual('a', tc.option.option)
        self.assertEqual({}, tc._extract_config())
        tc.option.option = 'b'
        self.assertEqual({'option': {'option': 'b'}}, tc._extract_config())
