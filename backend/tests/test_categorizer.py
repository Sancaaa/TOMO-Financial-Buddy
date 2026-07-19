from sqlalchemy import select

from app.models import Category
from app.services.categorizer import learn_from_correction, suggest_category


def test_builtin_makan(db, uid):
    assert suggest_category(db, "nasi goreng ayam", "expense", uid).name == "Makan"


def test_builtin_transport(db, uid):
    assert suggest_category(db, "gojek ke kampus", "expense", uid).name == "Transport"


def test_builtin_income_kiriman(db, uid):
    assert suggest_category(db, "kiriman bulanan", "income", uid).name == "Kiriman"


def test_fallback_lainnya(db, uid):
    assert suggest_category(db, "barang aneh qwerty", "expense", uid).name == "Lainnya"


def test_learns_from_correction(db, uid):
    hiburan = db.scalar(
        select(Category).where(Category.user_id == uid, Category.name == "Hiburan")
    )
    # awalnya token tak dikenal -> Lainnya
    assert suggest_category(db, "topup moblig", "expense", uid).name == "Lainnya"
    learn_from_correction(db, "topup moblig", hiburan)
    # setelah dikoreksi, token yang sama menuju Hiburan
    assert suggest_category(db, "topup moblig lagi", "expense", uid).name == "Hiburan"
