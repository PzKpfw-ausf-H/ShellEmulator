import unittest
import os
import yaml
from emulator import ShellEmulator


class TestShellEmulator(unittest.TestCase):
    def setUp(self):
        self.config_path = 'config.yaml'
        assert os.path.exists(self.config_path), "Файл config.yaml не найден"
        self.emulator = ShellEmulator(self.config_path)
        self.emulator.root.withdraw()

    def tearDown(self):
        self.emulator.close()

    def test_load_config(self):
        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)
        self.assertEqual(self.emulator.config['vfs_path'], config['vfs_path'])
        self.assertEqual(self.emulator.config['log_file'], config['log_file'])
        self.assertEqual(self.emulator.config['startup_script'], config['startup_script'])

    def test_ls_root(self):
        output = []
        self.emulator.append_text = lambda x: output.append(x)
        self.emulator.cmd_ls([])
        self.assertTrue(any(output), "Ожидается непустой вывод ls для корневой директории")

    def test_mkdir_and_cd(self):
        output = []
        self.emulator.append_text = lambda x: output.append(x)

        self.emulator.cmd_mkdir(['test_dir'])
        self.assertIn("Directory 'test_dir' created.\n", output)

        output.clear()
        self.emulator.cmd_cd(['test_dir'])
        self.assertIn("Changed directory to test_dir\n", output)

    def test_cd_up(self):
        output = []
        self.emulator.append_text = lambda x: output.append(x)

        self.emulator.cmd_mkdir(['subdir'])
        self.emulator.cmd_cd(['subdir'])

        output.clear()
        self.emulator.cmd_cd(['..'])
        self.assertIn("Moved to the parent directory\n", output)

    def test_uname(self):
        output = []
        self.emulator.append_text = lambda x: output.append(x)
        self.emulator.cmd_uname()
        self.assertIn("Linux emulator 5.10.0\n", output)

    def test_cat_existing_file(self):
        output = []
        self.emulator.append_text = lambda x: output.append(x)

        self.emulator.current_directory = 'root/'

        # Указываем точное имя файла внутри архива
        self.emulator.cmd_cat(['file1.txt'])

        # Ожидаемое содержимое файла `file1.txt`
        self.assertIn("This is file1!!!\n", output)

    def test_cat_nonexistent_file(self):
        output = []
        self.emulator.append_text = lambda x: output.append(x)
        self.emulator.cmd_cat(['nofile.txt'])
        self.assertIn("cat: nofile.txt: No such file\n", output)

    def test_exit(self):
        with self.assertRaises(SystemExit):
            self.emulator.cmd_exit([])


if __name__ == '__main__':
    unittest.main()
