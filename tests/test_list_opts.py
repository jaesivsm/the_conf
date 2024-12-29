from unittest import TestCase, mock

from the_conf import TheConf


class TestListOpts(TestCase):
    def setUp(self):
        self.conf = "the_conf.example.yml"

    @mock.patch("the_conf.files.read")
    def test_simple_list(self, read_patch):
        read_patch.return_value = [("myfile.json", {"intlist": [1, 2, 3]})]
        metaconf = {
            "parameters": [{"type": "list", "intlist": {"type": int}}],
            "source_order": ["files"],
            "config_files": ["myfile.json"],
        }

        tc = TheConf(metaconf)
        self.assertTrue(
            isinstance(tc.intlist, list),
            f"{tc.intlist} has type {type(tc.intlist)} not list",
        )
        self.assertEqual(3, len(tc.intlist))
        self.assertEqual(1, tc.intlist[0])
        self.assertEqual(2, tc.intlist[1])
        self.assertEqual(3, tc.intlist[2])
        tc.intlist.append(4)
        self.assertEqual(4, len(tc.intlist))
        self.assertEqual(4, tc.intlist[3])
        tc.intlist[3] = 5
        self.assertEqual(4, len(tc.intlist))
        self.assertEqual(5, tc.intlist[3])
        self.assertRaises(ValueError, setattr, tc, "intlist", "str value")
        self.assertRaises(ValueError, tc.intlist.__setitem__, 0, "str value")
        tc.intlist[3] = "5"
        self.assertEqual(4, len(tc.intlist))
        self.assertEqual(5, tc.intlist[3])

    def test_simple_list_from_env(self):
        metaconf = {
            "parameters": [{"type": "list", "intlist": {"type": int}}],
            "source_order": ["env"],
        }

        tc = TheConf(
            metaconf,
            environ={"INTLIST_0": 1, "INTLIST_1": 2, "INTLIST_2": 3},
        )
        self.assertTrue(
            isinstance(tc.intlist, list),
            f"{tc.intlist} has type {type(tc.intlist)} not list",
        )
        self.assertEqual(3, len(tc.intlist))
        self.assertEqual(1, tc.intlist[0])
        self.assertEqual(2, tc.intlist[1])
        self.assertEqual(3, tc.intlist[2])
        tc.intlist.append(4)
        self.assertEqual(4, len(tc.intlist))
        self.assertEqual(4, tc.intlist[3])
        tc.intlist[3] = 5
        self.assertEqual(4, len(tc.intlist))
        self.assertEqual(5, tc.intlist[3])
        self.assertRaises(ValueError, setattr, tc, "intlist", "str value")
        self.assertRaises(ValueError, tc.intlist.__setitem__, 0, "str value")
        tc.intlist[3] = "5"
        self.assertEqual(4, len(tc.intlist))
        self.assertEqual(5, tc.intlist[3])

    @mock.patch("the_conf.files.read")
    def test_complex_list(self, read_patch):
        read_patch.return_value = [
            (
                "myfile.json",
                {
                    "dictlist": [
                        {"myint": 1, "mystr": "a"},
                        {"myint": 2, "mystr": "b"},
                    ]
                },
            )
        ]
        metaconf = {
            "parameters": [
                {
                    "type": "list",
                    "dictlist": [
                        {"myint": {"type": int}},
                        {"mystr": {"type": str}},
                    ],
                }
            ],
            "source_order": ["files"],
            "config_files": ["myfile.json"],
        }

        tc = TheConf(metaconf)
        self.assertTrue(
            isinstance(tc.dictlist, list),
            f"{tc.dictlist} has type {type(tc.dictlist)} not list",
        )
        self.assertEqual(2, len(tc.dictlist))
        self.assertEqual(1, tc.dictlist[0].myint)
        self.assertEqual("a", tc.dictlist[0].mystr)
        self.assertEqual(2, tc.dictlist[1].myint)
        self.assertEqual("b", tc.dictlist[1].mystr)
        tc.dictlist[1] = {"myint": 3, "mystr": "c"}
        self.assertEqual(2, len(tc.dictlist))
        self.assertEqual(3, tc.dictlist[1].myint)
        self.assertEqual("c", tc.dictlist[1].mystr)
        tc.dictlist[1].myint = "3"
        self.assertEqual(3, tc.dictlist[1].myint)
        self.assertRaises(
            ValueError, setattr, tc.dictlist[0], "myint", "str value"
        )

    def test_complex_list_from_env(self):
        environ = {
            "DICTLIST_0_MYINT": 1,
            "DICTLIST_0_MYSTR": "a",
            "DICTLIST_1_MYINT": 2,
            "DICTLIST_1_MYSTR": "b",
        }
        metaconf = {
            "parameters": [
                {
                    "type": "list",
                    "dictlist": [
                        {"myint": {"type": int}},
                        {"mystr": {"type": str}},
                    ],
                }
            ],
            "source_order": ["env"],
        }

        tc = TheConf(metaconf, environ=environ)
        self.assertTrue(
            isinstance(tc.dictlist, list),
            f"{tc.dictlist} has type {type(tc.dictlist)} not list",
        )
        self.assertEqual(2, len(tc.dictlist))
        self.assertEqual(1, tc.dictlist[0].myint)
        self.assertEqual("a", tc.dictlist[0].mystr)
        self.assertEqual(2, tc.dictlist[1].myint)
        self.assertEqual("b", tc.dictlist[1].mystr)
        tc.dictlist[1] = {"myint": 3, "mystr": "c"}
        self.assertEqual(2, len(tc.dictlist))
        self.assertEqual(3, tc.dictlist[1].myint)
        self.assertEqual("c", tc.dictlist[1].mystr)
        tc.dictlist[1].myint = "3"
        self.assertEqual(3, tc.dictlist[1].myint)
        self.assertRaises(
            ValueError, setattr, tc.dictlist[0], "myint", "str value"
        )

    def test_loading_malformed_env_simple_list(self):
        metaconf = {
            "parameters": [{"type": "list", "intlist": {"type": int}}],
            "source_order": ["env"],
        }

        tc = TheConf(
            metaconf,
            environ={"INTLIST_0": 2, "INTLIST_10": 3},
        )
        assert tc.intlist == [2, 3]

    def test_complex_list_from_malformed_env(self):
        environ = {
            "DICTLIST_0_MYINT": 1,
            "DICTLIST_0_MYSTR": "a",
            "DICTLIST_10_MYINT": 2,
            "DICTLIST_10_MYSTR": "b",
        }
        metaconf = {
            "parameters": [
                {
                    "type": "list",
                    "dictlist": [
                        {"myint": {"type": int}},
                        {"mystr": {"type": str}},
                    ],
                }
            ],
            "source_order": ["env"],
        }

        tc = TheConf(metaconf, environ=environ)
        assert len(tc.dictlist) == 2
        assert tc.dictlist[0].myint == 1
        assert tc.dictlist[0].mystr == "a"
        assert tc.dictlist[2].myint == 1
        assert tc.dictlist[2].mystr == "b"


