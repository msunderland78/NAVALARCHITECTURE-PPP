import os
import sys
import urllib.error
import urllib.request


def main():
    host = os.getenv("PPP_HEALTHCHECK_HOST", "127.0.0.1")
    port = os.getenv("PPP_PORT", "8000")
    url = f"http://{host}:{port}/health"
    try:
        with urllib.request.urlopen(url, timeout=3) as response:
            if response.status != 200:
                sys.stderr.write(f"healthcheck status {response.status}\n")
                return 1
            response.read()
        return 0
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        sys.stderr.write(f"healthcheck failed: {error}\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
