# -*- coding: utf-8 -*-
from a2a.types import AgentCard, AgentCapabilities, AgentSkill
from v2.nacos import ClientConfigBuilder
from v2.nacos.ai.model.mcp.mcp import (
    McpServerBasicInfo,
    McpToolSpecification,
    McpEndpointSpec,
    McpTool,
)
from v2.nacos.ai.model.mcp.registry import ServerVersionDetail

from maintainer.ai.nacos_ai_maintainer_service import NacosAIMaintainerService


async def main():
    ai_client_config = (
        ClientConfigBuilder()
        .server_address(
            "localhost:8848",
        )
        .username(
            "nacos",
        )
        .password(
            "nacos",
        )
        .build()
    )
    mcp_service = await NacosAIMaintainerService.create_ai_service(
        ai_client_config,
    )
    tool_spec = [
        McpTool(
            name="test_tool",
            description="test tool",
            inputSchema={},
        ),
    ]
    mcp_tool_specification = McpToolSpecification(
        tools=tool_spec,
    )

    server_version_detail = ServerVersionDetail()
    server_version_detail.version = "0.1.0"
    server_basic_info = McpServerBasicInfo()
    server_basic_info.name = "nacos-mcp-server"
    server_basic_info.versionDetail = server_version_detail
    server_basic_info.description = "test mcp server"

    server_basic_info.protocol = "stdio"
    server_basic_info.frontProtocol = "stdio"

    await mcp_service.create_mcp_server(
        "public",
        "nacos-mcp-server",
        server_basic_info,
        mcp_tool_specification,
        McpEndpointSpec(),
    )
    await asyncio.sleep(3)
    print(
        await mcp_service.get_mcp_server_detail(
            "public",
            "nacos-mcp-server",
            "0.1.0",
        ),
    )

    print(
        await mcp_service.search_mcp_server(
            "public", "nacos-mcp-server", 1, 10
        )
    )
    print(await mcp_service.list_mcp_servers("public", "", 1, 10))
    server_version_detail.version = "0.2.0"
    await mcp_service.update_mcp_server(
        "public",
        "nacos-mcp-server",
        True,
        server_basic_info,
        mcp_tool_specification,
        McpEndpointSpec(),
    )
    await asyncio.sleep(3)
    await mcp_service.delete_mcp_server("public", "nacos-mcp-server")

    capabilities = AgentCapabilities(
        streaming=False,
        push_notifications=False,
    )
    skill = AgentSkill(
        id="dialog",
        name="Natural Language Dialog Skill",
        description="Enables natural language conversation and dialogue "
        "with users",
        tags=["natural language", "dialog", "conversation"],
        examples=[
            "Hello, how are you?",
            "Can you help me with something?",
        ],
    )

    agent_card = AgentCard(
        capabilities=capabilities,
        skills=[skill],
        name="nacos_a2a_agent",
        description="test_agent",
        default_input_modes=["text"],
        default_output_modes=["text"],
        url="0.0.0.0",
        version="1.0.0",
    )

    await mcp_service.register_agent(
        agent_card=agent_card, namespace_id="public", registration_type="URL"
    )
    print(
        await mcp_service.get_agent_card(
            namespace_id="public",
            agent_name="nacos_a2a_agent",
            registration_type="URL",
        )
    )
    agent_card.version = "1.0.1"
    await mcp_service.update_agent_card(
        agent_card=agent_card,
        namespace_id="public",
        set_as_latest=True,
        registration_type="URL",
    )
    print(
        await mcp_service.list_all_version_of_agent(
            namespace_id="public", agent_name="nacos_a2a_agent"
        )
    )
    print(
        await mcp_service.list_agent_cards_by_name(
            namespace_id="public",
            agent_name="nacos_a2a_agent",
            page_no=1,
            page_size=10,
        )
    )
    print(
        await mcp_service.search_agent_cards_by_name(
            namespace_id="public",
            agent_name_pattern="nacos_a2a_agent",
            page_no=1,
            page_size=10,
        )
    )
    await asyncio.sleep(100)
    await mcp_service.delete_agent(
        namespace_id="public", agent_name="nacos_a2a_agent"
    )


if __name__ == "__main__":
    import asyncio

    print(asyncio.run(main()))
