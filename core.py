import difflib
import html
import re
import logging
from typing import List, Tuple, Optional
from config import IGNORE_PATTERNS, SYNTAX_HIGHLIGHTING

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Regex patterns
IP_RE = re.compile(r"(?P<ip>\d{1,3}(?:\.\d{1,3}){3})_preCheck\.log$", re.I)
CMD_RE = re.compile(r"^(?:\s*[#$>]\s+|(?:[A-Za-z]:)?[/\\]).+")
ERR_RE = re.compile(r"\b(error|fail(?:ed)?)\b", re.I)
INV_RE = re.compile(r"invalid token", re.I)


class Color:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    END = "\033[0m"

    @classmethod
    def ok(cls, t: str) -> str:
        return f"{cls.GREEN}{t}{cls.END}"

    @classmethod
    def warn(cls, t: str) -> str:
        return f"{cls.YELLOW}{t}{cls.END}"

    @classmethod
    def fail(cls, t: str) -> str:
        return f"{cls.RED}{t}{cls.END}"


class LogStats:
    __slots__ = ("errors", "invalid", "commands")

    def __init__(self) -> None:
        self.errors = 0
        self.invalid = 0
        self.commands: List[str] = []

    @classmethod
    def from_file(cls, path) -> "LogStats":
        inst = cls()
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    if ERR_RE.search(line):
                        inst.errors += 1
                    if INV_RE.search(line):
                        inst.invalid += 1
                    if CMD_RE.match(line.strip()):
                        inst.commands.append(line.strip())
        except FileNotFoundError:
            logger.error("Log file not found: %s", path)
        except Exception as e:
            logger.error("Error reading log file %s: %s", path, e)
        return inst


