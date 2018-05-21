
def test_load_config():
    from scripts import load_config, configfile
    c = load_config(open(configfile))
    assert c is not None
