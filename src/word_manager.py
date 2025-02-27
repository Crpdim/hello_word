import json
import requests
from datetime import datetime
import random
import os
from typing import List, Dict, Optional
from collections import deque

class Word:
    def __init__(self, data: Dict):
        # 基础信息
        self.word = data.get("headWord", "")
        self.word_rank = data.get("wordRank", 0)
        
        # 获取 content.word 内容
        word_content = data.get("content", {}).get("word", {})
        
        # 音标
        self.phonetics = word_content.get("content", {}).get("usphone", "")  # 美式音标
        self.uk_phonetics = word_content.get("content", {}).get("ukphone", "")  # 英式音标
        
        # 例句 - 需要从 content 中获取
        self.examples = word_content.get("content", {}).get("sentence", {}).get("sentences", [])
        
        # 翻译和词性
        self.translation = word_content.get("content", {}).get("trans", [])
        
        # 同近义词
        self.synonyms = word_content.get("content", {}).get("syno", {}).get("synos", [])
        
        # 短语
        self.phrases = word_content.get("content", {}).get("phrase", {}).get("phrases", [])
        
        # 记忆方法
        self.memory_method = word_content.get("content", {}).get("remMethod", {}).get("val", "")
        
        # 同根词
        self.related_words = word_content.get("content", {}).get("relWord", {}).get("rels", [])
        
        # 学习进度相关属性
        self.last_reviewed = None
        self.review_count = 0
        self.correct_count = 0
        self.difficulty_level = 0

    def get_translations(self) -> List[str]:
        """获取所有中文翻译"""
        translations = []
        for trans in self.translation:
            if trans.get("tranCn"):
                pos = trans.get('pos', '')
                pos_str = f"[{pos}] " if pos else ""
                translations.append(f"{pos_str}{trans['tranCn']}")
        return translations

    def get_example_sentences(self) -> List[Dict[str, str]]:
        """获取例句"""
        return [
            {
                'en': example.get('sContent', ''),
                'cn': example.get('sCn', '')
            }
            for example in self.examples
        ]

    def get_phrases(self) -> List[Dict[str, str]]:
        """获取短语"""
        return [
            {
                'phrase': phrase.get('pContent', ''),
                'meaning': phrase.get('pCn', '')
            }
            for phrase in self.phrases
        ]

    def to_dict(self) -> Dict:
        """将单词对象转换为可序列化的字典，保存学习进度"""
        return {
            'word': self.word,
            'last_reviewed': self.last_reviewed.isoformat() if self.last_reviewed else None,
            'review_count': self.review_count,
            'correct_count': self.correct_count,
            'difficulty_level': self.difficulty_level
        }

    @classmethod
    def from_dict(cls, progress_data: Dict, original_data: Dict) -> 'Word':
        """从进度字典和原始数据创建单词对象"""
        word = cls(original_data)  # 使用原始数据创建对象
        word.last_reviewed = datetime.fromisoformat(progress_data['last_reviewed']) if progress_data.get('last_reviewed') else None
        word.review_count = progress_data.get('review_count', 0)
        word.correct_count = progress_data.get('correct_count', 0)
        word.difficulty_level = progress_data.get('difficulty_level', 0)
        return word

