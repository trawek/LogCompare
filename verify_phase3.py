import os
import shutil
from pathlib import Path
from reporting import Reporter
from localization import Localization

# Setup test environment
base_dir = Path("test_env_phase3_v2")
if base_dir.exists():
    try:
        shutil.rmtree(base_dir, ignore_errors=True)
    except Exception as e:
        print(f"Warning: Could not fully clean up {base_dir}: {e}")

if not base_dir.exists():
    base_dir.mkdir()

src_dir = base_dir / "logs"
src_dir.mkdir(exist_ok=True)
out_dir = base_dir / "output"
out_dir.mkdir(exist_ok=True)

# Create nested structure
(src_dir / "RegionA").mkdir(exist_ok=True)
(src_dir / "RegionB").mkdir(exist_ok=True)


# Create dummy logs
def create_logs(folder, ip, content_pre, content_post):
    (folder / f"{ip}_preCheck.log").write_text(content_pre, encoding="utf-8")
    (folder / f"{ip}_postCheck.log").write_text(content_post, encoding="utf-8")


create_logs(
    src_dir / "RegionA", "192.168.1.1", "Line 1\nLine 2", "Line 1\nLine 2"
)  # Identical
create_logs(src_dir / "RegionA", "192.168.1.2", "Line A", "Line B")  # Different
create_logs(src_dir / "RegionB", "10.0.0.1", "Config X", "Config X")  # Identical


# Create localization mock
class MockLoc:
    language = "en"

    def get_string(self, key, **kwargs):
        return key


if __name__ == "__main__":
    # Run Reporter
    print("Generating HTML Report...")
    reporter = Reporter(src_dir, out_dir, MockLoc(), "templates", "locales")
    html_path = reporter.generate()
    print(f"HTML Report generated at: {html_path}")

    # Verify HTML content for Tree View elements
    html_content = html_path.read_text(encoding="utf-8")
    if "RegionA" in html_content and "RegionB" in html_content:
        print("SUCCESS: Folder names found in HTML.")
    else:
        print("FAILURE: Folder names NOT found in HTML.")

    if '<details class="folder-group"' in html_content:
        print("SUCCESS: Tree view details element found.")
    else:
        print("FAILURE: Tree view details element NOT found.")

    if (
        'class="diff-row equal"' in html_content
        or 'class="diff-row equal"' in html_content
    ):
        print("SUCCESS: 'diff-row equal' class found in HTML.")
    else:
        print(
            "FAILURE: 'diff-row equal' class NOT found in HTML. Folding will not work!"
        )

    # Run CSV Export
    print("Exporting CSV...")
    csv_path = reporter.export_csv()
    print(f"CSV Report generated at: {csv_path}")

    # Verify CSV content
    csv_content = csv_path.read_text(encoding="utf-8")
    lines = csv_content.splitlines()
    print(f"CSV Lines: {len(lines)}")
    if len(lines) >= 4:  # Header + 3 hosts
        print("SUCCESS: CSV has expected number of lines.")
        if "RegionA" in csv_content and "192.168.1.1" in csv_content:
            print("SUCCESS: CSV contains expected data.")
        else:
            print("FAILURE: CSV missing expected data.")
    else:
        print("FAILURE: CSV has too few lines.")
