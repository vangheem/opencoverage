from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from .app import router


class Colors:
    GT_95 = "#3273dc"
    GT_85 = "#3298dc"
    GT_70 = "#ffdd57"
    GT_50 = "#f14668"
    GT_0 = "#6b1f2e"


COLORS = (
    (95, Colors.GT_95),
    (85, Colors.GT_85),
    (70, Colors.GT_70),
    (50, Colors.GT_50),
    (0, Colors.GT_0),
)


@router.get("/{org}/repos/{repo}/badge.svg")
async def get_badge(request: Request, org: str, repo: str):
    db = request.app.db
    _, reports = await db.get_reports(org, repo, limit=1)
    if len(reports) == 0:
        return JSONResponse({"reason": "notFound"}, status_code=404)

    report = reports[0]
    rate = round(report.line_rate * 100)
    for crate, color in COLORS:  # pragma: no cover
        if rate >= crate:
            break

    return Response(
        f"""<svg
  xmlns="http://www.w3.org/2000/svg"
  xmlns:xlink="http://www.w3.org/1999/xlink"
  width="122"
  height="20"
  role="img"
  aria-label="opencoverage: {rate}%"
>
  <title>opencoverage: {rate}%</title>
  <linearGradient id="s" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1" />
    <stop offset="1" stop-opacity=".1" />
  </linearGradient>
  <clipPath id="r">
    <rect width="122" height="20" rx="3" fill="#fff" />
  </clipPath>
  <g clip-path="url(#r)">
    <rect width="87" height="20" fill="#555" />
    <rect x="87" width="35" height="20" fill="{color}" />
    <rect width="122" height="20" fill="url(#s)" />
  </g>
  <g
    fill="#fff"
    text-anchor="middle"
    font-family="Verdana,Geneva,DejaVu Sans,sans-serif"
    text-rendering="geometricPrecision"
    font-size="110"
  >
    <text
      aria-hidden="true"
      x="445"
      y="150"
      fill="#010101"
      fill-opacity=".3"
      transform="scale(.1)"
      textLength="770"
    >
      opencoverage
    </text>
    <text x="445" y="140" transform="scale(.1)" fill="#fff" textLength="770">
      opencoverage
    </text>
    <text
      aria-hidden="true"
      x="1035"
      y="150"
      fill="#010101"
      fill-opacity=".3"
      transform="scale(.1)"
      textLength="250"
    >
      {rate}%
    </text>
    <text x="1035" y="140" transform="scale(.1)" fill="#fff" textLength="250">
      {rate}%
    </text>
  </g>
</svg>
""",
        media_type="image/svg+xml",
    )
