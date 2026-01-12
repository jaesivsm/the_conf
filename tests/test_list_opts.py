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

    @mock.patch("the_conf.files.read")
    def test_simple_list_priority_env_then_files(self, read_patch):
        """Test that env-provided list values aren't overwritten by files"""
        read_patch.return_value = [("myfile.json", {"intlist": [10, 20, 30]})]
        metaconf = {
            "parameters": [{"type": "list", "intlist": {"type": int}}],
            "source_order": ["env", "files"],
            "config_files": ["myfile.json"],
        }

        tc = TheConf(metaconf, environ={"INTLIST_0": 1, "INTLIST_1": 2})
        # ENV should have priority, not FILES
        assert 2 == len(tc.intlist)
        assert 1 == tc.intlist[0]
        assert 2 == tc.intlist[1]

    @mock.patch("the_conf.files.read")
    def test_complex_list_priority_env_then_files(self, read_patch):
        """Test that env-provided complex list values aren't overwritten by files"""
        read_patch.return_value = [
            (
                "myfile.json",
                {
                    "dictlist": [
                        {"myint": 10, "mystr": "file_a"},
                        {"myint": 20, "mystr": "file_b"},
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
            "source_order": ["env", "files"],
            "config_files": ["myfile.json"],
        }

        environ = {
            "DICTLIST_0_MYINT": 1,
            "DICTLIST_0_MYSTR": "env_a",
        }
        tc = TheConf(metaconf, environ=environ)
        # ENV should have priority for index 0, FILES should not overwrite
        assert 1 == len(tc.dictlist)
        assert 1 == tc.dictlist[0].myint
        assert "env_a" == tc.dictlist[0].mystr

    @mock.patch("the_conf.files.read")
    def test_list_partial_values_from_multiple_sources(self, read_patch):
        """Test that first source wins for each index independently"""
        read_patch.return_value = [
            ("myfile.json", {"intlist": [10, 20, 30, 40]})
        ]
        metaconf = {
            "parameters": [{"type": "list", "intlist": {"type": int}}],
            "source_order": ["env", "files"],
            "config_files": ["myfile.json"],
        }

        # ENV provides indices 0 and 2, FILES provides all 4
        tc = TheConf(metaconf, environ={"INTLIST_0": 1, "INTLIST_2": 3})
        # ENV values should be preserved, FILES should not overwrite them
        assert 2 == len(tc.intlist)
        assert 1 == tc.intlist[0]
        assert 3 == tc.intlist[1]

    @mock.patch("the_conf.files.read")
    def test_complex_list_field_priority(self, read_patch):
        """Test that individual fields in complex list respect priority"""
        read_patch.return_value = [
            (
                "myfile.json",
                {
                    "dictlist": [
                        {"myint": 100, "mystr": "from_file"},
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
            "source_order": ["env", "files"],
            "config_files": ["myfile.json"],
        }

        # ENV only provides myint, FILES provides both
        environ = {"DICTLIST_0_MYINT": 1}
        tc = TheConf(metaconf, environ=environ)
        # ENV's myint should win, FILES should not overwrite it
        assert 1 == len(tc.dictlist)
        assert 1 == tc.dictlist[0].myint
        # mystr is not set by ENV, so should not be set at all
        self.assertRaises(AttributeError, getattr, tc.dictlist[0], "mystr")

    def test_list_options_skipped_on_cmd(self):
        """Test that list options are automatically skipped for command line"""
        metaconf = {
            "parameters": [
                {"type": "list", "intlist": {"type": int}},
                {"regular_option": {"type": str, "default": "default_value"}},
            ],
            "source_order": ["cmd"],
            "config_files": [],
        }

        # List options should be silently ignored on command line
        # Only regular_option should be processed
        tc = TheConf(metaconf, cmd_line_opts=["--regular_option=test"])
        assert "test" == tc.regular_option
        # intlist should be empty since cmd is the only source and lists are skipped
        assert [] == list(tc.intlist)

    @mock.patch("the_conf.files.read")
    def test_multiple_files_list_priority(self, read_patch):
        """Test that first config file has priority for lists"""
        read_patch.return_value = [
            ("first.json", {"intlist": [1, 2, 3]}),
            ("second.json", {"intlist": [10, 20, 30]}),
        ]
        metaconf = {
            "parameters": [{"type": "list", "intlist": {"type": int}}],
            "source_order": ["files"],
            "config_files": ["first.json", "second.json"],
        }

        tc = TheConf(metaconf)
        # First file should have priority
        assert 3 == len(tc.intlist)
        assert 1 == tc.intlist[0]
        assert 2 == tc.intlist[1]
        assert 3 == tc.intlist[2]

    def test_list_priority_env_then_files_three_sources(self):
        """Test list priority with env and files (cmd skips lists automatically)"""
        import tempfile
        import os

        # Create a temp config file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yml", delete=False
        ) as f:
            f.write("intlist:\n  - 100\n  - 200\n")
            config_file = f.name

        try:
            metaconf = {
                "parameters": [{"type": "list", "intlist": {"type": int}}],
                "source_order": ["cmd", "env", "files"],
                "config_files": [config_file],
            }

            # CMD is in source order but lists are skipped on cmd
            # ENV provides index 0, FILES provides both indices
            tc = TheConf(
                metaconf,
                cmd_line_opts=[],
                environ={"INTLIST_0": 5},
            )
            # ENV should have priority for index 0
            assert 1 == len(tc.intlist)
            assert 5 == tc.intlist[0]
        finally:
            os.unlink(config_file)
