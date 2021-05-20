"""Tests utilities package."""
from unittest.mock import Mock

from warframe_metrics.utils.collect_data import collect_data
from warframe_metrics.utils.collect_data import from_url
from warframe_metrics.utils.collect_data import to_class
from warframe_metrics.utils.collect_data import to_stats
from warframe_metrics.utils.constants import ITEMS_URL
from warframe_metrics.utils.schema import LiveStats
from warframe_metrics.utils.schema import ShortItem
from warframe_metrics.utils.schema import Stat
from warframe_metrics.utils.schema import Stats


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
            "2021-05-17T21:00:00.000+00:00",
            1,
            3,
            4,
            5,
            7,
            8,
            9,
            0,
            10,
            11,
            12,
            "id1",
            0,
        ),
        Stats(
            "2021-06-17T21:00:00.000+00:00",
            1,
            3,
            4,
            5,
            7,
            8,
            9,
            0,
            10,
            11,
            12,
            "id2",
            3,
        ),
    ]
    live_stats = [
        LiveStats(
            "2021-05-02T00:00:00.000+00:00", 1, 2, 3, 4, 5, 6, 7, "buy", "id1", None
        ),
        LiveStats(
            "2021-05-03T00:00:00.000+00:00", 1, 2, 3, 4, 5, 6, 7, "sell", "id2", None
        ),
    ]
    s = Stat("test_item")
    s.add_live_stats("2021-05-02T00:00:00.000+00:00", 1, 2, 3, 4, 5, 6, 7, buy=True)
    s.add_live_stats("2021-05-02T00:00:00.000+00:00", 1, 2, 3, 4, 5, 6, 7, buy=False)
    s.add_stat("2021-05-17T21:00:00.000+00:00", 1, 3, 4, 5, 7, 8, 9, 0, 10, 11, 12, 0)
    s.add_stat("2021-06-17T21:00:00.000+00:00", 1, 3, 4, 5, 7, 8, 9, 0, 10, 11, 12, 3)

    stat = to_stats(stats, live_stats, "test_item")
    assert s.dates == stat.dates
    assert s.live_stat_sell.dates == stat.live_stat_sell.dates
