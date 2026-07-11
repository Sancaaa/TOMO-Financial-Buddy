from sqlalchemy import select

from app.models import Category
from app.services.categorizer import learn_from_correction, suggest_category


def test_builtin_makan(db):
    assert suggest_category(db, "nasi goreng ayam", "expense").name == "Makan"


def test_builtin_transport(db):
    assert suggest_category(db, "gojek ke kampus", "expense").name == "Transport"


def test_builtin_income_kiriman(db):
    assert suggest_category(db, "kiriman bulanan", "income").name == "Kiriman"


def test_fallback_lainnya(db):
    assert suggest_category(db, "barang aneh qwerty", "expense").name == "Lainnya"


def test_learns_from_correction(db):
    hiburan = db.scalar(select(Category).where(Category.name == "Hiburan"))
    # awalnya token tak dikenal -> Lainnya
    assert suggest_category(db, "topup moblig", "expense").name == "Lainnya"
    learn_from_correction(db, "topup moblig", hiburan)
    # setelah dikoreksi, token yang sama menuju Hiburan
    assert suggest_category(db, "topup moblig lagi", "expense").name == "Hiburan"
