from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base
import enum

class ConnectionStatus(str, enum.Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"

class WhatsAppInstance(Base):
    __tablename__ = "whatsapp_instances"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    instance_name = Column(String(100), unique=True, nullable=False)
    phone_number = Column(String(20), nullable=False)
    connection_status = Column(Enum(ConnectionStatus), default=ConnectionStatus.DISCONNECTED)
    qrcode_base64 = Column(Text, nullable=True)
    last_connected = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    user = relationship("User", back_populates="whatsapp_instances")
    
    def __repr__(self):
        return f"<WhatsAppInstance(id={self.id}, instance='{self.instance_name}', status='{self.connection_status}')>"