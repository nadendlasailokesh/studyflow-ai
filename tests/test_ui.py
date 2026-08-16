from src.utils.ui import ai_loading


def test_ai_loading_is_context_manager():

    assert callable(ai_loading)

    manager = ai_loading(
        "Testing..."
    )

    assert hasattr(
        manager,
        "__enter__"
    )

    assert hasattr(
        manager,
        "__exit__"
    )