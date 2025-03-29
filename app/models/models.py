from typing import List, Optional

from sqlalchemy import DateTime, ForeignKeyConstraint, Index, Integer, String, text
from sqlalchemy.dialects.mysql import TINYINT, VARCHAR
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import datetime


class Base(DeclarativeBase):
    pass


class Tblrole(Base):
    __tablename__ = "tblrole"
    __table_args__ = (Index("tblRole_unique", "role_name", unique=True),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    role_name: Mapped[str] = mapped_column(String(100))
    create_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime, server_default=text("CURRENT_TIMESTAMP")
    )
    update_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime, server_default=text("CURRENT_TIMESTAMP")
    )

    tbluser: Mapped[List["Tbluser"]] = relationship("Tbluser", back_populates="role")


class Tbluser(Base):
    __tablename__ = "tbluser"
    __table_args__ = (
        ForeignKeyConstraint(["role_id"], ["tblrole.id"], name="tbluser_tblrole_FK"),
        Index("tbluser_tblrole_FK", "role_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    role_id: Mapped[int] = mapped_column(Integer)
    email: Mapped[Optional[str]] = mapped_column(String(100))
    password: Mapped[Optional[str]] = mapped_column(String(100))
    create_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime, server_default=text("CURRENT_TIMESTAMP")
    )
    update_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime, server_default=text("CURRENT_TIMESTAMP")
    )
    avatar: Mapped[Optional[str]] = mapped_column(VARCHAR(500))

    role: Mapped["Tblrole"] = relationship("Tblrole", back_populates="tbluser")
    tblsesson: Mapped[List["Tblsesson"]] = relationship(
        "Tblsesson", back_populates="user"
    )


class Tblsesson(Base):
    __tablename__ = "tblsesson"
    __table_args__ = (
        ForeignKeyConstraint(["user_id"], ["tbluser.id"], name="tblsesson_tbluser_FK"),
        Index("tblsesson_tbluser_FK", "user_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer)
    token: Mapped[Optional[str]] = mapped_column(String(255))
    device_info: Mapped[Optional[str]] = mapped_column(String(255))
    ip_address: Mapped[Optional[str]] = mapped_column(String(255))
    ip_address: Mapped[Optional[str]] = mapped_column(String(255))
    location_city: Mapped[Optional[str]] = mapped_column(String(255))
    location_country: Mapped[Optional[str]] = mapped_column(String(255))
    login_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    logout_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    is_active: Mapped[Optional[int]] = mapped_column(TINYINT(1))
    is_trusted: Mapped[Optional[int]] = mapped_column(TINYINT(1))
    approval_code: Mapped[Optional[str]] = mapped_column(String(255))
    approval_expires: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    user: Mapped[Optional["Tbluser"]] = relationship(
        "Tbluser", back_populates="tblsesson"
    )
