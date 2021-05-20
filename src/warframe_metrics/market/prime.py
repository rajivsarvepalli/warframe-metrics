"""A module for analyzing prime parts."""
import datetime
import time
from contextlib import nullcontext
from datetime import timezone
from typing import List
from typing import Optional
from typing import Union

import pandas as pd
from alive_progress import alive_bar

from ..utils.collect_data import collect_data
from ..utils.collect_data import from_url
from ..utils.collect_data import to_class
from ..utils.collect_data import to_stats
from ..utils.constants import ITEMS_URL
from ..utils.constants import STATS_URL
from ..utils.schema import ItemStats
from ..utils.schema import LiveStats
from ..utils.schema import ShortItem
from ..utils.schema import Stat
from ..utils.schema import Stats


def best_primes_simple(vault_df: pd.DataFrame, buy: bool = False) -> pd.DataFrame:
    """Gets the best primes in order of the returned dataframe.

    Args:
        vault_df: The dataframe with columns of "Last Unvaulting", "Vault Date",
            "Item Name", and "Item Type". This format essentially follows from the
            chart on the wiki (https://warframe.fandom.com/wiki/Prime_Vault).
        buy: Whether you are trying to buy or sell.

    Returns:
        A pandas dataframe sorted in order of prefence. The first ones are either
        the best ranked to buy or sell (based on the parameter `buy`).
    """
    df = vault_df.copy()
    df["Last Unvaulting"] = pd.to_datetime(df["Last Unvaulting"]).dt.tz_localize(
        timezone.utc
    )
    df["Vault Date"] = pd.to_datetime(df["Vault Date"]).dt.tz_localize(timezone.utc)
    df["Currently Vaulted"] = df["Last Unvaulting"] < (
        datetime.datetime.now(tz=timezone.utc) - datetime.timedelta(days=120)
    )
    if buy:
        # df_refined = df.drop(df[df["Current Vaulted"] == True].index, inplace=False)
        df_refined = df.sort_values(
            ["Last Unvaulting", "Vault Date"], ascending=[False, True]
        )
    else:
        # df_refined = df.drop(df[df["Current Vaulted"] == False].index, inplace=False)
        df_refined = df.sort_values(
            ["Last Unvaulting", "Vault Date"], ascending=[True, False]
        )
    return df_refined


def get_change(current: float, previous: float) -> float:
    """Get the percent change."""
    if current == previous:
        return 100.0
    if previous != 0:
        return (abs(current - previous) / previous) * 100.0
    else:
        return 0


def generate_names(prime_items: ItemStats, vault_csv: str) -> pd.DataFrame:
    """Generate names for prime parts within the csv."""
    vault_csv = pd.read_csv(vault_csv)
    names_to_items = dict((k.lower(), v) for k, v in prime_items.name_items.items())
    new_rows = []
    for _, row in vault_csv.iterrows():
        item_name = row["Item Name"].lower()
        row = row.to_dict()
        for prime_name in names_to_items:
            if item_name in prime_name:
                row["Item Name"] = prime_name.title()
                new_rows.append(row)
                row = row.copy()
    return pd.DataFrame(new_rows)


def collect_prime_data(progress_bar: bool = False) -> ItemStats:
    """Collects primes from warframe market. Waits 1 second per 10 items collected."""
    json_data = from_url(ITEMS_URL)
    json_data = collect_data(json_data, ["payload", "items"])
    items = to_class(ShortItem, json_data)
    prime_items = []
    prime_stats = []
    if progress_bar:
        cm = alive_bar(len(items))
    else:
        cm = nullcontext()
    with cm as bar:
        for j, i in enumerate(items):
            if "prime" in i.item_name.lower():
                json_data = from_url(STATS_URL % (i.url_name))
                stat_closed = collect_data(
                    json_data, ["payload", "statistics_closed", "90days"]
                )
                stat_live = collect_data(
                    json_data, ["payload", "statistics_live", "48hours"]
                )
                stat_closed = to_class(Stats, stat_closed)
                stat_live = to_class(LiveStats, stat_live)
                stat = to_stats(stat_closed, stat_live, i.item_name)
                prime_stats.append(stat)
                prime_items.append(i)
                if j % 10 == 0:
                    time.sleep(1)
            if type(cm) is not nullcontext:
                bar()

    return ItemStats(prime_items, prime_stats)


