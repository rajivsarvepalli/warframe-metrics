"""Holds the utils required for processing Warframe market data."""
import time
from contextlib import nullcontext
from typing import Any
from typing import Dict
from typing import List
from typing import Union

import desert
import requests
from alive_progress import alive_bar

from .constants import ITEMS_URL
from .constants import STATS_URL
from .schema import ItemStats
from .schema import LiveStats
from .schema import ShortItem
from .schema import Stat
from .schema import Stats


def market_data(filters: Dict[str, Any], progress_bar: bool = False) -> ItemStats:
    """Collect data from warframe market API.

    Collects information from the warframe market API. Waits 1 second every
    10 items collected. This is to ensure we do not exceed limits.

    Args:
        filters: A dictionary of `ShortItem` attributes to values that will
            be used to filter the items for which statistics will be collected.
        progress_bar: Whether to use a progress bar or not.

    Returns:
        An object of `ItemStats` that contains all the collected data.
    """
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
            matched = all([getattr(i, f) == val for f, val in filters.items()])
            if matched is True:
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


def from_url(url: str) -> Any:
    """Gets json response from url."""
    resp = requests.get(url=url)
    resp_json = resp.json()
    return resp_json


def collect_data(resp_json: Dict, accesses: List[str]) -> Union[Dict, List]:
    """Collect data from url using requests."""
    resp_final = resp_json
    for acc in accesses:
        resp_final = resp_final[acc]
    return resp_final


def to_class(cls: Any, data: List[Dict]) -> List[object]:
    """Collects json response into dataclass using desert."""
    all_data = []
    for d in data:
        desert_cls = desert.schema(cls)
        all_data.append(desert_cls.load(d))
    return all_data


def to_stats(
    stats_closed: List[Stats], stats_live: List[LiveStats], item_name: str
) -> Stat:
    """Collects statistics into Stat object."""
    stat = Stat(item_name)
    for st in stats_closed:
        stat.add_stat(
            str_date=st.datetime,
            volume=st.volume,
            min_price=st.min_price,
            max_price=st.max_price,
            open_price=st.open_price,
            closed_price=st.closed_price,
            wa_price=st.wa_price,
            avg_price=st.avg_price,
            moving_avg=st.moving_avg,
            donch_top=st.donch_top,
            donch_bot=st.donch_bot,
            median=st.median,
            mod_rank=st.mod_rank,
        )
    for st in stats_live:
        if st.order_type == "buy":
            stat.add_live_stats(
                str_date=st.datetime,
                volume=st.volume,
                min_price=st.min_price,
                max_price=st.max_price,
                wa_price=st.wa_price,
                avg_price=st.avg_price,
                median=st.median,
                moving_avg=st.moving_avg,
                mod_rank=st.mod_rank,
                buy=True,
            )
        else:
            stat.add_live_stats(
                str_date=st.datetime,
                volume=st.volume,
                min_price=st.min_price,
                max_price=st.max_price,
                wa_price=st.wa_price,
                avg_price=st.avg_price,
                median=st.median,
                moving_avg=st.moving_avg,
                mod_rank=st.mod_rank,
                buy=False,
            )
    return stat
