"""Holds the objects required for processing Warframe market data."""
from __future__ import annotations

import datetime
from dataclasses import asdict
from dataclasses import dataclass
from json import dumps
from json import loads
from typing import Any
from typing import Dict
from typing import Iterator
from typing import List
from typing import Optional
from typing import Type
from typing import Union

import pandas as pd


def to_json(obj: Union[Stat, ItemStats, LiveStat]) -> str:
    """Dumps Stat, ItemStats, LiveStat into json string."""
    json_rep = obj.to_json()
    json_rep_str = dumps(json_rep, default=json_serial)
    return json_rep_str


def from_json(cls: Type, json_rep_str: str) -> Union[Stat, ItemStats, LiveStat]:
    """Loads Stat, ItemStats, LiveStat from json string."""
    json_rep = loads(json_rep_str, object_hook=date_hook)
    obj = cls.from_json(json_rep)
    return obj


def json_serial(obj: Any) -> int:
    """JSON serializer for objects not serializable by default json code."""
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return int(obj.timestamp() * 1000)
    raise TypeError("Type %s not serializable" % type(obj))


def date_hook(json_dict: Dict) -> Dict:
    """Date hook for reading values from json string."""
    for (key, value) in json_dict.items():
        if key == "dates":
            dates = []
            for v in value:
                dates.append(
                    datetime.datetime.fromtimestamp(v / 1000, tz=datetime.timezone.utc)
                )
            json_dict[key] = dates
    return json_dict


@dataclass
class ShortItem:
    """A singular item schema."""

    thumb: str
    id: str
    item_name: str
    url_name: str


@dataclass
class Stats:
    """A closed statistics schema."""

    datetime: str
    volume: int
    min_price: float
    max_price: float
    open_price: float
    closed_price: float
    avg_price: float
    wa_price: float
    median: float
    moving_avg: Optional[float]
    donch_top: float
    donch_bot: float
    id: str
    mod_rank: Optional[int]


@dataclass
class LiveStats:
    """A live statistics schema."""

    datetime: str
    volume: int
    min_price: float
    max_price: float
    avg_price: float
    wa_price: float
    median: float
    moving_avg: Optional[float]
    order_type: str
    id: str
    mod_rank: Optional[int]


class ItemStats(object):
    """A object to process and hold item,statistics pairs."""

    def __init__(self, items: List[ShortItem], stats: List[Stat]) -> None:
        """Create an ItemStats object."""
        item_stats = {}
        new_items = {}
        name_items = {}
        for i, s in zip(items, stats):
            if i.id in item_stats:
                raise ValueError("items has duplicate ids with id: " + i.id)
            if i.id in new_items:
                raise ValueError("items has duplicate ids with id: " + i.id)
            if i.item_name in name_items:
                raise ValueError("items has duplicate names with name: " + i.item_name)
            item_stats[i.id] = s
            new_items[i.id] = i
            name_items[i.item_name] = i
        self.item_stats = item_stats
        self.items = new_items
        self.name_items = name_items

    def get_stats(self, id: str) -> Stat:
        """Get statistics from item id."""
        return self.item_stats[id]

    def get_item_by_id(self, id: str) -> ShortItem:
        """Get item from item id."""
        return self.items[id]

    def get_item(self, name: str) -> ShortItem:
        """Get item from item name."""
        return self.name_items[name]

    def __iter__(self) -> Iterator:
        """Iterator over the dictionary of item ids to statistics."""
        return iter(self.item_stats.items())

    def to_json(self) -> Dict:
        """The object to json format."""
        items = []
        stats = []
        for it, stat in self.item_stats.items():
            items.append(asdict(self.get_item_by_id(it)))
            stats.append(stat.to_json())
        return {"items": items, "statistics": stats}

    @classmethod
    def from_json(cls: Type, json_data: Dict) -> ItemStats:
        """The object from a json format."""
        items = json_data["items"]
        stats = json_data["statistics"]
        item_objs = []
        stat_objs = []
        for it, st in zip(items, stats):
            item_objs.append(ShortItem(**it))
            stat_objs.append(Stat.from_json(st))
        return cls(item_objs, stat_objs)


