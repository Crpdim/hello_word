from config_manager import ConfigManager, STUDY_MODES
from word_manager import DataManager
from display import DisplayManager
from input_manager import InputManager
from memorization import MemoryAlgorithm
import sys

def main():
    managers = {}
    try:
        # 初始化各个管理器
        init_managers(managers)
        # 运行主循环
        run_main_loop(managers)
    except Exception as e:
        DisplayManager.show_error(f"程序错误: {str(e)}")
    finally:
        cleanup_resources(managers)

def init_managers(managers):
    """初始化所有管理器"""
    managers['config'] = ConfigManager()
    managers['data'] = DataManager(source_type="local")
    managers['display'] = DisplayManager(managers['config'])
    managers['input'] = InputManager()
    managers['memory'] = MemoryAlgorithm()
    
    # 加载词库
    try:
        managers['data'].load_data("data/KaoYanluan_1.json")
    except Exception as e:
        DisplayManager.show_error(f"加载词库失败: {str(e)}")
        sys.exit(1)

def cleanup_resources(managers):
    """清理资源"""
    for manager in managers.values():
        if hasattr(manager, 'cleanup'):
            try:
                manager.cleanup()
            except Exception as e:
                print(f"清理资源时出错: {str(e)}")

def run_main_loop(managers):
    """主循环"""
    while True:
        managers['display'].show_main_menu()
        choice = managers['input'].get_menu_choice(list(STUDY_MODES.keys()) + ['q'])
        
        if choice == 'q':
            if confirm_exit(managers):
                break
            continue
            
        mode_func = globals()[STUDY_MODES[choice][1]]
        try:
            mode_func(managers)
        except Exception as e:
            DisplayManager.show_error(f"模式运行出错: {str(e)}")

def confirm_exit(managers):
    """确认退出"""
    print("\n是否确认退出? (y/n)")
    if managers['input'].get_confirm():
        # 保存学习进度
        try:
            managers['data'].save_progress()
            print("学习进度已保存")
            # 显示学习统计
            print("\n学习统计:")
            stats = managers['data'].get_statistics()
            for key, value in stats.items():
                print(f"{key}: {value}")
        except Exception as e:
            print(f"保存进度时出错: {str(e)}")
        return True
    return False

def process_word(word, managers, word_index, total_words):
    """统一的单词处理逻辑"""
    while True:
        # 显示进度信息
        DataManager.show_info(f"\n进度: [{word_index + 1}/{total_words}]")
        if word.review_count > 0:        
            DataManager.show_info(f"复习次数: {word.review_count}, 正确次数: {word.correct_count}")

        # 显示单词
        managers['display'].display_word(word, managers['memory'], show_answer=False)
        
        command = managers['input'].get_input()
        
        if command == 'quit':
            return 'quit'
        elif command == 'help':
            managers['display'].show_help()
            continue
        elif command == 'skip':
            return 'skip'
        elif command in ['yes', 'no']:
            # 显示答案
            managers['display'].display_word(word, managers['memory'], show_answer=True)
            
            if command == 'yes':
                print("\n你真的认识这个单词吗? (y/n)")
                really_knew = managers['input'].get_confirm()
                managers['data'].update_word_status(word, really_knew)
                managers['memory'].update_memory(word.word, really_knew)
            else:
                managers['data'].update_word_status(word, False)
                managers['memory'].update_memory(word.word, False)
                print("\n按任意键继续...")
                managers['input'].wait_key()
                
            return 'next'

def normal_study_mode(managers):
    """顺序学习模式"""
    word_index = 0
    total_words = len(managers['data'].words)
    
    while word_index < total_words:
        try:
            word = managers['data'].get_word(word_index)
            result = process_word(word, managers, word_index, total_words)
            
            if result == 'quit':
                break
            elif result == 'skip':
                word_index += 1
            elif result == 'next':
                word_index += 1
                
        except Exception as e:
            DisplayManager.show_error(f"处理单词时出错: {str(e)}")
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

def smart_mode(managers):
    """智能学习模式 - 根据记忆算法调整复习"""
    while True:
        try:
            # 获取推荐学习的单词
            words = get_recommended_words(managers)
            if not words:
                print("当前没有需要学习的单词")
                break
                
            for i, word in enumerate(words):
                result = process_word(word, managers, i, len(words))
                if result == 'quit':
                    return
                    
        except Exception as e:
            DisplayManager.show_error(f"智能模式运行出错: {str(e)}")
            break

def get_recommended_words(managers, limit=10):
    """获取推荐学习的单词
    
    基于以下规则:
    1. 从未学习过的单词
    2. 正确率低于80%的单词
    3. 需要复习的单词
    """
    words = []
    memory = managers['memory']
    
    # 获取所有单词
    all_words = managers['data'].words
    
    # 1. 获取从未学习的单词
    new_words = [w for w in all_words if w.review_count == 0]
    if new_words:
        words.extend(new_words[:limit//2])
        
    # 2. 获取需要复习的单词
    review_words = [w for w in all_words 
                   if w.review_count > 0 and memory.should_review(w.word)]
    if review_words:
        words.extend(review_words[:(limit - len(words))])
        
    return words

if __name__ == "__main__":
    main()
