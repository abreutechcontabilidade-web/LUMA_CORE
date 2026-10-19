"""
patch_engine.py - Motor determinístico de aplicação de patches em slots HTML.
Garante atomicidade, rastreamento de profundidade de slots, validação LIFO estrita,
sanitização de atributos codificados/comentários e rollback fail-closed.
"""
import hashlib
import html
import os
import re
import tempfile
from html.parser import HTMLParser
from typing import Any, Dict, List, Optional, Set, Tuple

class PatchValidationError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.status_code = status_code

class SecurityViolationError(PatchValidationError):
    def __init__(self, message: str): super().__init__(message, status_code=400)

class ContractViolationError(PatchValidationError):
    def __init__(self, message: str): super().__init__(message, status_code=422)

class BaseConflictError(PatchValidationError):
    def __init__(self, message: str): super().__init__(message, status_code=409)

FORBIDDEN_TAGS: Set[str] = {"script", "iframe", "object", "embed", "base", "link", "style"}
HTML5_VOID_TAGS: Set[str] = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr"
}
DISALLOWED_SCHEMES = re.compile(r"^(javascript|data|vbscript):", re.IGNORECASE)
ON_EVENT_ATTR = re.compile(r"^on[a-z]+", re.IGNORECASE)
CONDITIONAL_OR_SPECIAL_COMMENT = re.compile(r"(\[if\s|<!\[cdata\[|-->)", re.IGNORECASE)

def decode_all_entities(val: str) -> str:
    current = val
    for _ in range(5):
        decoded = html.unescape(current)
        if decoded == current: break
        current = decoded
    return re.sub(r"[\x00-\x20\s]+", "", current)

class FragmentLIFOSecurityParser(HTMLParser):
    def __init__(self, allowed_tags: Set[str], allowed_roles: Set[str], allowed_actions: Set[str]):
        super().__init__(convert_charrefs=False)
        self.allowed_tags = allowed_tags
        self.allowed_roles = allowed_roles
        self.allowed_actions = allowed_actions
        self.stack: List[str] = []

    def handle_comment(self, data: str):
        if CONDITIONAL_OR_SPECIAL_COMMENT.search(data):
            raise SecurityViolationError(f"Comentário condicional/especial proibido: {data[:30]}")

    def handle_decl(self, decl: str):
        raise SecurityViolationError(f"Declaração/DOCTYPE proibido no fragmento: {decl[:30]}")

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]):
        tag_lower = tag.lower()
        if tag_lower in FORBIDDEN_TAGS: raise SecurityViolationError(f"Tag proibida: <{tag_lower}>")
        if self.allowed_tags and tag_lower not in self.allowed_tags: raise ContractViolationError(f"Tag <{tag_lower}> não permitida.")
        if tag_lower not in HTML5_VOID_TAGS: self.stack.append(tag_lower)

        for attr_name, attr_val in attrs:
            attr_lower = attr_name.lower()
            raw_val = str(attr_val or "").strip()
            if ON_EVENT_ATTR.match(attr_lower): raise SecurityViolationError(f"Handler inline proibido: {attr_name}")
            cleaned_uri = decode_all_entities(raw_val)
            if attr_lower in {"href", "src", "action", "data"} and DISALLOWED_SCHEMES.match(cleaned_uri): raise SecurityViolationError(f"URL insegura: {raw_val}")
            if attr_lower == "data-role" and self.allowed_roles and raw_val not in self.allowed_roles: raise ContractViolationError(f"data-role '{raw_val}' não declarado.")
            if attr_lower == "data-action" and self.allowed_actions and raw_val not in self.allowed_actions: raise ContractViolationError(f"data-action '{raw_val}' não declarado.")

    def handle_endtag(self, tag: str):
        tag_lower = tag.lower()
        if tag_lower in HTML5_VOID_TAGS: raise ContractViolationError(f"Tag void <{tag_lower}> não deve fechar.")
        if not self.stack: raise ContractViolationError(f"Fechamento órfão: </{tag_lower}>")
        expected_tag = self.stack[-1]
        if expected_tag != tag_lower: raise ContractViolationError(f"LIFO Error: esperado </{expected_tag}>, recebido </{tag_lower}>")
        self.stack.pop()

    def finalize(self):
        if self.stack: raise ContractViolationError(f"Tags não fechadas: {self.stack}")

