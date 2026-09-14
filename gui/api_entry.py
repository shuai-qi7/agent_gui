"""
外部调用入口，第三方项目只需要导入这个模块
调用函数 run_gui(model_name, model_name_dict, think_timeout, core_task_func)
model_name: 模型名称；model_name_list: 模型名称列表；think_timeout：预计模型的思考时间；core_task_func：核心的输出函数，输入是文本或文档
其中think_timeout可选择False关闭显示思考时间功能
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from typing import Callable, Union
from PySide6.QtWidgets import QApplication
from gui.main_windows import MainWindow
from gui.task_runner import test_func


# 对外暴露的主接口
def run_gui(
    model_name: str = "qwen3.8-max",
    model_name_dict: dict = {"qwen3.8-max": "API","qwen3-8B": "LOCAL"},
    think_timeout: Union[int, bool] = False,
    core_task_func: Callable[[str, str, int], str] = test_func,
) -> None:
    """
    启动配液智能体GUI界面
    :param model_name: 选择使用的模型名称，例如 "qwen3.8-max"
    :param model_name_dict: 可选的模型名称字典，键为模型名称，值为模型类型（如 "API" 或 "LOCAL"）
    :param think_timeout: 预计思考耗时，单位秒（界面提示用），可设置为 False 关闭显示思考时间功能
    :param core_task_func: 外部核心处理函数，签名必须：def func(user_input:str, model:str, timeout:int) -> str
    """
    # QApplication 单例处理
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    # 实例化主窗口，把外部参数注入窗口实例
    window = MainWindow(model_name, model_name_dict, think_timeout, core_task_func)

    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run_gui()
