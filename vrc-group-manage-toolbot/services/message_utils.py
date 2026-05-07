from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nonebot.matcher import Matcher

MAX_MESSAGE_LENGTH = 3800


async def send_long_message(matcher: "Matcher", text: str):
    for i in range(0, len(text), MAX_MESSAGE_LENGTH):
        chunk = text[i : i + MAX_MESSAGE_LENGTH]
        if i + MAX_MESSAGE_LENGTH >= len(text):
            await matcher.finish(chunk)
        else:
            await matcher.send(chunk)


def format_success(msg: str) -> str:
    return f"✅ {msg}"


def format_error(reason: str, hint: str = "") -> str:
    text = f"❌ 操作失败：{reason}"
    if hint:
        text += f"\n💡 提示：{hint}"
    return text


def format_query_result(title: str, content: str) -> str:
    return f"""【{title}】
{'─' * 20}
{content}
{'─' * 20}"""
