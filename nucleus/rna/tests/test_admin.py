from django.test import override_settings

import pytest

from nucleus.rna.admin import NoteAdminForm


@pytest.mark.parametrize(
    "note_markdown, expected_error",
    (
        (
            "Test with no trailing punctuation",
            "Notes must end with appropriate punctuation. Allowed marks are: . or !",
        ),
        (
            "Test note with a [URL][1] in it and no closing punctuation\r\n\r\n\r\n  [1]: http://example.com/test",
            "Notes must end with appropriate punctuation. Allowed marks are: . or !",
        ),
        (
            (
                "Multi-line test note with a [URL][1] in it.\r\n\r\n"
                "And DOES have terminal punctuation on this middle line.\r\n\r\n"
                "But not on this final line, with a second [URL][2] in it\r\n\r\n\r\n"
                "  [1]: http://example.com/test\r\n"
                "  [2]: http://example.com/test2"
            ),
            "Notes must end with appropriate punctuation. Allowed marks are: . or !",
        ),
        (
            "Test with disallowed trailing punctuation?",
            "Notes must end with appropriate punctuation. Allowed marks are: . or !",
        ),
        (
            "Test with allowed trailing punctuation!",
            None,
        ),
        (
            "Test note with a [URL][1] in it and closing punctuation.\r\n\r\n\r\n  [1]: http://example.com/test",
            None,
        ),
        (
            "Multi-line test note with a [URL][1] in it.\r\nAnd closing punctuation.\r\n\r\n\r\n  [1]: http://example.com/test",
            None,
        ),
        (
            (
                "Multi-line test note with a [URL][1] in it.\r\n\r\n"
                "And no terminal punctuation on this middle line\r\n\r\n"
                "AND with a second [URL][2] in it.\r\n\r\n\r\n"
                "  [1]: http://example.com/test\r\n"
                "  [2]: http://example.com/test2"
            ),
            None,
        ),
    ),
)
def test_noteadminform_clean_note(note_markdown, expected_error):
    form_data = {
        "note": note_markdown,
        "bug": 123132,
        "sort_num": 0,
    }
    form = NoteAdminForm(data=form_data)
    was_valid = form.is_valid()
    if expected_error:
        assert not was_valid
        assert form.errors["note"] == [expected_error]
    else:
        assert was_valid, "Expected form to be valid"


@pytest.mark.parametrize(
    "note_markdown, expected_error, settings_to_patch",
    (
        (
            "Test with no trailing punctuation will be allowed with setting disabled",
            None,
            {"RNA_NOTES_ENFORCE_CLOSING_PUNCTUATION": False},
        ),
        (
            "Test with DISALLOWED trailing punctuation!",
            "Notes must end with appropriate punctuation. Allowed marks are: ? or . or ¿",
            {"RNA_NOTES_EXPECTED_CLOSING_PUNCTUATION": ["?", ".", "¿"]},
        ),
    ),
)
def test_noteadminform_clean_note__amendable_via_settings(note_markdown, expected_error, settings_to_patch):
    form_data = {
        "note": note_markdown,
        "bug": 123132,
        "sort_num": 0,
    }
    with override_settings(**settings_to_patch):
        form = NoteAdminForm(data=form_data)
        was_valid = form.is_valid()
        if expected_error:
            assert not was_valid
            assert form.errors["note"] == [expected_error]
        else:
            assert was_valid, "Expected form to be valid"
