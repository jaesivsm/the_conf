
from unittest import TestCase, mock

from the_conf import TheConf


class TestListOpts(TestCase):

    def setUp(self):
        self.conf = 'the_conf.example.yml'

    @mock.patch('the_conf.files.read')
    def test_simple_list(self, read_patch):
        read_patch.return_value = [('myfile.json', {'int_list': [1, 2, 3]})]
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
        read_patch.return_value = [('myfile.json',
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

# FIXME nested list not supported yet
#    @mock.patch('the_conf.files.read')
#    def test_nested_list(self, read_patch):
#        read_patch.return_value = [
#            ('myfile.json',
#             {'high_list': [{'list_str': ['a', 'b', 'c'],
#                             'list_dict': [{'a': 'a', 'b': 3}],
#                             },
#                            {'list_int': [1, 2, 3],
#                             'my_str': 'my_str',
#                             'list_str': [{'my_str': 'c'}]},
#                            {'my_int': 3}]},
#             )]
#        metaconf = {'parameters': [
#                        {'type': 'list',
#                         'high_list': [
#                             {'my_str': {'type': 'str'}},
#                             {'my_int': {'type': 'int'}},
#                             {'type': 'list', 'list_str': {'type': 'str'}},
#                             {'type': 'list', 'list_int': {'type': 'int'}},
#                             {'type': 'list', 'list_dict': [
#                                {'a': {'type': 'str'}},
#                                {'b': {'type': 'int'}},
#                             ]}
#                         ]}
#                    ],
#                    'source_order': ['files'],
#                    'config_files': ['myfile.json']}
#
#        tc = TheConf(metaconf)
#        self.assertTrue(isinstance(tc.dict_list, list),
#                        f"{tc.dict_list} has type {type(tc.dict_list)} not list")
#        self.assertEqual(2, len(tc.dict_list))
#        self.assertEqual(1, tc.dict_list[0].my_int)
#        self.assertEqual('a', tc.dict_list[0].my_str)
#        self.assertEqual(2, tc.dict_list[1].my_int)
#        self.assertEqual('b', tc.dict_list[1].my_str)
#        tc.dict_list[1] = {'my_int': 3, 'my_str': 'c'}
#        self.assertEqual(2, len(tc.dict_list))
#        self.assertEqual(3, tc.dict_list[1].my_int)
#        self.assertEqual('c', tc.dict_list[1].my_str)
#        tc.dict_list[1].my_int = '3'
#        self.assertEqual(3, tc.dict_list[1].my_int)
#        self.assertRaises(ValueError,
#                          setattr, tc.dict_list[0], 'my_int', 'str value')
