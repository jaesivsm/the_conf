import unittest

from the_conf import files


class TestFileMethods(unittest.TestCase):

    def test_extract_value_priv(self):
        self.assertEqual(
            (['path'], 1),
            next(files.extract_value({'path': 1}, ['path'])))
        generator = files.extract_value({'path': {'path': 1}}, ['path', 'path'])
        self.assertEqual((['path', 'path'], 1), next(generator))
        generator = files.extract_value({'path': 1}, ['wrong'])
        self.assertRaises(ValueError, generator.__next__)

    def test_extract_value(self):
        paths = [['path1', 'sub'], ['path2'], ['path3']]
        config = {'path1': {'sub': 1}, 'path2': 2}
        self.assertEqual([(['path1', 'sub'], 1), (['path2'], 2)],
                list(files.extract_values(paths, config, '')))
