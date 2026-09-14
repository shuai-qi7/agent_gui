# chat_store.py
import json
import os
import time
from pathlib import Path
from typing import List, Dict, Optional

# 存储文件路径，项目根目录生成聊天记录文件
CHAT_HISTORY_FILE = Path(__file__).parent.parent / "chat_history.json"


def _get_default_chat_file() -> List[Dict]:
    """返回空的默认对话列表"""
    return []


def load_all_conversations() -> List[Dict]:
    """读取全部本地对话，文件不存在返回空列表"""
    if not CHAT_HISTORY_FILE.exists():
        return _get_default_chat_file()
    try:
        with open(CHAT_HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            return _get_default_chat_file()
        return data
    except (json.JSONDecodeError, IOError):
        # 文件损坏，返回空
        return _get_default_chat_file()


def save_all_conversations(conversations: List[Dict]) -> None:
    """把全部对话写入本地 json"""
    CHAT_HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(CHAT_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(conversations, f, ensure_ascii=False, indent=2)


def create_new_conversation(title: str = "Untitled experiment") -> Dict:
    """创建新对话，返回对话dict"""
    now = time.strftime("%Y-%m-%d %H:%M")
    conv_id = str(int(time.time() * 1000))  # 使用时间戳当唯一id
    new_conv = {
        "conv_id": conv_id,
        "title": title,
        "create_time": now,
        "messages": []  # messages: [{"role":"user","content":"xxx"},{"role":"agent","content":"xxx"}]
    }
    conv_list = load_all_conversations()
    conv_list.insert(0, new_conv)  # 新对话放最上面
    save_all_conversations(conv_list)
    return new_conv


def get_conversation_by_id(conv_id: str) -> Optional[Dict]:
    """根据id获取单个对话"""
    conv_list = load_all_conversations()
    for item in conv_list:
        if item.get("conv_id") == conv_id:
            return item
    return None


def append_message(conv_id: str, role: str, content: str) -> bool:
    """给某个对话追加消息
    role: user / agent
    """
    conv_list = load_all_conversations()
    for item in conv_list:
        if item.get("conv_id") == conv_id:
            item["messages"].append({"role": role, "content": content})
            save_all_conversations(conv_list)
            return True
    return False


def update_conversation_title(conv_id: str, new_title: str) -> bool:
    """修改对话标题"""
    conv_list = load_all_conversations()
    for item in conv_list:
        if item.get("conv_id") == conv_id:
            item["title"] = new_title
            save_all_conversations(conv_list)
            return True
    return False


if __name__ == "__main__":
    # ========= 第一步测试：直接运行这个py测试存储功能 =========
    print("===测试新建对话===")
    new_chat = create_new_conversation(title="测试实验对话")
    print("新建对话：", new_chat)

    print("\n===测试追加消息===")
    append_message(new_chat["conv_id"], "user", "你好，配液")
    append_message(new_chat["conv_id"], "agent", "收到指令")

    print("\n===读取全部对话===")
    all_conv = load_all_conversations()
    for c in all_conv:
        print(f'id:{c["conv_id"]}, title:{c["title"]}, msg_count:{len(c["messages"])}')

    print("\n===按id读取单条对话===")
    one = get_conversation_by_id(new_chat["conv_id"])
    print(one)

    print("\n===修改标题===")
    update_conversation_title(new_chat["conv_id"], "修改后的标题")
    print(get_conversation_by_id(new_chat["conv_id"])["title"])