def find_index(
    stat: Stat,
    unvault_date: datetime.datetime,
    time_delta: datetime.timedelta,
    num_days: Optional[int] = None,
) -> int:
    """Finds the index within the given timeframe from `Stat` object."""
    dates = stat.dates
    min_date = min(unvault_date, datetime.datetime.now(tz=timezone.utc) - time_delta)
    i = j = 0
    while dates[i] < min_date and i < len(dates):
        i += 1
    if num_days is None:
        j = len(dates)
    else:
        j = i + 1
        max_date = dates[i] + datetime.timedelta(days=num_days)
        while dates[j] < max_date and j < len(dates):
            j += 1
    return i, j


def get_stat_within_date(
    stat: Stat,
    stat_name: str,
    unvault_date: datetime.datetime,
    time_delta: datetime.timedelta,
    buy: Optional[bool] = None,
    num_days: Optional[int] = None,
) -> List[Union[float, int, datetime.datetime]]:
    """Finds the statistics within the given timeframe from `Stat` object."""
    # give the market time to settle down.
    unvault_date = unvault_date + datetime.timedelta(days=10)
    if buy is None:
        stat_list = getattr(stat, stat_name)
        i, j = find_index(stat, unvault_date, time_delta, num_days)
    elif buy:
        stat_list = getattr(stat.live_stat_buy, stat_name)
        i, j = find_index(stat.live_stat_buy, unvault_date, time_delta, num_days)
    else:
        stat_list = getattr(stat.live_stat_sell, stat_name)
        i, j = find_index(stat.live_stat_sell, unvault_date, time_delta, num_days)
    if i >= len(stat_list):
        return [0]
    return stat_list[i:j]


def best_prime_complex(
    vault_csv: str, prime_data: ItemStats, buy: bool = False
) -> pd.DataFrame:
    """Gets the best primes based on a ranking system.

    Collects the best primes based on a ranking system. This ranking system
    esentially generates a metric of 4 normalized metrics. The 4 metrics
    used are ratio of volume bought to volume sold, the price difference over
    between now and unvaulting time, the percent price difference over
    between now and unvaulting time, and the date difference between now and
    the unvaulting time. These 4 metrics are normalized between 0 and 1, and
    averaged. This average of the 4 metrics is used to rank the items. When buying
    items, ascending order is used, otherwise, descending order is used.

    Args:
        vault_csv: A string (can be a download url) of the location of the csv file
            for vault dates. This must have columns of "Last Unvaulting", "Vault Date",
            "Item Name", and "Item Type". This format essentially follows from
            the chart on the wiki (https://warframe.fandom.com/wiki/Prime_Vault).
        prime_data: The `ItemStats` object for prime data. Only prime data is required,
            and additional data will not affect the rankings.
        buy: A boolean representing whether we are buying or selling warframe parts.

    Returns:
        A dataframe sorted in the desired order based on the parameter `buy`.
    """
    vault_df = generate_names(prime_data, vault_csv)
    best_primes = best_primes_simple(vault_df, buy=buy)
    percent_thresh = 30
    days_to_consider = 10
    time_delta = datetime.timedelta(days=120)
    rows_list = []
    for _, p in best_primes.iterrows():
        item = prime_data.get_item(p["Item Name"])
        stat = prime_data.get_stats(item.id)

        unvaulted_date = p["Last Unvaulting"]
        if unvaulted_date is None:
            unvaulted_date = datetime.datetime.now(
                tz=timezone.utc
            ) - datetime.timedelta(days=90)
        date_diff = datetime.datetime.now(tz=timezone.utc) - unvaulted_date
        max_buys = get_stat_within_date(
            stat, "max_prices", unvaulted_date, time_delta, buy=True
        )
        min_sells = get_stat_within_date(
            stat, "min_prices", unvaulted_date, time_delta, buy=False
        )
        # max_buys = stat.get_live_stats('max_prices', buy=True)
        # min_sells = stat.get_live_stats('min_prices', buy=False)
        min_sell = sum(min_sells) / len(min_sells)
        max_buy = sum(max_buys) / len(max_buys)

        if get_change(max_buy, min_sell) > percent_thresh:
            selling_price = min_sell
        else:
            selling_price = (max_buy + min_sell) / 2.0
        prev_lows = get_stat_within_date(
            stat,
            "avg_prices",
            unvaulted_date,
            time_delta,
            buy=None,
            num_days=days_to_consider,
        )
        prev_low = sum(prev_lows) / len(prev_lows)
        volumes_buy = get_stat_within_date(
            stat, "volumes", unvaulted_date, time_delta, buy=True
        )
        volume_buy = sum(volumes_buy)
        volumes_sell = get_stat_within_date(
            stat, "volumes", unvaulted_date, time_delta, buy=False
        )
        volume_sell = sum(volumes_sell)
        diff = selling_price - prev_low
        percent_diff = get_change(selling_price, prev_low)
        volume_ratio = volume_buy / volume_sell
        row = {
            "Item Name": p["Item Name"],
            "Volume Ratio": volume_ratio,
            "Price Diff": diff,
            "Percent Price Diff": percent_diff,
            "Date Diff": date_diff.total_seconds(),
            "Currently Vaulted": p["Currently Vaulted"],
            "Item Type": p["Item Type"],
        }
        rows_list.append(row)
    df = pd.DataFrame(rows_list)
    df = normalize(
        df, ["Volume Ratio", "Price Diff", "Percent Price Diff", "Date Diff"]
    )
    df["Metric"] = (
        df["Volume Ratio"]
        + df["Price Diff"]
        + df["Percent Price Diff"]
        + df["Date Diff"]
    ) / 4.0
    if buy:
        df = df.sort_values("Metric", ascending=True)
    else:
        df = df.sort_values("Metric", ascending=False)
    return df


