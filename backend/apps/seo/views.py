from django.http import HttpResponse
from django.utils import timezone


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
