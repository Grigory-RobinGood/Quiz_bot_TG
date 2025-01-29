import asyncio

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery
from typing import Dict, Any, Callable, Awaitable


class CallbackQueryMiddleware(BaseMiddleware):
    def __init__(self):
        self.user_futures: Dict[int, asyncio.Future] = {}

    async def __call__(
            self,
            handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id
        if user_id in self.user_futures:
            future = self.user_futures[user_id]
            if not future.done():
                future.set_result(event)
            return  # Прекращаем дальнейшую обработку
        return await handler(event, data)