def normalize(df: pd.DataFrame, features: List[str]) -> pd.DataFrame:
    """Normalize a data frame columns for `features` columns."""
    result = df.copy()
    for feature_name in features:
        max_value = df[feature_name].max()
        min_value = df[feature_name].min()
        result[feature_name] = (df[feature_name] - min_value) / (max_value - min_value)
    return result


def prime_ranking(
    vault_csv: str,
    category: str,
    prime_data: Optional[ItemStats],
    buy: bool = False,
    quick: bool = False,
) -> List[str]:
    """Gets the best primes based on a ranking system.

    Collects the best primes based on a ranking system. This ranking system
    esentially generates a metric of 4 normalized metrics. The 4 metrics
    used are ratio of volume bought to volume sold, the price difference over
    between now and unvaulting time, the percent price difference over
    between now and unvaulting time, and the date difference between now and
    the unvaulting time. These 4 metrics are normalized between 0 and 1, and
    averaged. This average of the 4 metrics is used to rank the items. When buying
    items, ascending order is used, otherwise, descending order is used.

    Args:
        vault_csv: A string (can be a download url) of the location of the csv file
            for vault dates. This must have columns of "Last Unvaulting", "Vault Date",
            "Item Name", and "Item Type". This format essentially follows from
            the chart on the wiki (https://warframe.fandom.com/wiki/Prime_Vault).
        category: The category of items to sort. The categories are from the wiki
            table located at https://warframe.fandom.com/wiki/Prime_Vault.
        prime_data: The `ItemStats` object for prime data. Only prime data is required,
            and additional data will not affect the rankings. This is not required if
            using the quick method.
        buy: A boolean representing whether we are buying or selling warframe parts.
        quick: If quick is True, then a method of ranking is used only ranks
            based on dates. Therefore, no prime data is required and warframe
            market's api does not need to be consulted.

    Returns:
        A dataframe sorted in the desired order based on the parameter `buy`.
    """
    if quick:
        vault_df = pd.read_csv(vault_csv)
        best_primes = best_primes_simple(vault_df, category, buy=buy)
    else:
        best_primes = best_prime_complex(
            vault_csv=vault_csv, category=category, prime_data=prime_data, buy=buy
        )
    best_primes = best_primes[best_primes["Item Type"].str.lower() == category.lower()]
    return best_primes["Item Name"].to_list()
