import os
from pathlib import Path
from core import DiffEngine
from jinja2 import Environment, FileSystemLoader

# Setup paths
base_dir = Path(os.getcwd())
templates_dir = base_dir / "templates"
output_file = base_dir / "verification_report.html"

# Create dummy content with test cases for Ignore Rules and Syntax Highlighting
pre_content = [
    "Short line 1",
    "last login : 20/11/25 10:00:00",  # Should be ignored if next line matches normalized
    "Interface GigabitEthernet1/0/1 is up",  # Syntax: up (success)
    "IP address is 192.168.1.1",  # Syntax: IP
    "00:11:22:33:44:55",  # Syntax: MAC
    'description "Critical Link"',  # Syntax: string, keyword
    "Alarm severity critical detected",  # Syntax: error
    "COMMON CONTEXT BEFORE",
    "MOVED BLOCK LINE 1",
    "MOVED BLOCK LINE 2",
    "MOVED BLOCK LINE 3",
    "COMMON CONTEXT AFTER",
]

post_content = [
    "Short line 1",
    "last login : 21/11/25 11:00:00",  # Different timestamp, should be ignored -> Identical
    "Interface GigabitEthernet1/0/1 is down",  # Syntax: down (error), Diff: Changed
    "IP address is 192.168.1.2",  # Diff: Changed IP
    "00:11:22:33:44:55",
    'description "Backup Link"',  # Diff: Changed string
    "Alarm severity critical detected",
    "COMMON CONTEXT BEFORE",
    "COMMON CONTEXT AFTER",
    "MOVED BLOCK LINE 1",
    "MOVED BLOCK LINE 2",
    "MOVED BLOCK LINE 3",
]

# Generate diff
engine = DiffEngine()
diff_result = engine.diff(pre_content, post_content)


# Mock translation function
def t(key, **kwargs):
    defaults = {
        "diff_view_title": "Verification Report: {ip}",
        "back_to_host_btn": "Back",
        "search_label": "Search",
        "search_placeholder": "Search...",
        "prev_diff_btn": "Prev",
        "next_diff_btn": "Next",
        "legend_added": "Added",
        "legend_changed": "Changed",
        "legend_removed": "Removed",
        "legend_moved": "Moved",
    }
    val = defaults.get(key, key)
    if isinstance(val, str):
        return val.format(**kwargs)
    return val


env = Environment(loader=FileSystemLoader(templates_dir))
template = env.get_template("diff_view.html")

html = template.render(
    t=t,
    ip="TEST_HOST",
    pre_file="pre_check.log",
    post_file="post_check.log",
    lines=diff_result["lines"],
    is_custom_comparison=True,
)

output_file.write_text(html, encoding="utf-8")
print(f"Verification report generated at: {output_file}")
