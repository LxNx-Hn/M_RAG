"""Check zero-point gaps, ranking eligibility and lossless SVG image export."""

import base64
import io
import sys
import unittest
from unittest.mock import patch
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, PngImagePlugin

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "FINALDOCS/ANALYSIS"))
sys.path.insert(0, str(ROOT / "FINALDOCS/BUILD"))
from plot_questions import (  # noqa: E402
    display_values,
    extremes,
    plt,
    type_profiles,
    PROFILE_AXES,
    TYPES,
    profile_coordinates,
)
from svg_export import reencode_svg_pngs  # noqa: E402


class PlotExportTests(unittest.TestCase):
    def test_type_panels_preserve_all_questions_and_raw_seconds(self):
        data = pd.read_csv(ROOT / "FINALDOCS/ANALYSIS/QUERY_LEVEL_RESULTS.csv")
        selected = data[data.condition == "H1C0S0"]
        with patch("plot_questions.save"):
            type_profiles(data, "H1C0S0", "unused")
        fig = plt.gcf()
        try:
            self.assertEqual(len(fig.axes), 4)
            self.assertEqual(
                [len(selected[selected.question_type == t]) for t in TYPES],
                [8, 29, 20, 3],
            )
            for ax, typ in zip(fig.axes, TYPES):
                group = selected[selected.question_type == typ]
                self.assertEqual(len(ax.lines), len(group) + 6)
                for line, row in zip(ax.lines, group.itertuples()):
                    original = np.array([getattr(row, m) for m in PROFILE_AXES])
                    expected = original.copy()
                    expected[expected == 0] = np.nan
                    expected[-1] = 1 - expected[-1] / 180
                    np.testing.assert_allclose(
                        line.get_ydata(), expected, equal_nan=True
                    )
        finally:
            plt.close(fig)
        with self.assertRaises(AssertionError):
            profile_coordinates([0.5, 0.5, 0.5, 0.5, 0.5, 181])

    def test_zero_gap_is_not_connected_and_input_is_preserved(self):
        original = np.array([0.3, 0.2, 0.0, 0.8, 0.9])
        snapshot = original.copy()
        fig, ax = plt.subplots()
        try:
            line = ax.plot(display_values(original))[0]
            segments = list(line.get_path().iter_segments(remove_nans=True))
            self.assertEqual([code for _, code in segments], [1, 2, 1, 2])
            np.testing.assert_array_equal(original, snapshot)
            self.assertTrue(np.isnan(display_values([np.nan])[0]))
        finally:
            plt.close(fig)

    def test_zero_faithfulness_is_excluded_from_highlight_ranking(self):
        data = pd.DataFrame(
            [
                {"query_id": q, "condition": c, "faithfulness": value}
                for q, before, after in [("zero", 0.0, 1.0), ("valid", 0.4, 0.6)]
                for c, value in [("before", before), ("after", after)]
            ]
        )
        self.assertEqual(
            extremes(data, "after", "before", "faithfulness"), (["valid"], [])
        )

    def test_png_reencoding_preserves_pixels_and_metadata(self):
        original = Image.new("RGBA", (3, 2), (12, 34, 56, 78))
        metadata = PngImagePlugin.PngInfo()
        metadata.add_text("source", "export-test")
        stream = io.BytesIO()
        original.save(stream, format="PNG", pnginfo=metadata, compress_level=1)
        svg = "data:image/png;base64," + base64.b64encode(stream.getvalue()).decode(
            "ascii"
        )
        encoded = reencode_svg_pngs(svg)
        decoded = Image.open(io.BytesIO(base64.b64decode(encoded.split(",", 1)[1])))
        self.assertEqual(decoded.tobytes(), original.tobytes())
        self.assertEqual(decoded.info["source"], "export-test")
        self.assertEqual(reencode_svg_pngs(encoded), encoded)


if __name__ == "__main__":
    unittest.main()
