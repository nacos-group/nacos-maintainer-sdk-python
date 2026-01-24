import socket
import nacos
import mcp.types as mcp_types

from loguru import logger
from app import settings
from collections.abc import Sequence
from typing import Any

from v2.nacos import NacosNamingService, ClientConfigBuilder, GRPCConfig, Instance, SubscribeServiceParam, \
    RegisterInstanceParam, DeregisterInstanceParam, BatchRegisterInstanceParam, GetServiceParam, ListServiceParam, \
    ListInstanceParam, NacosConfigService, ConfigParam

from maintainer.ai.model.nacos_mcp_info import McpCapability, McpEndpointSpec, McpServerBasicInfo, \
	McpServerRemoteServiceConfig, McpTool, McpToolSpecification
from maintainer.common.ai_maintainer_client_config_builder import AIMaintainerClientConfigBuilder
from maintainer.ai.nacos_mcp_service import NacosAIMaintainerService
from fastapi_mcp import FastApiMCP

def get_local_ip() -> str:
    """获取本地内网IP"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))  # 不会真的发包
        return s.getsockname()[0]
    finally:
        s.close()

def mount_mcp(app):
    """返回 mcp 实例，便于外部拿 tools 列表"""
    mcp = FastApiMCP(
        fastapi=app,
        name="Algorithm Service API",
        description="Stream and batch processing algorithm service",
    )
    mcp.mount_http()
    return mcp

class BasicNacosRegistrar:

    def __init__(self):
        self.client = nacos.NacosClient(
            server_addresses=settings.NACOS_SERVER_ADDR,
            namespace=settings.NACOS_NAMESPACE,
            username=settings.NACOS_USERNAME or None,
            password=settings.NACOS_PASSWORD or None,
        )
        self._registered = False

    @staticmethod
    async def register(service_name: str, port: int, enabled: bool = False):

        if not enabled:
            logger.info(f"Skip Nacos registration for service={service_name}, port={port}")
            return

        ip_or_host = get_local_ip()

        client_config = (ClientConfigBuilder()
                         .server_address(settings.NACOS_SERVER_ADDR).namespace_id(settings.NACOS_NAMESPACE)
                         .username(settings.NACOS_USERNAME).password(settings.NACOS_PASSWORD)
                         .log_level('INFO')
                         .grpc_config(GRPCConfig(grpc_timeout=5000, max_keep_alive_ms=60000))
                         .build())

        naming_client = await NacosNamingService.create_naming_service(client_config)

        response = await naming_client.register_instance(
            request=RegisterInstanceParam(
                service_name=service_name,
                group_name=settings.SERVICE_GROUP,
                ip=ip_or_host,
                port=port,
                ephemeral=True
            )
        )

        if response:
            logger.info(
                f"✅ Registered service={service_name}, host={ip_or_host}, port={port} to Nacos successfully"
            )
        else:
            logger.error(
                f"❌ Failed to register service={service_name}, host={ip_or_host}, port={port} to Nacos"
            )
        return naming_client

    @staticmethod
    async def register_mcp(
            service_name: str,
            port: int,
            version: str,
            enabled: bool = False,
            tools: Sequence[mcp_types.Tool] | None = None,
    ) -> None:

        if not enabled:
            logger.info(f"Skip Nacos registration mcp for service={service_name}, port={port}")
            return

        ip_or_host = get_local_ip()

        ai_client_config = (AIMaintainerClientConfigBuilder().server_address(settings.NACOS_SERVER_ADDR)
                            .username(settings.NACOS_USERNAME).password(settings.NACOS_PASSWORD).build())
        mcp_service = await NacosAIMaintainerService.create_mcp_service(ai_client_config)
        namespace_id = settings.NACOS_NAMESPACE
        server_specification = McpServerBasicInfo(remoteServerConfig=McpServerRemoteServiceConfig())
        server_specification.name = service_name
        server_specification.version = version
        server_specification.protocol = "mcp-sse"
        server_specification.frontProtocol = "mcp-sse"
        server_specification.remoteServerConfig.exportPath = "/mcp"

        tool_specification = McpToolSpecification()
        if tools:
            converted_tools: list[McpTool] = []
            for tool in tools:
                tool_name = getattr(tool, "name", None)
                tool_schema: Any = getattr(tool, "inputSchema", None)

                if not tool_name:
                    logger.warning("Skip MCP tool without name: %s", tool)
                    continue

                if tool_schema is None:
                    logger.warning("Skip MCP tool without input schema: %s", tool_name)
                    continue

                if not isinstance(tool_schema, dict):
                    logger.warning("Skip MCP tool with invalid schema type: %s", tool_name)
                    continue

                converted_tools.append(
                    McpTool(
                        name=tool_name,
                        description=getattr(tool, "description", None),
                        inputSchema=tool_schema,
                    )
                )

            if converted_tools:
                tool_specification.tools = converted_tools
                server_specification.capabilities = [McpCapability.TOOL]
        endpoint_specification = McpEndpointSpec()
        endpoint_specification.type = "REF"
        if endpoint_specification.data is None:
            endpoint_specification.data = {}
        endpoint_specification.data['namespaceId'] = namespace_id
        endpoint_specification.data['serviceName'] = service_name
        endpoint_specification.data['groupName'] = settings.SERVICE_GROUP

        mcp_detail = None

        try:
            mcp_detail = await mcp_service.get_mcp_server_detail(namespace_id, service_name, version)
        except Exception as e:
            logger.error(f"get_mcp_server_detail: {e}")

        if mcp_detail:
            response = await mcp_service.update_mcp_server(
                namespace_id,
                service_name,
                True,
                server_specification,
                tool_specification,
                endpoint_specification)
        else:
            response = await mcp_service.create_mcp_server(
                namespace_id,
                service_name,
                server_specification,
                tool_specification,
                endpoint_specification,
            )

        if response:
            logger.info(
                f"✅ Registered mcp service={service_name}, host={ip_or_host}, port={port} to Nacos successfully"
            )
        else:
            logger.error(
                f"❌ Failed to register mcp service={service_name}, host={ip_or_host}, port={port} to Nacos"
            )

    @staticmethod
    async def deregister(nacos_naming_service: NacosNamingService,service_name: str, port: int):
        if nacos_naming_service:
            ip_or_host = get_local_ip()
            await nacos_naming_service.deregister_instance(
                request=DeregisterInstanceParam(service_name=service_name,
                                                group_name=settings.SERVICE_GROUP,
                                                ip=ip_or_host,
                                                port=port,
                                                ephemeral=True)
            )
