from PySide6.QtCore import QRunnable, QObject, Signal
import os
import re
from langchain_openai import ChatOpenAI

model = ChatOpenAI(
    model_name="qwen3.8-max",
    temperature=0,
    api_key=os.environ.get("QWEN_API_KEY"),
    base_url=os.environ.get("QWEN_BASE_URL")
)

def test_func(user_text: str) -> str:
    return model.invoke(user_text).content

class WorkerSignals(QObject):
    agent_reply_signal = Signal(str)

class AgentWorker(QRunnable):
    def __init__(self, user_text: str, task_func=test_func):
        super().__init__()
        self.user_text = user_text
        self.task_func = task_func
        self.signals = WorkerSignals()
        self.setAutoDelete(True) 

    def run(self):
        # 子线程执行任务函数
        reply_text = self.task_func(self.user_text)
        # 信号发送
        self.signals.agent_reply_signal.emit(reply_text)

