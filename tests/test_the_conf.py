from unittest import TestCase, mock

from the_conf import TheConf


class TestTheConfObj(TestCase):
    def setUp(self):
        self.conf = "the_conf.example.yml"

    def test_conf_loading(self):
        tc = TheConf(self.conf, cmd_line_opts=["--stuff=stuff"])
        self.assertEqual("choice 1", tc.example)
        self.assertRaises(ValueError, setattr, tc, "example", "wrong value")
        tc.example = "choice 2"
        self.assertEqual("choice 2", tc.example)
        self.assertRaises(AttributeError, getattr, tc.nested, "value")
        self.assertRaises(ValueError, setattr, tc.nested, "value", "wrong val")
        tc.nested.value = 2
        self.assertEqual(2, tc.nested.value)
        self.assertEqual(1, tc.int_value)

    def test_conf_reloading_no_overwrite(self):
        tc = TheConf(self.conf, cmd_line_opts=[])
        self.assertRaises(AttributeError, getattr, tc, "config")
        tc = TheConf(self.conf, cmd_line_opts=["--stuff=the conf"])
        self.assertEqual("the conf", tc.config)

    def test_loading_from_env(self):
        metaconf = {
            "parameters": [{"option": {"type": str}}],
            "source_order": ["env"],
            "config_files": [],
        }
        tc = TheConf(metaconf, environ={"STUFF": "true", "OPTION": "value"})
        self.assertEqual("value", tc.option)

    def test_loading_nested_from_env(self):
        metaconf = {
            "parameters": [{"option": [{"option": {"type": str}}]}],
            "source_order": ["env"],
        }
        tc = TheConf(
            metaconf, environ={"OPTION_OPTION": "value", "OPTION": "stuff"}
        )
        self.assertEqual("value", tc.option.option)

    def test_conf_from_obj(self):
        metaconf = {
            "parameters": [{"option": {"type": str, "default": "a"}}],
            "config_files": [],
        }
        tc = TheConf(metaconf, cmd_line_opts=[])
        self.assertEqual("a", tc.option)
        tc.option = 1
        self.assertEqual("1", tc.option)

    def test_casting(self):
        metaconf = {
            "parameters": [
                {"option1": {"type": str, "default": "a"}},
                {"option2": {"type": int, "default": "1"}},
            ],
            "config_files": [],
        }
        tc = TheConf(metaconf, cmd_line_opts=[])
        self.assertEqual("a", tc.option1)
        self.assertEqual(1, tc.option2)
        tc.option1, tc.option2 = "b", "2"
        self.assertEqual("b", tc.option1)
        self.assertEqual(2, tc.option2)

    def test_read_only(self):
        tc = TheConf(
            {
                "parameters": [
                    {"option1": {"default": "a", "read_only": True}},
                    {"option2": {"read_only": True}},
                ],
                "config_files": [],
            },
            cmd_line_opts=["--option2=stuff"],
        )
        self.assertEqual("a", tc.option1)
        self.assertEqual("stuff", tc.option2)
        self.assertRaises(AttributeError, setattr, tc, "option1", "read only")
        self.assertRaises(AttributeError, setattr, tc, "option2", "read only")

    def test_trigger_error_w_required(self):
        metaconf = {
            "parameters": [{"option": {"type": str, "required": True}}],
            "config_files": [],
        }
        self.assertRaises(ValueError, TheConf, metaconf, cmd_line_opts=[])
        tc = TheConf(metaconf, cmd_line_opts=["--option=stuff"])
        self.assertEqual("stuff", tc.option)

    def test_extract_config(self):
        metaconf = {
            "parameters": [
                {"option": [{"option": {"type": str, "default": "a"}}]}
            ],
            "config_files": [],
        }
        tc = TheConf(metaconf, cmd_line_opts=[])
        self.assertEqual("a", tc.option.option)
        self.assertEqual({}, tc._extract_config())
        tc.option.option = "b"
        self.assertEqual({"option": {"option": "b"}}, tc._extract_config())

    def test_false_default(self):
        metaconf = {
            "parameters": [{"option": {"type": bool, "default": False}}],
            "source_order": ["env"],
            "config_files": [],
        }
        tc = TheConf(metaconf, environ={})
        self.assertFalse(tc.option)

    def test_default_cast_type(self):
        metaconf = {
            "parameters": [{"option": {"default": 0}}],
            "source_order": ["env"],
            "config_files": [],
        }
        tc = TheConf(metaconf, environ={})
        assert 0 == tc.option
        tc = TheConf(metaconf, environ={"OPTION": "1"})
        assert 1 == tc.option

    def test_env_var_with_underscore(self):
        metaconf = {
            "parameters": [{"eki": [{"eki_patang": {"default": 0}}]}],
            "source_order": ["env"],
            "config_files": [],
        }
        tc = TheConf(metaconf, environ={})
        assert 0 == tc.eki.eki_patang
        tc = TheConf(metaconf, environ={"EKI_EKI_PATANG": "1"})
        assert 1 == tc.eki.eki_patang

    def test_set_to_path(self):
        metaconf = {
            "parameters": [{"option": {"type": int, "default": 1}}],
            "source_order": ["env"],
            "config_files": [],
        }
        tc = TheConf(metaconf, environ={})
        self.assertEqual(1, tc.option)
        tc._set_to_path(["option"], 2)
        self.assertEqual(2, tc.option)
        del tc.option
        self.assertEqual(1, tc.option)

    @mock.patch("the_conf.files.open")
    def test_bool_from_str(self, yaml_load):
        yaml_load.return_value.__enter__.return_value.read.return_value = (
            "boolean: bla"
        )
        metaconf = {
            "source_order": ["files"],
            "config_files": ["bla.yml"],
            "parameters": [{"boolean": {"type": bool, "default": False}}],
        }
        tc = TheConf(metaconf)
        assert tc.boolean is True
        tc.boolean = ""
        assert tc.boolean is False

    @mock.patch("the_conf.files.open")
    def test_bool_from_none(self, yaml_load):
        yaml_load.return_value.__enter__.return_value.read.return_value = (
            "boolean: null"
        )
        metaconf = {
            "source_order": ["files"],
            "config_files": ["bla.yml"],
            "parameters": [{"boolean": {"type": bool, "default": True}}],
        }
        tc = TheConf(metaconf)
        assert tc.boolean is False
        tc.boolean = None
        assert tc.boolean is False

    @mock.patch("the_conf.files.open")
    def test_bool_from_int(self, yaml_load):
        yaml_load.return_value.__enter__.return_value.read.return_value = (
            "boolean: 2"
        )
        metaconf = {
            "source_order": ["files"],
            "config_files": ["bla.yml"],
            "parameters": [{"boolean": {"type": bool, "default": False}}],
        }
        tc = TheConf(metaconf)
        assert tc.boolean is True
        tc.boolean = 1
        assert tc.boolean is True

    @mock.patch("the_conf.files.open")
    def test_bool_from_zero(self, yaml_load):
        yaml_load.return_value.__enter__.return_value.read.return_value = (
            "boolean: 0"
        )
        metaconf = {
            "source_order": ["files"],
            "config_files": ["bla.yml"],
            "parameters": [{"boolean": {"type": bool, "default": True}}],
        }
        tc = TheConf(metaconf)
        assert tc.boolean is False
        tc.boolean = 0.0
        assert tc.boolean is False

    def test_source_priority_env_then_files(self):
        """Test that when env is loaded first, files should not overwrite it"""
        import tempfile
        import os

        # Create a temp config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write("option: from_file\n")
            config_file = f.name

        try:
            metaconf = {
                "parameters": [{"option": {"type": str}}],
                "source_order": ["env", "files"],
                "config_files": [config_file],
            }
            # Env provides the value first
            tc = TheConf(metaconf, environ={"OPTION": "from_env"})
            # The value should remain from env, not overwritten by files
            assert tc.option == "from_env"
        finally:
            os.unlink(config_file)

    @mock.patch("the_conf.files.open")
    def test_source_priority_env_then_cmd(self, mock_open):
        """Test that when env is loaded first, cmd should not overwrite it"""
        metaconf = {
            "parameters": [{"option": {"type": str}}],
            "source_order": ["env", "cmd"],
            "config_files": [],
        }
        # Env provides the value first
        tc = TheConf(metaconf, environ={"OPTION": "from_env"}, cmd_line_opts=["--option=from_cmd"])
        # The value should remain from env, not overwritten by cmd
        assert tc.option == "from_env"

    def test_multiple_config_files_priority(self):
        """Test priority when loading multiple config files"""
        import tempfile
        import os

        # Create two temp config files
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write("option: from_first\n")
            first_file = f.name

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write("option: from_second\n")
            second_file = f.name

        try:
            metaconf = {
                "parameters": [{"option": {"type": str}}],
                "source_order": ["files"],
                "config_files": [first_file, second_file],
            }
            tc = TheConf(metaconf)
            # First file in the list should have priority
            assert tc.option == "from_first"
        finally:
            os.unlink(first_file)
            os.unlink(second_file)
