import hashlib
import pytest
from patch_engine import (
    apply_patch_transaction,
    ContractViolationError,
    SecurityViolationError,
    BaseConflictError,
)

MANIFEST_COMPLETO = {
    "slots": {
        "slot-main": ["div", "span", "input", "br", "p", "button", "a"],
        "slot-list": ["ul", "li", "span"],
    },
    "data_roles": ["entrada", "saida"],
    "actions": ["salvar"],
}

HTML_BASE = """<!DOCTYPE html>
<html>
<body>
  <div id="slot-main"><div class="nested">Original</div></div>
  <div id="slot-list"></div>
</body>
</html>"""


@pytest.fixture
def base_file(tmp_path):
    target = tmp_path / "app.html"
    target.write_text(HTML_BASE, encoding="utf-8")
    initial_sha = hashlib.sha256(HTML_BASE.encode("utf-8")).hexdigest()
    return {"path": str(target), "sha": initial_sha, "manifest": MANIFEST_COMPLETO}


LIFO_TEST_CASES = [
    # 1. Void elements permitidos e válidos sem fechamento
    (
        "LIFO-01-VOID-VALID",
        "slot-main",
        "replace_inner",
        "<div><span>Nome:</span><br><input data-role='entrada'></div>",
        None,
        "Void tags aceitas normalmente sem fechamento"
    ),
    # 2. Rejeição de fechamento explícito de void element
    (
        "LIFO-02-VOID-EXPLICIT-CLOSE",
        "slot-main",
        "replace_inner",
        "<div><br></br></div>",
        ContractViolationError,
        "Rejeita fechamento explícito </br>"
    ),
    # 3. Aninhamento LIFO cruzado/invertido
    (
        "LIFO-03-CROSS-NESTING",
        "slot-main",
        "replace_inner",
        "<div><span>Texto</div></span>",
        ContractViolationError,
        "Rejeita inversão <span> fechado por </div>"
    ),
    # 4. Tag de fechamento órfã sem abertura
    (
        "LIFO-04-ORPHAN-CLOSE",
        "slot-main",
        "replace_inner",
        "<span>Texto</span></div>",
        ContractViolationError,
        "Rejeita </div> sem tag de abertura"
    ),
    # 5. Tag aberta deixada sem fechar no final do fragmento
    (
        "LIFO-05-UNCLOSED-TAG",
        "slot-main",
        "replace_inner",
        "<div><span>Texto</span>",
        ContractViolationError,
        "Rejeita <div> pendente de fechamento"
    ),
    # 6. Rejeição de <p> sem fechamento (regra de rigor estrutural)
    (
        "LIFO-06-OPTIONAL-P-UNCLOSED",
        "slot-main",
        "replace_inner",
        "<p>Primeiro paragrafo<p>Segundo paragrafo</p>",
        ContractViolationError,
        "Rejeita <p> implícito sem fechamento explícito </p>"
    ),
    # 7. Injeção de protocolo javascript com ofuscação de entidades HTML
    (
        "LIFO-07-OBFUSCATED-URI",
        "slot-main",
        "replace_inner",
        "<div><a href='jav&#x09;ascript:alert(1)'>Link</a></div>",
        SecurityViolationError,
        "Detecta esquema javascript mesmo com entidade hex tab"
    ),
]


@pytest.mark.parametrize("test_id,target_slot,op,fragment,expected_exc,desc", LIFO_TEST_CASES)
def test_lifo_and_rollback(base_file, test_id, target_slot, op, fragment, expected_exc, desc):
    target_path = base_file["path"]
    initial_sha = base_file["sha"]
    manifest = base_file["manifest"]

    payload = {
        "schema_version": "1.0",
        "base_sha256": initial_sha,
        "mutations": [
            {
                "target_slot": target_slot,
                "op": op,
                "html": fragment
            }
        ]
    }

    if expected_exc is None:
        new_sha = apply_patch_transaction(target_path, payload, manifest)
        assert new_sha != initial_sha

        with open(target_path, "r", encoding="utf-8") as f:
            final_content = f.read()

        assert fragment in final_content
        assert hashlib.sha256(final_content.encode("utf-8")).hexdigest() == new_sha
    else:
        with pytest.raises(expected_exc):
            apply_patch_transaction(target_path, payload, manifest)

        # Prova de integridade de Rollback
        with open(target_path, "r", encoding="utf-8") as f:
            content_after = f.read()

        sha_after = hashlib.sha256(content_after.encode("utf-8")).hexdigest()
        assert sha_after == initial_sha, f"FALHA DE ROLLBACK NO CENÁRIO {test_id}: Disco foi modificado!"
