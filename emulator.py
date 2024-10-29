import os
import sys
import tempfile
import yaml
import csv
import tkinter as tk
from tkinter import scrolledtext, messagebox


class ShellEmulator:
    def __init__(self, config_path):
        self.load_config(config_path)
        # Создаем временную директорию для виртуальной файловой системы. После работы файлы будут удалены
        self.temp_dir = tempfile.TemporaryDirectory()
        self.current_path = self.temp_dir.name  # Начальный путь — это временная директория
        self.log_actions = []
        self.init_gui()
        self.run_startup_script()

    def load_config(self, config_path):
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        self.log_file = config['log_file']
        self.startup_script = config['startup_script']

    def init_gui(self):
        self.root = tk.Tk()
        self.root.title("Shell Emulator")

        self.text_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, height=20, width=80, state='disabled')
        self.text_area.pack(padx=10, pady=10)

        self.entry = tk.Entry(self.root, width=80)
        self.entry.pack(padx=10, pady=(0, 10))
        self.entry.bind("<Return>", self.handle_command)

        self.display_prompt()
        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)

    def display_prompt(self):
        prompt = f"user@emulator:{self.current_path}$ "
        self.append_text(prompt)

    def append_text(self, text):
        self.text_area.config(state='normal')
        self.text_area.insert(tk.END, text)
        self.text_area.see(tk.END)
        self.text_area.config(state='disabled')

    def handle_command(self, event):
        command = self.entry.get().strip()
        self.entry.delete(0, tk.END)
        self.append_text(command + "\n")
        self.log_action(command)
        if command:
            self.execute_command(command)
        self.display_prompt()

    def execute_command(self, command_line):
        parts = command_line.split()
        if not parts:
            return
        cmd = parts[0]
        args = parts[1:]
        commands = {
            'ls': self.cmd_ls,
            'cd': self.cmd_cd,
            'exit': self.cmd_exit,
            'uname': self.cmd_uname,
            'mkdir': self.cmd_mkdir,
            'cat': self.cmd_cat
        }
        func = commands.get(cmd, self.cmd_unknown)
        func(args)

    def cmd_ls(self, args):
        try:
            items = os.listdir(self.current_path)
            self.append_text('  '.join(items) + '\n')
        except Exception as e:
            self.append_text(f"ls: {e}\n")

    def cmd_cd(self, args):
        if not args:
            self.append_text("cd: missing operand\n")
            return
        new_path = os.path.join(self.current_path, args[0])
        if os.path.isdir(new_path):
            self.current_path = new_path
            self.append_text(f"Changed directory to '{args[0]}'\n")
        else:
            self.append_text(f"cd: no such file or directory: {args[0]}\n")

    def cmd_mkdir(self, args):
        if not args:
            self.append_text("mkdir: missing operand\n")
            return
        new_dir = os.path.join(self.current_path, args[0])
        try:
            os.mkdir(new_dir)
            self.append_text(f"Directory '{args[0]}' created.\n")
        except FileExistsError:
            self.append_text(f"mkdir: cannot create directory '{args[0]}': File exists\n")
        except Exception as e:
            self.append_text(f"mkdir: {e}\n")

    def cmd_cat(self, args):
        if not args:
            self.append_text("cat: missing operand\n")
            return
        file_path = os.path.join(self.current_path, args[0])
        if os.path.isfile(file_path):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                self.append_text(content + '\n')
            except Exception as e:
                self.append_text(f"cat: {e}\n")
        else:
            self.append_text(f"cat: {args[0]}: No such file\n")

    def cmd_uname(self, args):
        self.append_text("Linux emulator 5.10.0\n")

    def cmd_exit(self, args):
        self.save_log()
        self.temp_dir.cleanup()  # Удаляем временную директорию
        self.root.destroy()
        sys.exit(0)

    def cmd_unknown(self, args):
        self.append_text("Unknown command\n")

    def log_action(self, command):
        self.log_actions.append([command])

    def save_log(self):
        with open(self.log_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Command'])
            writer.writerows(self.log_actions)

    def run_startup_script(self):
        if not os.path.exists(self.startup_script):
            return
        with open(self.startup_script, 'r') as f:
            commands = f.readlines()
        for cmd in commands:
            cmd = cmd.strip()
            if cmd:
                self.append_text(f"{cmd}\n")
                self.log_action(cmd)
                self.execute_command(cmd)

    def on_exit(self):
        self.cmd_exit([])

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python emulator.py <config.yaml>")
        sys.exit(1)
    config_path = sys.argv[1]
    emulator = ShellEmulator(config_path)
    emulator.run()
