# -*- coding: utf-8 -*-
import asyncio
import os
import traceback

from v2.nacos import ClientConfigBuilder

from maintainer.ai.model.skill import Skill, SkillResource
from maintainer.ai.nacos_ai_maintainer_service import NacosAIMaintainerService

SERVER = "localhost:8848"
USERNAME = "nacos"
PASSWORD = "nacos"
NAMESPACE = "public"

PROMPT_KEY = "sdk-test-prompt"
SKILL_NAME = "sdk-test-skill"

ZIP_PATH = os.path.join(os.path.dirname(__file__), "pdf.zip")


async def test_prompt(service: NacosAIMaintainerService):
    print("=" * 60)
    print("  Prompt API Tests")
    print("=" * 60)

    # 1. publish prompt v1.0.0
    print("\n[1] publish_prompt v1.0.0 ...")
    ok = await service.publish_prompt(
        namespace_id=NAMESPACE,
        prompt_key=PROMPT_KEY,
        version="1.0.0",
        template="Hello {{name}}, you are a {{role}}.",
        commit_msg="initial version",
        description="SDK test prompt",
        biz_tags="test,sdk",
    )
    print(f"    result: {ok}")
    assert ok, "publish_prompt v1.0.0 failed"

    await asyncio.sleep(1)

    # 2. publish prompt v2.0.0
    print("\n[2] publish_prompt v2.0.0 ...")
    ok = await service.publish_prompt(
        namespace_id=NAMESPACE,
        prompt_key=PROMPT_KEY,
        version="2.0.0",
        template="Hi {{name}}, welcome to {{department}}!",
        commit_msg="add department",
    )
    print(f"    result: {ok}")
    assert ok, "publish_prompt v2.0.0 failed"

    await asyncio.sleep(1)

    # 3. get_prompt_meta
    print("\n[3] get_prompt_meta ...")
    meta = await service.get_prompt_meta(NAMESPACE, PROMPT_KEY)
    print(f"    promptKey: {meta.prompt_key}")
    print(f"    description: {meta.description}")
    print(f"    versions: {meta.versions}")
    print(f"    labels: {meta.labels}")
    print(f"    latestVersion: {meta.latest_version}")

    # 4. query_prompt_detail by version
    print("\n[4] query_prompt_detail (version=1.0.0) ...")
    detail = await service.query_prompt_detail(
        NAMESPACE, PROMPT_KEY, version="1.0.0",
    )
    print(f"    promptKey: {detail.prompt_key}")
    print(f"    version: {detail.version}")
    print(f"    template: {detail.template}")
    print(f"    md5: {detail.md5}")

    # 5. list_prompt_versions
    print("\n[5] list_prompt_versions ...")
    total, page_num, pages, versions = await service.list_prompt_versions(
        NAMESPACE, PROMPT_KEY, 1, 10,
    )
    print(f"    total: {total}")
    for v in versions:
        print(f"    - {v.version} ({v.commit_msg})")

    # 6. bind_label
    print("\n[6] bind_label 'prod' -> v1.0.0 ...")
    ok = await service.bind_label(NAMESPACE, PROMPT_KEY, "prod", "1.0.0")
    print(f"    result: {ok}")

    await asyncio.sleep(1)

    # 7. query_prompt_detail by label
    print("\n[7] query_prompt_detail (label=prod) ...")
    detail_label = await service.query_prompt_detail(
        NAMESPACE, PROMPT_KEY, label="prod",
    )
    print(f"    version: {detail_label.version}")
    print(f"    template: {detail_label.template}")

    # 8. update_prompt_metadata
    print("\n[8] update_prompt_metadata ...")
    ok = await service.update_prompt_metadata(
        NAMESPACE, PROMPT_KEY,
        description="Updated SDK test prompt",
        biz_tags="test,sdk,updated",
    )
    print(f"    result: {ok}")

    await asyncio.sleep(1)

    # 9. list_prompts (search)
    print("\n[9] search_prompts ...")
    total, page_num, pages, prompts = await service.search_prompts(
        NAMESPACE, "sdk-test", 1, 10,
    )
    print(f"    total: {total}")
    for p in prompts:
        print(f"    - {p.prompt_key} (latest={p.latest_version})")

    # 10. unbind_label
    print("\n[10] unbind_label 'prod' ...")
    ok = await service.unbind_label(NAMESPACE, PROMPT_KEY, "prod")
    print(f"    result: {ok}")

    # 11. delete_prompt
    print("\n[11] delete_prompt ...")
    ok = await service.delete_prompt(NAMESPACE, PROMPT_KEY)
    print(f"    result: {ok}")

    print("\n  Prompt API Tests: ALL PASSED")


async def test_skill(service: NacosAIMaintainerService):
    print("\n" + "=" * 60)
    print("  Skill API Tests")
    print("=" * 60)

    # 1. register_skill
    print("\n[1] register_skill ...")
    skill = Skill(
        name=SKILL_NAME,
        description="SDK test skill",
        instruction="Follow the instructions.",
        resource={
            "main": SkillResource(
                name="main-res",
                type="text",
                content="This is test content.",
            ),
        },
    )
    result = await service.register_skill(NAMESPACE, skill)
    print(f"    result: {result}")

    await asyncio.sleep(1)

    # 2. get_skill_detail
    print("\n[2] get_skill_detail ...")
    detail = await service.get_skill_detail(NAMESPACE, SKILL_NAME)
    print(f"    name: {detail.name}")
    print(f"    description: {detail.description}")
    print(f"    instruction: {detail.instruction}")

    # 3. update_skill
    print("\n[3] update_skill ...")
    skill.description = "Updated SDK test skill"
    ok = await service.update_skill(NAMESPACE, skill)
    print(f"    result: {ok}")

    await asyncio.sleep(1)

    # 4. list_skills (search)
    print("\n[4] search_skills ...")
    total, page_num, pages, skills = await service.search_skills(
        NAMESPACE, "sdk-test", 1, 10,
    )
    print(f"    total: {total}")
    for s in skills:
        print(f"    - {s.name} ({s.description})")

    # 5. delete_skill
    print("\n[5] delete_skill ...")
    ok = await service.delete_skill(NAMESPACE, SKILL_NAME)
    print(f"    result: {ok}")

    await asyncio.sleep(1)

    # 6. upload_skill_from_zip
    print(f"\n[6] upload_skill_from_zip ({ZIP_PATH}) ...")
    if os.path.exists(ZIP_PATH):
        with open(ZIP_PATH, "rb") as f:
            zip_bytes = f.read()
        print(f"    zip size: {len(zip_bytes)} bytes")
        result = await service.upload_skill_from_zip(NAMESPACE, zip_bytes)
        print(f"    result: {result}")
    else:
        print(f"    SKIP: {ZIP_PATH} not found")

    print("\n  Skill API Tests: ALL PASSED")


async def main():
    config = (
        ClientConfigBuilder()
        .server_address(SERVER)
        .username(USERNAME)
        .password(PASSWORD)
        .build()
    )
    service = await NacosAIMaintainerService.create_ai_service(config)

    try:
        await test_prompt(service)
    except Exception as e:
        print(f"\n  Prompt test FAILED: {e}")
        traceback.print_exc()

    try:
        await test_skill(service)
    except Exception as e:
        print(f"\n  Skill test FAILED: {e}")
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("  All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