# FIXME nested list not supported yet
#    @mock.patch('the_conf.files.read')
#    def test_nested_list(self, read_patch):
#        read_patch.return_value = [
#            ('myfile.json',
#             {'high_list': [{'list_str': ['a', 'b', 'c'],
#                             'list_dict': [{'a': 'a', 'b': 3}],
#                             },
#                            {'list_int': [1, 2, 3],
#                             'mystr': 'mystr',
#                             'list_str': [{'mystr': 'c'}]},
#                            {'myint': 3}]},
#             )]
#        metaconf = {'parameters': [
#                        {'type': 'list',
#                         'high_list': [
#                             {'mystr': {'type': 'str'}},
#                             {'myint': {'type': 'int'}},
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
#        self.assertTrue(isinstance(tc.dictlist, list),
#                        f"{tc.dictlist} has type {type(tc.dictlist)} not list")
#        self.assertEqual(2, len(tc.dictlist))
#        self.assertEqual(1, tc.dictlist[0].myint)
#        self.assertEqual('a', tc.dictlist[0].mystr)
#        self.assertEqual(2, tc.dictlist[1].myint)
#        self.assertEqual('b', tc.dictlist[1].mystr)
#        tc.dictlist[1] = {'myint': 3, 'mystr': 'c'}
#        self.assertEqual(2, len(tc.dictlist))
#        self.assertEqual(3, tc.dictlist[1].myint)
#        self.assertEqual('c', tc.dictlist[1].mystr)
#        tc.dictlist[1].myint = '3'
#        self.assertEqual(3, tc.dictlist[1].myint)
#        self.assertRaises(ValueError,
#                          setattr, tc.dictlist[0], 'myint', 'str value')
