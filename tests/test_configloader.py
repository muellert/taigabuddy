
def test_load_config():
    from main.config import config
    assert hasattr(config, 'api_url')
