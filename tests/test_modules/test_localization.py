import pytest
from tgintegration import BotController, Response


class TestLocalization:

    @pytest.mark.asyncio
    async def test_lang(self, controller: BotController):
        async with controller.collect(count=1) as res:  # type: Response
            await controller.send_command("/lang")
        assert res.messages[0].text == "Current Language is 🇺🇸 English (United States)"


