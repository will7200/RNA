from datetime import datetime
from typing import List

from sqlalchemy import Column, Integer, String, Text, Enum, Boolean, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.orm import relationship

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
    commands: List['HostCommand'] = relationship("HostCommand", backref="hosts", cascade="all,delete",
                                                 uselist=True)  # type: ignore

    # Setup Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'name', name='hosts_user_id_name_unique'),
    )

    def __repr__(self):
        return f'<Host {self.id}>'


class HostCommand(Base, UpdateMixin):
    """Host Commands Holds Commands for hosts"""
    __tablename__ = "host_commands"
    id = Column(Integer, primary_key=True)
    command = Column(Text, nullable=False, index=True)
    status = Column(Boolean, nullable=False, default=1)
    latest_result = Column(Text, nullable=True)
    last_completed_at = Column(DateTime, nullable=True)
    host_id = Column(Integer, ForeignKey('hosts.id'), nullable=False)
    events: List['HostCommandEvent'] = relationship("HostCommandEvent", backref="host_commands", cascade="all,delete",
                                                    uselist=True, lazy='joined')  # type: ignore

    # Setup Constraints
    __table_args__ = (
        UniqueConstraint('host_id', 'command', name='host_id_command_unique'),
    )

    def __repr__(self):
        return f'<HostCommand {self.id}>'


class HostCommandEvent(Base, UpdateMixin):
    """Host Commands Holds Commands for hosts"""
    __tablename__ = "host_commands_events"
    id = Column(Integer, primary_key=True)
    result = Column(Text, nullable=False)
    completed_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    host_command_id = Column(Integer, ForeignKey('host_commands.id'), nullable=False)

    __trigger__ = """
    CREATE TRIGGER create_new_command_event 
   AFTER INSERT ON host_commands_events
BEGIN
	update host_commands
	set last_completed = new.last_completed_at, lasest_result = new.result
	where id = new.host_id
	END;
    """

    def __repr__(self):
        return f'<HostCommandEvent {self.id}>'
