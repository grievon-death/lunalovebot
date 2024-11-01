from datetime import datetime, timedelta, timezone


def naive_dt_utc_br(dt: datetime) -> str:
    """
    Retorna uma string no formato de data BR.
    """
    return dt.astimezone(timezone(timedelta(hours=-3)))\
        .strftime('%d/%m/%Y %H:%M:%S')
