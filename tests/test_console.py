from io import StringIO

from rich.console import Console

from utils.console import (
    format_metric,
    highlight_markers,
    metrics_panel,
    new_progress_bar,
    section_header,
    summary_panel,
    two_column_panel,
)


def make_test_console() -> tuple[Console, StringIO]:
    buffer = StringIO()
    return Console(file=buffer, force_terminal=False, width=80), buffer


def test_format_metric_uses_plain_decimals_at_the_threshold():
    assert format_metric(1e-3) == "0.0010"


def test_format_metric_uses_scientific_notation_below_the_threshold():
    assert format_metric(9.9e-4) == "9.90e-04"
    assert format_metric(-9.9e-4) == "-9.90e-04"


def test_format_metric_keeps_zero_as_a_plain_decimal():
    assert format_metric(0.0) == "0.0000"


def test_format_metric_passes_non_floats_through():
    assert format_metric(3) == "3"
    assert format_metric("n/a") == "n/a"


def test_highlight_markers_renders_bracketed_text_literally():
    test_console, buffer = make_test_console()

    test_console.print(highlight_markers("[bold] stays literal", {}))

    assert "[bold] stays literal" in buffer.getvalue()


def test_highlight_markers_styles_mapped_substrings():
    assert highlight_markers("a <|user|> b", {"<|user|>": "blue"}) == ("a [blue]<|user|>[/blue] b")


def test_highlight_markers_styles_substrings_containing_brackets():
    test_console, buffer = make_test_console()

    test_console.print(highlight_markers("say [pad] now", {"[pad]": "red"}))

    assert "say [pad] now" in buffer.getvalue()


def test_helpers_render_to_an_injected_console():
    test_console, buffer = make_test_console()

    section_header("Phase", console=test_console)
    summary_panel({"Model": "demo"}, title="Configuration", console=test_console)
    metrics_panel({"loss": 0.5}, console=test_console)
    two_column_panel({"Question": "why"}, title="Sample", console=test_console)
    with new_progress_bar(console=test_console) as progress:
        progress.add_task("working", total=1)

    output = buffer.getvalue()
    assert "Phase" in output
    assert "Configuration" in output
    assert "0.5000" in output
    assert "Sample" in output
