import os
import zipfile
import yaml
from tkinter import Tk, Text, END, Entry, StringVar, Frame, BOTH, LEFT, RIGHT, Y, Scrollbar


class ShellEmulator:
    def __init__(self, config_path):
        # Загрузка конфигурации
        self.load_config(config_path)

        # Инициализация GUI
        self.root = Tk()
        self.root.title("Shell Emulator")
        self.root.geometry("800x600")
        self.root.minsize(400, 410)  # Минимальный размер окна для предотвращения исчезновения элементов

        # Основной фрейм
        self.frame = Frame(self.root)
        self.frame.pack(expand=True, fill=BOTH)

        # Поле для вывода текста
        self.text_area = Text(self.frame, wrap='word')
        self.text_area.pack(expand=True, fill=BOTH, side=LEFT)

        # Полоса прокрутки
        scrollbar = Scrollbar(self.frame, command=self.text_area.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.text_area.config(yscrollcommand=scrollbar.set)

        # Строка ввода команд
        self.command_var = StringVar()
        self.command_entry = Entry(self.root, textvariable=self.command_var)
        self.command_entry.pack(fill='x')
        self.command_entry.bind("<Return>", self.enter_command)

        # Открываем виртуальную файловую систему
        self.vfs = zipfile.ZipFile(self.config['vfs_path'], 'a')
        self.current_directory = 'root/'  # Устанавливаем root как корневую директорию

        # Запуск стартового скрипта
        self.setup_startup_script()

    def load_config(self, config_path):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

    def setup_startup_script(self):
        startup_script = self.config.get('startup_script')
        if startup_script:
            with open(startup_script, 'r') as script:
                for line in script:
                    self.execute_command(line.strip())

    def enter_command(self, event):
        command = self.command_var.get().strip()
        self.append_text(f"> {command}\n")  # Показываем команду в выводе
        self.execute_command(command)
        self.command_var.set("")  # Очищаем строку ввода после выполнения
        return "break"

    def execute_command(self, command):
        if command.startswith("ls"):
            self.cmd_ls(command.split()[1:])
        elif command.startswith("cd"):
            self.cmd_cd(command.split()[1:])
        elif command.startswith("mkdir"):
            self.cmd_mkdir(command.split()[1:])
        elif command.startswith("cat"):
            self.cmd_cat(command.split()[1:])
        elif command.startswith("uname"):
            self.cmd_uname()
        elif command.startswith("exit"):
            self.root.quit()
        else:
            self.append_text(f"Command not found: {command}\n")

    def cmd_ls(self, args):
        contents = [name for name in self.vfs.namelist() if name.startswith(self.current_directory)]
        if not contents:
            self.append_text("\n")
        else:
            for item in contents:
                relative_item = os.path.relpath(item, self.current_directory)
                if '/' not in relative_item.strip('/'):
                    self.append_text(f"{relative_item}\n")

    def cmd_cd(self, args):
        if not args:
            self.append_text("cd: missing operand\n")
            return

        if args[0] == "..":
            # Переход на уровень выше
            if self.current_directory != "root/":
                self.current_directory = os.path.dirname(self.current_directory.rstrip('/')) + '/'
                self.append_text("Moved to the parent directory\n")
            else:
                self.append_text("Already at the root directory\n")
        else:
            # Переход в указанную директорию
            target_directory = os.path.join(self.current_directory, args[0])
            target_directory = target_directory if target_directory.endswith('/') else f"{target_directory}/"

            if any(item.startswith(target_directory) for item in self.vfs.namelist()):
                self.current_directory = target_directory
                self.append_text(f"Changed directory to {args[0]}\n")
            else:
                self.append_text(f"cd: no such file or directory: {args[0]}\n")

    def cmd_mkdir(self, args):
        if not args:
            self.append_text("mkdir: missing operand\n")
            return

        directory_name = args[0]
        new_directory_path = os.path.join(self.current_directory, directory_name)
        new_directory_path = new_directory_path if new_directory_path.endswith('/') else f"{new_directory_path}/"

        if new_directory_path in self.vfs.namelist():
            self.append_text(f"mkdir: cannot create directory '{directory_name}': File exists\n")
            return

        new_dir_info = zipfile.ZipInfo(new_directory_path)
        self.vfs.writestr(new_dir_info, '')
        self.append_text(f"Directory '{directory_name}' created.\n")

    def cmd_cat(self, args):
        if not args:
            self.append_text("cat: missing operand\n")
            return

        file_path = os.path.join(self.current_directory, args[0])
        if file_path in self.vfs.namelist():
            with self.vfs.open(file_path, 'r') as file:
                self.append_text(file.read().decode('utf-8') + '\n')
        else:
            self.append_text(f"cat: {args[0]}: No such file\n")

    def cmd_uname(self):
        self.append_text("Linux emulator 5.10.0\n")

    def append_text(self, text):
        self.text_area.insert(END, text)
        self.text_area.see(END)

    def close(self):
        self.vfs.close()
        self.root.quit()


if __name__ == "__main__":
    config_path = "config.yaml"  # Укажите путь к файлу конфигурации
    emulator = ShellEmulator(config_path)
    emulator.root.mainloop()
    emulator.close()



