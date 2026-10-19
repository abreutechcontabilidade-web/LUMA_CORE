"""
patch_engine.py - Motor determinístico com rastreamento de profundidade e validação LIFO estrita.
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
    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class ContractViolationError(PatchValidationError):
    def __init__(self, message: str):
        super().__init__(message, status_code=422)


class BaseConflictError(PatchValidationError):
    def __init__(self, message: str):
        super().__init__(message, status_code=409)


FORBIDDEN_TAGS: Set[str] = {"script", "iframe", "object", "embed", "base", "link", "style"}
HTML5_VOID_TAGS: Set[str] = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr"
}
DISALLOWED_SCHEMES = re.compile(r"^(javascript|data|vbscript):", re.IGNORECASE)
ON_EVENT_ATTR = re.compile(r"^on[a-z]+", re.IGNORECASE)


class FragmentLIFOSecurityParser(HTMLParser):
    """
    Parser para fragmentos. Exige fechamento explícito de todas as tags não-void.
    Garante fechamento estrito em ordem LIFO e ausência de injeções inline/protocolos maliciosos.
    """
    def __init__(self, allowed_tags: Set[str], allowed_roles: Set[str], allowed_actions: Set[str]):
        super().__init__(convert_charrefs=False)
        self.allowed_tags = allowed_tags
        self.allowed_roles = allowed_roles
        self.allowed_actions = allowed_actions
        self.stack: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]):
        tag_lower = tag.lower()

        if tag_lower in FORBIDDEN_TAGS:
            raise SecurityViolationError(f"Tag proibida encontrada: <{tag_lower}>")

        if self.allowed_tags and tag_lower not in self.allowed_tags:
            raise ContractViolationError(f"Tag <{tag_lower}> não permitida para este slot")

        if tag_lower not in HTML5_VOID_TAGS:
            self.stack.append(tag_lower)

        for attr_name, attr_val in attrs:
            attr_lower = attr_name.lower()
            raw_val = str(attr_val or "").strip()
            # Decodifica entidades antes de testar protocolos maliciosos
            decoded_val = html.unescape(raw_val).replace("\t", "").replace("\n", "").replace("\r", "")

            if ON_EVENT_ATTR.match(attr_lower):
                raise SecurityViolationError(f"Handler de evento inline proibido: {attr_name}")

            if attr_lower in {"href", "src", "action"} and DISALLOWED_SCHEMES.match(decoded_val):
                raise SecurityViolationError(f"Esquema de URL inseguro: {raw_val}")

            if attr_lower == "data-role" and self.allowed_roles:
                if raw_val not in self.allowed_roles:
                    raise ContractViolationError(f"data-role '{raw_val}' não declarado no manifesto")

            if attr_lower == "data-action" and self.allowed_actions:
                if raw_val not in self.allowed_actions:
                    raise ContractViolationError(f"data-action '{raw_val}' não declarado no manifesto")

    def handle_endtag(self, tag: str):
        tag_lower = tag.lower()

        if tag_lower in HTML5_VOID_TAGS:
            raise ContractViolationError(f"Tag void <{tag_lower}> não deve possuir tag de fechamento </{tag_lower}>")

        if not self.stack:
            raise ContractViolationError(f"Tag de fechamento órfã sem abertura correspondente: </{tag_lower}>")

        expected_tag = self.stack[-1]
        if expected_tag != tag_lower:
            raise ContractViolationError(
                f"Erro de aninhamento LIFO: esperado </{expected_tag}>, mas recebido </{tag_lower}>"
            )

        self.stack.pop()

    def finalize(self):
        if self.stack:
            raise ContractViolationError(f"Tags não fechadas ao término do fragmento: {self.stack}")


class SlotBoundaryFinder(HTMLParser):
    """
    Rastreia com precisão os limites de início e fim de um slot no documento base,
    mesmo que o slot contenha elementos filhos do mesmo tipo de tag.
    """
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

        if self.match_count == 0:
            raise ContractViolationError(f"Slot #{self.target_id} não encontrado no HTML base", 422)
        if self.match_count > 1:
            raise ContractViolationError(f"Ambiguidade: Slot #{self.target_id} duplicado no HTML base", 422)
        if self.close_tag_start == -1:
            raise ContractViolationError(f"Fechamento do slot #{self.target_id} não localizado", 422)

        return self.open_tag_start, self.open_tag_end, self.close_tag_start, self.close_tag_end

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]):
        tag_lower = tag.lower()
        attr_dict = {k.lower(): v for k, v in attrs}

        if attr_dict.get("id") == self.target_id:
            self.match_count += 1
            self.inside_target = True
            self.target_tag = tag_lower
            self.depth = 1
            # Calcula os índices baseados no ponteiro do parser
            line, offset = self.getpos()
            # Encontra a posição exata da abertura da tag
            self.open_tag_start = self._calculate_raw_offset(line, offset)
            # Encontra o fim do '>' desta tag de abertura
            self.open_tag_end = self.raw_html.find(">", self.open_tag_start) + 1
            return

        if self.inside_target and tag_lower not in HTML5_VOID_TAGS:
            if tag_lower == self.target_tag:
                self.depth += 1

    def handle_endtag(self, tag: str):
        tag_lower = tag.lower()
        if self.inside_target and tag_lower == self.target_tag:
            self.depth -= 1
            if self.depth == 0:
                line, offset = self.getpos()
                self.close_tag_start = self._calculate_raw_offset(line, offset)
                self.close_tag_end = self.raw_html.find(">", self.close_tag_start) + 1
                self.inside_target = False

    def _calculate_raw_offset(self, line: int, col: int) -> int:
        lines = self.raw_html.splitlines(keepends=True)
        return sum(len(lines[i]) for i in range(line - 1)) + col


def calculate_sha256(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def apply_patch_transaction(
    target_filepath: str,
    patch: Dict[str, Any],
    manifest: Dict[str, Any],
    post_smoke_check: Optional[callable] = None
) -> str:
    if not isinstance(patch, dict):
        raise PatchValidationError("Patch payload deve ser um objeto JSON", 400)

    base_sha256 = patch.get("base_sha256")
    if not base_sha256 or not isinstance(base_sha256, str) or len(base_sha256) != 64:
        raise PatchValidationError("base_sha256 inválido ou ausente", 400)

    mutations = patch.get("mutations")
    if not isinstance(mutations, list) or len(mutations) == 0:
        raise PatchValidationError("mutations deve conter pelo menos uma operação", 400)

    with open(target_filepath, "r", encoding="utf-8") as f:
        original_content = f.read()

    current_sha256 = calculate_sha256(original_content)
    if current_sha256 != base_sha256:
        raise BaseConflictError(f"Conflito de Base: SHA esperado {base_sha256}, atual {current_sha256}")

    slots_manifest = manifest.get("slots", {})
    allowed_roles = set(manifest.get("data_roles", []))
    allowed_actions = set(manifest.get("actions", []))

    working_content = original_content

    for mut in mutations:
        target_slot = mut.get("target_slot")
        op = mut.get("op")

        if target_slot in {"html", "body", "head"}:
            raise ContractViolationError(f"Tentativa de mutação direta do nó raiz '{target_slot}'", 403)

        if target_slot not in slots_manifest:
            raise ContractViolationError(f"Slot target '{target_slot}' não homologado no manifesto", 422)

        allowed_tags = set(slots_manifest.get(target_slot, []))

        # Rastreamento robusto dos limites do slot
        finder = SlotBoundaryFinder(target_slot)
        o_start, o_end, c_start, c_end = finder.find_bounds(working_content)

        if op == "set_text":
            text_val = str(mut.get("text", ""))
            safe_text = html.escape(text_val)
            working_content = working_content[:o_end] + safe_text + working_content[c_start:]

        elif op in {"replace_inner", "append_html"}:
            fragment = mut.get("html", "")
            if not isinstance(fragment, str):
                raise PatchValidationError("Campo 'html' deve ser string", 400)

            # Validação LIFO e segurança
            parser = FragmentLIFOSecurityParser(allowed_tags, allowed_roles, allowed_actions)
            parser.feed(fragment)
            parser.close()
            parser.finalize()

            if op == "replace_inner":
                working_content = working_content[:o_end] + fragment + working_content[c_start:]
            elif op == "append_html":
                working_content = working_content[:c_start] + fragment + working_content[c_start:]
        else:
            raise PatchValidationError(f"Operação '{op}' desconhecida", 400)

    if post_smoke_check and not post_smoke_check(working_content):
        raise PatchValidationError("Falha no smoke test pós-mutação", 500)

    # Substituição Atômica com Rollback por Isolamento em Arquivo Temporário
    target_dir = os.path.dirname(os.path.abspath(target_filepath))
    temp_fd, temp_path = tempfile.mkstemp(dir=target_dir, prefix="luma_patch_", suffix=".tmp")
    try:
        with os.fdopen(temp_fd, "w", encoding="utf-8") as f:
            f.write(working_content)
        os.replace(temp_path, target_filepath)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    return calculate_sha256(working_content)
