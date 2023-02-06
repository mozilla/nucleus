import inspect
import json

from nucleus.settings import (
    SENSITIVE_FIELDS_TO_MASK_ENTIRELY,
    SENSITIVE_FIELDS_TO_MASK_PARTIALLY,
    before_send,
)


def test_pre_sentry_sanitisation__before_send_setup():
    # It's tricky getting hold of the live/configured sentry_sdk Client in tests
    # but we can at least confirm the source is set up how we expect

    # Sense check that we're passing in the params
    _func_source = inspect.getsource(before_send)
    assert "with_default_keys=True,\n" in _func_source

    # check the rest of the params are commented out, but ready for use
    assert "# sensitive_keys=SENSITIVE_FIELDS_TO_MASK_ENTIRELY,\n" in _func_source
    assert "# partial_keys=SENSITIVE_FIELDS_TO_MASK_PARTIALLY,\n" in _func_source
    assert "# mask_position=POSITION.LEFT," in _func_source
    assert "# off_set=3" in _func_source

    assert SENSITIVE_FIELDS_TO_MASK_ENTIRELY == []

    assert SENSITIVE_FIELDS_TO_MASK_PARTIALLY == []


example_unsanitised_data = {
    # Default blocklist
    "password": "This is in sentry_processor's default set of keys to scrub",
    "secret": "This is in sentry_processor's default set of keys to scrub",
    "passwd": "This is in sentry_processor's default set of keys to scrub",
    "api_key": "This is in sentry_processor's default set of keys to scrub",
    "apikey": "This is in sentry_processor's default set of keys to scrub",
    "dsn": "This is in sentry_processor's default set of keys to scrub",
    "token": "This is in sentry_processor's default set of keys to scrub AND out blocklist of keys",
    # Custom blocklist is currently empty
    # "some_key": "These items are on our blocklist and should be removed entirely",
    # Partial masking list is currently empty
    # "some_other_key": "Should be partially masked.",
}

expected_sanitised_data = {
    "password": "********",
    "secret": "********",
    "passwd": "********",
    "api_key": "********",
    "apikey": "********",
    "dsn": "********",
    "token": "********",
}


def _prep_test_data(shared_datadir, data_to_splice):
    retval = []

    raw_json = (shared_datadir / "example_sentry_payload.json").read_text()

    for payload in data_to_splice:
        fake_event = json.loads(raw_json)["payload"]

        # Splice in some fake data we expect to be sanitised
        fake_event["exception"]["values"][0]["stacktrace"]["frames"][1]["vars"].update(
            payload,
        )

        # This gets filtered by filter_http
        _request = {}
        _request["data"] = payload
        _request["cookies"] = payload
        _request["env"] = payload
        _request["headers"] = payload
        _request["query_string"] = "?" + "&".join(
            [f"{key}={val}" for key, val in payload.items()],
        )
        fake_event["request"] = _request

        # This gets filtered by filter_extra - where we add a nested version, too
        fake_event["extra"].update(payload)
        fake_event["extra"]["nested"] = payload

        retval.append(fake_event)

    return retval


def test_pre_sentry_sanitisation(shared_datadir):
    # Be sure that sentry_processor is dropping/masking what we expect it to.
    # Note that this test is worked backwards from the sentry_processor code,
    # not based on actual Sentry data payloads (which we should also do.)

    # (datadir is a pytest fixture from pytest-datadir)

    noop_because_hint_is_not_used = None

    input_event, expected_sanitised_event = _prep_test_data(
        shared_datadir=shared_datadir,
        data_to_splice=[example_unsanitised_data, expected_sanitised_data],
    )

    output = before_send(
        event=input_event,
        hint=noop_because_hint_is_not_used,
    )
    assert output == expected_sanitised_event
