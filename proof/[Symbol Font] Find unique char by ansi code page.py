from fontTools.agl import LEGACY_AGL2UV


def generate_supported_char_by_code_page(code_pages: list[int]) -> dict[int, set[str]]:
    supported_char_by_code_page: dict[int, set[str]] = {}

    for code_page in code_pages:
        code_page_encoding_name = f"cp{code_page}"

        for codepoint in range(0, 256):
            try:
                codepoint_byte = int.to_bytes(codepoint, 1, "big")
                char = codepoint_byte.decode(code_page_encoding_name)
            except UnicodeDecodeError:
                continue

            if code_page not in supported_char_by_code_page:
                supported_char_by_code_page[code_page] = set()
            
            supported_char_by_code_page[code_page].add(char)
        
    return supported_char_by_code_page


def generate_unique_char_by_code_page(supported_char_by_code_page: dict[int, set[str]]) -> dict[int, set[str]]:
    unique_char_by_code_page: dict[int, set[str]] = {}

    for codepoint, char_set in supported_char_by_code_page.items():
        unique_char_by_code_page[codepoint] = set(char_set)

        for other_codepoint, other_char_set in supported_char_by_code_page.items():
            if other_codepoint == codepoint:
                continue
            
            unique_char_by_code_page[codepoint] -= other_char_set

    return unique_char_by_code_page


def generate_unique_adobe_glyph_name_by_code_page(unique_char_by_code_page: dict[int, set[str]]) -> dict[int, set[str]]:
    unique_adobe_glyph_name_by_code_page: dict[int, set[str]] = {}

    for codepoint, char_set in unique_char_by_code_page.items():
        unique_adobe_glyph_name_by_code_page[codepoint] = set()

        for char in char_set:
            found = False
            for legacy_adobe_glyph_name, adobe_codepoints in LEGACY_AGL2UV.items():
                for adobe_codepoint in adobe_codepoints:
                    if adobe_codepoint == ord(char):
                        unique_adobe_glyph_name_by_code_page[codepoint].add(legacy_adobe_glyph_name.lower())
                        found = True
            
            if not found:
                print(char)
                print(hex(ord(char)))
    
    return unique_adobe_glyph_name_by_code_page


def main():
    code_pages = [
        874,
        932,
        936,
        949,
        950,
        1250,
        1251,
        1252,
        1253,
        1254,
        1255,
        1256,
        1257,
        1258,
    ]


    supported_char_by_code_page = generate_supported_char_by_code_page(code_pages)
    unique_char_by_code_page = generate_unique_char_by_code_page(supported_char_by_code_page)
    unique_adobe_glyph_name_by_code_page = generate_unique_adobe_glyph_name_by_code_page(unique_char_by_code_page)

    #for codepoint, char_set in unique_char_by_code_page.items():
    #    print(f"{codepoint} {char_set}")


    #for codepoint, adobe_glyph_name in unique_adobe_glyph_name_by_code_page.items():
    #    print(f"{codepoint}: {adobe_glyph_name},")
    #    print()


if __name__ == "__main__":
    main()
