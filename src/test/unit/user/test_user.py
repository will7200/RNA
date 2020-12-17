import pytest


def test_set_password(admin_user):
    assert admin_user.password_hash != "password", "is plain text"


def test_check_password(admin_user):
    assert admin_user.check_password("password")
