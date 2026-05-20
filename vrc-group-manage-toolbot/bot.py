import nonebot
from nonebot.adapters.onebot.v11 import Adapter
from nonebot import get_driver, logger
from services.scheduler_service import scheduler_service

# 初始化 NoneBot
nonebot.init()

# 注册适配器
driver = get_driver()
driver.register_adapter(Adapter)


@driver.on_startup
async def _startup():
    scheduler_service.start_scheduler()

@driver.on_shutdown
async def _shutdown():
    from utils import get_vrc_client
    await get_vrc_client().close()
    scheduler_service.shutdown_scheduler()


app = nonebot.get_app()

if __name__ == "__main__":
    nonebot.load_from_toml("pyproject.toml")
    nonebot.run()
