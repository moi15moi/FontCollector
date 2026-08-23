from pathlib import Path
import textwrap


def render_function(file_content: list[str], dict_name: str, unicode_mapping_file: Path):
    mapping: dict[int, int] = {}
    with open(unicode_mapping_file, encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith("#"):
                continue
            pua_code_str, unicode_str, _ = line.split("\t")
            unicode = int(unicode_str, 16)
            pua_code = int(pua_code_str, 16)
            mapping[unicode] = pua_code

    file_content.append(f"{dict_name} : dict[int, int] = {{")
    for unicode, pua_code in sorted(mapping.items()):
        file_content.append(f"    {hex(unicode)}: {hex(pua_code)},")
    file_content.append("}")
    file_content.append("")


def main():
    SOURCES = [
        {
            "file": Path(__file__).parent.joinpath("ArabicPUASimplified.txt"),
            "function": "arabic_simplified_cmap_mapping",
        },
        {
            "file": Path(__file__).parent.joinpath("ArabicPUATraditional.txt"),
            "function": "arabic_traditional_cmap_mapping",
        },
    ]

    c_file_content = []

    c_file_content.append(textwrap.dedent("""\
    # WARNING - THIS FILE IS AUTO-GENERATED. DO NOT EDIT IT MANUALLY.
    # Regenerate with: python legacy_cmap/gen_cmap.py
    """))

    for source in SOURCES:
        render_function(c_file_content, source["function"], source["file"])

    c_file_path = Path(__file__).parent.parent.joinpath("font_collector", "font", "legacy_cmap_mapping.py")
    c_file_path.write_text("\n".join(c_file_content), encoding="utf-8")



if __name__ == "__main__":
    main()
