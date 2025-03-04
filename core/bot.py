import logging
from random import choice
from datetime import datetime

from discord import Embed, Intents, Message
from discord.ext.commands import Context, Bot

from core import (Controll, naive_dt_utc_br, get_command_args,
                  get_command_message, prettify_quote)
from models.quote import Quotes
from models.indicator import Indicators
from models.lunch_place import LunchPlace
from models.news import News

LOGGER = logging.getLogger(__name__)

ERROR_MESSAGE = '**Ooops.**\n> Alguma coisa deu errado, melhor fuçar os logs!'
ARG_FAULT = '**Ooops.**\n> É necessária uma mensagem!'
WITHOUT_INFO = '**Ooops.**\n> Não há informações no momento.'
INVALID_ARGS = '**Ooops.**\n> Valor inválido!'

client = Bot(command_prefix='--', intents=Intents.all())


@client.event
async def on_message(message: Message) -> None:
    try:
        if not message.guild:
            return

        await client.process_commands(message)
    except Exception as e:
        LOGGER.error(e)


@client.command(aliases=['q'])
async def quote(ctx: Context) -> None:
    """
    Salva uma mensagem no banco de dados.
    """
    server = ctx.guild.id
    message = get_command_message(ctx.message.content)

    if not message:
        await ctx.send(ARG_FAULT)
        return
    elif not isinstance(message, str):
        await ctx.send(INVALID_ARGS)
        return

    try:
        model = Quotes(
            message=message,
            server=server,
            created_by=ctx.author.name,
            created_at=datetime.now(),
        )
        model.create()
    except Exception as e:
        LOGGER.error(e)
        await ctx.send(ERROR_MESSAGE)
        return
    else:
        indicator = Indicators(server)
        await indicator.q_usage(ctx.author.name)
        

    try:
        await ctx.send(embed=prettify_quote(model))
    except Exception as e:
        LOGGER.exception(e)
        await ctx.send(ERROR_MESSAGE)


@client.command(aliases=['rq'])
async def random_quote(ctx: Context) -> None:
    """
    Captura uma mensasgem aleatória.
    """
    try:
        server = ctx.guild.id
        model = Quotes()
        ids = model.get_ids_by_server(server)

        if not ids:
            await ctx.send(WITHOUT_INFO)
            return

        id = choice(ids)
        quote = model.get(id)
        await ctx.send(f'{quote.message}')
    except Exception as e:
        LOGGER.error(e)
        await ctx.send(ERROR_MESSAGE)
    else:
        indicator = Indicators(server)
        controll = Controll(server)
        await indicator.rq_usage(ctx.author.name)
        await controll.set_last_quote(id)


@client.command(aliases=['iq'])
async def indicator_quote(ctx: Context, quantity: int=5) -> None:
    """
    Indicador do top de usuário que mais usam o comando `quote`.
    quantity: <int> :Tamanho máximo da lista.
    """
    server = ctx.guild.id
    indicator = Indicators(server=server)

    try:
        quoters = await indicator.q_get()

        if not quoters:
            await ctx.send(WITHOUT_INFO)
            return

    except Exception as e:
        LOGGER.error(e)
        await ctx.send(ERROR_MESSAGE)
        return

    try:
        quoters_k = sorted(quoters, key=quoters.get, reverse=True) if quoters else []
        _quoters = Embed(type='rich')

        for key in quoters_k[:quantity]:
            _quoters.add_field(
                name=key,
                value=quoters[key],
            )

        await ctx.send(f'**Top {quantity} criadores:**', embed=_quoters)
    except Exception as e:
        LOGGER.error(e)
        await ctx.send(ERROR_MESSAGE)


@client.command(aliases=['irq'])
async def indicator_random_quote(ctx: Context, quantity: int=5) -> None:
    """
    Retorna o TOP criadores de mensagens e os que mais usam o comando randomquote.
    quantity: int :Tamanho da lista.
    """
    server = ctx.guild.id
    indicator = Indicators(server=server)

    try:
        requesters = await indicator.rq_get()

        if not requesters:
            await ctx.send(WITHOUT_INFO)
            return

    except Exception as e:
        LOGGER.error(e)
        await ctx.send(ERROR_MESSAGE)
        return

    try:
        requesters_k = sorted(requesters, key=requesters.get, reverse=True)
        _requesters = Embed(type='rich')

        for key in requesters_k[:quantity]:
            _requesters.add_field(
                name=key,
                value=requesters[key],
            )

        await ctx.send(f'**Top {quantity} requesters:**', embed=_requesters)

    except Exception as e:
        LOGGER.error(e)
        await ctx.send(ERROR_MESSAGE)


