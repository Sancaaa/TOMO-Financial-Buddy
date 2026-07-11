from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class KeywordRule(Base):
    """Aturan kata kunci -> kategori yang dipelajari dari koreksi user.

    Setiap kali user mengoreksi kategori sebuah transaksi, token dari deskripsinya
    dipetakan ke kategori terpilih dan `hits` bertambah. Saat menebak kategori,
    token dengan total hits tertinggi menang.
    """

    __tablename__ = "keyword_rules"
    __table_args__ = (UniqueConstraint("keyword", "category_id", name="uq_keyword_category"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    keyword: Mapped[str] = mapped_column(String(40), index=True)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE")
    )
    hits: Mapped[int] = mapped_column(Integer, default=1)
