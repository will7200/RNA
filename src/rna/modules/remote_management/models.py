import os
from base64 import b64encode, b64decode
from datetime import datetime
from typing import List

from Crypto.Cipher import AES
from scrypt import scrypt
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

    def encrypt_authentication_information(self, password: str):
        """encrypt password and/or private key with AES GCM"""
        if self.private_key:
            self.private_key = encrypt_aes_gcm(self.private_key.encode('utf8'), password.encode('utf8'))

        if self.password:
            self.password = encrypt_aes_gcm(self.password.encode('utf8'), password.encode('utf8'))

    def decrypt_authentication_information(self, password):
        """decrypt decrypted password and/or private key"""
        if self.password:
            self.password = decrypt_aes_gcm(self.password, password)
        if self.private_key:
            self.private_key = decrypt_aes_gcm(self.private_key, password)


def encrypt_aes_gcm(msg, password):
    kdf_salt = os.urandom(16)
    secret_key = scrypt.hash(password, kdf_salt, N=16384, r=8, p=1, buflen=32)
    aes_cipher = AES.new(secret_key, AES.MODE_GCM)
    ciphertext, authTag = aes_cipher.encrypt_and_digest(msg)
    return f'{b64encode(kdf_salt).decode()}$${b64encode(ciphertext).decode()}$${b64encode(aes_cipher.nonce).decode()}$${b64encode(authTag).decode()}'


def decrypt_aes_gcm(encrypted_msg, password):
    (kdfSalt, ciphertext, nonce, authTag) = [b64decode(x) for x in encrypted_msg.split('$$')]
    secret_key = scrypt.hash(password, kdfSalt, N=16384, r=8, p=1, buflen=32)
    aes_cipher = AES.new(secret_key, AES.MODE_GCM, nonce)
    plaintext = aes_cipher.decrypt_and_verify(ciphertext, authTag)
    return plaintext


class HostCommand(Base, UpdateMixin):
    """Host Commands Holds Commands for hosts"""
    __tablename__ = "host_commands"
    id = Column(Integer, primary_key=True)
    command = Column(Text, nullable=False, index=True)
    status = Column(Boolean, nullable=False, default=1)
    latest_result = Column(Text, nullable=True)
    latest_exit_code = Column(Integer, nullable=True)
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
    guid = Column(String(155), nullable=True)
    result = Column(Text, nullable=False)
    exit_code = Column(Integer, nullable=False)
    completed_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    host_command_id = Column(Integer, ForeignKey('host_commands.id'), nullable=False)

    def __repr__(self):
        return f'<HostCommandEvent {self.id}>'
