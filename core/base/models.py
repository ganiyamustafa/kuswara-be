from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.inspection import inspect
from uuid import UUID

Base = declarative_base()

class BaseModel(Base):
  __abstract__ = True

  class config:
    from_attributes = True

  def to_dict(self):
    return {c.key: str(getattr(self, c.key)) if isinstance(getattr(self, c.key), UUID) else getattr(self, c.key) for c in inspect(self).mapper.column_attrs}
