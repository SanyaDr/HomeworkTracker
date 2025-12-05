# tests/test_fixtures.py
def test_test_db_fixture(test_db):
    """Просто проверяем что фикстура test_db работает"""
    assert test_db is not None
    print("✅ Фикстура test_db работает!")

def test_client_fixture(client):
    """Проверяем что фикстура client работает"""
    assert client is not None
    print("✅ Фикстура client работает!")