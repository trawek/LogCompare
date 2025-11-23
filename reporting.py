# log_comparator/reporting.py

import datetime as dt
import logging
from concurrent.futures import ProcessPoolExecutor, as_completed
import json
from pathlib import Path
from typing import Dict, Tuple
import threading
import base64
from io import BytesIO
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from jinja2 import Environment, FileSystemLoader
from core import DiffEngine, IP_RE
from localization import Localization


class InterruptedException(Exception):
    pass


def run_single_host_processing(task_data: dict) -> dict:
    ip, pre_f_str, post_f_str = (
        task_data["ip"],
        task_data["pre_path"],
        task_data["post_path"],
    )
    out_dir, lang_code, output_format = (
        Path(task_data["output_dir"]),
        task_data["lang_code"],
        task_data["output_format"],
    )
    templates_path, locales_path = (
        task_data["templates_path"],
        task_data["locales_path"],
    )
    folder = task_data.get("folder", ".")

    pre_f, post_f = Path(pre_f_str), Path(post_f_str)
    loc = Localization(lang_code, locales_path)
    env = Environment(loader=FileSystemLoader(templates_path))
    status_key = "missing"

    # Ensure output subdir for diffs exists (might be race condition if not pre-created, but usually fine)
    # Actually Reporter creates 'diffs', but we might want structure there too?
    # For now flat diffs folder is fine, or we can replicate structure.
    # Let's keep flat diffs folder for simplicity of linking, filenames are unique by IP.

    if not post_f.exists():
        return {"ip": ip, "folder": folder, "status_key": status_key, "line_stats": {}}

    pre_lines = pre_f.read_text(errors="ignore").splitlines()
    post_lines = post_f.read_text(errors="ignore").splitlines()
    diff_result = DiffEngine().diff(pre_lines, post_lines)

    if output_format != "json" and output_format != "csv":
        diff_template = env.get_template("diff_view.html")
        diff_html = diff_template.render(
            t=loc.get_string,
            is_custom_comparison=False,
            ip=ip,
            pre_file=pre_f.name,
            post_file=post_f.name,
            lines=diff_result["lines"],
        )
        (out_dir / "diffs" / f"diff_{ip}.html").write_text(diff_html, encoding="utf-8")
        host_template = env.get_template("host.html")
        host_html = host_template.render(
            t=loc.get_string, ip=ip, diff_file_path=f"diffs/diff_{ip}.html"
        )
        (out_dir / f"host_{ip}.html").write_text(host_html, encoding="utf-8")

    status_key = "different" if diff_result["is_different"] else "identical"
    return {
        "ip": ip,
        "folder": folder,
        "status_key": status_key,
        "line_stats": diff_result["stats"],
    }


