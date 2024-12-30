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
        assert isinstance(
            tc.intlist, list
        ), f"{tc.intlist} has type {type(tc.intlist)} not list"
        assert 3 == len(tc.intlist)
        assert 1 == tc.intlist[0]
        assert 2 == tc.intlist[1]
        assert 3 == tc.intlist[2]
        tc.intlist.append(4)
        assert 4 == len(tc.intlist)
        assert 4 == tc.intlist[3]
        tc.intlist[3] = 5
        assert 4 == len(tc.intlist)
        assert 5 == tc.intlist[3]
        self.assertRaises(ValueError, setattr, tc, "intlist", "str value")
        self.assertRaises(ValueError, tc.intlist.__setitem__, 0, "str value")
        tc.intlist[3] = "5"
        assert 4 == len(tc.intlist)
        assert 5 == tc.intlist[3]

    def test_simple_list_from_env(self):
        metaconf = {
            "parameters": [{"type": "list", "intlist": {"type": int}}],
            "source_order": ["env"],
        }

        tc = TheConf(
            metaconf,
            environ={"INTLIST_0": 1, "INTLIST_1": 2, "INTLIST_2": 3},
        )
        assert isinstance(
            tc.intlist, list
        ), f"{tc.intlist} has type {type(tc.intlist)} not list"
        assert 3 == len(tc.intlist)
        assert 1 == tc.intlist[0]
        assert 2 == tc.intlist[1]
        assert 3 == tc.intlist[2]
        tc.intlist.append(4)
        assert 4 == len(tc.intlist)
        assert 4 == tc.intlist[3]
        tc.intlist[3] = 5
        assert 4 == len(tc.intlist)
        assert 5 == tc.intlist[3]
        self.assertRaises(ValueError, setattr, tc, "intlist", "str value")
        self.assertRaises(ValueError, tc.intlist.__setitem__, 0, "str value")
        tc.intlist[3] = "5"
        assert 4 == len(tc.intlist)
        assert 5 == tc.intlist[3]

    @mock.patch("the_conf.files.read")
    def test_complex_list(self, read_patch):
        config = {
            "dictlist": [
                {"myint": 1, "mystr": "a"},
                {"myint": 2, "mystr": "b"},
            ]
        }
        read_patch.return_value = [("myfile.json", config)]
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
        assert isinstance(
            tc.dictlist, list
        ), f"{tc.dictlist} has type {type(tc.dictlist)} not list"
        assert 2 == len(tc.dictlist)
        assert 1 == tc.dictlist[0].myint
        assert "a" == tc.dictlist[0].mystr
        assert 2 == tc.dictlist[1].myint
        assert "b" == tc.dictlist[1].mystr
        tc.dictlist[1] = {"myint": 3, "mystr": "c"}
        assert 2 == len(tc.dictlist)
        assert 3 == tc.dictlist[1].myint
        assert "c" == tc.dictlist[1].mystr
        tc.dictlist[1].myint = "3"
        assert 3 == tc.dictlist[1].myint
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
        assert isinstance(
            tc.dictlist, list
        ), f"{tc.dictlist} has type {type(tc.dictlist)} not list"
        assert 2 == len(tc.dictlist)
        assert 1 == tc.dictlist[0].myint
        assert "a" == tc.dictlist[0].mystr
        assert 2 == tc.dictlist[1].myint
        assert "b" == tc.dictlist[1].mystr
        tc.dictlist[1] = {"myint": 3, "mystr": "c"}
        assert 2 == len(tc.dictlist)
        assert 3 == tc.dictlist[1].myint
        assert "c" == tc.dictlist[1].mystr
        tc.dictlist[1].myint = "3"
        assert 3 == tc.dictlist[1].myint
        self.assertRaises(
            ValueError, setattr, tc.dictlist[0], "myint", "str value"
        )

    def test_simple_list_from_malformed_env(self):
        metaconf = {
            "parameters": [{"type": "list", "intlist": {"type": int}}],
            "source_order": ["env"],
        }

        tc = TheConf(
            metaconf,
            environ={"INTLIST_1": 2, "INTLIST_10": 3},
        )
        assert tc.intlist == [2, 3]

    def test_complex_list_from_malformed_env(self):
        environ = {
            "DICTLIST_1_MYINT": 1,
            "DICTLIST_1_MYSTR": "a",
            "DICTLIST_10_MYINT": 2,
            "DICTLIST_10_MYSTR": "b",
            "MYSTR": "eki",
        }
        metaconf = {
            "parameters": [
                {
                    "type": "list",
                    "dictlist": [
                        {"myint": {"type": int}},
                        {"mystr": {"type": str}},
                    ],
                },
                {"mystr": {"type": str}},
                {"myint": {"type": int, "required": False}},
            ],
            "source_order": ["env"],
        }

        tc = TheConf(metaconf, environ=environ)
        assert 2 == len(tc.dictlist), tc.dictlist
        assert 1 == tc.dictlist[0].myint
        assert "a" == tc.dictlist[0].mystr
        assert 2 == tc.dictlist[1].myint
        assert "b" == tc.dictlist[1].mystr
        assert "eki" == tc.mystr
        self.assertRaises(AttributeError, getattr, tc, "myint")
