import logging
from random import choice
from datetime import datetime

from discord import Embed, Intents, Message
from discord.ext.commands import Context, Bot

from core import naive_dt_utc_br
from models.quote import Quotes
from models.indicator import Indicators

LOGGER = logging.getLogger(__name__)
ERROR_MESSAGE = '**Ooops.**\n> Alguma coisa deu errado, melhor fuçar os logs!'
ARG_FAULT = '**Ooops.**\n> É necessária uma mensagem!'

client = Bot(command_prefix='--', intents=Intents.all())


@client.event
async def on_message(message: Message) -> None:
    LOGGER.debug('\nAuhtor: %s\nMessage: %s' % (message.author.name, message.content))
    await client.process_commands(message)


@client.command(aliases=['q'])
async def quote(ctx: Context) -> None:
    """
    Salva uma mensagem no banco de dados.
    """
    server = ctx.guild.id
    all_message = ctx.message.content
    all_message = all_message.split(' ')
    _, message = all_message[0], all_message[1:]
    message = ' '.join(message)

    if not message:
        await ctx.send(ARG_FAULT)
        return

    try:
        model = Quotes(
            message=message,
            server=server,
            created_by=ctx.author.name,
            created_at=datetime.now(),
        )
        model.create()
        indicator = Indicators(server)
        await indicator.add_quote_for(ctx.author.name)
    except Exception as e:
        LOGGER.error(e)
        await ctx.send(ERROR_MESSAGE)
        return

    try:
        embed = Embed(type='rich', )
        embed.add_field(
            name='Usuário',
            value=model.created_by,
        )
        embed.add_field(
            name='Data',
            value=naive_dt_utc_br(model.created_at),
        )
        embed.add_field(
            name='Mensagem',
            value=model.message,
            inline=False,
        )
        await ctx.send(embed=embed)
    except Exception as e:
        LOGGER.exception(e)
        await ctx.send(ERROR_MESSAGE)


@client.command(aliases=['rq'])
async def randomquote(ctx: Context) -> None:
    """
    Captura uma mensasgem aleatória.
    """
    try:
        server = ctx.guild.id
        model = Quotes()
        ids = model.get_ids_by_server(server)
        id = choice(ids)
        quote = model.get(id)

        if not quote:
            await ctx.send(ERROR_MESSAGE)

        indicator = Indicators(server)
        await indicator.add_request_for(ctx.author.name)
        await ctx.send(quote.message)
    except Exception as e:
        LOGGER.error(e)
        await ctx.send(ERROR_MESSAGE)


@client.command(aliases=['i'])
async def indicators(ctx: Context, quantity: int=5) -> None:
    """
    Retorna o TOP criadores de mensagens e os que mais usam o comando randomquote.
    quantity: int :Tamanho da lista.
    """
    server = ctx.guild.id
    indicator = Indicators(server=server)

    try:
        quoters = await indicator.get_quoters()
        requesters = await indicator.get_requesters()
        quoters_k = sorted(quoters, key=quoters.get, reverse=True) if quoters else []
        requesters_k = sorted(requesters, key=requesters.get, reverse=True) if requesters else []
    except Exception as e:
        LOGGER.error(e)
        await ctx.send(ERROR_MESSAGE)
        return

    try:
        _quoters = Embed(type='rich')
        _requesters = Embed(type='rich')

        for key in quoters_k[quantity:]:
            _quoters.add_field(
                name=key,
                value=quoters[key],
            )

        for key in requesters_k[quantity:]:
            _requesters.add_field(
                name=key,
                value=requesters[key],
            )

        await ctx.send(f'**Top {quantity} criadores:**', embed=_quoters) if quoters else None
        await ctx.send(f'**Top {quantity}:**', embed=_requesters) if requesters else None
    except Exception as e:
        LOGGER.error(e)
        await ctx.send(ERROR_MESSAGE)
