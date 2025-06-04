from maintainer.ai.model.nacos_mcp_info import McpServerBasicInfo, \
	McpToolSpecification, McpEndpointSpec
from maintainer.common.ai_maintainer_client_config_builder import AIMaintainerClientConfigBuilder
from maintainer.ai.nacos_mcp_service import NacosAIMaintainerService


async def main():
	ai_client_config = AIMaintainerClientConfigBuilder().server_address(
			"127.0.0.1:8848").username(
			'nacos').password(
			'nacos').build()
	mcp_service = await NacosAIMaintainerService.create_mcp_service(ai_client_config)
	await mcp_service.get_mcp_server_detail("public", "nacos-mcp-server", "0.1.0")
	await mcp_service.search_mcp_server("public", "nacos-mcp-server", 1, 10)
	await mcp_service.list_mcp_servers("public", "", 1, 10)
	await mcp_service.update_mcp_server("public", "nacos-mcp-server", True, McpServerBasicInfo(), McpToolSpecification(), McpEndpointSpec())
	await mcp_service.delete_mcp_server("public", "nacos-mcp-server")
	await mcp_service.create_mcp_server("public","nacos-mcp-server",McpServerBasicInfo(),McpToolSpecification(),McpEndpointSpec())

if __name__ == '__main__':
	import asyncio
	print(asyncio.run(main()))
