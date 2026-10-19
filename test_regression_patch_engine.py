import hashlib, os, shutil, tempfile, unittest
from patch_engine import apply_patch_transaction, calculate_sha256, find_slot_bounds, SecurityViolationError, ContractViolationError

BASE_HTML = """<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8"><title>App</title></head><body><div id="slot-header"><div class="inner"><span data-role="score-x">0</span></div></div><div id="slot-main"><button data-action="new-game">Novo</button></div><div id="slot-controls"></div></body></html>"""
MANIFEST = {"slots": {"slot-header": ["div", "span"], "slot-main": ["div", "span", "button", "p", "input", "br"], "slot-controls": ["button", "span", "div", "a"]}, "data_roles": ["score-x", "score-o"], "actions": ["reset-game", "new-game"]}

class TestPatchEngineRegression(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.target_file = os.path.join(self.test_dir, "index.html")
        with open(self.target_file, "w", encoding="utf-8") as f: f.write(BASE_HTML)
        self.initial_sha = calculate_sha256(BASE_HTML)
    def tearDown(self): shutil.rmtree(self.test_dir, ignore_errors=True)
    def _assert_rollback(self, msg=""):
        with open(self.target_file, "r", encoding="utf-8") as f: content = f.read()
        self.assertEqual(calculate_sha256(content), self.initial_sha, f"FALHA DE ROLLBACK: {msg}")

    def test_nested_tags_depth_tracking(self):
        o_s, o_e, c_s, c_e = find_slot_bounds(BASE_HTML, "slot-header")
        inner = BASE_HTML[o_e:c_s]
        self.assertIn('<div class="inner">', inner); self.assertIn('</div>', inner)

    def test_conditional_comments_rejection(self):
        cases = ["<div><!--[if IE]><span>Bug</span><![endif]--></div>", "<div><!--[if !IE]>Conteudo<![endif]--></div>", "<!DOCTYPE html><div><span>Teste</span></div>"]
        for payload_frag in cases:
            payload = {"schema_version": "1.0", "base_sha256": self.initial_sha, "mutations": [{"target_slot": "slot-main", "op": "replace_inner", "html": payload_frag}]}
            with self.assertRaises(SecurityViolationError): apply_patch_transaction(self.target_file, payload, MANIFEST)
            self._assert_rollback(f"Cond comment: {payload_frag}")

    def test_encoded_entity_uri_schemes(self):
        evasion_fragments = ["<div><a href='jav&#x09;ascript:alert(1)'>Link</a></div>", "<div><a href='jav&#10;ascript:alert(1)'>Link</a></div>", "<div><a href='&#x6a;&#x61;&#x76;&#x61;&#x73;&#x63;&#x72;&#x69;&#x70;&#x74;:alert(1)'>Link</a></div>", "<div><a href='vb&#x73;cript:msgbox(1)'>Link</a></div>", "<div><a href='data&#x3a;text/html,<script>'>Link</a></div>"]
        for frag in evasion_fragments:
            payload = {"schema_version": "1.0", "base_sha256": self.initial_sha, "mutations": [{"target_slot": "slot-controls", "op": "append_html", "html": frag}]}
            with self.assertRaises(SecurityViolationError): apply_patch_transaction(self.target_file, payload, MANIFEST)
            self._assert_rollback(f"Evasion: {frag}")

    def test_malformed_fragments(self):
        malformed = [("<div><span>Texto</div></span>", "LIFO invertido"), ("<div><p>Paragrafo sem fechar</div>", "<p> sem fechar"), ("<div><input></input></div>", "Fechamento de input"), ("<div><br></br></div>", "Fechamento de br"), ("<span>Texto</span></div>", "Órfã"), ("<div><span>Texto</span>", "Não fechada")]
        for frag, label in malformed:
            payload = {"schema_version": "1.0", "base_sha256": self.initial_sha, "mutations": [{"target_slot": "slot-main", "op": "replace_inner", "html": frag}]}
            with self.assertRaises(ContractViolationError, msg=f"Deveria rejeitar {label}"): apply_patch_transaction(self.target_file, payload, MANIFEST)
            self._assert_rollback(f"Malformado: {label}")

    def test_valid_mutation_success(self):
        valid_fragment = "<div><p>Texto</p><br><input data-role='score-x'></div>"
        payload = {"schema_version": "1.0", "base_sha256": self.initial_sha, "mutations": [{"target_slot": "slot-main", "op": "replace_inner", "html": valid_fragment}]}
        new_sha = apply_patch_transaction(self.target_file, payload, MANIFEST)
        self.assertNotEqual(new_sha, self.initial_sha)
        with open(self.target_file, "r", encoding="utf-8") as f: content = f.read()
        self.assertIn(valid_fragment, content); self.assertEqual(calculate_sha256(content), new_sha)

if __name__ == "__main__": unittest.main()