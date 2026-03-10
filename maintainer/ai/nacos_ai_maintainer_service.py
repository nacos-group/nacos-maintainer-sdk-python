# -*- coding: utf-8 -*-
from typing import List, Tuple, Optional

from a2a.types import AgentCard
from pydantic import TypeAdapter
from v2.nacos import ClientConfig
from v2.nacos.ai.model.a2a.a2a import AgentCardDetailInfo
from v2.nacos.ai.model.mcp.mcp import (
    McpServerBasicInfo,
    McpServerDetailInfo,
    McpToolSpecification,
    McpEndpointSpec,
)
from v2.nacos.common.constants import Constants

from maintainer.ai.model.a2a import AgentVersionDetail, AgentCardVersionInfo
from maintainer.ai.model.prompt import (
    PromptMetaSummary,
    PromptMetaInfo,
    PromptVersionSummary,
    PromptVersionInfo,
)
from maintainer.ai.model.skill import Skill, SkillBasicInfo
from maintainer.common.auth import RequestResource
from maintainer.nacos_maintainer_client import NacosMaintainerClient
from maintainer.transport.client_http_proxy import ClientHttpProxy, HttpRequest


DEFAULT_NAMESPACE_ID = "public"


class NacosAIMaintainerService(NacosMaintainerClient):
    def __init__(self, ai_client_config: ClientConfig):
        super().__init__(ai_client_config, Constants.AI_MODULE)
        self.http_proxy = ClientHttpProxy(
            self.logger,
            ai_client_config,
            self.http_agent,
        )

    @staticmethod
    async def create_mcp_service(client_config: ClientConfig):
        return await NacosAIMaintainerService.create_ai_service(client_config)

    @staticmethod
    async def create_ai_service(client_config: ClientConfig):
        return NacosAIMaintainerService(client_config)

    async def list_mcp_servers(
        self,
        namespace_id: str,
        mcp_name: str,
        page_no: int,
        page_size: int,
    ) -> Tuple[int, int, int, List[McpServerBasicInfo]]:
        if namespace_id is None or len(namespace_id) == 0:
            namespace_id = DEFAULT_NAMESPACE_ID

        params = {
            "pageNo": page_no,
            "pageSize": page_size,
            "namespaceId": namespace_id,
            "mcpName": mcp_name,
            "search": "accurate",
        }
        request_resource = RequestResource(
            Constants.AI_MODULE,
            namespace_id,
            "",
            None,
        )
        request = HttpRequest(
            path="/nacos/v3/admin/ai/mcp/list",
            method="GET",
            request_resource=request_resource,
            params=params,
        )
        result = await self.http_proxy.request(request)
        if result["code"] != 0:
            self.logger.error(f"list ai servers failed, result:{result}")
            raise Exception(result["message"])

        result_data = result["data"]
        total_count = result_data["totalCount"]
        page_number = result_data["pageNumber"]
        page_available = result_data["pagesAvailable"]
        page_items = result_data["pageItems"]
        try:
            adapter = TypeAdapter(List[McpServerBasicInfo])
            mcp_servers: List[McpServerBasicInfo] = adapter.validate_python(
                page_items,
            )
        except Exception as e:
            self.logger.error(e)
            raise

        return total_count, page_number, page_available, mcp_servers

    async def search_mcp_server(
        self,
        namespace_id: str,
        mcp_name: str,
        page_no: int,
        page_size: int,
    ) -> Tuple[int, int, int, List[McpServerBasicInfo]]:
        if namespace_id is None or len(namespace_id) == 0:
            namespace_id = DEFAULT_NAMESPACE_ID

        params = {
            "pageNo": page_no,
            "pageSize": page_size,
            "namespaceId": namespace_id,
            "mcpName": mcp_name,
            "search": "blur",
        }
        request_resource = RequestResource(
            Constants.AI_MODULE,
            namespace_id,
            "",
            None,
        )
        request = HttpRequest(
            path="/nacos/v3/admin/ai/mcp/list",
            method="GET",
            request_resource=request_resource,
            params=params,
        )
        result = await self.http_proxy.request(request)
        if result["code"] != 0:
            self.logger.error(f"search ai server failed, result:{result}")
            raise Exception(result["message"])

        result_data = result["data"]
        total_count = result_data["totalCount"]
        page_number = result_data["pageNumber"]
        page_available = result_data["pagesAvailable"]
        page_items = result_data["pageItems"]
        try:
            adapter = TypeAdapter(List[McpServerBasicInfo])
            mcp_servers: List[McpServerBasicInfo] = adapter.validate_python(
                page_items,
            )
        except Exception as e:
            self.logger.error(e)
            raise
        return total_count, page_number, page_available, mcp_servers

    async def get_mcp_server_detail(
        self,
        namespace_id: str,
        mcp_name: str,
        version: str,
    ) -> McpServerDetailInfo:
        if namespace_id is None or len(namespace_id) == 0:
            namespace_id = DEFAULT_NAMESPACE_ID

        params = {
            "namespaceId": namespace_id,
            "mcpName": mcp_name,
            "version": version,
        }
        request_resource = RequestResource(
            Constants.AI_MODULE,
            namespace_id,
            "",
            mcp_name,
        )
        request = HttpRequest(
            path="/nacos/v3/admin/ai/mcp",
            method="GET",
            request_resource=request_resource,
            params=params,
        )
        result = await self.http_proxy.request(request)
        if result["code"] != 0:
            self.logger.error(f"get mcp server detail failed, result:{result}")
            raise Exception(result["message"])

        result_data = result["data"]
        try:
            adapter = TypeAdapter(McpServerDetailInfo)
            mcp_server: McpServerDetailInfo = adapter.validate_python(
                result_data,
            )
        except Exception as e:
            self.logger.error(e)
            raise
        return mcp_server

    async def create_mcp_server(
        self,
        namespace_id: str,
        mcp_name: str,
        server_spec: McpServerBasicInfo,
        tool_spec: McpToolSpecification,
        endpoint_spec: McpEndpointSpec,
    ) -> bool:
        if namespace_id is None or len(namespace_id) == 0:
            namespace_id = DEFAULT_NAMESPACE_ID

        params = {
            "namespaceId": namespace_id,
            "mcpName": mcp_name,
            "serverSpecification": server_spec.model_dump_json(
                exclude_none=True,
            ),
        }
        if tool_spec is not None:
            params["toolSpecification"] = tool_spec.model_dump_json(
                exclude_none=True,
            )
        if endpoint_spec is not None:
            params["endpointSpecification"] = endpoint_spec.model_dump_json(
                exclude_none=True,
            )

        request_resource = RequestResource(
            Constants.AI_MODULE,
            namespace_id,
            "",
            mcp_name,
        )
        request = HttpRequest(
            path="/nacos/v3/admin/ai/mcp",
            method="POST",
            request_resource=request_resource,
            data=params,
        )
        result = await self.http_proxy.request(request)
        if result["code"] != 0:
            self.logger.error(f"create mcp server failed, result:{result}")
            return False

        return True

    async def update_mcp_server(
        self,
        namespace_id: str,
        mcp_name: str,
        is_latest: bool,
        server_spec: McpServerBasicInfo,
        tool_spec: McpToolSpecification,
        endpoint_spec: McpEndpointSpec,
    ):
        if namespace_id is None or len(namespace_id) == 0:
            namespace_id = DEFAULT_NAMESPACE_ID

        params = {
            "namespaceId": namespace_id,
            "mcpName": mcp_name,
            "latest": is_latest,
            "serverSpecification": server_spec.model_dump_json(
                exclude_none=True,
            ),
        }
        if tool_spec is not None:
            params["toolSpecification"] = tool_spec.model_dump_json(
                exclude_none=True,
            )
        if endpoint_spec is not None:
            params["endpointSpecification"] = endpoint_spec.model_dump_json(
                exclude_none=True,
            )

        request_resource = RequestResource(
            Constants.AI_MODULE,
            namespace_id,
            "",
            mcp_name,
        )
        request = HttpRequest(
            path="/nacos/v3/admin/ai/mcp",
            method="PUT",
            request_resource=request_resource,
            data=params,
        )
        result = await self.http_proxy.request(request)
        if result["code"] != 0:
            self.logger.error(f"update mcp server failed, result:{result}")
            return False

        return True

    async def delete_mcp_server(
        self,
        namespace_id: str,
        mcp_name: str,
    ) -> bool:
        if namespace_id is None or len(namespace_id) == 0:
            namespace_id = DEFAULT_NAMESPACE_ID

        params = {
            "namespaceId": namespace_id,
            "mcpName": mcp_name,
        }
        request_resource = RequestResource(
            Constants.AI_MODULE,
            namespace_id,
            "",
            mcp_name,
        )
        request = HttpRequest(
            path="/nacos/v3/admin/ai/mcp",
            method="DELETE",
            request_resource=request_resource,
            params=params,
        )
        result = await self.http_proxy.request(request)
        if result["code"] != 0:
            self.logger.error(f"delete mcp server failed, result:{result}")
            return False

        return True

    async def register_agent(
        self,
        agent_card: AgentCard,
        namespace_id: str,
        registration_type: str,
    ) -> bool:
        if namespace_id is None or len(namespace_id) == 0:
            namespace_id = Constants.DEFAULT_NAMESPACE_ID

        params = {
            "agentCard": agent_card.model_dump_json(),
            "namespaceId": namespace_id,
            "agentName": agent_card.name,
            "registrationType": registration_type,
        }

        request_source = RequestResource(
            Constants.AI_MODULE,
            namespace_id,
            "",
            agent_card.name,
        )
        request = HttpRequest(
            path="/nacos/v3/admin/ai/a2a",
            method="POST",
            request_resource=request_source,
            params=params,
        )
        result = await self.http_proxy.request(request)
        if result["code"] != 0:
            self.logger.error(f"register agent failed, result:{result}")
            return False

        return True

    async def get_agent_card(
        self,
        agent_name: str,
        version:str,
        namespace_id: str,
        registration_type: str,
    ) -> AgentCardDetailInfo:
        if namespace_id is None or len(namespace_id) == 0:
            namespace_id = Constants.DEFAULT_NAMESPACE_ID

        params = {
            "agentName": agent_name,
            "version": version,
            "namespaceId": namespace_id,
            "registrationType": registration_type,
        }

        request_source = RequestResource(
            Constants.AI_MODULE,
            namespace_id,
            "",
            agent_name,
        )
        request = HttpRequest(
            path="/nacos/v3/admin/ai/a2a",
            method="GET",
            request_resource=request_source,
            params=params,
        )
        result = await self.http_proxy.request(request)
        if result["code"] != 0:
            self.logger.error(f"get agent card failed, result:{result}")
            raise Exception(result["message"])

        result_data = result["data"]
        try:
            adapter = TypeAdapter(AgentCardDetailInfo)
            agent_card_detail_info: AgentCardDetailInfo = (
                adapter.validate_python(
                    result_data,
                )
            )
        except Exception as e:
            self.logger.error(e)
            raise
        return agent_card_detail_info

    async def update_agent_card(
        self,
        agent_card: AgentCard,
        namespace_id: str,
        set_as_latest: bool,
        registration_type: str,
    ) -> bool:
        if namespace_id is None or len(namespace_id) == 0:
            namespace_id = Constants.DEFAULT_NAMESPACE_ID

        params = {
            "agentCard": agent_card.model_dump_json(),
            "namespaceId": namespace_id,
            "agentName": agent_card.name,
            "setAsLatest": set_as_latest,
            "registrationType": registration_type,
        }

        request_source = RequestResource(
            Constants.AI_MODULE,
            namespace_id,
            "",
            agent_card.name,
        )
        request = HttpRequest(
            path="/nacos/v3/admin/ai/a2a",
            method="PUT",
            request_resource=request_source,
            params=params,
        )
        result = await self.http_proxy.request(request)
        if result["code"] != 0:
            self.logger.error(f"update agent card failed, result:{result}")
            return False

        return True

    async def delete_agent(
        self,
        agent_name: str,
        namespace_id: str,
        version: str,
    ) -> bool:
        if namespace_id is None or len(namespace_id) == 0:
            namespace_id = Constants.DEFAULT_NAMESPACE_ID

        params = {
            "agentName": agent_name,
            "namespaceId": namespace_id,
            "version": version,
        }

        request_source = RequestResource(
            Constants.AI_MODULE,
            namespace_id,
            "",
            agent_name,
        )
        request = HttpRequest(
            path="/nacos/v3/admin/ai/a2a",
            method="DELETE",
            request_resource=request_source,
            params=params,
        )
        result = await self.http_proxy.request(request)
        if result["code"] != 0:
            self.logger.error(f"delete agent failed, result:{result}")
            return False

        return True

    async def list_all_version_of_agent(
        self,
        agent_name: str,
        namespace_id: str,
    ) -> List[AgentVersionDetail]:
        if namespace_id is None or len(namespace_id) == 0:
            namespace_id = Constants.DEFAULT_NAMESPACE_ID

        params = {
            "agentName": agent_name,
            "namespaceId": namespace_id,
        }

        request_source = RequestResource(
            Constants.AI_MODULE,
            namespace_id,
            "",
            agent_name,
        )
        request = HttpRequest(
            path="/nacos/v3/admin/ai/a2a/version/list",
            method="GET",
            request_resource=request_source,
            params=params,
        )
        result = await self.http_proxy.request(request)
        if result["code"] != 0:
            self.logger.error(
                f"list all version of agent failed, result:{result}",
            )
            raise Exception(result["message"])

        result_data = result["data"]
        try:
            adapter = TypeAdapter(List[AgentVersionDetail])
            agent_version_detail_list: List[
                AgentVersionDetail
            ] = adapter.validate_python(
                result_data,
            )
        except Exception as e:
            self.logger.error(e)
            raise
        return agent_version_detail_list

    async def search_agent_cards_by_name(
        self,
        namespace_id: str,
        agent_name_pattern: str,
        page_no: int,
        page_size: int,
    ) -> Tuple[int, int, int, List[AgentCardVersionInfo]]:
        return await self._list_or_search_agent_cards_by_name(
            namespace_id,
            agent_name_pattern,
            page_no,
            page_size,
            True,
        )

    async def list_agent_cards_by_name(
        self,
        namespace_id: str,
        agent_name: str,
        page_no: int,
        page_size: int,
    ) -> Tuple[int, int, int, List[AgentCardVersionInfo]]:
        return await self._list_or_search_agent_cards_by_name(
            namespace_id,
            agent_name,
            page_no,
            page_size,
            False,
        )

    async def _list_or_search_agent_cards_by_name(
        self,
        namespace_id: str,
        agent_name: str,
        page_no: int,
        page_size: int,
        is_blur: bool,
    ) -> Tuple[int, int, int, List[AgentCardVersionInfo]]:
        if namespace_id is None or len(namespace_id) == 0:
            namespace_id = DEFAULT_NAMESPACE_ID

        params = {
            "namespaceId": namespace_id,
            "agentName": agent_name,
            "pageNo": page_no,
            "pageSize": page_size,
            "search": "blur" if is_blur else "accurate",
        }

        request_source = RequestResource(
            Constants.AI_MODULE,
            namespace_id,
            "",
            None,
        )

        request = HttpRequest(
            path="/nacos/v3/admin/ai/a2a/list",
            method="GET",
            request_resource=request_source,
            params=params,
        )

        result = await self.http_proxy.request(request)
        if result["code"] != 0:
            self.logger.error(f"list agent cards failed, result:{result}")
            raise Exception(result["message"])

        result_data = result["data"]
        total_count = result_data["totalCount"]
        page_number = result_data["pageNumber"]
        page_available = result_data["pagesAvailable"]
        page_items = result_data["pageItems"]
        try:
            adapter = TypeAdapter(List[AgentCardVersionInfo])
            agent_card_version_info_list: List[
                AgentCardVersionInfo
            ] = adapter.validate_python(
                page_items,
            )
        except Exception as e:
            self.logger.error(e)
            raise

        return (
            total_count,
            page_number,
            page_available,
            agent_card_version_info_list,
        )

    # ========== Prompt Maintainer Service ==========

    async def list_prompts(
        self,
        namespace_id: str,
        prompt_key: str,
        search: str,
        biz_tags: Optional[str],
        page_no: int,
        page_size: int,
    ) -> Tuple[int, int, int, List[PromptMetaSummary]]:
        if namespace_id is None or len(namespace_id) == 0:
            namespace_id = DEFAULT_NAMESPACE_ID

        params = {
            "namespaceId": namespace_id,
            "promptKey": prompt_key,
            "search": search,
            "pageNo": page_no,
            "pageSize": page_size,
        }
        if biz_tags is not None and len(biz_tags) > 0:
            params["bizTags"] = biz_tags

        request_resource = RequestResource(
            Constants.AI_MODULE, namespace_id, "", prompt_key,
        )
        request = HttpRequest(
            path="/nacos/v3/admin/ai/prompt/list",
            method="GET",
            request_resource=request_resource,
            params=params,
        )
        result = await self.http_proxy.request(request)
        if result["code"] != 0:
            self.logger.error(f"list prompts failed, result:{result}")
            raise Exception(result["message"])

        result_data = result["data"]
        total_count = result_data["totalCount"]
        page_number = result_data["pageNumber"]
        page_available = result_data["pagesAvailable"]
        page_items = result_data["pageItems"]
        adapter = TypeAdapter(List[PromptMetaSummary])
        prompts = adapter.validate_python(page_items)
        return total_count, page_number, page_available, prompts

    async def search_prompts(
        self,
        namespace_id: str,
        prompt_key: str,
        page_no: int,
        page_size: int,
        biz_tags: Optional[str] = None,
    ) -> Tuple[int, int, int, List[PromptMetaSummary]]:
        return await self.list_prompts(
            namespace_id, prompt_key, "blur", biz_tags, page_no, page_size,
        )

    async def get_prompt_meta(
        self,
        namespace_id: str,
        prompt_key: str,
    ) -> PromptMetaInfo:
        if namespace_id is None or len(namespace_id) == 0:
            namespace_id = DEFAULT_NAMESPACE_ID

        params = {
            "namespaceId": namespace_id,
            "promptKey": prompt_key,
        }
        request_resource = RequestResource(
            Constants.AI_MODULE, namespace_id, "", prompt_key,
        )
        request = HttpRequest(
            path="/nacos/v3/admin/ai/prompt/metadata",
            method="GET",
            request_resource=request_resource,
            params=params,
        )
        result = await self.http_proxy.request(request)
        if result["code"] != 0:
            self.logger.error(f"get prompt meta failed, result:{result}")
            raise Exception(result["message"])

        adapter = TypeAdapter(PromptMetaInfo)
        return adapter.validate_python(result["data"])

    async def query_prompt_detail(
        self,
        namespace_id: str,
        prompt_key: str,
        version: Optional[str] = None,
        label: Optional[str] = None,
    ) -> PromptVersionInfo:
        if namespace_id is None or len(namespace_id) == 0:
            namespace_id = DEFAULT_NAMESPACE_ID

        params = {
            "namespaceId": namespace_id,
            "promptKey": prompt_key,
        }
        if version is not None and len(version) > 0:
            params["version"] = version
        if label is not None and len(label) > 0:
            params["label"] = label

        request_resource = RequestResource(
            Constants.AI_MODULE, namespace_id, "", prompt_key,
        )
        request = HttpRequest(
            path="/nacos/v3/admin/ai/prompt/detail",
            method="GET",
            request_resource=request_resource,
            params=params,
        )
        result = await self.http_proxy.request(request)
        if result["code"] != 0:
            self.logger.error(
                f"query prompt detail failed, result:{result}",
            )
            raise Exception(result["message"])

        adapter = TypeAdapter(PromptVersionInfo)
        return adapter.validate_python(result["data"])

    async def publish_prompt(
        self,
        namespace_id: str,
        prompt_key: str,
        version: str,
        template: str,
        commit_msg: Optional[str] = None,
        description: Optional[str] = None,
        biz_tags: Optional[str] = None,
    ) -> bool:
        if namespace_id is None or len(namespace_id) == 0:
            namespace_id = DEFAULT_NAMESPACE_ID

        params = {
            "namespaceId": namespace_id,
            "promptKey": prompt_key,
            "version": version,
            "template": template,
        }
        if commit_msg is not None and len(commit_msg) > 0:
            params["commitMsg"] = commit_msg
        if description is not None and len(description) > 0:
            params["description"] = description
        if biz_tags is not None and len(biz_tags) > 0:
            params["bizTags"] = biz_tags

        request_resource = RequestResource(
            Constants.AI_MODULE, namespace_id, "", prompt_key,
        )
        request = HttpRequest(
            path="/nacos/v3/admin/ai/prompt",
            method="POST",
            request_resource=request_resource,
            data=params,
        )
        result = await self.http_proxy.request(request)
        if result["code"] != 0:
            self.logger.error(f"publish prompt failed, result:{result}")
            return False

        return True

    async def delete_prompt(
        self,
        namespace_id: str,
        prompt_key: str,
    ) -> bool:
        if namespace_id is None or len(namespace_id) == 0:
            namespace_id = DEFAULT_NAMESPACE_ID

        params = {
            "namespaceId": namespace_id,
            "promptKey": prompt_key,
        }
        request_resource = RequestResource(
            Constants.AI_MODULE, namespace_id, "", prompt_key,
        )
        request = HttpRequest(
            path="/nacos/v3/admin/ai/prompt",
            method="DELETE",
            request_resource=request_resource,
            params=params,
        )
        result = await self.http_proxy.request(request)
        if result["code"] != 0:
            self.logger.error(f"delete prompt failed, result:{result}")
            return False

        return True

    async def list_prompt_versions(
        self,
        namespace_id: str,
        prompt_key: str,
        page_no: int,
        page_size: int,
    ) -> Tuple[int, int, int, List[PromptVersionSummary]]:
        if namespace_id is None or len(namespace_id) == 0:
            namespace_id = DEFAULT_NAMESPACE_ID

        params = {
            "namespaceId": namespace_id,
            "promptKey": prompt_key,
            "pageNo": page_no,
            "pageSize": page_size,
        }
        request_resource = RequestResource(
            Constants.AI_MODULE, namespace_id, "", prompt_key,
        )
        request = HttpRequest(
            path="/nacos/v3/admin/ai/prompt/versions",
            method="GET",
            request_resource=request_resource,
            params=params,
        )
        result = await self.http_proxy.request(request)
        if result["code"] != 0:
            self.logger.error(
                f"list prompt versions failed, result:{result}",
            )
            raise Exception(result["message"])

        result_data = result["data"]
        total_count = result_data["totalCount"]
        page_number = result_data["pageNumber"]
        page_available = result_data["pagesAvailable"]
        page_items = result_data["pageItems"]
        adapter = TypeAdapter(List[PromptVersionSummary])
        versions = adapter.validate_python(page_items)
        return total_count, page_number, page_available, versions

    async def update_prompt_metadata(
        self,
        namespace_id: str,
        prompt_key: str,
        description: Optional[str] = None,
        biz_tags: Optional[str] = None,
    ) -> bool:
        if namespace_id is None or len(namespace_id) == 0:
            namespace_id = DEFAULT_NAMESPACE_ID

        params = {
            "namespaceId": namespace_id,
            "promptKey": prompt_key,
        }
        if description is not None:
            params["description"] = description
        if biz_tags is not None:
            params["bizTags"] = biz_tags

        request_resource = RequestResource(
            Constants.AI_MODULE, namespace_id, "", prompt_key,
        )
        request = HttpRequest(
            path="/nacos/v3/admin/ai/prompt/metadata",
            method="PUT",
            request_resource=request_resource,
            data=params,
        )
        result = await self.http_proxy.request(request)
        if result["code"] != 0:
            self.logger.error(
                f"update prompt metadata failed, result:{result}",
            )
            return False

        return True

    async def bind_label(
        self,
        namespace_id: str,
        prompt_key: str,
        label: str,
        version: str,
    ) -> bool:
        if namespace_id is None or len(namespace_id) == 0:
            namespace_id = DEFAULT_NAMESPACE_ID

        params = {
            "namespaceId": namespace_id,
            "promptKey": prompt_key,
            "label": label,
            "version": version,
        }
        request_resource = RequestResource(
            Constants.AI_MODULE, namespace_id, "", prompt_key,
        )
        request = HttpRequest(
            path="/nacos/v3/admin/ai/prompt/label",
            method="PUT",
            request_resource=request_resource,
            data=params,
        )
        result = await self.http_proxy.request(request)
        if result["code"] != 0:
            self.logger.error(f"bind label failed, result:{result}")
            return False

        return True

    async def unbind_label(
        self,
        namespace_id: str,
        prompt_key: str,
        label: str,
    ) -> bool:
        if namespace_id is None or len(namespace_id) == 0:
            namespace_id = DEFAULT_NAMESPACE_ID

        params = {
            "namespaceId": namespace_id,
            "promptKey": prompt_key,
            "label": label,
        }
        request_resource = RequestResource(
            Constants.AI_MODULE, namespace_id, "", prompt_key,
        )
        request = HttpRequest(
            path="/nacos/v3/admin/ai/prompt/label",
            method="DELETE",
            request_resource=request_resource,
            params=params,
        )
        result = await self.http_proxy.request(request)
        if result["code"] != 0:
            self.logger.error(f"unbind label failed, result:{result}")
            return False

        return True

    # ========== Skill Maintainer Service ==========

    async def register_skill(
        self,
        namespace_id: str,
        skill: Skill,
    ) -> str:
        if namespace_id is None or len(namespace_id) == 0:
            namespace_id = DEFAULT_NAMESPACE_ID

        params = {
            "namespaceId": namespace_id,
            "skillCard": skill.model_dump_json(
                exclude_none=True, by_alias=True,
            ),
        }
        request_resource = RequestResource(
            Constants.AI_MODULE, namespace_id, "", skill.name,
        )
        request = HttpRequest(
            path="/nacos/v3/admin/ai/skills",
            method="POST",
            request_resource=request_resource,
            data=params,
        )
        result = await self.http_proxy.request(request)
        if result["code"] != 0:
            self.logger.error(f"register skill failed, result:{result}")
            raise Exception(result["message"])

        return result["data"]

    async def get_skill_detail(
        self,
        namespace_id: str,
        skill_name: str,
    ) -> Skill:
        if namespace_id is None or len(namespace_id) == 0:
            namespace_id = DEFAULT_NAMESPACE_ID

        params = {
            "namespaceId": namespace_id,
            "skillName": skill_name,
        }
        request_resource = RequestResource(
            Constants.AI_MODULE, namespace_id, "", skill_name,
        )
        request = HttpRequest(
            path="/nacos/v3/admin/ai/skills",
            method="GET",
            request_resource=request_resource,
            params=params,
        )
        result = await self.http_proxy.request(request)
        if result["code"] != 0:
            self.logger.error(
                f"get skill detail failed, result:{result}",
            )
            raise Exception(result["message"])

        adapter = TypeAdapter(Skill)
        return adapter.validate_python(result["data"])

    async def update_skill(
        self,
        namespace_id: str,
        skill: Skill,
    ) -> bool:
        if namespace_id is None or len(namespace_id) == 0:
            namespace_id = DEFAULT_NAMESPACE_ID

        params = {
            "namespaceId": namespace_id,
            "skillCard": skill.model_dump_json(
                exclude_none=True, by_alias=True,
            ),
        }
        request_resource = RequestResource(
            Constants.AI_MODULE, namespace_id, "", skill.name,
        )
        request = HttpRequest(
            path="/nacos/v3/admin/ai/skills",
            method="PUT",
            request_resource=request_resource,
            data=params,
        )
        result = await self.http_proxy.request(request)
        if result["code"] != 0:
            self.logger.error(f"update skill failed, result:{result}")
            return False

        return True

    async def delete_skill(
        self,
        namespace_id: str,
        skill_name: str,
    ) -> bool:
        if namespace_id is None or len(namespace_id) == 0:
            namespace_id = DEFAULT_NAMESPACE_ID

        params = {
            "namespaceId": namespace_id,
            "skillName": skill_name,
        }
        request_resource = RequestResource(
            Constants.AI_MODULE, namespace_id, "", skill_name,
        )
        request = HttpRequest(
            path="/nacos/v3/admin/ai/skills",
            method="DELETE",
            request_resource=request_resource,
            params=params,
        )
        result = await self.http_proxy.request(request)
        if result["code"] != 0:
            self.logger.error(f"delete skill failed, result:{result}")
            return False

        return True

    async def list_skills(
        self,
        namespace_id: str,
        skill_name: str,
        search: str,
        page_no: int,
        page_size: int,
    ) -> Tuple[int, int, int, List[SkillBasicInfo]]:
        if namespace_id is None or len(namespace_id) == 0:
            namespace_id = DEFAULT_NAMESPACE_ID

        params = {
            "namespaceId": namespace_id,
            "skillName": skill_name,
            "search": search,
            "pageNo": page_no,
            "pageSize": page_size,
        }
        request_resource = RequestResource(
            Constants.AI_MODULE, namespace_id, "", skill_name,
        )
        request = HttpRequest(
            path="/nacos/v3/admin/ai/skills/list",
            method="GET",
            request_resource=request_resource,
            params=params,
        )
        result = await self.http_proxy.request(request)
        if result["code"] != 0:
            self.logger.error(f"list skills failed, result:{result}")
            raise Exception(result["message"])

        result_data = result["data"]
        total_count = result_data["totalCount"]
        page_number = result_data["pageNumber"]
        page_available = result_data["pagesAvailable"]
        page_items = result_data["pageItems"]
        adapter = TypeAdapter(List[SkillBasicInfo])
        skills = adapter.validate_python(page_items)
        return total_count, page_number, page_available, skills

    async def search_skills(
        self,
        namespace_id: str,
        skill_name: str,
        page_no: int,
        page_size: int,
    ) -> Tuple[int, int, int, List[SkillBasicInfo]]:
        return await self.list_skills(
            namespace_id, skill_name, "blur", page_no, page_size,
        )

    async def upload_skill_from_zip(
        self,
        namespace_id: str,
        zip_bytes: bytes,
    ) -> str:
        if namespace_id is None or len(namespace_id) == 0:
            namespace_id = DEFAULT_NAMESPACE_ID

        import aiohttp

        form_data = aiohttp.FormData()
        form_data.add_field("namespaceId", namespace_id)
        form_data.add_field(
            "file",
            zip_bytes,
            filename="skill.zip",
            content_type="application/zip",
        )

        request_resource = RequestResource(
            Constants.AI_MODULE, namespace_id, "", None,
        )
        request = HttpRequest(
            path="/nacos/v3/admin/ai/skills/upload",
            method="POST",
            request_resource=request_resource,
        )
        request.form_data = form_data
        result = await self.http_proxy.request(request)
        if result["code"] != 0:
            self.logger.error(
                f"upload skill from zip failed, result:{result}",
            )
            raise Exception(result["message"])

        return result["data"]