class LiveStat(object):
    """A object to process and hold live statistics."""

    def __init__(self, item_name: str, buy: bool = False) -> None:
        """Create an LiveStat object."""
        self.item_name = item_name
        self.buy = buy
        self.max_prices = []
        self.min_prices = []
        self.dates = []
        self.volumes = []
        self.avg_prices = []
        self.medians = []
        self.wa_prices = []
        self.mod_ranks = []
        self.moving_avgs = []

    def add_stat(
        self,
        str_date: str,
        min_price: float,
        max_price: float,
        volume: int,
        avg_price: float,
        wa_price: float,
        median: float,
        moving_avg: Optional[float],
        mod_rank: Optional[int] = None,
    ) -> None:
        """Add live statistics."""
        if mod_rank:
            self.mod_ranks.append(mod_rank)
        self.volumes.append(volume)
        self.medians.append(median)
        if moving_avg:
            self.moving_avgs.append(moving_avg)
        else:
            self.moving_avgs.append(0)
        self.avg_prices.append(avg_price)
        date = datetime.datetime.strptime(str_date, "%Y-%m-%dT%H:%M:%S.%f%z")
        self.max_prices.append(max_price)
        self.min_prices.append(min_price)
        self.dates.append(date)
        self.wa_prices.append(wa_price)

    def to_json(self) -> Dict:
        """The object to json format."""
        json_data = self.__dict__.copy()
        return json_data

    @classmethod
    def from_json(cls: Type, json_data: Dict) -> LiveStat:
        """The object from a json format."""
        live_stat = cls(json_data["item_name"], json_data["buy"])
        for key in json_data:
            setattr(live_stat, key, json_data[key])
        return live_stat


