# log_comparator/main.py

import argparse
import sys
import os
import logging
from pathlib import Path
import multiprocessing

from core import Color
from reporting import Reporter
from gui import GuiApp
from localization import Localization, SUPPORTED_LANGUAGES
from utils import resource_path

logging.basicConfig(
    filename="log_comparator.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


def main():
    parser = argparse.ArgumentParser(description="Log Comparator Final")
    parser.add_argument("src", nargs="?", help="Directory containing log files")
    parser.add_argument("out", nargs="?", help="Output directory for HTML reports")
    parser.add_argument("--gui", action="store_true", help="Force GUI mode")
    parser.add_argument(
        "--lang",
        default="pl",
        choices=SUPPORTED_LANGUAGES.keys(),
        help="Set language for the application",
    )
    parser.add_argument(
        "--format",
        default="html",
        choices=["html", "json", "pdf"],
        help="Set the output report format",
    )
    args = parser.parse_args()

    # Rozwiązujemy ścieżki raz, w głównym punkcie aplikacji
    templates_path = resource_path("templates")
    locales_path = resource_path("locales")

    # Tworzymy obiekt lokalizacji z poprawną ścieżką
    loc = Localization(args.lang, locales_path=locales_path)

    if args.gui or not (args.src and args.out):
        try:
            # Przekazujemy gotowe ścieżki do GUI
            app = GuiApp(loc, templates_path, locales_path)
            app.run()
        except Exception as e:
            print(f"An unexpected application error occurred: {e}")
            logging.exception("GUI mode failed to start or crashed.")
            sys.exit(1)
    else:
        try:
            src_path, out_path = Path(args.src), Path(args.out)
            if not src_path.is_dir():
                print(Color.fail(f"Error: Source directory does not exist: {src_path}"))
                sys.exit(1)

            print(
                Color.warn(
                    f"Generating comparison report in '{args.format}' format in: {out_path}"
                )
            )
            # Przekazujemy gotowe ścieżki do Reportera
            reporter = Reporter(
                src_path,
                out_path,
                loc,
                templates_path,
                locales_path,
                output_format=args.format,
            )
            report_path = reporter.generate()
            print(Color.ok(f"Report generated successfully: {report_path}"))

            try:
                os.startfile(report_path)
            except Exception:
                print(Color.warn("Could not automatically open the report."))

        except Exception as e:
            print(Color.fail(f"An unexpected error occurred: {e}"))
            logging.exception("CLI execution failed.")
            sys.exit(1)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
