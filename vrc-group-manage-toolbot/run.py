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
    
    # 从 pyproject.toml 加载配置和插件
    nonebot.load_from_toml("pyproject.toml")
    
    # 运行 bot（不引用 bot:app，避免重复初始化）
    nonebot.run()
