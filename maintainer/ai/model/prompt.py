# -*- coding: utf-8 -*-
from typing import Optional, List, Dict

from pydantic import BaseModel, Field


class PromptMetaSummary(BaseModel):
    schema_version: Optional[int] = Field(default=1, alias="schemaVersion")
    prompt_key: Optional[str] = Field(default=None, alias="promptKey")
    description: Optional[str] = None
    biz_tags: Optional[List[str]] = Field(default=None, alias="bizTags")
    latest_version: Optional[str] = Field(default=None, alias="latestVersion")
    gmt_modified: Optional[int] = Field(default=None, alias="gmtModified")

    model_config = {"populate_by_name": True}


class PromptMetaInfo(PromptMetaSummary):
    versions: Optional[List[str]] = None
    labels: Optional[Dict[str, str]] = None


class PromptVersionSummary(BaseModel):
    prompt_key: Optional[str] = Field(default=None, alias="promptKey")
    version: Optional[str] = None
    commit_msg: Optional[str] = Field(default=None, alias="commitMsg")
    src_user: Optional[str] = Field(default=None, alias="srcUser")
    gmt_modified: Optional[int] = Field(default=None, alias="gmtModified")

    model_config = {"populate_by_name": True}


class PromptVersionInfo(PromptVersionSummary):
    template: Optional[str] = None
    md5: Optional[str] = None
