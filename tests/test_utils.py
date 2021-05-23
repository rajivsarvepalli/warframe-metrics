"""Tests utilities package."""
import datetime
from dataclasses import asdict
from datetime import timezone
from unittest.mock import Mock

from warframe_metrics.utils.collect_data import collect_data
from warframe_metrics.utils.collect_data import from_url
from warframe_metrics.utils.collect_data import to_class
from warframe_metrics.utils.collect_data import to_stats
from warframe_metrics.utils.constants import ITEMS_URL
from warframe_metrics.utils.schema import from_json
from warframe_metrics.utils.schema import ItemStats
from warframe_metrics.utils.schema import LiveStats
from warframe_metrics.utils.schema import ShortItem
from warframe_metrics.utils.schema import Stat
from warframe_metrics.utils.schema import Stats
from warframe_metrics.utils.schema import to_json


def test_from_url(requests_mock: Mock) -> None:
    """Tests getting json from url."""
    requests_mock.get(ITEMS_URL, json={"items": "test"})
    resp = from_url(ITEMS_URL)
    assert resp == {"items": "test"}


def test_collect_data(requests_mock: Mock) -> None:
    """Tests required information from json."""
    requests_mock.get(ITEMS_URL, json={"payload": {"items": [{"test": "here"}]}})
    resp = from_url(ITEMS_URL)
    data = collect_data(resp, ["payload", "items"])
    assert data == [{"test": "here"}]


def test_to_class(requests_mock: Mock) -> None:
    """Tests required information from json."""
    items = [
        {
            "id": "54aae292e7798909064f1575",
            "item_name": "Secura Dual Cestra",
            "thumb": (
                "icons/en/thumbs/secura_dual_cestra"
                ".3d47a4ec6675ff774bb0da9b16c53e0e.128x128.png"
            ),
            "url_name": "secura_dual_cestra",
        },
        {
            "id": "54ca39abe7798915c1c11e10",
            "item_name": "Creeping Bullseye",
            "thumb": (
                "icons/en/thumbs/Creeping_Bullseye."
                "dfcb8d21b36d9e2a2632f37c75b3532f.128x128.png"
            ),
            "url_name": "creeping_bullseye",
        },
        {
            "id": "54d4c727e77989281cc7d753",
            "item_name": "Mutalist Alad V Assassinate (Key)",
            "thumb": (
                "icons/en/thumbs/Mutalist_Alad_V_Assassinate_Key"
                ".7540fb6d7ef2b2843352e32c9ff64e73.128x128.png"
            ),
            "url_name": "mutalist_alad_v_assassinate_key",
        },
        {
            "id": "54e0c9eee7798903744178b0",
            "item_name": "Irradiating Disarm",
            "thumb": (
                "icons/en/thumbs/Irradiating_Disarm"
                ".cffd5ed77e1365babfd3e9559b96ebc6.128x128.png"
            ),
            "url_name": "irradiating_disarm",
        },
        {
            "id": "54e644ffe779897594fa68cf",
            "item_name": "Antimatter Absorb",
            "thumb": (
                "icons/en/thumbs/Antimatter_Absorb"
                ".1402d671df9b6f5ae2504d6abec4d4fd.128x128.png"
            ),
            "url_name": "antimatter_absorb",
        },
        {
            "id": "551085aee77989729e1416d0",
            "item_name": "Arcane Barrier",
            "thumb": (
                "icons/en/thumbs/Arcane_Barrier"
                ".c4b3b25fcc9c874a4bfc0f8998b9f5bd.128x128.png"
            ),
            "url_name": "arcane_barrier",
        },
        {
            "id": "551085c9e7798972b4a2b206",
            "item_name": "Arcane Ice",
            "thumb": (
                "icons/en/thumbs/arcane_ice"
                ".d3cb62ba9923dcf396c854fb857e5718.128x128.png"
            ),
            "url_name": "arcane_ice",
        },
        {
            "id": "55e797d2e7798924849dd9f0",
            "item_name": "Telos Boltor",
            "thumb": (
                "icons/en/thumbs/telos_boltor"
                ".9a109e6b666017c81b2402e7031243b5.128x128.png"
            ),
            "url_name": "telos_boltor",
        },
        {
            "id": "56783f24cbfa8f0432dd899c",
            "item_name": "Frost Prime Set",
            "thumb": (
                "icons/en/thumbs/frost_prime_set"
                ".4f8ff8605be1afaab9a0e5cc3c67cb21.128x128.png"
            ),
            "url_name": "frost_prime_set",
        },
        {
            "id": "56a7b2a51133f656cb085d93",
            "item_name": "Catalyzer Link",
            "thumb": (
                "icons/en/thumbs/Catalyzer_Link"
                ".8ffa520e67c52e10b51ccc1cec6b7f88.128x128.png"
            ),
            "url_name": "catalyzer_link",
        },
    ]
    requests_mock.get(ITEMS_URL, json={"payload": {"items": items}})
    resp = from_url(ITEMS_URL)
    data = collect_data(resp, ["payload", "items"])
    objects = to_class(ShortItem, data)
    correct_objs = []
    for i in items:
        correct_objs.append(ShortItem(**i))
    assert objects == correct_objs


