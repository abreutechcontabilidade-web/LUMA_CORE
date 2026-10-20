import urllib.request, urllib.parse, urllib.error, json, time, random
from email.utils import parsedate_to_datetime

class GitHubRateLimitError(Exception):
    pass

def search_game_repo(query_terms, max_retries=3, max_wait_seconds=10):
    # GATE-32: per_page=5 para ter mais opções
    api_url = f"https://api.github.com/search/repositories?q={urllib.parse.quote(query_terms)}&sort=stars&order=desc&per_page=5"
    retries = 0
    while retries < max_retries:
        try:
            req = urllib.request.Request(api_url, headers={'User-Agent': 'LUMA_CORE_Agent'})
            with urllib.request.urlopen(req, timeout=10) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            if e.code in [403, 429]:
                wait_time = None
                retry_after = e.headers.get('Retry-After')
                reset_time = e.headers.get('X-RateLimit-Reset')
                if retry_after:
                    try: wait_time = int(retry_after)
                    except ValueError:
                        try:
                            dt = parsedate_to_datetime(retry_after)
                            wait_time = max(0, int(dt.timestamp() - time.time()))
                        except Exception: pass
                if wait_time is None and reset_time:
                    try: wait_time = max(0, int(reset_time) - int(time.time()))
                    except ValueError: pass
                if wait_time is None: wait_time = (2 ** retries) + random.uniform(0, 1)
                if wait_time > max_wait_seconds:
                    raise GitHubRateLimitError(f"Espera de {wait_time}s excede o maximo de {max_wait_seconds}s.")
                print(f"[GITHUB API] Rate limit. A aguardar {wait_time:.2f}s...")
                time.sleep(wait_time)
                retries += 1
            else:
                raise e
        except Exception as e:
            print(f"[GITHUB API] Erro de rede: {e}")
            retries += 1
            time.sleep(2)
    raise GitHubRateLimitError("Maximo de retentativas excedido.")