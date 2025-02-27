from config_manager import ConfigManager
from word_manager import DataManager
from display import DisplayManager
from input_manager import InputManager
from memorization import MemoryAlgorithm

def main():
    managers = {}
    try:
        managers['config'] = ConfigManager()
        managers['data'] = DataManager(source_type="local")
        managers['display'] = DisplayManager(managers['config'])
        managers['input'] = InputManager()
        managers['memory'] = MemoryAlgorithm()
        
        run_main_loop(managers)
    except Exception as e:
        print(f"程序错误：{str(e)}")
    finally:
        # 确保资源正确关闭
        for manager in managers.values():
            if hasattr(manager, 'cleanup'):
                manager.cleanup()

def run_main_loop(managers):
    try:
        # 加载词库
        try:
            managers['data'].load_data("data/KaoYanluan_1.json")
        except Exception as e:
            print(f"加载词库失败: {str(e)}")
            return
        # normal_study_mode(managers)
        review_mode(managers)
    except Exception as e:
        print(f"程序初始化失败: {str(e)}")

def normal_study_mode(managers):
    # 顺序模式
    word_index = 0
    while True:
        try:
            word = managers['data'].get_word(word_index)
            
            # 首先显示单词（不显示答案）
            managers['display'].display_word(word, managers['memory'], show_answer=False)
            
            # 获取用户输入
            command = managers['input'].get_input()
            
            if command == 'quit':
                break
            elif command in ['yes', 'no']:
                # 无论用户选择yes还是no，都先显示答案
                managers['display'].display_word(word, managers['memory'], show_answer=True)
                
                # 如果用户选择yes，需要二次确认
                if command == 'yes':
                    really_knew = managers['input'].get_confirm()
                    managers['data'].update_word_status(word, really_knew)
                    managers['memory'].update_memory(word.word, really_knew)
                else:  # command == 'no'
                    managers['data'].update_word_status(word, False)
                    managers['memory'].update_memory(word.word, False)
                
                    # 等待用户查看答案
                    print("\n按任意键继续...")
                    managers['input'].wait_key()
                
                word_index += 1
                
        except Exception as e:
            print(f"程序运行出错: {str(e)}")
            break


def review_mode(managers):
    word_index = 0
    while True:
        try:
            revied_words = managers['data'].get_review_words()
            words_count = len(revied_words)
            if word_index >= words_count:
                print("没有需要复习的单词了")
                print(managers['data'].get_statistics())
                break
            word_index %= words_count
            word = managers['data'].get_review_words()[word_index]
            
            # 首先显示单词（不显示答案）
            managers['display'].display_word(word, managers['memory'], show_answer=False)
            
            # 获取用户输入
            command = managers['input'].get_input()
            
            if command == 'quit':
                break
            elif command in ['yes', 'no']:
                # 无论用户选择yes还是no，都先显示答案
                managers['display'].display_word(word, managers['memory'], show_answer=True)
                
                # 如果用户选择yes，需要二次确认
                if command == 'yes':
                    really_knew = managers['input'].get_confirm()
                    managers['data'].update_word_status(word, really_knew)
                    managers['memory'].update_memory(word.word, really_knew)
                else:  # command == 'no'
                    managers['data'].update_word_status(word, False)
                    managers['memory'].update_memory(word.word, False)
                
                    # 等待用户查看答案
                    print("\n按任意键继续...")
                    managers['input'].wait_key()
                
                word_index += 1
                
        except Exception as e:
            print(f"程序运行出错: {str(e)}")
            break


if __name__ == "__main__":
    main()