class SlotBoundaryFinder(HTMLParser):
    def __init__(self, target_id: str):
        super().__init__(convert_charrefs=False)
        self.target_id = target_id
        self.depth = 0
        self.inside_target = False
        self.target_tag: Optional[str] = None
        self.match_count = 0
        self.open_tag_start = -1
        self.open_tag_end = -1
        self.close_tag_start = -1
        self.close_tag_end = -1
        self.raw_html = ""

    def find_bounds(self, raw_html: str) -> Tuple[int, int, int, int]:
        self.raw_html = raw_html
        self.feed(raw_html)
        self.close()
        if self.match_count == 0: raise ContractViolationError(f"Slot #{self.target_id} ausente.")
        if self.match_count > 1: raise ContractViolationError(f"Slot #{self.target_id} duplicado.")
        if self.close_tag_start == -1: raise ContractViolationError(f"Fechamento do slot #{self.target_id} não localizado.")
        return self.open_tag_start, self.open_tag_end, self.close_tag_start, self.close_tag_end

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]):
        tag_lower = tag.lower()
        attr_dict = {k.lower(): v for k, v in attrs}
        if attr_dict.get("id") == self.target_id:
            self.match_count += 1
            self.inside_target = True
            self.target_tag = tag_lower
            self.depth = 1
            line, col = self.getpos()
            self.open_tag_start = self._calc_offset(line, col)
            self.open_tag_end = self.raw_html.find(">", self.open_tag_start) + 1
            return
        if self.inside_target and tag_lower not in HTML5_VOID_TAGS:
            if tag_lower == self.target_tag: self.depth += 1

    def handle_endtag(self, tag: str):
        tag_lower = tag.lower()
        if self.inside_target and tag_lower == self.target_tag:
            self.depth -= 1
            if self.depth == 0:
                line, col = self.getpos()
                self.close_tag_start = self._calc_offset(line, col)
                self.close_tag_end = self.raw_html.find(">", self.close_tag_start) + 1
                self.inside_target = False

    def _calc_offset(self, line: int, col: int) -> int:
        lines = self.raw_html.splitlines(keepends=True)
        return sum(len(lines[i]) for i in range(line - 1)) + col

def calculate_sha256(content: str) -> str: return hashlib.sha256(content.encode("utf-8")).hexdigest()

def find_slot_bounds(html_content: str, slot_id: str) -> Tuple[int, int, int, int]:
    finder = SlotBoundaryFinder(slot_id)
    return finder.find_bounds(html_content)

def apply_patch_transaction(target_filepath: str, patch: Dict[str, Any], manifest: Dict[str, Any], post_smoke_check: Optional[callable] = None) -> str:
    if not isinstance(patch, dict): raise PatchValidationError("Patch deve ser dict")
    base_sha256 = patch.get("base_sha256")
    if not base_sha256 or len(base_sha256) != 64: raise PatchValidationError("base_sha256 inválido")
    mutations = patch.get("mutations")
    if not isinstance(mutations, list) or len(mutations) == 0: raise PatchValidationError("mutations vazio")

    with open(target_filepath, "r", encoding="utf-8") as f: current_content = f.read()
    if calculate_sha256(current_content) != base_sha256: raise BaseConflictError("Hash divergente")

    slots_manifest = manifest.get("slots", {})
    allowed_roles = set(manifest.get("data_roles", []))
    allowed_actions = set(manifest.get("actions", []))
    working_content = current_content

    for mut in mutations:
        target_slot = mut.get("target_slot")
        op = mut.get("op")
        if target_slot in {"html", "body", "head"}: raise ContractViolationError(f"Nó raiz '{target_slot}' proibido.")
        if target_slot not in slots_manifest: raise ContractViolationError(f"Slot '{target_slot}' não homologado.")
        
        allowed_tags_for_slot = set(slots_manifest.get(target_slot, []))
        o_start, o_end, c_start, c_end = find_slot_bounds(working_content, target_slot)

        if op == "set_text":
            safe_text = html.escape(str(mut.get("text", "")))
            working_content = working_content[:o_end] + safe_text + working_content[c_start:]
        elif op in {"replace_inner", "append_html"}:
            fragment = mut.get("html", "")
            if not isinstance(fragment, str): raise PatchValidationError("html deve ser string")
            sec_parser = FragmentLIFOSecurityParser(allowed_tags_for_slot, allowed_roles, allowed_actions)
            sec_parser.feed(fragment); sec_parser.close(); sec_parser.finalize()
            if op == "replace_inner": working_content = working_content[:o_end] + fragment + working_content[c_start:]
            elif op == "append_html": working_content = working_content[:c_start] + fragment + working_content[c_start:]
        else: raise PatchValidationError(f"Op desconhecida: {op}")

    if post_smoke_check and not post_smoke_check(working_content): raise PatchValidationError("Smoke test falhou", 500)

    target_dir = os.path.dirname(os.path.abspath(target_filepath))
    temp_fd, temp_path = tempfile.mkstemp(dir=target_dir, prefix="patch_tmp_")
    try:
        with os.fdopen(temp_fd, "w", encoding="utf-8") as f: f.write(working_content)
        os.replace(temp_path, target_filepath)
    finally:
        if os.path.exists(temp_path): os.remove(temp_path)
    return calculate_sha256(working_content)