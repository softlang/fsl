import re
import time
from collections import defaultdict
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import unquote, urlsplit

import requests


CONTACT_EMAIL = "softlang@uni-koblenz.de"


def retry_delay(response, attempt):
    """Honor Retry-After (seconds or HTTP date), plus exponential backoff."""
    delay = 5 * (2 ** attempt)
    value = response.headers.get("Retry-After") if response is not None else None
    if value:
        try:
            seconds = float(value)
        except ValueError:
            try:
                seconds = (
                    parsedate_to_datetime(value) - datetime.now(timezone.utc)
                ).total_seconds()
            except (ValueError, TypeError, OverflowError):
                seconds = 0
        delay = max(delay, seconds)
    return delay


def query_batch(session, host, titles):
    """Return (query data or None, request metadata). At most 4 attempts."""
    params = {
        "action": "query",
        "format": "json",
        "formatversion": "2",
        "titles": "|".join(titles),
        "redirects": "1",
        "prop": "info",
        "inprop": "url",
        "maxlag": "5",
    }

    for attempt in range(4):
        response = None
        meta = {"http_status": None, "api_code": None, "message": None}

        # Conservative pacing, including across consecutive function calls.
        time.sleep(1)

        try:
            response = session.get(
                f"https://{host}/w/api.php",
                params=params,
                timeout=(10, 30),
                allow_redirects=False,
            )
            meta["http_status"] = response.status_code

            if response.status_code != 200:
                meta["message"] = f"HTTP {response.status_code}"
                temporary = response.status_code in {429, 500, 502, 503, 504}
            else:
                try:
                    data = response.json()
                except ValueError:
                    return None, {**meta, "message": "Non-JSON API response"}

                if not isinstance(data, dict):
                    return None, {**meta, "message": "Unexpected API response"}

                if "error" in data:
                    error = data["error"]
                    meta.update(
                        api_code=error.get("code"),
                        message=error.get("info"),
                    )
                    temporary = error.get("code") in {"maxlag", "ratelimited"}
                elif isinstance(data.get("query", {}).get("pages"), list):
                    return data["query"], meta
                else:
                    return None, {**meta, "message": "Missing page results"}

        except (requests.Timeout, requests.ConnectionError) as exc:
            meta["message"] = str(exc)
            temporary = True
        except requests.RequestException as exc:
            return None, {**meta, "message": str(exc)}

        # Includes immediate stop for HTTP 401/403: don't retry access denial.
        if not temporary or attempt == 3:
            return None, meta

        time.sleep(retry_delay(response, attempt))


def check_wikipedia_links(links):
    """
    Accept up to 50 ordinary Wikipedia /wiki/... URLs, across editions.

    Return statuses:
      exists       -> resolved page exists
      missing      -> API explicitly says resolved page is missing
      invalid      -> API explicitly rejects the page title
      invalid_url  -> malformed/unsupported input URL; no request made
      check_failed -> existence unknown; inspect HTTP/API code and message

    Section anchors (#History) are ignored, not checked.
    """
    links = list(links)
    if len(links) > 50:
        raise ValueError("Pass at most 50 links per call.")
    if CONTACT_EMAIL == "YOUR_EMAIL_HERE":
        raise ValueError("Set CONTACT_EMAIL before running.")

    results = []
    groups = defaultdict(list)

    for index, link in enumerate(links):
        row = {
            "url": link,
            "status": "invalid_url",
            "http_status": None,
            "api_code": None,
            "message": None,
            "resolved_title": None,
            "resolved_url": None,
            "redirected": False,
        }
        results.append(row)

        try:
            parsed = urlsplit(link)
            host = (parsed.hostname or "").lower()
            # Accept desktop and mobile URLs; query the desktop API.
            host = host.replace(".m.wikipedia.org", ".wikipedia.org")
            title = unquote(parsed.path[len("/wiki/"):]).replace("_", " ")

            if (
                parsed.scheme not in {"http", "https"}
                or not re.fullmatch(r"[a-z0-9-]+\.wikipedia\.org", host)
                or host == "www.wikipedia.org"
                or parsed.username is not None
                or parsed.password is not None
                or parsed.port is not None
                or not parsed.path.startswith("/wiki/")
                or parsed.query  # This skeleton checks current article URLs.
                or not title.strip()
                or "|" in title
                or any(ord(c) < 32 for c in title)
            ):
                raise ValueError("Expected a Wikipedia /wiki/Article URL.")

            groups[host].append((index, title))
        except (ValueError, TypeError, AttributeError) as exc:
            row["message"] = str(exc)

    with requests.Session() as session:
        session.headers["User-Agent"] = (
            f"WikiLinkChecker/1.0 (mailto:{CONTACT_EMAIL})"
        )

        for host, entries in groups.items():
            titles = list(dict.fromkeys(title for _, title in entries))
            query, meta = query_batch(session, host, titles)

            if query is None:
                for index, _ in entries:
                    results[index].update(meta, status="check_failed")
                continue

            # Reconcile normalization (e.g. capitalization) and redirects.
            mappings = {}
            for key in ("normalized", "converted", "redirects"):
                mappings.update(
                    (item["from"], item["to"])
                    for item in query.get(key, [])
                )
            redirect_sources = {
                item["from"] for item in query.get("redirects", [])
            }
            pages = {page["title"]: page for page in query["pages"]}

            for index, title in entries:
                seen = set()
                redirected = False
                while title in mappings and title not in seen:
                    seen.add(title)
                    redirected |= title in redirect_sources
                    title = mappings[title]

                page = pages.get(title)
                row = results[index]
                row.update(meta, resolved_title=title, redirected=redirected)

                if page is None:
                    row.update(
                        status="check_failed",
                        message="No matching result; redirect may be unresolved.",
                    )
                elif "invalid" in page:
                    row.update(
                        status="invalid",
                        message=page.get("invalidreason"),
                    )
                elif "missing" in page:
                    row["status"] = "missing"
                elif page.get("pageid", 0) > 0:
                    row.update(
                        status="exists",
                        resolved_url=page.get("fullurl"),
                    )
                else:
                    row.update(
                        status="check_failed",
                        message="API did not confirm a stored page.",
                    )

    return results
