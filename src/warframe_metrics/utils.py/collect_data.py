from typing import Type, List, Dict
import requests
from .schema import LiveStats, Stat, Stats
import desert


def from_url(url: str) -> Dict:
    resp = requests.get(url=url)
    resp_json = resp.json()
    return resp_json


def collect_data(resp_json: Dict, accesses: List[str]) -> Dict:
    """Collect data from url using requests."""
    resp_final = resp_json
    for acc in accesses:
        resp_final = resp_final[acc]
    return resp_final


def to_class(cls: Type, data: List[Dict]) -> List[Type]:
    all_data = []
    for d in data:
        desert_cls = desert.schema(cls)
        all_data.append(desert_cls.load(d))
    return all_data


def to_stats(stats_closed: List[Stats], stats_live: List[LiveStats], item_name: str) -> Stat:
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
