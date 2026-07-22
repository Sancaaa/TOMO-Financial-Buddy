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


def _cat_id(auth_client, name):
    return next(c for c in auth_client.get("/categories").json() if c["name"] == name)["id"]


def test_web_patch_category_teaches_categorizer(auth_client):
    # Koreksi kategori lewat web (PATCH) harus mengajari categorizer, sama seperti
    # tombol kategori di bot Telegram.
    tx = auth_client.post("/transactions/quick", json={"text": "topup moblig 20k"}).json()
    assert tx["category"]["name"] == "Lainnya"

    hiburan = _cat_id(auth_client, "Hiburan")
    r = auth_client.patch(f"/transactions/{tx['id']}", json={"category_id": hiburan})
    assert r.status_code == 200
    assert r.json()["category"]["name"] == "Hiburan"

    # transaksi berikutnya dengan token yang sama -> otomatis Hiburan
    tx2 = auth_client.post(
        "/transactions/quick", json={"text": "topup moblig 20k"}
    ).json()
    assert tx2["category"]["name"] == "Hiburan"


def test_web_patch_without_category_change_does_not_learn(auth_client):
    # Ubah field non-kategori tidak boleh membuat aturan baru (regresi).
    tx = auth_client.post(
        "/transactions/quick", json={"text": "barang qwerty 15k"}
    ).json()
    assert tx["category"]["name"] == "Lainnya"

    auth_client.patch(f"/transactions/{tx['id']}", json={"amount": 30000})

    tx2 = auth_client.post(
        "/transactions/quick", json={"text": "barang qwerty 15k"}
    ).json()
    assert tx2["category"]["name"] == "Lainnya"
