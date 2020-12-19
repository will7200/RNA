from sqlalchemy import Column, Integer, String, Text, Enum, Boolean, ForeignKey, UniqueConstraint

from rna.modules import Base, UpdateMixin
from rna.modules.core.remote_management.schemas import AuthenticationMethod


class Host(Base, UpdateMixin):
    """Host Model for database creation and user"""
    __tablename__ = "hosts"
    id = Column(Integer, primary_key=True)

    # Host Information
    name = Column(String(128), nullable=False, index=True)
    # Max DNS Entries length can be 253 characters long
    hostname = Column(String(253), nullable=False, index=True)
    port = Column(Integer, nullable=False, default=22)
    # Unix usernames are maxed out at 32 characters
    username = Column(String(32), nullable=True)
    ssh_options = Column(Text, nullable=True)
    authentication_method = Column(Enum(AuthenticationMethod), nullable=True)
    password = Column(String(128), nullable=True)
    private_key = Column(Text, nullable=True)
    encrypt_authentication = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Setup Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'name', name='hosts_user_id_name_unique'),
    )

    def __repr__(self):
        return f'<Host {self.id}>'
