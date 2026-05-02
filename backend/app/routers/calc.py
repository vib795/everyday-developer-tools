import ipaddress
from datetime import datetime

import markdown as md_lib
import pytz
from croniter import croniter
from fastapi import APIRouter

from ..schemas.calc import (
    ChmodRequest,
    ChmodResponse,
    CidrRequest,
    CidrResponse,
    ColorConvertRequest,
    ColorConvertResponse,
    ContrastRequest,
    ContrastResponse,
    CronNextRunsRequest,
    CronNextRunsResponse,
    MarkdownPreviewRequest,
    MarkdownPreviewResponse,
)
from ..services.chmod import chmod_calc
from ..services.color import (
    contrast_ratio,
    parse_color,
    rgb_to_hex,
    rgb_to_hsl,
    rgb_to_oklch,
)

router = APIRouter(prefix="/api/calc", tags=["calc"])


@router.post("/cron-next", response_model=CronNextRunsResponse)
def cron_next(payload: CronNextRunsRequest) -> CronNextRunsResponse:
    try:
        tz = pytz.timezone(payload.timezone) if payload.timezone else pytz.UTC
        base = datetime.now(tz=tz)
        it = croniter(payload.expression, base)
        runs = [it.get_next(datetime).isoformat() for _ in range(payload.count)]
        return CronNextRunsResponse(runs=runs)
    except Exception as e:  # noqa: BLE001
        return CronNextRunsResponse(error=f"{type(e).__name__}: {e}")


@router.post("/color", response_model=ColorConvertResponse)
def color_convert(payload: ColorConvertRequest) -> ColorConvertResponse:
    try:
        r, g, b = parse_color(payload.color)
    except ValueError as e:
        return ColorConvertResponse(error=str(e))
    h, s, l = rgb_to_hsl(r, g, b)  # noqa: E741
    L, C, hh = rgb_to_oklch(r, g, b)
    return ColorConvertResponse(
        hex=rgb_to_hex(r, g, b),
        rgb=f"rgb({r}, {g}, {b})",
        hsl=f"hsl({h}, {s}%, {l}%)",
        oklch=f"oklch({L} {C} {hh})",
    )


@router.post("/contrast", response_model=ContrastResponse)
def contrast(payload: ContrastRequest) -> ContrastResponse:
    try:
        fg = parse_color(payload.foreground)
        bg = parse_color(payload.background)
    except ValueError as e:
        return ContrastResponse(error=str(e))
    ratio = round(contrast_ratio(fg, bg), 2)
    return ContrastResponse(
        ratio=ratio,
        aa_normal=ratio >= 4.5,
        aa_large=ratio >= 3.0,
        aaa_normal=ratio >= 7.0,
        aaa_large=ratio >= 4.5,
    )


@router.post("/chmod", response_model=ChmodResponse)
def chmod(payload: ChmodRequest) -> ChmodResponse:
    try:
        num, sym = chmod_calc(payload.value)
    except ValueError as e:
        return ChmodResponse(error=str(e))
    return ChmodResponse(numeric=num, symbolic=sym)


@router.post("/cidr", response_model=CidrResponse)
def cidr(payload: CidrRequest) -> CidrResponse:
    try:
        net = ipaddress.ip_network(payload.cidr.strip(), strict=False)
    except ValueError as e:
        return CidrResponse(error=str(e))

    # Don't materialize hosts() for /64 IPv6 etc. — derive endpoints arithmetically.
    is_v4 = isinstance(net, ipaddress.IPv4Network)
    if net.num_addresses <= 1:
        first_host = last_host = None
        num_hosts = net.num_addresses
    elif is_v4 and net.prefixlen <= 30:
        first_host = str(net.network_address + 1)
        last_host = str(net.broadcast_address - 1)
        num_hosts = net.num_addresses - 2
    elif is_v4:
        # /31, /32 — point-to-point or single host
        first_host = str(net.network_address)
        last_host = str(net.broadcast_address)
        num_hosts = net.num_addresses
    else:
        # IPv6 — every address is a host (no broadcast)
        first_host = str(net.network_address + 1)
        last_host = str(net.broadcast_address)
        num_hosts = net.num_addresses

    return CidrResponse(
        network=str(net.network_address),
        netmask=str(net.netmask),
        broadcast=str(net.broadcast_address) if is_v4 else None,
        first_host=first_host,
        last_host=last_host,
        num_hosts=num_hosts,
        prefix=net.prefixlen,
        version=net.version,
    )


@router.post("/markdown", response_model=MarkdownPreviewResponse)
def markdown_preview(payload: MarkdownPreviewRequest) -> MarkdownPreviewResponse:
    html = md_lib.markdown(payload.text, extensions=["fenced_code", "tables", "sane_lists"])
    return MarkdownPreviewResponse(html=html)