class Stat(object):
    """A object to process and hold live and closed statistics."""

    def __init__(self, item_name: str) -> None:
        """Create an Stat object."""
        self.item_name = item_name
        self.dates = []
        self.volumes = []
        self.avg_prices = []
        self.medians = []
        self.mod_ranks = []
        self.min_prices = []
        self.max_prices = []
        self.open_prices = []
        self.closed_prices = []
        self.wa_prices = []
        self.moving_avgs = []
        self.donch_tops = []
        self.donch_bots = []
        self.live_stat_buy = LiveStat(item_name, buy=True)
        self.live_stat_sell = LiveStat(item_name, buy=False)

    def add_stat(
        self,
        str_date: str,
        volume: int,
        min_price: float,
        max_price: float,
        open_price: float,
        closed_price: float,
        wa_price: float,
        avg_price: float,
        moving_avg: Optional[float],
        donch_top: float,
        donch_bot: float,
        median: float,
        mod_rank: Optional[int] = None,
    ) -> None:
        """Add closed statistics."""
        if mod_rank is not None or len(self.mod_ranks) > 0:
            self.mod_ranks.append(mod_rank)
        self.volumes.append(volume)
        self.medians.append(median)
        self.avg_prices.append(avg_price)
        date = datetime.datetime.strptime(str_date, "%Y-%m-%dT%H:%M:%S.%f%z")
        self.dates.append(date)
        self.min_prices.append(min_price)
        self.max_prices.append(max_price)
        self.open_prices.append(open_price)
        self.closed_prices.append(closed_price)
        self.wa_prices.append(wa_price)
        if moving_avg is not None:
            self.moving_avgs.append(moving_avg)
        else:
            self.moving_avgs.append(0)
        self.donch_tops.append(donch_top)
        self.donch_bots.append(donch_bot)

    def add_live_stats(
        self,
        str_date: str,
        min_price: float,
        max_price: float,
        volume: int,
        avg_price: float,
        wa_price: float,
        median: float,
        moving_avg: Optional[float],
        mod_rank: Optional[int] = None,
        buy: bool = False,
    ) -> None:
        """Add live statistics."""
        if buy:
            self.live_stat_buy.add_stat(
                str_date,
                min_price,
                max_price,
                volume,
                avg_price,
                wa_price,
                median,
                moving_avg,
                mod_rank=mod_rank,
            )
        else:
            self.live_stat_sell.add_stat(
                str_date,
                min_price,
                max_price,
                volume,
                avg_price,
                wa_price,
                median,
                moving_avg,
                mod_rank=mod_rank,
            )

    def plot_stat(self, stat_to_plot: str) -> None:
        """Helper function to plot statistics."""
        import matplotlib.dates as mdates
        import matplotlib.pyplot as plt
        import seaborn as sns

        if "live__" in stat_to_plot:
            stat_to_plot = stat_to_plot.replace("live__", "")
            stat = getattr(self.live_stat_sell, stat_to_plot)
        else:
            stat = getattr(self, stat_to_plot)
        sns.lineplot(x=self.dates, y=stat, ci=None, marker="o")
        plt.xlabel("Dates")
        y_label = (" ".join(stat_to_plot.split("_"))).title()
        plt.ylabel(y_label)
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=10))
        plt.show()

    def plot_stats(self, stats_to_plot: str) -> None:
        """Helper function to plot multiple statistics."""
        import matplotlib.dates as mdates
        import matplotlib.pyplot as plt
        import seaborn as sns

        final_ylabel = ""
        for stat_to_plot in stats_to_plot:
            if "live__" in stat_to_plot:
                stat_to_plot = stat_to_plot.replace("live__", "")
                stat = getattr(self.live_stat_sell, stat_to_plot)
            else:
                stat = getattr(self, stat_to_plot)
                sns.lineplot(x=self.dates, y=stat, ci=None, marker="o")
            y_label = (" ".join(stat_to_plot.split("_"))).title()
            final_ylabel += y_label + "/"
        plt.xlabel("Dates")
        plt.ylabel(final_ylabel[:-1])
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=10))
        plt.show()

    def get_live_stats(self, stat_name: str, buy: bool = False) -> List:
        """Get the live statistics."""
        if buy:
            stat = getattr(self.live_stat_buy, stat_name)
        else:
            stat = getattr(self.live_stat_sell, stat_name)
        return stat

    def merge(self, other: Stat, newer: bool = True) -> None:
        """Merge two `Stat` object togther based on dates.

        Combine two `Stat` objecst using the dates replaced to be only
        year, month, and day. These replaced dates are then used to merge
        the two stat objects. The idea is to combined new collected data
        with old stored data. This merge is done in-place and does not
        return a new Stat `object`. Please note that this function is not
        highly optimized and expects one statistics to be collected each
        days. The live statistics are simply set to the newer `Stat` object
        chosen based on the `newer` parameter.

        Args:
            other: The `Stat` to merge with.
            newer: A boolean representing whether the parameter `other`
                represents a newer Stat object or an older one. The newer
                Stat object's values are taken when there are overlapping dates.

        Raises:
            ValueError: If the `Stat` objects have different item names.
        """
        if other.item_name != self.item_name:
            raise ValueError("Merging stats for different items.")
        self_dates = [
            d.replace(minute=0, hour=0, second=0, microsecond=0) for d in self.dates
        ]
        other_dates = [
            d.replace(minute=0, hour=0, second=0, microsecond=0) for d in other.dates
        ]
        other_stat = other.__dict__.copy()
        stat = self.__dict__.copy()
        stat.pop("live_stat_buy")
        stat.pop("live_stat_sell")
        other_stat.pop("live_stat_buy")
        other_stat.pop("live_stat_sell")
        other_stat["date_key"] = other_dates
        stat["date_key"] = self_dates
        other_stat_df = pd.DataFrame(other_stat)
        stat_df = pd.DataFrame(stat)
        merged = pd.merge(
            stat_df,
            other_stat_df,
            left_on="date_key",
            right_on="date_key",
            how="outer",
            suffixes=("_left", "_right"),
        )
        stat.pop("date_key")
        main_attr = "dates_right"
        sec_attr = "dates_left"
        if newer is False:
            main_attr = "dates_left"
            sec_attr = "dates_right"
        merged.loc[merged[main_attr].isna(), main_attr] = merged[sec_attr]
        merged = merged.sort_values(by=[main_attr])
        for attr in stat:
            main_attr = attr + "_right"
            sec_attr = attr + "_left"
            if newer is False:
                main_attr = attr + "_left"
                sec_attr = attr + "_right"
            merged.loc[merged[main_attr].isna(), main_attr] = merged[sec_attr]
            values = merged[main_attr].to_list()
            if "dates" in main_attr:
                values = [v.to_pydatetime() for v in values]
            setattr(self, attr, values)
        if newer:
            self.live_stat_buy = other.live_stat_buy
            self.live_stat_sell = other.live_stat_sell

    def to_json(self) -> Dict:
        """The object to json format."""
        json_data = self.__dict__.copy()
        json_data["live_stat_buy"] = self.live_stat_buy.to_json()
        json_data["live_stat_sell"] = self.live_stat_sell.to_json()
        return json_data

    @classmethod
    def from_json(cls: Type, json_data: Dict) -> Stat:
        """The object from a json format."""
        stat = cls(json_data["item_name"])
        for key in json_data:
            if key == "live_stat_buy" or key == "live_stat_sell":
                loaded_live_stat = LiveStat.from_json(json_data[key])
                setattr(stat, key, loaded_live_stat)
            else:
                setattr(stat, key, json_data[key])
        return stat
