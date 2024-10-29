import unittest
import os
from emulator import ShellEmulator
import tempfile
import yaml


class TestCommands(unittest.TestCase):
    def setUp(self):
        # Создаем временную директорию для тестов
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config = {
            'log_file': os.path.join(self.temp_dir.name, 'log.csv'),
            'startup_script': os.path.join(self.temp_dir.name, 'startup.sh')
        }

        # Создаем временный конфигурационный файл
        self.config_path = os.path.join(self.temp_dir.name, 'config.yaml')
        with open(self.config_path, 'w') as f:
            yaml.dump(self.config, f)

        # Инициализируем эмулятор без запуска GUI
        self.emulator = ShellEmulator(self.config_path)
        self.emulator.root.withdraw()  # Скрыть GUI во время тестов

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_ls_root(self):
        # Тест команды ls в корневой директории временной файловой системы
        output = []
        self.emulator.append_text = lambda x: output.append(x)
        self.emulator.cmd_ls([])
        self.assertIn('\n', output)  # Корневая директория должна быть пустой по умолчанию

    def test_mkdir_and_cd(self):
        # Тест команд mkdir и cd
        output = []
        self.emulator.append_text = lambda x: output.append(x)
        self.emulator.cmd_mkdir(['test_dir'])
        self.assertIn("Directory 'test_dir' created.\n", output)
        self.emulator.cmd_cd(['test_dir'])
        self.assertIn("Changed directory to 'test_dir'\n", output)

    def test_cd_invalid(self):
        # Тест команды cd с несуществующей директорией
        output = []
        self.emulator.append_text = lambda x: output.append(x)
        self.emulator.cmd_cd(['nonexistent'])
        self.assertIn("cd: no such file or directory: nonexistent\n", output)

    def test_uname(self):
        # Тест команды uname
        output = []
        self.emulator.append_text = lambda x: output.append(x)
        self.emulator.cmd_uname([])
        self.assertIn("Linux emulator 5.10.0\n", output)

    def test_cat_nonexistent(self):
        # Тест команды cat для несуществующего файла
        output = []
        self.emulator.append_text = lambda x: output.append(x)
        self.emulator.cmd_cat(['nofile.txt'])
        self.assertIn("cat: nofile.txt: No such file\n", output)

    def test_cat_existing_file(self):
        # Создание временного файла для тестирования команды cat
        test_file_path = os.path.join(self.emulator.current_path, 'file1.txt')
        with open(test_file_path, 'w') as f:
            f.write('Hello World')

        output = []
        self.emulator.append_text = lambda x: output.append(x)
        self.emulator.cmd_cat(['file1.txt'])
        self.assertIn("Hello World\n", output)

    def test_exit(self):
        # Тест команды exit
        with self.assertRaises(SystemExit):
            self.emulator.cmd_exit([])


if __name__ == '__main__':
    unittest.main()
