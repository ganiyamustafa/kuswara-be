from pydantic import BaseModel
from typing import List, Optional

class CheckSongSchema(BaseModel):
  link: str

class AddSongSchema(BaseModel):
  link: str
  name: str
  artists: List[str]
  is_cover: bool
  alternative_names: Optional[List[str]] = None
  seek: Optional[str] = None

  def dict(self, **kwargs):
    # Customize the dictionary representation here
    original_dict = super().dict(**kwargs)
    del original_dict['artists']

    return original_dict