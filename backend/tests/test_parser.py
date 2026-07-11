from datetime import datetime, timezone
from decimal import Decimal

from app.services.parser import parse_quick_input

NOW = datetime(2026, 7, 5, 12, 0, tzinfo=timezone.utc)


def p(text):
    return parse_quick_input(text, NOW)


def test_suffix_k():
    r = p("makan 15k")
    assert r.amount == Decimal(15000)
    assert r.type == "expense"
    assert "makan" in r.description.lower()


def test_suffix_rb():
    assert p("gojek 24rb").amount == Decimal(24000)


def test_dot_thousands():
    assert p("nasi padang 25.000").amount == Decimal(25000)


def test_juta_comma_decimal():
    assert p("laptop 1,5jt").amount == Decimal(1500000)


def test_juta_dot_decimal():
    assert p("hp 2.5jt").amount == Decimal(2500000)


def test_income_keyword():
    r = p("dapet 50k dari nyokap")
    assert r.type == "income"
    assert r.amount == Decimal(50000)


def test_backdate_kemarin():
    r = p("kemarin makan 20k")
    assert r.amount == Decimal(20000)
    assert r.occurred_at.day == 4


def test_backdate_hari_lalu():
    r = p("3 hari lalu makan 12k")
    assert r.occurred_at.day == 2
    assert r.amount == Decimal(12000)


def test_backdate_tanggal():
    r = p("tgl 2 bayar kos 800rb")
    assert r.amount == Decimal(800000)
    assert r.occurred_at.day == 2
    assert "kos" in r.description.lower()


def test_quantity_is_not_amount():
    # "2" adalah jumlah barang, "36rb" adalah harga
    assert p("beli 2 kopi 36rb").amount == Decimal(36000)


def test_filler_prefix_stripped():
    r = p("bayar listrik 150rb")
    assert "listrik" in r.description.lower()
    assert not r.description.lower().startswith("bayar")


def test_no_amount_returns_none():
    assert p("halo apa kabar") is None


def test_kg_not_parsed_as_thousand():
    # "5kg" tidak boleh jadi 5000; harga sebenarnya 30rb
    assert p("beras 5kg 30rb").amount == Decimal(30000)
