# AI Agent GUI

基于 **PySide6** 和 **LangChain OpenAI** 构建的桌面聊天界面。

项目提供统一的 `run_gui()` 接口，可以将外部大语言模型、LangChain 模型或自定义处理函数接入 GUI。AI 返回内容支持 Markdown，可显示标题、列表、引用、代码块和链接等格式。

## 安装依赖

### 使用 pip 安装

```bash
python -m pip install PySide6 langchain-openai
```

## 启动界面

直接运行接口入口文件：

```bash
python api_entry.py
```

`api_entry.py` 默认执行：

```python
if __name__ == "__main__":
    run_gui()
```

因此可以直接打开聊天界面。

## 对外接口

第三方程序只需要导入：

```python
from api_entry import run_gui
```

接口定义：

```python
def run_gui(
    model_name: str = "qwen3.8-max",
    model_name_dict: dict = {
        "qwen3.8-max": "API",
        "qwen3-8B": "LOCAL",
    },
    think_timeout: int | bool = False,
    core_task_func: callable = test_func,
) -> None:
    ...
```

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `model_name` | `str` | `"qwen3.8-max"` | GUI 启动后默认选择的模型 |
| `model_name_dict` | `dict` | 内置模型字典 | 可供用户选择的模型及其类型 |
| `think_timeout` | `int \| bool` | `False` | 预计思考时间，单位为秒；设置为 `False` 时关闭时间提示 |
| `core_task_func` | `Callable` | `test_func` | 实际处理用户输入并返回回复的函数 |

`model_name_dict` 的键是传给核心函数的模型名称，值是界面中展示的模型类型，例如：

```python
{
    "qwen3.8-max": "API",
    "qwen3-8B": "LOCAL",
}
```