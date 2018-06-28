
def test_get_userstories_stats():
    """Test whether we can get the user stories statistics from Taiga

       Actually, this code rather tests whether the required Taiga instance is
       running, and that the given URL, which needs to be generated inside Taiga,
       is correct.
    """
    import requests as req
    from main import app
    config = app.config
    URL = config['USERSTORIES_URL']
    r = req.get(URL)
    assert r.status_code == 200