def test_to_stat() -> None:
    """Test adding to `Stat` object using `to_stat`."""
    stats = [
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
            volume=1,
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
    s = Stat("test_item")
    s.add_live_stats(
        str_date="2021-05-02T00:00:00.000+00:00",
        volume=1,
        min_price=2,
        max_price=3,
        avg_price=4,
        wa_price=5,
        median=6,
        moving_avg=7,
        mod_rank=None,
        buy=True,
    )
    s.add_live_stats(
        str_date="2021-05-03T00:00:00.000+00:00",
        volume=1,
        min_price=2,
        max_price=3,
        avg_price=4,
        wa_price=5,
        median=6,
        moving_avg=None,
        mod_rank=None,
        buy=False,
    )
    s.add_stat(
        str_date="2021-05-17T21:00:00.000+00:00",
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
        mod_rank=3,
    )
    s.add_stat(
        str_date="2021-05-18T21:00:00.000+00:00",
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
        mod_rank=0,
    )

    stat = to_stats(stats, live_stats, "test_item")
    assert s.dates == stat.dates
    assert s.live_stat_sell.dates == stat.live_stat_sell.dates
    correct_dates_closed = [
        datetime.datetime(year=2021, month=5, day=17, hour=21, tzinfo=timezone.utc),
        datetime.datetime(year=2021, month=5, day=18, hour=21, tzinfo=timezone.utc),
    ]
    assert stat.dates == correct_dates_closed
    correct_dates_live_sell = [
        datetime.datetime(year=2021, month=5, day=3, tzinfo=timezone.utc),
    ]
    correct_dates_live_buy = [
        datetime.datetime(year=2021, month=5, day=2, tzinfo=timezone.utc),
    ]
    assert stat.live_stat_sell.dates == correct_dates_live_sell
    assert stat.live_stat_buy.dates == correct_dates_live_buy
    assert [1, 2] == stat.volumes
    assert [3, 3] == stat.min_prices
    assert [4, 4] == stat.max_prices
    assert [5, 5] == stat.open_prices
    assert [7, 7] == stat.closed_prices
    assert [8, 8] == stat.avg_prices
    assert [9, 9] == stat.wa_prices
    assert [0, 0] == stat.medians
    assert [10, 0] == stat.moving_avgs
    assert [11, 11] == stat.donch_tops
    assert [12, 12] == stat.donch_bots
    assert [0, 3] == stat.mod_ranks
    assert [1] == stat.live_stat_buy.volumes
    assert [1] == stat.live_stat_sell.volumes
    assert [2] == stat.live_stat_buy.min_prices
    assert [2] == stat.live_stat_sell.min_prices
    assert [3] == stat.live_stat_buy.max_prices
    assert [3] == stat.live_stat_sell.max_prices
    assert [4] == stat.live_stat_buy.avg_prices
    assert [4] == stat.live_stat_sell.avg_prices
    assert [5] == stat.live_stat_buy.wa_prices
    assert [5] == stat.live_stat_sell.wa_prices
    assert [6] == stat.live_stat_buy.medians
    assert [6] == stat.live_stat_sell.medians
    assert [7] == stat.live_stat_buy.moving_avgs
    assert [0] == stat.live_stat_sell.moving_avgs


def compare(stat1: Stat, stat2: Stat) -> bool:
    """Compare two stat objects."""
    b1 = stat1.live_stat_sell.__dict__ == stat2.live_stat_sell.__dict__
    b2 = stat1.live_stat_buy.__dict__ == stat2.live_stat_buy.__dict__
    b3 = True
    for k1 in stat1.__dict__:
        if k1 not in ["live_stat_sell", "live_stat_buy"]:
            if stat1.__dict__[k1] != stat2.__dict__[k1]:
                b3 = False
    return b1 and b2 and b3


def test_json() -> None:
    """Tests json serialization of objects."""
    s = Stat("test_item")
    s.add_live_stats(
        str_date="2021-05-02T00:00:00.000+00:00",
        volume=1,
        min_price=2,
        max_price=3,
        avg_price=4,
        wa_price=5,
        median=6,
        moving_avg=7,
        mod_rank=None,
        buy=True,
    )
    s.add_live_stats(
        str_date="2021-05-03T00:00:00.000+00:00",
        volume=1,
        min_price=2,
        max_price=3,
        avg_price=4,
        wa_price=5,
        median=6,
        moving_avg=None,
        mod_rank=None,
        buy=False,
    )
    s.add_stat(
        str_date="2021-05-17T21:00:00.000+00:00",
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
        mod_rank=3,
    )
    s.add_stat(
        str_date="2021-05-18T21:00:00.000+00:00",
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
        mod_rank=0,
    )
    s3 = Stat("test_item")
    s3.add_live_stats(
        str_date="2021-05-02T00:00:00.000+00:00",
        volume=1,
        min_price=2,
        max_price=3,
        avg_price=4,
        wa_price=5,
        median=6,
        moving_avg=7,
        mod_rank=None,
        buy=True,
    )
    s3.add_live_stats(
        str_date="2021-05-03T00:00:00.000+00:00",
        volume=1,
        min_price=2,
        max_price=3,
        avg_price=4,
        wa_price=5,
        median=6,
        moving_avg=None,
        mod_rank=None,
        buy=False,
    )
    s3.add_stat(
        str_date="2021-05-17T21:00:00.000+00:00",
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
        mod_rank=3,
    )
    s3.add_stat(
        str_date="2021-05-18T21:00:00.000+00:00",
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
        mod_rank=0,
    )
    json_rep_str = to_json(s)
    s2 = from_json(Stat, json_rep_str)
    assert compare(s2, s)
    assert compare(s2, s3)
    item = ShortItem("test1", "id1", "item_name", "url")
    data = ItemStats([item], [s3])
    json_rep_str = to_json(data)
    item_stats = from_json(ItemStats, json_rep_str)
    for id, st in item_stats:
        assert compare(data.get_stats(id), st)
        assert asdict(data.get_item_by_id(id)) == asdict(item)
