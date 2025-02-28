import json
import os

class ConfigManager:
    def __init__(self, config_path="config/config.json"):
        self.config_path = config_path
        self.config = self.load_config()

    def validate_config(self, config):
        required_fields = {
            'display': ['show_translations', 'show_sentences'],
            'mode': ['default'],
            'memorization': ['algorithm', 'intervals']
        }
        
        for section, fields in required_fields.items():
            if section not in config:
                raise ValueError(f"配置缺少{section}部分")
            for field in fields:
                if field not in config[section]:
                    raise ValueError(f"配置缺少{section}.{field}字段")

    def load_config(self):
        """加载配置文件"""
        if not os.path.exists(self.config_path):
            self._create_default_config()
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            self.validate_config(config)
            return config

    def update_config(self, new_config):
        """更新配置"""
        self.config.update(new_config)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=4)
    
    def get(self, key):
        """支持嵌套键的配置获取，如 'display.show_phonetics'"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return None
        return value

STUDY_MODES = {
    '1': ('学习模式', 'normal_study_mode'),
    '2': ('复习模式', 'review_mode'),
    '3': ('智能模式', 'smart_mode'),  # 根据记忆算法自动安排
}

# class ModeManager:
    
#     def __init__(self):
#         self.mode = "vocab"  # 默认模式

#     def switch_mode(self, mode):
#         """切换学习模式"""
#         if mode in ["vocab", "long_sentence"]:
#             self.mode = mode

#     def get_mode(self):
#         """获取当前模式"""
#         return self.mode


