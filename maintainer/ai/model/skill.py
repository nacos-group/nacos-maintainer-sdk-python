# -*- coding: utf-8 -*-
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field


class SkillResource(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class Skill(BaseModel):
    namespace_id: Optional[str] = Field(default=None, alias="namespaceId")
    name: Optional[str] = None
    description: Optional[str] = None
    instruction: Optional[str] = None
    resource: Optional[Dict[str, SkillResource]] = None

    model_config = {"populate_by_name": True}


class SkillBasicInfo(BaseModel):
    namespace_id: Optional[str] = Field(default=None, alias="namespaceId")
    name: Optional[str] = None
    description: Optional[str] = None
    update_time: Optional[int] = Field(default=None, alias="updateTime")

    model_config = {"populate_by_name": True}
