# -*- coding: utf-8 -*-
import asyncio

from a2a.types import AgentCard, AgentCapabilities, AgentSkill
from v2.nacos import ClientConfigBuilder
from v2.nacos.ai.model.mcp.mcp import (
    McpServerBasicInfo,
    McpToolSpecification,
    McpEndpointSpec,
    McpTool,
)
from v2.nacos.ai.model.mcp.registry import ServerVersionDetail

from maintainer.ai.model.skill import Skill, SkillResource
from maintainer.ai.nacos_ai_maintainer_service import NacosAIMaintainerService


async def mcp_example(service: NacosAIMaintainerService):
    """MCP Server management example."""
    print("=== MCP Server Example ===")

    tool_spec = [
        McpTool(name="test_tool", description="test tool", inputSchema={}),
    ]
    mcp_tool_specification = McpToolSpecification(tools=tool_spec)

    server_version_detail = ServerVersionDetail()
    server_version_detail.version = "0.1.0"
    server_basic_info = McpServerBasicInfo()
    server_basic_info.name = "nacos-mcp-server"
    server_basic_info.versionDetail = server_version_detail
    server_basic_info.description = "test mcp server"
    server_basic_info.protocol = "stdio"
    server_basic_info.frontProtocol = "stdio"

    await service.create_mcp_server(
        "public", "nacos-mcp-server",
        server_basic_info, mcp_tool_specification, McpEndpointSpec(),
    )
    await asyncio.sleep(3)
    print(await service.get_mcp_server_detail(
        "public", "nacos-mcp-server", "0.1.0",
    ))
    print(await service.search_mcp_server(
        "public", "nacos-mcp-server", 1, 10,
    ))
    print(await service.list_mcp_servers("public", "", 1, 10))

    server_version_detail.version = "0.2.0"
    await service.update_mcp_server(
        "public", "nacos-mcp-server", True,
        server_basic_info, mcp_tool_specification, McpEndpointSpec(),
    )
    await asyncio.sleep(3)
    await service.delete_mcp_server("public", "nacos-mcp-server")
    print("=== MCP Server Example Done ===\n")


async def a2a_example(service: NacosAIMaintainerService):
    """A2A Agent management example."""
    print("=== A2A Agent Example ===")

    capabilities = AgentCapabilities(
        streaming=False, push_notifications=False,
    )
    skill = AgentSkill(
        id="dialog",
        name="Natural Language Dialog Skill",
        description="Enables natural language conversation and dialogue "
        "with users",
        tags=["natural language", "dialog", "conversation"],
        examples=["Hello, how are you?", "Can you help me with something?"],
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

    await service.register_agent(
        agent_card=agent_card, namespace_id="public",
        registration_type="URL",
    )
    print(await service.get_agent_card(
        namespace_id="public", agent_name="nacos_a2a_agent",
        registration_type="URL",
    ))
    agent_card.version = "1.0.1"
    await service.update_agent_card(
        agent_card=agent_card, namespace_id="public",
        set_as_latest=True, registration_type="URL",
    )
    print(await service.list_all_version_of_agent(
        namespace_id="public", agent_name="nacos_a2a_agent",
    ))
    print(await service.list_agent_cards_by_name(
        namespace_id="public", agent_name="nacos_a2a_agent",
        page_no=1, page_size=10,
    ))
    print(await service.search_agent_cards_by_name(
        namespace_id="public", agent_name_pattern="nacos_a2a_agent",
        page_no=1, page_size=10,
    ))
    await service.delete_agent(
        namespace_id="public", agent_name="nacos_a2a_agent",
    )
    print("=== A2A Agent Example Done ===\n")


async def prompt_example(service: NacosAIMaintainerService):
    """Prompt management example."""
    print("=== Prompt Example ===")

    print("[1] Publishing prompt v1.0.0...")
    result = await service.publish_prompt(
        namespace_id="public",
        prompt_key="example-prompt",
        version="1.0.0",
        template="Hello {{name}}, you are a {{role}}.",
        commit_msg="initial version",
        description="Example prompt template",
    )
    print(f"    publish result: {result}")

    print("[2] Getting prompt metadata...")
    meta = await service.get_prompt_meta("public", "example-prompt")
    print(f"    meta: {meta}")

    print("[3] Querying prompt detail...")
    detail = await service.query_prompt_detail(
        "public", "example-prompt", version="1.0.0",
    )
    print(f"    detail: {detail}")

    print("[4] Publishing prompt v2.0.0...")
    await service.publish_prompt(
        namespace_id="public",
        prompt_key="example-prompt",
        version="2.0.0",
        template="Hi {{name}}, welcome to {{department}}!",
        commit_msg="add department variable",
    )

    print("[5] Listing prompt versions...")
    total, page_num, pages, versions = await service.list_prompt_versions(
        "public", "example-prompt", 1, 10,
    )
    print(f"    total: {total}, versions: {versions}")

    print("[6] Binding label 'prod' to v1.0.0...")
    await service.bind_label("public", "example-prompt", "prod", "1.0.0")

    print("[7] Querying prompt by label 'prod'...")
    detail_by_label = await service.query_prompt_detail(
        "public", "example-prompt", label="prod",
    )
    print(f"    detail: {detail_by_label}")

    print("[8] Updating prompt metadata...")
    await service.update_prompt_metadata(
        "public", "example-prompt",
        description="Updated description",
        biz_tags="tag1,tag2",
    )

    print("[9] Listing all prompts...")
    total, page_num, pages, prompts = await service.search_prompts(
        "public", "example", 1, 10,
    )
    print(f"    total: {total}, prompts: {prompts}")

    print("[10] Unbinding label...")
    await service.unbind_label("public", "example-prompt", "prod")

    print("[11] Deleting prompt...")
    await service.delete_prompt("public", "example-prompt")
    print("=== Prompt Example Done ===\n")


async def skill_example(service: NacosAIMaintainerService):
    """Skill management example."""
    print("=== Skill Example ===")

    print("[1] Registering skill...")
    skill = Skill(
        name="example-skill",
        description="An example skill for testing",
        instruction="Follow the instructions to complete the task.",
        resource={
            "main": SkillResource(
                name="main-resource",
                type="text",
                content="This is the main resource content.",
            ),
        },
    )
    result = await service.register_skill("public", skill)
    print(f"    register result: {result}")

    print("[2] Getting skill detail...")
    detail = await service.get_skill_detail("public", "example-skill")
    print(f"    detail: {detail}")

    print("[3] Updating skill...")
    skill.description = "Updated skill description"
    await service.update_skill("public", skill)

    print("[4] Listing skills...")
    total, page_num, pages, skills = await service.search_skills(
        "public", "example", 1, 10,
    )
    print(f"    total: {total}, skills: {skills}")

    print("[5] Deleting skill...")
    await service.delete_skill("public", "example-skill")
    print("=== Skill Example Done ===\n")


async def main():
    ai_client_config = (
        ClientConfigBuilder()
        .server_address("localhost:8848")
        .username("nacos")
        .password("nacos")
        .build()
    )
    service = await NacosAIMaintainerService.create_ai_service(
        ai_client_config,
    )

    await prompt_example(service)
    await skill_example(service)
    await mcp_example(service)
    await a2a_example(service)


if __name__ == "__main__":
    print(asyncio.run(main()))
