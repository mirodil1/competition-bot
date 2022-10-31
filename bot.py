import asyncio
from datetime import datetime
import logging
from re import U

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from tgbot.config import load_config
from tgbot.filters.admin import AdminFilter
from tgbot.handlers.admin import register_admin
from tgbot.handlers.echo import register_echo
from tgbot.handlers.user import register_user
from tgbot.middlewares.environment import EnvironmentMiddleware
from tgbot.middlewares.check_sub import CheckSubscriptionMiddleware
from tgbot.misc.db import db

import random
from datetime import datetime
logger = logging.getLogger(__name__)


def register_all_middlewares(dp, config):
    dp.setup_middleware(EnvironmentMiddleware(config=config))
    dp.setup_middleware(CheckSubscriptionMiddleware())

def register_all_filters(dp):
    dp.filters_factory.bind(AdminFilter)


def register_all_handlers(dp):
    register_admin(dp)
    register_user(dp)

    register_echo(dp)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info("Starting bot")
    config = load_config(".env")

    storage = RedisStorage2() if config.tg_bot.use_redis else MemoryStorage()
    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp = Dispatcher(bot, storage=storage)

    bot['config'] = config

    # create db
    await db.create()

    register_all_middlewares(dp, config)
    register_all_filters(dp)
    register_all_handlers(dp)

    # full_name = ["name", "surname", "middle-name"]

    # for i in range(100):
    #     await db.add_user(
    #             id=random.randint(100000, 99999999),
    #             full_name=random.choice(full_name),
    #             phone_number=None,
    #             username=None,
    #             score=random.randint(100, 9999),
    #             joined_date=datetime.now()
    #         )

    # start
    try:
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
