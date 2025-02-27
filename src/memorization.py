import json
import os
from datetime import datetime, timedelta

class MemoryAlgorithm:
    def __init__(self):
        self.intervals = [1, 3, 7, 15, 30]  # 间隔天数
        self.word_stats = {}  # 记录每个单词的学习状态
        self.stats_file = "data/memory_stats.json"
        self.load_stats()

    def load_stats(self):
        if os.path.exists(self.stats_file):
            with open(self.stats_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for word, stats in data.items():
                    stats['next_review'] = datetime.fromisoformat(stats['next_review'])
                self.word_stats = data

    def save_stats(self):
        os.makedirs(os.path.dirname(self.stats_file), exist_ok=True)
        with open(self.stats_file, 'w', encoding='utf-8') as f:
            data = {word: {**stats, 
                   'next_review': stats['next_review'].isoformat()} 
                   for word, stats in self.word_stats.items()}
            json.dump(data, f, ensure_ascii=False, indent=2)

    def init_word(self, word):
        """初始化单词学习状态"""
        if word not in self.word_stats:
            self.word_stats[word] = {
                'level': 0,  # 当前复习级别
                'next_review': datetime.now(),  # 下次复习时间
                'correct_count': 0,  # 正确次数
                'total_count': 0,  # 总次数
            }

    def update_memory(self, word, correct):
        """更新单词记忆状态"""
        self.init_word(word)
        stats = self.word_stats[word]
        stats['total_count'] += 1

        if correct:
            stats['correct_count'] += 1
            # 根据正确率动态调整级别
            accuracy = stats['correct_count'] / stats['total_count']
            if accuracy >= 0.8 and stats['level'] < len(self.intervals) - 1:
                stats['level'] += 1
        else:
            # 错误时降级更多，增加复习频率
            stats['level'] = max(0, stats['level'] - 2)

        # 动态调整复习间隔
        base_days = self.intervals[stats['level']]
        accuracy = stats['correct_count'] / stats['total_count']
        adjusted_days = int(base_days * (0.5 + accuracy))
        
        stats['next_review'] = datetime.now() + timedelta(days=max(1, adjusted_days))
        self.save_stats()

    def should_review(self, word):
        """检查单词是否需要复习"""
        if word not in self.word_stats:
            return True
        return datetime.now() >= self.word_stats[word]['next_review']

    def get_mastery_level(self, word):
        """获取掌握程度 (0-100)"""
        if word not in self.word_stats:
            return 0
        stats = self.word_stats[word]
        if stats['total_count'] == 0:
            return 0
        return int((stats['correct_count'] / stats['total_count']) * 100)