class Reporter:
    def __init__(
        self,
        src: Path,
        out: Path,
        loc: Localization,
        templates_path: str,
        locales_path: str,
        output_format: str = "html",
        cancel_event: threading.Event = None,
    ):
        self.src, self.out, self.loc, self.output_format, self.cancel_event = (
            src,
            out,
            loc,
            output_format,
            cancel_event,
        )
        self.templates_path = templates_path
        self.locales_path = locales_path
        self.env = Environment(loader=FileSystemLoader(self.templates_path))
        (self.out / "diffs").mkdir(parents=True, exist_ok=True)

    def _parse_summary_file(self, file_path: Path) -> dict:
        stats = {}
        if not file_path.exists():
            return {"Error": f"File not found: {file_path.name}"}
        try:
            with file_path.open("r", encoding="utf-8") as f:
                for line in f:
                    if ":" in line:
                        key, val = line.split(":", 1)
                        if clean_key := key.strip().lstrip("- ").strip():
                            stats[clean_key] = val.strip()
        except Exception as e:
            logging.error(f"Could not parse summary file {file_path}: {e}")
            stats["Error"] = "Could not parse file."
        return stats

    def _collect_pairs(self) -> Dict[str, Tuple[Path, Path]]:
        pairs = {}
        # Recursive search for preCheck logs
        # We look for files ending with _preCheck.log
        for pre_path in self.src.rglob("*_preCheck.log"):
            if m := IP_RE.search(pre_path.name):
                ip = m.group("ip")
                # Assume postCheck is in the same directory
                post_path = pre_path.parent / f"{ip}_postCheck.log"
                pairs[ip] = (pre_path, post_path)
        return pairs

    def _prepare_report_data(self) -> dict:
        pairs = self._collect_pairs()
        if not pairs:
            raise RuntimeError("No log files found.")
        host_results = []

        tasks = []
        for ip, paths in pairs.items():
            try:
                rel_folder = paths[0].parent.relative_to(self.src)
                folder_str = str(rel_folder)
                if folder_str == ".":
                    folder_str = "Root"
            except ValueError:
                folder_str = "External"

            tasks.append(
                {
                    "ip": ip,
                    "pre_path": str(paths[0]),
                    "post_path": str(paths[1]),
                    "output_dir": str(self.out),
                    "lang_code": self.loc.language,
                    "output_format": self.output_format,
                    "templates_path": self.templates_path,
                    "locales_path": self.locales_path,
                    "folder": folder_str,
                }
            )

        with ProcessPoolExecutor() as executor:
            future_to_task = {
                executor.submit(run_single_host_processing, task): task
                for task in tasks
            }
            for future in as_completed(future_to_task):
                if self.cancel_event and self.cancel_event.is_set():
                    executor.shutdown(wait=False, cancel_futures=True)
                    raise InterruptedException("Generation stopped by user.")
                try:
                    host_results.append(future.result())
                except Exception as e:
                    logging.error(
                        f"Error processing task {future_to_task[future]['ip']}: {e}"
                    )

        if self.cancel_event and self.cancel_event.is_set():
            raise InterruptedException("Generation stopped by user.")

        # Sort by folder then IP
        host_results.sort(key=lambda x: (x["folder"], x["ip"]))

        total_line_stats = {"identical": 0, "changed": 0, "added": 0, "removed": 0}
        status_counts = {"identical": 0, "different": 0, "missing": 0}

        for res in host_results:
            status_counts[res["status_key"]] += 1
            for key in total_line_stats:
                total_line_stats[key] += res.get("line_stats", {}).get(key, 0)

        for result in host_results:
            result["status"] = self.loc.get_string(result["status_key"])
            result["link"] = f"host_{result['ip']}.html"
            line_stats = result.get("line_stats", {})
            result["changed"] = line_stats.get("changed", 0)
            result["added"] = line_stats.get("added", 0)
            result["removed"] = line_stats.get("removed", 0)

        pre_summary = self._parse_summary_file(self.src / "summary_preCheck.txt")
        post_summary = self._parse_summary_file(self.src / "summary_postCheck.txt")

        host_status_segments = []
        total_hosts = len(host_results)
        if total_hosts > 0:
            segment_data = [
                ("different", "status_different", "#f44336"),
                ("identical", "status_identical", "#4caf50"),
                ("missing", "status_missing", "#9e9e9e"),
            ]
            for status, key, color in segment_data:
                count = status_counts.get(status, 0)
                if count > 0:
                    host_status_segments.append(
                        {
                            "label": self.loc.get_string(key),
                            "count": count,
                            "percentage": (count / total_hosts) * 100,
                            "color": color,
                        }
                    )

        return {
            "t": self.loc.get_string,
            "generation_time": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "pre_summary": pre_summary,
            "post_summary": post_summary,
            "hosts": host_results,
            "total_hosts": len(host_results),
            "total_line_stats": total_line_stats,
            "status_counts": status_counts,
            "host_status_segments": host_status_segments,
        }

    def generate(self) -> Path:
        report_data = self._prepare_report_data()
        if self.cancel_event and self.cancel_event.is_set():
            raise InterruptedException("Generation stopped.")

        template = self.env.get_template("index.html")
        html_string = template.render(report_data)
        index_path = self.out / "index.html"
        index_path.write_text(html_string, encoding="utf-8")

        if self.output_format == "pdf":
            try:
                import weasyprint

                report_data["is_pdf_report"] = True
                html_for_pdf = template.render(report_data)
                pdf_path = self.out / "report.pdf"
                weasyprint.HTML(string=html_for_pdf, base_url=str(self.out)).write_pdf(
                    pdf_path
                )
                return pdf_path
            except ImportError:
                raise ImportError("WeasyPrint library not found.")
        elif self.output_format == "json":
            for key in ["t", "lang_code", "host_status_segments", "total_line_stats"]:
                report_data.pop(key, None)
            json_path = self.out / "report.json"
            with json_path.open("w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=4, ensure_ascii=False)
            return json_path

        return index_path

    def export_csv(self) -> Path:
        """Generates a CSV report."""
        import csv

        report_data = self._prepare_report_data()
        if self.cancel_event and self.cancel_event.is_set():
            raise InterruptedException("Generation stopped.")

        csv_path = self.out / "report.csv"
        hosts = report_data.get("hosts", [])

        with csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            # Header
            writer.writerow(
                [
                    "Folder",
                    "IP",
                    "Status",
                    "Changed Lines",
                    "Added Lines",
                    "Removed Lines",
                ]
            )

            for host in hosts:
                writer.writerow(
                    [
                        host.get("folder", ""),
                        host.get("ip", ""),
                        host.get("status_key", ""),
                        host.get("changed", 0),
                        host.get("added", 0),
                        host.get("removed", 0),
                    ]
                )
        return csv_path
