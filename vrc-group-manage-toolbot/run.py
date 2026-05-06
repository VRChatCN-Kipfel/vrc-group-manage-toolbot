"""
启动脚本 - 用于开发环境
"""

import nonebot
from nonebot.adapters.onebot.v11 import Adapter

if __name__ == "__main__":
    # 初始化 NoneBot
    nonebot.init()
    
    # 注册适配器
    driver = nonebot.get_driver()
    driver.register_adapter(Adapter)
    
    # 加载内置插件
    nonebot.load_builtin_plugins("echo")
    
    # 从 pyproject.toml 加载配置和插件
    nonebot.load_from_toml("pyproject.toml")
    
    # 运行 bot
    nonebot.run(app="bot:app")
