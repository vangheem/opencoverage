import os
from io import StringIO
from typing import Dict, List

from lxml import etree
from unidiff import PatchSet

from opencoverage import types


class ParsingException(Exception):
    ...


def get_el(el: etree.Element, name: str) -> etree.Element:
    rel = el.find(name)
    if rel is None:
        raise ParsingException(f"Could not find element: {name}")
    return rel


def parse_files(data: str) -> Dict[str, str]:
    files: Dict[str, str] = {}
    lines: List[str] = []
    filename = None
    for line in data.strip().splitlines():
        if line == "<<<<<< EOF":
            if filename is not None:
                files[filename] = "\n".join(lines)
            lines = []
            filename = None
        else:
            if filename is None:
                # line should start with # path
                _, _, filename = line.partition("# path=")
            else:
                lines.append(line)
    return files


def parse_raw_coverage_data(data: bytes) -> types.CoverageData:
    text = data.decode("utf-8")
    toc_raw, _, files_data = text.partition("<<<<<< network")
    toc = [li for li in toc_raw.splitlines() if li]

    coverage_files = parse_files(files_data)

    for filename, cov_data in coverage_files.items():
        try:
            dom = etree.fromstring(cov_data)
        except etree.XMLSyntaxError:
            continue

        base_report_path = get_el(get_el(dom, "sources"), "source").text
        file_coverage = {}
        for pel in get_el(dom, "packages").findall("package"):
            for classes in pel.findall("classes"):
                for klass in classes.findall("class"):
                    lines = {}
                    for lel in get_el(klass, "lines").findall("line"):
                        lines[int(lel.attrib["number"])] = int(lel.attrib["hits"])

                    # find correct filename
                    filename = klass.attrib["filename"]
                    if filename not in toc:
                        for part in reversed(base_report_path.split(os.path.sep)):
                            filename = f"{part}{os.path.sep}{filename}"
                            if filename in toc:
                                break
                        else:
                            # could not find valid path, ignore file
                            continue

                    file_coverage[filename] = types.FileCoverageData(
                        line_rate=float(klass.attrib["line-rate"]),
                        branch_rate=float(klass.attrib["branch-rate"]),
                        complexity=float(klass.attrib["complexity"]),
                        lines=lines,
                    )

        return types.CoverageData(
            base_path=None,
            version=dom.attrib["version"],
            timestamp=int(dom.attrib["timestamp"]),
            lines_covered=int(dom.attrib["lines-covered"]),
            lines_valid=int(dom.attrib["lines-valid"]),
            line_rate=float(dom.attrib["line-rate"]),
            branches_covered=int(dom.attrib["branches-covered"]),
            branches_valid=int(dom.attrib["branches-valid"]),
            branch_rate=float(dom.attrib["branch-rate"]),
            complexity=int(dom.attrib["complexity"]),
            file_coverage=file_coverage,
        )
    else:
        raise ParsingException("Could not find coverage file")


def parse_diff(data: str) -> List[types.DiffCoverage]:
    patch_set = PatchSet(StringIO(data))

    diff_datas = []
    for pfile in patch_set:
        if pfile.is_binary_file or pfile.is_removed_file:
            continue
        lines = []
        for chunk in pfile:
            for line in chunk.target_lines():
                if line.is_added:
                    # only care about added lines
                    lines.append(line.target_line_no)
        if len(lines) > 0:
            diff_datas.append(
                types.DiffCoverage(
                    filename=pfile.path, lines=lines, line_rate=0.0, hits=0, misses=0
                )
            )

    return diff_datas
