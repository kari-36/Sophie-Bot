import pytest
from tgintegration import BotController, InvalidResponseError, Response


class TestArgumentParser:

    @pytest.mark.asyncio
    async def test_args(self, controller: BotController):
        args = ["test", "69420"]
        async with controller.collect(count=1) as res:  # type: Response
            message = await controller.send_command("testargs", args=args)

        assert message.text == res.full_text

    @pytest.mark.asyncio
    async def test_missing_args(self, controller: BotController):
        async with controller.collect(count=1) as res:  # type: Response
            await controller.send_command("testargs", args=['test'])
        assert res.full_text == "Not enough arghs! missing field 'arg_two'"

    @pytest.mark.asyncio
    async def test_none_args(self, controller: BotController):
        async with controller.collect(count=1) as res:  # type: Response
            await controller.send_command('testargs')
        assert res.full_text == 'Not enough args!'

    @pytest.mark.asyncio
    async def test_inherited(self, controller: BotController):
        args = ['test', '123', 'meh']
        async with controller.collect(count=1) as res:  # type: Response
            await controller.send_command("testinheritedargs", args=args)

        assert res.full_text == " ".join(args)

    @pytest.mark.asyncio
    async def test_default_arg(self, controller: BotController):
        async with controller.collect(count=1) as res:  # type: Response
            await controller.send_command("testdefaultarg")

        assert res.full_text == 'default'

    @pytest.mark.asyncio
    async def test_arg_parse_method(self, controller: BotController):
        args = ['CaPiTal', "Nothing"]
        async with controller.collect(count=1) as res:  # type: Response
            await controller.send_command("testargparsemethod", args=args)

        assert res.full_text == "capital PASSED"

    @pytest.mark.asyncio
    async def test_arg_parse_method_blocking(self, controller: BotController):
        with pytest.raises(InvalidResponseError):
            async with controller.collect(max_wait=2):  # type: Response
                await controller.send_command("testargparsemethodblock", args=['something'])

    @pytest.mark.asyncio
    async def test_optional_args(self, controller: BotController):
        async with controller.collect(count=1) as res:  # type: Response
            await controller.send_command("testoptionalargs", args=['something'])
        assert res.full_text == "something None"
