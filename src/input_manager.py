import msvcrt

class InputManager:
    def __init__(self):
        self.commands = {
            b'y': 'yes',     # Y键 - 知道这个词
            b'n': 'no',      # N键 - 不知道
            b'q': 'quit',    # Q键 - 退出
            b'h': 'help',    # H键 - 显示帮助
            b's': 'skip',    # S键 - 跳过
            b' ': 'next',    # 空格键 - 下一个
        }

    def get_input(self):
        """获取用户输入（无需按回车）"""
        while True:
            if msvcrt.kbhit():
                key = msvcrt.getch().lower()
                if key in self.commands:
                    return self.commands[key]

    def get_confirm(self):
        """获取确认输入"""
        while True:
            if msvcrt.kbhit():
                key = msvcrt.getch().lower()
                if key in [b'y', b'n']:
                    return self.commands[key] == 'yes'

    def get_answer(self):
        """获取用户输入的答案"""
        return input("\nYour translation: ").strip()

    def wait_key(self):
        """等待用户按任意键"""
        while True:
            if msvcrt.kbhit():
                return msvcrt.getch()

    def get_menu_choice(self, valid_choices):
        """获取菜单选择
        
        Args:
            valid_choices: 有效的选择列表,如 ['1','2','3','q']
            
        Returns:
            str: 用户选择的选项
        """
        while True:
            if msvcrt.kbhit():
                key = msvcrt.getch().lower()
                choice = key.decode('utf-8')
                if choice in valid_choices:
                    return choice
