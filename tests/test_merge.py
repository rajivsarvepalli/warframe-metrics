"""Tests merging of Stat objects."""
import datetime
from datetime import timezone
from typing import Tuple

from warframe_metrics.utils.collect_data import to_stats
from warframe_metrics.utils.schema import LiveStats
from warframe_metrics.utils.schema import Stat
from warframe_metrics.utils.schema import Stats


def compare(stat1: Stat, stat2: Stat) -> bool:
    """Compare two stat objects."""
    b1 = stat1.live_stat_sell.__dict__ == stat2.live_stat_sell.__dict__
    b2 = stat1.live_stat_buy.__dict__ == stat2.live_stat_buy.__dict__
    b3 = True
    for k1 in stat1.__dict__:
        if k1 not in ["live_stat_sell", "live_stat_buy"]:
            if stat1.__dict__[k1] != stat2.__dict__[k1]:
                print(stat1.__dict__[k1])
                print(stat2.__dict__[k1])
                b3 = False
    return b1 and b2 and b3


def set_stats() -> Tuple[Stat, Stat]:
    """Create two stat objects to test."""
    stats = [
        Stats(
            datetime="2021-05-16T21:00:00.000+00:00",
            volume=3,
            min_price=3,
            max_price=4,
            open_price=5,
            closed_price=7,
            avg_price=8,
            wa_price=9,
            median=0,
            moving_avg=10,
            donch_top=11,
            donch_bot=12,
            id="id1",
            mod_rank=0,
        ),
        Stats(
            datetime="2021-05-17T21:00:00.000+00:00",
            volume=1,
            min_price=3,
            max_price=4,
            open_price=5,
            closed_price=7,
            avg_price=8,
            wa_price=9,
            median=0,
            moving_avg=10,
            donch_top=11,
            donch_bot=12,
            id="id1",
            mod_rank=0,
        ),
        Stats(
            datetime="2021-05-18T21:00:00.000+00:00",
            volume=2,
            min_price=3,
            max_price=4,
            open_price=5,
            closed_price=7,
            avg_price=8,
            wa_price=9,
            median=0,
            moving_avg=None,
            donch_top=11,
            donch_bot=12,
            id="id2",
            mod_rank=3,
        ),
    ]
    live_stats = [
        LiveStats(
            datetime="2021-05-02T00:00:00.000+00:00",
            volume=1,
            min_price=2,
            max_price=3,
            avg_price=4,
            wa_price=5,
            median=6,
            moving_avg=7,
            order_type="buy",
            id="id1",
            mod_rank=None,
        ),
        LiveStats(
            datetime="2021-05-03T00:00:00.000+00:00",
            volume=2,
            min_price=2,
            max_price=3,
            avg_price=4,
            wa_price=5,
            median=6,
            moving_avg=None,
            order_type="sell",
            id="id2",
            mod_rank=None,
        ),
    ]
    stat = to_stats(stats, live_stats, "test_item")
    stats = [
        Stats(
            datetime="2021-05-17T21:00:00.000+00:00",
            volume=101,
            min_price=3,
            max_price=4,
            open_price=5,
            closed_price=7,
            avg_price=8,
            wa_price=9,
            median=0,
            moving_avg=10,
            donch_top=11,
            donch_bot=12,
            id="id1",
            mod_rank=0,
        ),
        Stats(
            datetime="2021-05-18T21:00:00.000+00:00",
            volume=103,
            min_price=3,
            max_price=4,
            open_price=5,
            closed_price=7,
            avg_price=8,
            wa_price=9,
            median=0,
            moving_avg=None,
            donch_top=11,
            donch_bot=12,
            id="id2",
            mod_rank=3,
        ),
        Stats(
            datetime="2021-05-19T21:00:00.000+00:00",
            volume=11,
            min_price=3,
            max_price=4,
            open_price=5,
            closed_price=7,
            avg_price=8,
            wa_price=9,
            median=0,
            moving_avg=None,
            donch_top=11,
            donch_bot=12,
            id="id2",
            mod_rank=3,
        ),
    ]
    live_stats = [
        LiveStats(
            datetime="2021-06-02T00:00:00.000+00:00",
            volume=102,
            min_price=2,
            max_price=3,
            avg_price=4,
            wa_price=5,
            median=6,
            moving_avg=7,
            order_type="buy",
            id="id1",
            mod_rank=None,
        ),
        LiveStats(
            datetime="2021-06-03T00:00:00.000+00:00",
            volume=100,
            min_price=2,
            max_price=3,
            avg_price=4,
            wa_price=5,
            median=6,
            moving_avg=None,
            order_type="sell",
            id="id2",
            mod_rank=None,
        ),
    ]
    stat2 = to_stats(stats, live_stats, "test_item")
    return stat, stat2


def test_to_stat() -> None:
    """Test merging to `Stat` object."""
    stat, stat2 = set_stats()

    stat.merge(stat2)
    correct_dates = [
        datetime.datetime(year=2021, month=5, day=16, hour=21, tzinfo=timezone.utc),
        datetime.datetime(year=2021, month=5, day=17, hour=21, tzinfo=timezone.utc),
        datetime.datetime(year=2021, month=5, day=18, hour=21, tzinfo=timezone.utc),
        datetime.datetime(year=2021, month=5, day=19, hour=21, tzinfo=timezone.utc),
    ]
    assert stat.dates == correct_dates
    assert stat.volumes == [3, 101, 103, 11]
    assert stat.live_stat_buy.volumes == [102]
    assert stat.live_stat_sell.volumes == [100]
    stat_test, stat2 = set_stats()
    stat_test.merge(stat2, newer=False)
    assert stat_test.dates == correct_dates
    assert stat_test.volumes == [3, 1, 2, 11]
    assert stat_test.live_stat_buy.volumes == [1]
    assert stat_test.live_stat_sell.volumes == [2]
    stat, stat_test2 = set_stats()
    stat_test2.merge(stat)
    assert stat_test2.dates == correct_dates
    assert compare(stat_test2, stat_test)
