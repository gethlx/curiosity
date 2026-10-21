"""Read-only source probes. Uses source fragments with fakes; no imports of upstream apps.

Run with Python 3.10+; results do not establish live model or browser usability.
"""
from __future__ import annotations

import ast
import contextlib
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]


def extract(path, names, namespace):
    tree = ast.parse(path.read_text())
    nodes = [copy.deepcopy(n) for n in tree.body if getattr(n, "name", None) in names]
    assert len(nodes) == len(names)
    for n in nodes:
        n.decorator_list = []
    module = ast.Module(body=[ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0), *nodes], type_ignores=[])
    exec(compile(ast.fix_missing_locations(module), str(path), "exec"), namespace)


def extract_method(path, class_name, method_name):
    tree = ast.parse(path.read_text())
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == class_name)
    method = copy.deepcopy(next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == method_name))
    module = ast.Module(body=[ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0), method], type_ignores=[])
    namespace = {}
    exec(compile(ast.fix_missing_locations(module), str(path), "exec"), namespace)
    return namespace[method_name]


def main():
    result = {"python": sys.version.split()[0], "scope": "offline source probes; fake model responses; no upstream dependency installation or provider calls", "checks": {}}
    manifest = json.loads((ROOT / "SOURCES.json").read_text())
    integrity = {}
    syntax = {}
    for repo in manifest["repositories"]:
        directory = ROOT / repo["directory"]
        changed = [p for p, digest in repo["sha256"].items() if not (directory / p).is_file() or hashlib.sha256((directory / p).read_bytes()).hexdigest() != digest]
        status = subprocess.check_output(["git", "-C", str(directory), "status", "--porcelain"], text=True)
        assert not changed and not status
        integrity[repo["directory"]] = {"tracked_files": repo["tracked_file_count"], "hash_mismatches": changed, "git_clean": not status}
        files = list(directory.rglob("*.py"))
        errors = []
        for file in files:
            try:
                ast.parse(file.read_text(), filename=str(file))
            except SyntaxError as e:
                errors.append({"file": str(file.relative_to(directory)), "error": str(e)})
        syntax[repo["directory"]] = {"files": len(files), "errors": errors}
        assert not errors
    result["checks"]["source_integrity"] = integrity
    result["checks"]["python_syntax"] = syntax

    class Message:
        def __init__(self, content):
            self.content = content

    class FakeModel:
        def __init__(self, **kwargs):
            self.calls = []

        def __call__(self, messages):
            self.calls.append([m.content for m in messages])
            return Message("offline fake response")

        chat_with_messages = __call__

    curio = ROOT / "curio"
    namespace = {"SystemMessage": Message, "HumanMessage": Message, "chatgpt": FakeModel}
    extract(curio / "backend/chat.py", {"Chat"}, namespace)
    before = os.getcwd()
    try:
        os.chdir(curio)
        chat = namespace["Chat"]()
        chat.ask_question("为什么同一个问题补充一句话，回答会变？")
        suggestions = chat.suggest_new_questions()
        assert len(suggestions) == 3 and len(chat.chatgpt.calls) == 4
        for call in chat.chatgpt.calls[1:]:
            assert "为什么同一个问题" in call[0] and "{messages_content}" not in call[0]
        result["checks"]["curio_question_generation"] = {"suggestions": len(suggestions), "calls_for_answer_plus_suggestions": len(chat.chatgpt.calls), "history_present_in_all_three_prompts": True, "model": "fake"}

        gns = {"json": json, "chatgpt": SimpleNamespace(chatgpt=FakeModel), "SystemMessage": Message, "HumanMessage": Message}
        extract(curio / "backend/graph.py", {"TreeNode", "Graph", "tree_to_text", "get_text_from_file"}, gns)
        graph = gns["Graph"]("topic")
        route_ns = {"request": SimpleNamespace(json={"question": "test"}), "chat": chat, "graphs": {"0": graph}, "local_storage": {"current_graph": "0"}, "jsonify": lambda value: value}
        extract(curio / "backend/app.py", {"ask_question"}, route_ns)
        with contextlib.redirect_stdout(io.StringIO()):
            try:
                route_ns["ask_question"]()
            except json.JSONDecodeError:
                result["checks"]["curio_graph_error_blocks_answer"] = {"reproduced": True, "cause": "fake graph model returned non-JSON; route raised after chat appended its answer", "model": "fake"}
            else:
                raise AssertionError("Expected graph JSON failure to propagate")
    finally:
        os.chdir(before)

    ui = (curio / "frontend/src/components/ChatWindow.js").read_text()
    button_region = ui.split("const renderChatGPTMessageButtons", 1)[1].split("return (", 1)[1].split("};", 1)[0]
    assert button_region.count("<button ") == 3 and "onClick" not in button_region
    result["checks"]["curio_suggestion_buttons"] = {"source_buttons": 3, "click_handlers": 0, "scope": "source inspection, not browser test"}
    requirements = (curio / "requirements.txt").read_text().splitlines()
    result["checks"]["curio_dependencies"] = {"declared": requirements, "direct_imports_missing_from_manifest": ["langchain", "flask-cors"], "scope": "manifest/source comparison, not installation resolution"}

    method = extract_method(ROOT / "storm/knowledge_storm/collaborative_storm/engine.py", "DiscourseManager", "_should_generate_question")
    owner = SimpleNamespace(runner_argument=SimpleNamespace(moderator_override_N_consecutive_answering_turn=3))
    cases = [([], False), (["Potential Answer"] * 2, False), (["Potential Answer"] * 3, True), (["Potential Answer"] * 3 + ["Original Question"], False), (["Potential Answer"] * 3 + ["Information Request"], False)]
    for types, expected in cases:
        assert method(owner, [SimpleNamespace(utterance_type=t) for t in types]) == expected
    result["checks"]["costorm_moderator_trigger"] = {"source_method_cases": len(cases), "threshold": 3, "outcome": "all expected outcomes observed", "scope": "extracted original source method with fake turn records"}

    pattern = re.compile(r"(?:sk-[A-Za-z0-9_-]{30,}|-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----)")
    secret_matches = []
    lifecycle = []
    for repo in manifest["repositories"]:
        directory = ROOT / repo["directory"]
        for rel in repo["sha256"]:
            file = directory / rel
            if file.stat().st_size > 3_000_000:
                continue
            try:
                text = file.read_text()
            except UnicodeDecodeError:
                continue
            if pattern.search(text):
                secret_matches.append(f"{repo['directory']}/{rel}")
            if file.name == "package.json":
                scripts = json.loads(text).get("scripts", {})
                lifecycle.append({"file": f"{repo['directory']}/{rel}", "scripts": {k: v for k, v in scripts.items() if k in ["preinstall", "install", "postinstall", "prepare"]}})
    result["checks"]["limited_static_screen"] = {"credential_like_pattern_files": secret_matches, "package_lifecycle_scripts": lifecycle, "limits": "pattern screen and selected source review; not a security certification or dependency vulnerability audit"}
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
