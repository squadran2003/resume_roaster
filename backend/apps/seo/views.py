from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.html import escape


DOMAIN = "https://resume-roaster.com"

PUBLIC_PATHS = [
    "/",
    "/login",
    "/register",
]


def robots_txt(request):
    lines = [
        "User-agent: *",
        "Allow: /",
        "Allow: /share/",
        "",
        "# Disallow authenticated app routes",
        "Disallow: /dashboard",
        "Disallow: /upload",
        "Disallow: /analysis/",
        "Disallow: /linkedin",
        "Disallow: /account",
        "Disallow: /api/",
        "Disallow: /admin/",
        "",
        f"Sitemap: {DOMAIN}/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def sitemap_xml(request):
    today = timezone.now().strftime("%Y-%m-%d")
    urls = []
    for path in PUBLIC_PATHS:
        priority = "1.0" if path == "/" else "0.8"
        changefreq = "weekly" if path == "/" else "monthly"
        urls.append(
            f"  <url>\n"
            f"    <loc>{DOMAIN}{path}</loc>\n"
            f"    <lastmod>{today}</lastmod>\n"
            f"    <changefreq>{changefreq}</changefreq>\n"
            f"    <priority>{priority}</priority>\n"
            f"  </url>"
        )

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>"
    )
    return HttpResponse(xml, content_type="application/xml")


def share_scorecard(request, token):
    """Server-side rendered share page with OG meta tags.

    Social crawlers don't execute JS, so OG tags must be in the initial HTML.
    Browsers get a page that immediately redirects to the frontend SPA.
    """
    from apps.analysis.models import AnalysisResult

    result = get_object_or_404(
        AnalysisResult, share_token=token, status=AnalysisResult.Status.DONE,
    )

    score = result.match_score or 0
    job_title = escape(result.job_description.title or "a job position")
    company = escape(result.job_description.company or "")
    title = f"I scored {score}/100 on my resume match!"
    description = f"{score}/100 match score for {job_title}"
    if company:
        description += f" @ {company}"
    description += ". Roast your resume too!"

    frontend_url = settings.FRONTEND_URL.rstrip("/")
    share_page_url = f"{frontend_url}/share/{token}"
    # Image endpoint is on this backend server
    image_url = request.build_absolute_uri(f"/api/v1/analysis/shared/{token}/image.png")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Resume Score: {score}/100 — Resume Roaster</title>
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(description)}">
<meta property="og:image" content="{escape(image_url)}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:type" content="website">
<meta property="og:url" content="{escape(share_page_url)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{escape(title)}">
<meta name="twitter:description" content="{escape(description)}">
<meta name="twitter:image" content="{escape(image_url)}">
<meta http-equiv="refresh" content="0;url={escape(share_page_url)}">
</head>
<body>
<p>Redirecting to <a href="{escape(share_page_url)}">Resume Roaster</a>...</p>
</body>
</html>"""
    return HttpResponse(html, content_type="text/html")
