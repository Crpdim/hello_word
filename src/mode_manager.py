class ModeManager:
    def __init__(self):
        self.mode = "vocab"  # 默认模式

    def switch_mode(self, mode):
        """切换学习模式"""
        if mode in ["vocab", "long_sentence"]:
            self.mode = mode

    def get_mode(self):
        """获取当前模式"""
        return self.mode