@client.command(aliases=['qid'])
async def quote_by_id(ctx: Context) -> None:
    """
    Retorna uma mensagem pelo ID.
    """
    server = ctx.guild.id

    try:
        id = int(get_command_args(ctx.message.content))
        model = Quotes()
        quote = model.get(id)

        if not quote:
            await ctx.send(WITHOUT_INFO)

        await ctx.send(f'{quote.message}\n> By: {quote.created_by}')
    except Exception as e:
        LOGGER.error(e)
        await ctx.send(INVALID_ARGS)
        return
    else:
        indicator = Indicators(server)
        controll = Controll(server)
        await indicator.rq_usage(ctx.author.name)
        await controll.set_last_quote()


@client.command(aliases=['l'])
async def lunch_place(ctx: Context) -> None:
    """
    Salva um local de almoço no banco de dados.
    """
    server = ctx.guild.id
    place = get_command_message(ctx.message.content)

    if not place:
        await ctx.send(ARG_FAULT)
        return

    try:
        model = LunchPlace(
            place=place,
            server=server,
            created_by=ctx.author.name,
            created_at=datetime.now(),
        )
        model.create()
    except Exception as e:
        LOGGER.error(e)
        await ctx.send(ERROR_MESSAGE)
        return

    try:
        embed = Embed(type='rich')
        embed.add_field(
            name='ID',
            value=model.id,
        )
        embed.add_field(
            name='Usuário',
            value=model.created_by,
            inline=False,
        )
        embed.add_field(
            name='Data',
            value=naive_dt_utc_br(model.created_at),
            inline=False,
        )
        embed.add_field(
            name='Local',
            value=model.place,
            inline=False,
        )
        await ctx.send(embed=embed)
    except Exception as e:
        LOGGER.exception(e)
        await ctx.send(ERROR_MESSAGE)


@client.command(aliases=['rl', 'onde_vamos_almoçar'])
async def random_lunch_place(ctx: Context) -> None:
    """
    Captura um local de almoço aleatório.
    """
    try:
        server = ctx.guild.id
        model = LunchPlace()
        ids = model.get_ids_by_server(server)
        _id = choice(ids)
        place = model.get(_id)

        if not place:
            await ctx.send(WITHOUT_INFO)

        await ctx.send(f'> {model.get_random_intro()} {place.place}!')
    except Exception as e:
        LOGGER.error(e)
        await ctx.send(ERROR_MESSAGE)


@client.command(aliases=['lqi'])
async def last_quote_info(ctx: Context) -> None:
    """
    Captura todas as informações do quote anterior.
    """
    try:
        model = Quotes()
        controll = Controll(ctx.guild.id)
        id = await controll.get_last_quote()
        quote = model.get(id)

        if not quote:
            await ctx.send(WITHOUT_INFO)
            return

        await ctx.send('', embed=prettify_quote(quote))
    except Exception as e:
        LOGGER.error(e)
        await ctx.send(ERROR_MESSAGE)


@client.command(aliases=['n', 'nw', 'jornal'])
async def news(ctx: Context) -> None:
    """
    Captura as últimas 5 notícias em uma fonte selecionada. Opções: [bbc, cnn, tecmundo]
    """
    try:
        source = get_command_args(ctx.message.content) or 'bbc'
        _news = News(source=source.lower())
        responses = await _news.get()

        for response in responses[:5]:
            embed = Embed(type='rich')
            embed.add_field(
                name='Título',
                value=response.new,
                inline=False
            )
            embed.add_field(
                name='Publicado',
                value=response.date,
                inline=False,
            )
            embed.add_field(
                name='Notícia completa',
                value=response.link,
                inline=False,
            )
            embed.set_image(url=response.image)
            await ctx.send('', embed=embed)

    except Exception as e:
        LOGGER.error(e)
        await ctx.send(ERROR_MESSAGE)
