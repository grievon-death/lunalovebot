import logging

from discord import Embed, Intents, Message
from discord.ext.commands import Context, Bot


from models.quote import Quotes
from models.indicator import Indicators

LOGGER = logging.getLogger(__name__)

client = Bot(command_prefix='--', intents=Intents.all())


@client.event
async def on_message(message: Message) -> None:
    LOGGER.debug('\nAuhtor: %s\nMessage: %s' % (message.author.name, message.content))
    await client.process_commands(message)


@client.command(aliases=['q'])
async def quote(ctx: Context) -> str:
    """
    Salva uma mensagem no banco de dados.
    """
    server = ctx.guild.id
    all_message = ctx.message.content
    all_message = all_message.split(' ')
    _, message = all_message[0], all_message[1:]
    message = ' '.join(message)

    if not message:
        return await ctx.send('Ooops, você não escreveu nada!')

    try:
        model = Quotes()
        model.message = message
        model.created_by = ctx.author.name
        model.server = server
        response = await model.create()
    except Exception as e:
        LOGGER.error(e)
        return await ctx.send(f'Foi mal, aconteceu que {str(e.args)}')

    # TODO: Fazer embed no response.
    return await ctx.send(str(response))
