import nonebot
from nonebot.adapters.onebot.v11 import Adapter
from nonebot import get_driver

# 初始化 NoneBot
nonebot.init()

# 注册适配器
driver = get_driver()
driver.register_adapter(Adapter)


@driver.on_shutdown
async def _shutdown():
    from utils import get_vrc_client
    await get_vrc_client().close()


app = nonebot.get_app()

if __name__ == "__main__":
    nonebot.load_from_toml("pyproject.toml")
    nonebot.run()
