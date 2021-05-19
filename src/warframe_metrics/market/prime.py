import pandas as pd
import datetime
from ..utils.schema import ItemStats, ShortItem, Stat, LiveStats, Stats
from typing import Optional, List, Union
from ..utils.constants import ITEMS_URL, STATS_URL
from ..utils.collect_data import from_url, collect_data, to_class, to_stats
import time


def best_primes_simple(
    vault_df: pd.DataFrame, category: str, buy: bool = False
) -> pd.DataFrame:
    df = vault_df.copy()
    df["Last Unvaulting"] = pd.to_datetime(df["Last Unvaulting"])
    df["Vault Date"] = pd.to_datetime(df["Vault Date"])
    df["Current Vaulted"] = df["Last Unvaulting"] < (
        datetime.datetime.utcnow() - datetime.timedelta(days=120)
    )
    if buy:
        df_refined = df.drop(df[df["Current Vaulted"] == True].index, inplace=False)
        df_refined = df_refined.sort_values(
            ["Last Unvaulting", "Vault Date"], ascending=[False, True]
        )
    else:
        df_refined = df.drop(df[df["Current Vaulted"] == False].index, inplace=False)
        df_refined = df_refined.sort_values(
            ["Last Unvaulting", "Vault Date"], ascending=[True, False]
        )
    return df_refined[df_refined["Item Type"].lower() == category.lower()]


def get_change(current, previous):
    if current == previous:
        return 100.0
    if previous != 0:
        return (abs(current - previous) / previous) * 100.0
    else:
        return 0


def generate_names(prime_items: ItemStats, vault_csv: str) -> pd.DataFrame:
    vault_csv = pd.read_csv(vault_csv)
    names_to_items = dict((k, v.lower()) for k, v in prime_items.name_items.items())
    new_rows = []
    for _, row in vault_csv.iterrows():
        item_name = row["Item Name"].lower()
        row = row.to_dict()
        for prime_name in names_to_items:
            if item_name in prime_name:
                row.update("Item Name", prime_name.title())
                row = row.copy()
                new_rows.append(row)
    return pd.DataFrame(new_rows)


def collect_prime_data() -> ItemStats:
    json_data = from_url(ITEMS_URL)
    json_data = collect_data(json_data, ["payload", "items"])
    items = to_class(ShortItem, json_data)
    prime_items = []
    prime_stats = []
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

    return ItemStats(prime_items, prime_stats)


def find_index(
    stat: Stat,
    unvault_date: datetime.datetime,
    time_delta: datetime.timedelta,
    num_days: Optional[int] = None,
) -> int:
    dates = getattr(stat, "dates")
    min_date = max(unvault_date, datetime.datetime.utcnow() - time_delta)
    i = j = 0
    while dates[i] < min_date and i < len(dates):
        i += 1
    if num_days is None:
        j = len(dates)
    else:
        j = i
        max_date = min_date + datetime.timedelta(days=num_days)
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
    vault_csv: str, category: str, prime_data: ItemStats, buy: bool = False
) -> pd.DataFrame:
    vault_df = generate_names(prime_data, vault_csv)
    best_primes = best_primes_simple(vault_df, category, buy=buy)
    percent_thresh = 30
    days_to_consider = 10
    time_delta = datetime.timedelta(days=120)
    rows_list = []
    for _, p in best_primes.iterrows():
        item = prime_data.get_item(p["Item Name"])
        stat = prime_data.get_stat(item.id)
        unvaulted_date = p["Last Unvaulting"]
        if unvaulted_date is None:
            unvaulted_date = datetime.datetime.utcnow() - datetime.timedelta(days=90)
        date_diff = datetime.datetime.utcnow() - unvaulted_date
        max_buys = get_stat_within_date(
            stat, "max_prices", unvaulted_date, time_delta, buy=True
        )
        min_sells = get_stat_within_date(
            stat, "min_prices", unvaulted_date, time_delta, buy=False
        )
        # max_buys = stat.get_live_stats('max_prices', buy=True)
        # min_sells = stat.get_live_stats('min_prices', buy=False)
        min_sell = min(min_sells)
        max_buy = min(max_buys)
        if get_change(min_sell, max_buy) > percent_thresh:
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
        prev_low = min(prev_lows)
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
            "Volume Ratio": volume_ratio,
            "Price Diff": diff,
            "Percent Price Diff": percent_diff,
            "Date Diff": date_diff.timestamp(),
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
        df.sort("Metric", ascending=False)
    else:
        df.sort("Metric", ascending=True)
    return df


def normalize(df, features):
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
    if quick:
        vault_df = pd.read_csv(vault_csv)
        best_primes = best_primes_simple(vault_df, category, buy=buy)
    else:
        best_primes = best_prime_complex(
            vault_csv=vault_csv, category=category, prime_data=prime_data, buy=buy
        )
    return best_primes["Item Name"].to_list()
