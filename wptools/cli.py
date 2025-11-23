from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .client import WPAdminClient, WPAdminCredentials
from .exceptions import WPAuthenticationError, WPRequestError
from .exporter import export_to_php_file


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export WordPress data as a PHP array")
    parser.add_argument("--url", required=True, help="Base URL of the WordPress site (e.g. https://example.com)")
    parser.add_argument("--username", required=True, help="Administrator username")
    parser.add_argument("--password", required=True, help="Administrator password")
    parser.add_argument("--output", default="wordpress-export.php", help="Path to write the PHP export file")
    parser.add_argument("--timeout", type=int, default=10, help="HTTP timeout in seconds")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.debug:
        import logging

        logging.basicConfig(level=logging.DEBUG, format="[%(levelname)s] %(message)s")
    creds = WPAdminCredentials(
        base_url=args.url,
        username=args.username,
        password=args.password,
        timeout=args.timeout,
    )
    client = WPAdminClient(creds)

    try:
        print("[1/3] Connexion à WordPress…")
        client.login()
        print("[2/3] Récupération du contenu…")
        data = client.export_content()
        print("[3/3] Génération du fichier PHP…")
        output_path = export_to_php_file(data, Path(args.output))
        print(f"Export terminé: {output_path}")
        return 0
    except WPAuthenticationError as exc:
        print(f"Erreur d'authentification: {exc}", file=sys.stderr)
    except WPRequestError as exc:
        print(f"Erreur lors de la récupération des données: {exc}", file=sys.stderr)
    except Exception as exc:  # pragma: no cover - catch-all for unexpected issues
        print(f"Erreur inattendue: {exc}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
