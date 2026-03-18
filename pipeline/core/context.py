# 全局数据容器
class WorkflowContext:

    def __init__(self):
        self.data = {}

    def set(self, key, value):
        self.data[key] = value

    def setdefault(self, key, value):
        if key not in self.data:
            self.data[key] = value
        return self.data[key]

    def get(self, key, default=None):
        return self.data.get(key, default)