class DataManager:
    def __init__(self, source_type="local"):
        self.source_type = source_type
        self.words: List[Word] = []
        self.words_data: List[Dict] = []  # 保存原始数据
        self.current_book = ""
        self.progress_file = "data/progress.json"
        self.wrong_words: List[Word] = []
        self.review_history: Dict = {}
        self.cache_size = 100
        self.word_cache = deque(maxlen=self.cache_size)
        self.current_index = 0

    def load_data(self, source: str) -> None:
        """加载词库和学习进度"""
        self.current_book = os.path.basename(source)
        if self.source_type == "local":
            self.load_local(source)
        elif self.source_type == "remote":
            self.load_remote(source)
        self.load_progress()

    def load_local(self, filepath: str) -> None:
        """加载本地词库"""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                self.words_data = json.load(file)
                # 检查数据是否成功加载
                if not self.words_data:
                    raise ValueError("词库数据为空")
                    
                # 检查数据结构
                for word_data in self.words_data:
                    if "headWord" not in word_data or "content" not in word_data:
                        raise ValueError(f"无效的单词数据格式: {word_data.get('headWord', 'unknown')}")
                        
                self.words = [Word(word_data) for word_data in self.words_data]
                print(f"成功加载 {len(self.words)} 个单词")
                
        except FileNotFoundError:
            raise FileNotFoundError(f"找不到词库文件: {filepath}")
        except json.JSONDecodeError:
            raise ValueError(f"词库文件 {filepath} 格式错误")
        except Exception as e:
            raise Exception(f"加载词库失败: {str(e)}")

    def load_remote(self, api_url: str) -> None:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            self.words = [Word(word) for word in data]
        else:
            raise Exception("远程数据加载失败")

    def save_progress(self) -> None:
        """保存学习进度"""
        progress = {
            'book': self.current_book,
            'words': [word.to_dict() for word in self.words],
            'wrong_words': [word.to_dict() for word in self.wrong_words],
            'review_history': self.review_history
        }
        os.makedirs(os.path.dirname(self.progress_file), exist_ok=True)
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)

    def load_progress(self) -> None:
        """加载学习进度"""
        if os.path.exists(self.progress_file):
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                progress = json.load(f)
                if progress.get('book') == self.current_book:
                    # 创建单词原始数据的映射
                    word_data_map = {word['headWord']: word for word in self.words_data}
                    
                    # 使用进度数据和原始数据重建单词列表
                    self.words = []
                    for word_progress in progress['words']:
                        word_name = word_progress['word']
                        if word_name in word_data_map:
                            word = Word.from_dict(word_progress, word_data_map[word_name])
                            self.words.append(word)
                    
                    # 处理错词本
                    self.wrong_words = []
                    for word_progress in progress['wrong_words']:
                        word_name = word_progress['word']
                        if word_name in word_data_map:
                            word = Word.from_dict(word_progress, word_data_map[word_name])
                            self.wrong_words.append(word)
                    
                    self.review_history = progress.get('review_history', {})

    def _preload_words(self, start_index: int, count: int = 20):
        """预加载单词到缓存"""
        end_index = min(start_index + count, len(self.words))
        self.word_cache.extend(self.words[start_index:end_index])

    def get_word(self, index: int) -> Optional[Word]:
        """获取单词，支持缓存"""
        if not self.words:
            raise ValueError("词库为空")
            
        real_index = index % len(self.words)
        if not self.word_cache or real_index >= self.current_index + len(self.word_cache):
            self._preload_words(real_index)
            self.current_index = real_index
            
        cache_index = real_index - self.current_index
        return self.word_cache[cache_index]

    def get_review_words(self, count: int = 10) -> List[Word]:
        """获取需要复习的单词"""
        review_words = [
            word for word in self.words 
            if word.review_count > 0 and 
            (word.correct_count / word.review_count < 0.8 if word.review_count > 0 else True)
        ]
        return random.sample(review_words, min(count, len(review_words)))

    def add_to_wrong_words(self, word: Word) -> None:
        """添加到错词本"""
        if word not in self.wrong_words:
            self.wrong_words.append(word)

    def remove_from_wrong_words(self, word: Word) -> None:
        """从错词本中移除"""
        if word in self.wrong_words:
            self.wrong_words.remove(word)

    def update_word_status(self, word: Word, correct: bool) -> None:
        """更新单词学习状态"""
        try:
            word.last_reviewed = datetime.now()
            word.review_count += 1
            if correct:
                word.correct_count += 1
                self.remove_from_wrong_words(word)
            else:
                self.add_to_wrong_words(word)

            # 更新难度级别
            if word.review_count >= 3:
                accuracy = word.correct_count / word.review_count
                if accuracy > 0.8:
                    word.difficulty_level = 0
                elif accuracy > 0.6:
                    word.difficulty_level = 1
                else:
                    word.difficulty_level = 2

            # 记录复习历史
            date = datetime.now().strftime('%Y-%m-%d')
            if date not in self.review_history:
                self.review_history[date] = {'total': 0, 'correct': 0}
            self.review_history[date]['total'] += 1
            if correct:
                self.review_history[date]['correct'] += 1

            self.save_progress()
        except Exception as e:
            print(f"更新单词状态失败: {str(e)}")

    def get_statistics(self) -> Dict:
        """获取学习统计信息"""
        total_words = len(self.words)
        reviewed_words = sum(1 for word in self.words if word.review_count > 0)
        mastered_words = sum(1 for word in self.words 
                           if word.review_count > 0 and 
                           word.correct_count / word.review_count >= 0.8)
        
        return {
            'total_words': total_words,
            'reviewed_words': reviewed_words,
            'mastered_words': mastered_words,
            'wrong_words_count': len(self.wrong_words),
            'review_history': self.review_history
        }