class DiffEngine:
    """
    Core engine for comparing log files with advanced features like
    moved block detection and anchor-based alignment.
    """

    def __init__(self, ignore_patterns: Optional[List[str]] = None):
        self.ignore_patterns = [re.compile(p) for p in (ignore_patterns or [])]

    def _read_file(self, file_path: str) -> List[str]:
        """Reads a file and returns a list of lines."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                return f.readlines()
        except FileNotFoundError:
            logger.error("File not found: %s", file_path)
            return []
        except Exception as e:
            logger.error("Error reading file %s: %s", file_path, e)
            return []

    def _normalize_line(self, line: str) -> str:
        """
        Removes ignored patterns from the line for comparison purposes.
        """
        normalized = line
        for pattern in IGNORE_PATTERNS:
            normalized = re.sub(pattern, "[[IGNORED]]", normalized)
        return normalized

    def _apply_syntax_highlighting(self, text: str) -> str:
        """
        Applies syntax highlighting to the text using regex patterns.
        """
        highlighted = text
        for cls, pattern in SYNTAX_HIGHLIGHTING.items():
            try:
                # Use a lambda or simple replacement.
                # Be careful about overlapping matches or HTML tags if text is already escaped.
                # Here we assume text is HTML escaped, so we should be careful.
                highlighted = re.sub(
                    pattern, rf'<span class="{cls}">\g<0></span>', highlighted
                )
            except re.error:
                pass
        return highlighted

    def _get_intra_line_diff(self, line1: str, line2: str) -> Tuple[str, str]:
        matcher = difflib.SequenceMatcher(None, line1, line2)
        html1 = []
        html2 = []

        for opcode, a0, a1, b0, b1 in matcher.get_opcodes():
            text1 = html.escape(line1[a0:a1])
            text2 = html.escape(line2[b0:b1])

            if opcode == "equal":
                html1.append(self._apply_syntax_highlighting(text1))
                html2.append(self._apply_syntax_highlighting(text2))
            elif opcode == "replace":
                html1.append(
                    f'<span class="diff-change-del">{self._apply_syntax_highlighting(text1)}</span>'
                )
                html2.append(
                    f'<span class="diff-change-ins">{self._apply_syntax_highlighting(text2)}</span>'
                )
            elif opcode == "delete":
                html1.append(
                    f'<span class="diff-change-del">{self._apply_syntax_highlighting(text1)}</span>'
                )
            elif opcode == "insert":
                html2.append(
                    f'<span class="diff-change-ins">{self._apply_syntax_highlighting(text2)}</span>'
                )

        return "".join(html1), "".join(html2)

    def diff(self, pre_lines: List[str], post_lines: List[str]) -> dict:
        # Use anchor-based diff
        return self._diff_with_anchors(pre_lines, post_lines)

    def _diff_standard(self, pre_lines: List[str], post_lines: List[str]) -> dict:
        # Normalize for comparison
        norm_pre = [self._normalize_line(l) for l in pre_lines]
        norm_post = [self._normalize_line(l) for l in post_lines]

        matcher = difflib.SequenceMatcher(None, norm_pre, norm_post, autojunk=False)

        diff_lines = []
        stats = {"identical": 0, "changed": 0, "added": 0, "removed": 0}

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                stats["identical"] += i2 - i1
                for i, j in zip(range(i1, i2), range(j1, j2)):
                    # Check if original lines are different (e.g. timestamp)
                    orig_pre = pre_lines[i]
                    orig_post = post_lines[j]

                    pre_content = html.escape(orig_pre)
                    pre_content = self._apply_syntax_highlighting(pre_content)

                    post_content = html.escape(orig_post)
                    post_content = self._apply_syntax_highlighting(post_content)

                    diff_lines.append(
                        {
                            "tag": "equal",
                            "pre": {"num": i + 1, "content_html": pre_content},
                            "post": {"num": j + 1, "content_html": post_content},
                        }
                    )
            elif tag == "replace":
                stats["changed"] += max(i2 - i1, j2 - j1)
                for i, j in zip(range(i1, i2), range(j1, j2)):
                    pre_content, post_content = self._get_intra_line_diff(
                        pre_lines[i], post_lines[j]
                    )
                    diff_lines.append(
                        {
                            "tag": "replace",
                            "pre": {"num": i + 1, "content_html": pre_content},
                            "post": {"num": j + 1, "content_html": post_content},
                        }
                    )
            elif tag == "delete":
                stats["removed"] += i2 - i1
                for i in range(i1, i2):
                    content = html.escape(pre_lines[i])
                    content = self._apply_syntax_highlighting(content)
                    diff_lines.append(
                        {
                            "tag": "delete",
                            "pre": {"num": i + 1, "content_html": content},
                            "post": {"num": "", "content_html": ""},
                        }
                    )
            elif tag == "insert":
                stats["added"] += j2 - j1
                for j in range(j1, j2):
                    content = html.escape(post_lines[j])
                    content = self._apply_syntax_highlighting(content)
                    diff_lines.append(
                        {
                            "tag": "insert",
                            "pre": {"num": "", "content_html": ""},
                            "post": {"num": j + 1, "content_html": content},
                        }
                    )

        # Post-processing: Detect moved blocks
        self._detect_moved_blocks(diff_lines)

        is_different = (
            stats["added"] > 0 or stats["removed"] > 0 or stats["changed"] > 0
        )
        return {"stats": stats, "lines": diff_lines, "is_different": is_different}

    def _detect_moved_blocks(self, diff_lines: List[dict]):
        """
        Analyzes diff_lines to find blocks of code that were deleted and inserted elsewhere.
        Marks them as 'moved_from' and 'moved_to'.
        """
        # 1. Collect potential blocks
        deleted_blocks = []  # List of (start_index, end_index, content_str)
        inserted_blocks = []

        current_block = []
        start_idx = -1

        for i, line in enumerate(diff_lines):
            if line["tag"] == "delete":
                if not current_block:
                    start_idx = i
                current_block.append(line["pre"]["content_html"])
            else:
                if current_block:
                    deleted_blocks.append(
                        {
                            "start": start_idx,
                            "end": i,
                            "content": "".join(current_block),
                        }
                    )
                    current_block = []

        # Flush last block
        if current_block:
            deleted_blocks.append(
                {
                    "start": start_idx,
                    "end": len(diff_lines),
                    "content": "".join(current_block),
                }
            )

        current_block = []
        start_idx = -1
        for i, line in enumerate(diff_lines):
            if line["tag"] == "insert":
                if not current_block:
                    start_idx = i
                current_block.append(line["post"]["content_html"])
            else:
                if current_block:
                    inserted_blocks.append(
                        {
                            "start": start_idx,
                            "end": i,
                            "content": "".join(current_block),
                        }
                    )
                    current_block = []

        if current_block:
            inserted_blocks.append(
                {
                    "start": start_idx,
                    "end": len(diff_lines),
                    "content": "".join(current_block),
                }
            )

        # 2. Match blocks
        # Simple exact match for now. Can be improved with similarity check.
        # We iterate through deleted blocks and try to find a match in inserted blocks.

        used_inserts = set()

        for del_block in deleted_blocks:
            # Skip very short blocks (e.g. 1 line) to avoid noise, unless unique?
            # Let's match everything for now.

            best_match = None

            for ins_idx, ins_block in enumerate(inserted_blocks):
                if ins_idx in used_inserts:
                    continue

                if del_block["content"] == ins_block["content"]:
                    best_match = ins_idx
                    break

            if best_match is not None:
                # Mark as moved
                ins_block = inserted_blocks[best_match]
                used_inserts.add(best_match)

                # Update tags in diff_lines
                for i in range(del_block["start"], del_block["end"]):
                    diff_lines[i]["tag"] = "moved_from"
                    # Add link to where it moved? Optional.

                for i in range(ins_block["start"], ins_block["end"]):
                    diff_lines[i]["tag"] = "moved_to"

    def _find_anchors(
        self, pre_lines: List[str], post_lines: List[str]
    ) -> List[Tuple[int, int]]:
        """
        Finds unique lines that appear exactly once in both files and are identical.
        Returns a list of (pre_index, post_index) tuples.
        """
        # 1. Count occurrences
        pre_counts = {}
        for i, line in enumerate(pre_lines):
            norm = self._normalize_line(line).strip()
            if not norm:
                continue
            if norm not in pre_counts:
                pre_counts[norm] = []
            pre_counts[norm].append(i)

        post_counts = {}
        for i, line in enumerate(post_lines):
            norm = self._normalize_line(line).strip()
            if not norm:
                continue
            if norm not in post_counts:
                post_counts[norm] = []
            post_counts[norm].append(i)

        # 2. Find candidates (unique in both)
        candidates = []
        for line, indices in pre_counts.items():
            if len(indices) == 1:
                if line in post_counts and len(post_counts[line]) == 1:
                    candidates.append((indices[0], post_counts[line][0]))

        # 3. Sort by pre_index
        candidates.sort(key=lambda x: x[0])

        # 4. Filter crossing anchors (keep longest increasing subsequence of post_indices)
        # Simple greedy approach: keep anchor if post_index > last_post_index
        anchors = []
        last_post = -1
        for pre_idx, post_idx in candidates:
            if post_idx > last_post:
                anchors.append((pre_idx, post_idx))
                last_post = post_idx

        return anchors

    def _diff_with_anchors(self, pre_lines: List[str], post_lines: List[str]) -> dict:
        anchors = self._find_anchors(pre_lines, post_lines)

        # Add start and end virtual anchors
        full_anchors = [(-1, -1)] + anchors + [(len(pre_lines), len(post_lines))]

        all_diff_lines = []
        stats = {"identical": 0, "changed": 0, "added": 0, "removed": 0}

        for k in range(len(full_anchors) - 1):
            start_pre, start_post = full_anchors[k]
            end_pre, end_post = full_anchors[k + 1]

            # Extract slice between anchors
            sub_pre = pre_lines[start_pre + 1 : end_pre]
            sub_post = post_lines[start_post + 1 : end_post]

            # Run standard diff on slice
            # We need to adjust line numbers in the result!
            sub_result = self.diff_slice(
                sub_pre, sub_post, start_pre + 1, start_post + 1
            )

            all_diff_lines.extend(sub_result["lines"])
            for key in stats:
                stats[key] += sub_result["stats"][key]

            # Add the anchor itself (if not the virtual start/end)
            if k < len(full_anchors) - 2:
                anchor_pre_idx = end_pre
                anchor_post_idx = end_post

                line_content_pre = pre_lines[anchor_pre_idx]
                content_html_pre = html.escape(line_content_pre)
                content_html_pre = self._apply_syntax_highlighting(content_html_pre)

                line_content_post = post_lines[anchor_post_idx]
                content_html_post = html.escape(line_content_post)
                content_html_post = self._apply_syntax_highlighting(content_html_post)

                all_diff_lines.append(
                    {
                        "tag": "equal",
                        "pre": {
                            "num": anchor_pre_idx + 1,
                            "content_html": content_html_pre,
                        },
                        "post": {
                            "num": anchor_post_idx + 1,
                            "content_html": content_html_post,
                        },
                    }
                )
                stats["identical"] += 1

        # Post-processing: Detect moved blocks (global)
        self._detect_moved_blocks(all_diff_lines)

        is_different = (
            stats["added"] > 0 or stats["removed"] > 0 or stats["changed"] > 0
        )
        return {"stats": stats, "lines": all_diff_lines, "is_different": is_different}

    def diff_slice(
        self,
        pre_lines: List[str],
        post_lines: List[str],
        pre_offset: int,
        post_offset: int,
    ) -> dict:
        # Normalize for comparison
        norm_pre = [self._normalize_line(l) for l in pre_lines]
        norm_post = [self._normalize_line(l) for l in post_lines]

        matcher = difflib.SequenceMatcher(None, norm_pre, norm_post, autojunk=False)

        diff_lines = []
        stats = {"identical": 0, "changed": 0, "added": 0, "removed": 0}

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                stats["identical"] += i2 - i1
                for i, j in zip(range(i1, i2), range(j1, j2)):
                    orig_pre = pre_lines[i].rstrip()
                    orig_post = post_lines[j].rstrip()

                    pre_content = html.escape(orig_pre)
                    pre_content = self._apply_syntax_highlighting(pre_content)
                    post_content = html.escape(orig_post)
                    post_content = self._apply_syntax_highlighting(post_content)

                    diff_lines.append(
                        {
                            "tag": "equal",
                            "pre": {
                                "num": pre_offset + i + 1,
                                "content_html": pre_content,
                            },
                            "post": {
                                "num": post_offset + j + 1,
                                "content_html": post_content,
                            },
                        }
                    )
            elif tag == "replace":
                stats["changed"] += max(i2 - i1, j2 - j1)
                # Use zip_longest to handle unequal lengths
                from itertools import zip_longest

                pre_indices = range(i1, i2)
                post_indices = range(j1, j2)

                for i, j in zip_longest(pre_indices, post_indices, fillvalue=None):
                    pre_data = {"num": "", "content_html": ""}
                    post_data = {"num": "", "content_html": ""}

                    if i is not None:
                        pre_line = pre_lines[i].rstrip()
                        if j is not None:
                            # Intra-line diff if both exist
                            pre_content, post_content = self._get_intra_line_diff(
                                pre_line, post_lines[j].rstrip()
                            )
                            pre_data = {
                                "num": pre_offset + i + 1,
                                "content_html": pre_content,
                            }
                            post_data = {
                                "num": post_offset + j + 1,
                                "content_html": post_content,
                            }
                        else:
                            # Only pre exists (treated as delete in replace block)
                            content = html.escape(pre_line)
                            content = self._apply_syntax_highlighting(content)
                            pre_data = {
                                "num": pre_offset + i + 1,
                                "content_html": content,
                            }
                    elif j is not None:
                        # Only post exists (treated as insert in replace block)
                        content = html.escape(post_lines[j].rstrip())
                        content = self._apply_syntax_highlighting(content)
                        post_data = {
                            "num": post_offset + j + 1,
                            "content_html": content,
                        }

                    diff_lines.append(
                        {
                            "tag": "replace",
                            "pre": pre_data,
                            "post": post_data,
                        }
                    )
            elif tag == "delete":
                stats["removed"] += i2 - i1
                for i in range(i1, i2):
                    content = html.escape(pre_lines[i].rstrip())
                    content = self._apply_syntax_highlighting(content)
                    diff_lines.append(
                        {
                            "tag": "delete",
                            "pre": {"num": pre_offset + i + 1, "content_html": content},
                            "post": {"num": "", "content_html": ""},
                        }
                    )
            elif tag == "insert":
                stats["added"] += j2 - j1
                for j in range(j1, j2):
                    content = html.escape(post_lines[j].rstrip())
                    content = self._apply_syntax_highlighting(content)
                    diff_lines.append(
                        {
                            "tag": "insert",
                            "pre": {"num": "", "content_html": ""},
                            "post": {
                                "num": post_offset + j + 1,
                                "content_html": content,
                            },
                        }
                    )

        return {"stats": stats, "lines": diff_lines}
