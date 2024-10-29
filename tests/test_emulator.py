import unittest
import os
import tempfile
import yaml
from emulator import ShellEmulator


class TestEmulator(unittest.TestCase):
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

        # Инициализируем эмулятор
        self.emulator = ShellEmulator(self.config_path)
        self.emulator.root.withdraw()  # Скрыть GUI во время тестов

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_load_config(self):
        # Проверка, что конфигурация загружена правильно
        self.assertEqual(self.emulator.log_file, self.config['log_file'])
        self.assertEqual(self.emulator.startup_script, self.config['startup_script'])

    def test_log_action(self):
        # Тест записи действия в лог
        self.emulator.log_action('ls')
        self.assertIn(['ls'], self.emulator.log_actions)

    def test_save_log(self):
        # Тест сохранения лога в файл
        self.emulator.log_action('ls')
        self.emulator.save_log()
        with open(self.config['log_file'], 'r') as f:
            content = f.read()
        self.assertIn('ls', content)

    def test_run_startup_script_empty(self):
        # Проверка запуска пустого стартового скрипта
        try:
            self.emulator.run_startup_script()
        except Exception as e:
            self.fail(f"run_startup_script() raised Exception unexpectedly: {e}")


if __name__ == '__main__':
    unittest.main()
