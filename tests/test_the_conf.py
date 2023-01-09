from unittest import TestCase, mock

from the_conf import TheConf


class TestTheConfObj(TestCase):

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

    def test_false_default(self):
        metaconf = {'parameters': [
                        {'option': {'type': bool, 'default': False}}],
                    'source_order': ['env'],
                    'config_files': []}
        tc = TheConf(metaconf, environ={})
        self.assertFalse(tc.option)

    def test_set_to_path(self):
        metaconf = {'parameters': [
                        {'option': {'type': int, 'default': 1}}],
                    'source_order': ['env'],
                    'config_files': []}
        tc = TheConf(metaconf, environ={})
        self.assertEqual(1, tc.option)
        tc._set_to_path(['option'], 2)
        self.assertEqual(2, tc.option)
        del tc.option
        self.assertEqual(1, tc.option)

    @mock.patch('the_conf.files.read')
    def test_simple_list(self, read_patch):
        read_patch.return_value = [('myfile.json', 'json',
                                    {'int_list': [1, 2, 3]})]
        metaconf = {'parameters': [
                        {'type': 'list',
                         'int_list': {'type': int}}],
                    'source_order': ['files'],
                    'config_files': ['myfile.json']}

        tc = TheConf(metaconf)
        self.assertTrue(isinstance(tc.int_list, list),
                        f"{tc.int_list} has type {type(tc.int_list)} not list")
        self.assertEqual(3, len(tc.int_list))
        self.assertEqual(1, tc.int_list[0])
        self.assertEqual(2, tc.int_list[1])
        self.assertEqual(3, tc.int_list[2])
        tc.int_list.append(4)
        self.assertEqual(4, len(tc.int_list))
        self.assertEqual(4, tc.int_list[3])
        tc.int_list[3] = 5
        self.assertEqual(4, len(tc.int_list))
        self.assertEqual(5, tc.int_list[3])
        self.assertRaises(ValueError, setattr, tc, 'int_list', 'str value')
        self.assertRaises(ValueError, tc.int_list.__setitem__, 0, 'str value')
        tc.int_list[3] = '5'
        self.assertEqual(4, len(tc.int_list))
        self.assertEqual(5, tc.int_list[3])

    @mock.patch('the_conf.files.read')
    def test_complex_list(self, read_patch):
        read_patch.return_value = [('myfile.json', 'json',
                                    {'dict_list': [
                                        {'my_int': 1, 'my_str': 'a'},
                                        {'my_int': 2, 'my_str': 'b'}]})]
        metaconf = {'parameters': [
                        {'type': 'list',
                         'dict_list': [{'my_int': {'type': int}},
                                       {'my_str': {'type': str}}]}],
                    'source_order': ['files'],
                    'config_files': ['myfile.json']}

        tc = TheConf(metaconf)
        self.assertTrue(isinstance(tc.dict_list, list),
                        f"{tc.dict_list} has type {type(tc.dict_list)} not list")
        self.assertEqual(2, len(tc.dict_list))
        self.assertEqual(1, tc.dict_list[0].my_int)
        self.assertEqual('a', tc.dict_list[0].my_str)
        self.assertEqual(2, tc.dict_list[1].my_int)
        self.assertEqual('b', tc.dict_list[1].my_str)
        tc.dict_list[1] = {'my_int': 3, 'my_str': 'c'}
        self.assertEqual(2, len(tc.dict_list))
        self.assertEqual(3, tc.dict_list[1].my_int)
        self.assertEqual('c', tc.dict_list[1].my_str)
        tc.dict_list[1].my_int = '3'
        self.assertEqual(3, tc.dict_list[1].my_int)
        self.assertRaises(ValueError,
                          setattr, tc.dict_list[0], 'my_int', 'str value')
