import os
from config_manager import STUDY_MODES
from colorama import init, Fore, Style

init()  # 初始化colorama

class DisplayManager:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.current_mode = "review"  # 默认为复习模式

    @staticmethod
    def show_error(message):
        """显示错误信息"""
        print(f"{Fore.RED}{message}{Style.RESET_ALL}")
        
    @staticmethod
    def show_info(message):
        """显示信息"""
        print(f"{Fore.CYAN}{message}{Style.RESET_ALL}")

    def show_main_menu(self):
        """显示主菜单"""
        self.clear_screen()
        print(f"\n{Fore.CYAN}═══════════════════════{Style.RESET_ALL}")
        print(f"{Fore.GREEN}请选择学习模式:{Style.RESET_ALL}")
        for key, (name, _) in STUDY_MODES.items():
            print(f"{Fore.YELLOW}{key}{Style.RESET_ALL}. {name}")
        print(f"{Fore.YELLOW}q{Style.RESET_ALL}. 退出程序")
        print(f"{Fore.CYAN}═══════════════════════{Style.RESET_ALL}")

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_word(self, word, memory_algorithm, show_answer=False):
        """显示单词内容"""
        self.clear_screen()
        mastery = memory_algorithm.get_mastery_level(word.word)
        beauty_mode = self.config_manager.get("display.show_tips")
        if beauty_mode:
            print(f"\n{Fore.CYAN}═══════════════════════════════════{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Word{Style.RESET_ALL}: {Fore.YELLOW}{word.word}{Style.RESET_ALL}")
        if beauty_mode:
            print(f"{Fore.BLUE}Mastery: {mastery}%{Style.RESET_ALL}")
        
        if self.config_manager.get("display.show_phonetics"):
            if word.phonetics or word.uk_phonetics:
                if word.phonetics:
                    print(f"{Fore.GREEN}US{Style.RESET_ALL}: [{word.phonetics}]")
                if word.uk_phonetics:
                    print(f"{Fore.GREEN}UK{Style.RESET_ALL}: [{word.uk_phonetics}]")

        if show_answer:
            if word.translation:
                print(f"\n{Fore.GREEN}Translations:{Style.RESET_ALL}")
                for trans in word.get_translations():
                    print(f" • {trans}")
            
            if self.config_manager.get("display.show_sentences") and word.examples:
                print(f"\n{Fore.GREEN}Examples:{Style.RESET_ALL}")
                for example in word.get_example_sentences()[:2]:
                    print(f" • {example['en']}")
                    print(f"   {Fore.BLUE}{example['cn']}{Style.RESET_ALL}")
            
            if self.config_manager.get("display.show_phrases") and word.phrases:
                print(f"\n{Fore.GREEN}Phrases:{Style.RESET_ALL}")
                for phrase in word.get_phrases():
                    print(f" • {phrase['phrase']}")
                    print(f"   {Fore.BLUE}{phrase['meaning']}{Style.RESET_ALL}")
            
            if self.config_manager.get("display.show_memory_method") and word.memory_method:
                print(f"\n{Fore.GREEN}Memory Tip:{Style.RESET_ALL}")
                print(f" • {word.memory_method}")
        if beauty_mode:
            print(f"\n{Fore.CYAN}═══════════════════════════════════{Style.RESET_ALL}")
            if not show_answer:
                print("\nDo you know this word?")
                print(f"{Fore.GREEN}Y{Style.RESET_ALL} - Yes, I know it")
                print(f"{Fore.RED}N{Style.RESET_ALL} - No, show me the meaning")
                print(f"{Fore.YELLOW}Q{Style.RESET_ALL} - Quit")
            else:
                print("\nDid you really know it?")
                print(f"{Fore.GREEN}Y{Style.RESET_ALL} - Yes, mark as known")
                print(f"{Fore.RED}N{Style.RESET_ALL} - No, mark as unknown")

    def display_result(self, correct):
        """显示答题结果"""
        if correct:
            print(f"\n{Fore.GREEN}✓ Correct!{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.RED}✗ Incorrect!{Style.RESET_ALL}")

    def show_help():
        """显示帮助信息"""
        print(f"\n{Fore.CYAN}══════ 快捷键说明 ══════{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}y{Style.RESET_ALL} - 认识这个单词")
        print(f"{Fore.YELLOW}n{Style.RESET_ALL} - 不认识")
        print(f"{Fore.YELLOW}s{Style.RESET_ALL} - 跳过当前单词")
        print(f"{Fore.YELLOW}h{Style.RESET_ALL} - 显示帮助")
        print(f"{Fore.YELLOW}q{Style.RESET_ALL} - 退出当前模式")
        print(f"{Fore.CYAN}═══════════════════════{Style.RESET_ALL}")
        input("\n按任意键继续...")