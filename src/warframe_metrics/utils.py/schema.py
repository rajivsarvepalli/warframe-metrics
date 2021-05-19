from typing import List, Optional
from dataclasses import dataclass
import datetime
import seaborn as sns
import matplotlib.pyplot as plt, matplotlib.dates as mdates


@dataclass
class ShortItem:
    thumb: str
    id: str
    item_name: str
    url_name: str


@dataclass
class Stats:
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
    def __init__(self, items, stats):
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

    def get_stats(self, id):
        return self.item_stats[id]

    def get_item_by_id(self, id: str):
        return self.items[id]

    def get_item(self, name: str) -> ShortItem:
        return self.name_items[name]

    def __iter__(self):
        return iter(self.item_stats.items())


class LiveStat(object):
    def __init__(self, item_name: str, buy: bool = False) -> None:
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


class Stat(object):
    def __init__(self, item_name: str) -> None:
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
        mod_rank=None,
    ) -> None:
        if mod_rank:
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
        self.avg_prices.append(avg_price)
        if moving_avg:
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
    ):
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

    def plot_stat(self, stat_to_plot):
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

    def plot_stats(self, stats_to_plot):
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
        if buy:
            stat = getattr(self.live_stat_buy, stat_name)
        else:
            stat = getattr(self.live_stat_sell, stat_name)
        return stat
