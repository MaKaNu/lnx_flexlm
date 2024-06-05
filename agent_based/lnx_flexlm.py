from datetime import datetime

from cmk.base.check_legacy_includes.azure import Metric
from .agent_based_api.v1 import *

def discover_lnx_flexlm(section):
    yield Service()

def check_lnx_flexlm(section):
    date_format = "%d-%b-%Y"
    now = datetime.now()
    yield Result(state=State.OK, summary="Enough licenses available, no license expired.")
    for sector, use, total, expire_date in section:
        if not expire_date:
            expire_date = now
        date = datetime.strptime(expire_date, date_format)
        time_delta = date - now

        yield Metric(f"{sector}_licenses",
                     int(use),
                     levels=(int(total)*0.95, int(total)*0.99),
                     boundaries=(0, int(total))
                     )

        if int(time_delta.days) < 5 or int(use) > 0.99*int(total):
            state = State.CRIT
            notice_msg = f"{sector}: is CRITICAL, see service details"
        elif int(time_delta.days) < 30 or int(use) / int(total) > 0.95:
            state = State.WARN
            notice_msg = f"{sector}: is WARNING, see service details"
        else:
            state = State.OK
            notice_msg = f"{sector}: is OK, see service details"
        detail_msg = f"{sector} details: {use} of {total} licenses are used. The license expires in {time_delta.days} days."
        yield Result(state=state, notice=notice_msg, details=detail_msg)
    return

register.check_plugin(
    name="lnx_flexlm",
    service_name="FlexLM License Status",
    discovery_function=discover_lnx_flexlm,
    check_function=check_lnx_flexlm,
)
