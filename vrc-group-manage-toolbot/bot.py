import nonebot
from nonebot.adapters.onebot.v11 import Adapter
from nonebot import get_driver, logger
from services.scheduler_service import scheduler_service
from services.global_config import global_config
from services.config_reload import config_reload_service

nonebot.init()

driver = get_driver()
driver.register_adapter(Adapter)


@driver.on_startup
async def _startup():
    scheduler_service.start_scheduler()

    async def on_config_reload(generation: int):
        await global_config.reload()
        logger.info(f"配置热重载完成 generation={generation}")

    config_reload_service.subscribe(on_config_reload, first=True)
    config_reload_service.start_watching()


@driver.on_shutdown
async def _shutdown():
    config_reload_service.stop_watching()
    from utils import get_vrc_client
    await get_vrc_client().close()
    scheduler_service.shutdown_scheduler()


app = nonebot.get_app()

if __name__ == "__main__":
    nonebot.load_from_toml("pyproject.toml")
    nonebot.run()
