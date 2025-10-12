import logging
from pathlib import Path
from typing import Optional

from .ass.ass_document import AssDocument
from .font import (
    FontCollection,
    FontFile,
    FontSelectionStrategy,
    VariableFontFace,
    font_weight_to_name
)

_logger = logging.getLogger(__name__)


def collect_subtitle_fonts(
        subtitle: AssDocument,
        font_collection: FontCollection,
        font_strategy: FontSelectionStrategy,
        collect_draw_fonts: bool,
        convert_variable_to_collection: bool = False,
        output_variable_font_directory: Optional[Path] = None
    ) -> set[FontFile]:
    """
    Collect the fonts used in a given subtitle (ASS) document.

    Args:
        subtitle (AssDocument): The ASS subtitle document to be analyzed.
        font_collection (FontCollection): The collection of available fonts that will be used to match against the subtitle's styles.
        font_strategy (FontSelectionStrategy): The strategy used to select the best matching font for each style.
        collect_draw_fonts (bool): Whether to include fonts used in ASS drawing commands (`\\pN` commands).
        convert_variable_to_collection (bool): If True, variable fonts found in the subtitle will be converted into
            a TrueType Collection (TTC) file and written to the specified output directory.
        output_variable_font_directory (Optional[Path]): The directory where converted variable fonts will be saved, if applicable.
            Required when `convert_variable_to_collection` is True.

    Returns:
        A set of `FontFile` objects representing all fonts used by the ASS document.
    """
    fonts_file_found: set[FontFile] = set()

    used_styles = subtitle.get_used_style(collect_draw_fonts)

    nbr_font_not_found = 0

    for style, usage_data in used_styles.items():

        font_result = font_collection.get_used_font_by_style(style, font_strategy)

        # Did not found the font
        if font_result is None:
            nbr_font_not_found += 1
            _logger.error(
                f"Could not find font '{style.fontname}'\n"
                f"Used on lines: {' '.join(str(line) for line in usage_data.ordered_lines)}"
            )
        else:
            log_msg = ""
            if font_result.need_faux_bold:
                log_msg = f"Faux bold used for '{style.fontname}' (requested weight {style.weight}-{(font_weight_to_name(style.weight))}, got {font_result.font_face.weight}-{(font_weight_to_name(font_result.font_face.weight))})."
            elif font_result.mismatch_bold:
                log_msg = f"Mismatched weight for '{style.fontname}' (requested weight {style.weight}-{(font_weight_to_name(style.weight))}, got {font_result.font_face.weight}-{(font_weight_to_name(font_result.font_face.weight))})."
            if font_result.mismatch_italic:
                log_msg = f"Mismatched italic for '{style.fontname}' (requested {'' if style.italic else 'non-'}italic, got {'' if font_result.font_face.is_italic else 'non-'}italic)."

            if log_msg:
                _logger.warning(
                    f"{log_msg}\n"
                    f"Used on lines: {' '.join(str(line) for line in usage_data.ordered_lines)}"
                )


            missing_glyphs = font_result.font_face.get_missing_glyphs(usage_data.characters_used)
            if len(missing_glyphs) > 0:
                _logger.warning(f"'{style.fontname}' is missing the following glyphs used: {missing_glyphs}")


            if font_result.font_face.font_file is None:
                raise ValueError(f"This font_face \"{font_result.font_face}\" isn't linked to any FontFile.")

            if convert_variable_to_collection and isinstance(font_result.font_face, VariableFontFace):
                if output_variable_font_directory is None:
                    raise ValueError("When ``convert_variable_to_collection`` is True, you must provide a value for ``output_variable_font_directory``.")
                font_name = font_result.font_face.get_best_family_prefix_from_lang().value
                font_filename = output_variable_font_directory.joinpath(f"{font_name}.ttc")
                generated_font_file = font_result.font_face.variable_font_to_collection(font_filename)
                fonts_file_found.add(generated_font_file)
            else:
                fonts_file_found.add(font_result.font_face.font_file)

    if nbr_font_not_found == 0:
        _logger.info(f"All font(s) found")
    else:
        _logger.error(f"{nbr_font_not_found} font(s) could not be found.")

    return fonts_file_found

