import hashlib
import inspect
import os
import re
import shutil
import tempfile
import unittest
from unittest.mock import patch

import patch_engine
from backup_manager import create_timestamped_backup

BASE_HTML = """<!DOCTYPE html>
<html>
<body>
  <div id="slot-header"><span data-role="score-x">0</span></div>
  <div id="slot-main"><button data-action="new-game">Novo</button></div>
  <div id="slot-controls"></div>
</body>
</html>"""

MANIFEST = {
    "slots": {
        "slot-header": ["div", "span"],
        "slot-main": ["div", "span", "button"],
        "slot-controls": ["button", "span", "div"],
    },
    "data_roles": ["score-x", "score-o"],
    "actions": ["reset-game", "new-game"],
}

class TestBackupAndApiCompatibility(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.target_file = os.path.join(self.test_dir, "index.html")
        with open(self.target_file, "w", encoding="utf-8") as f:
            f.write(BASE_HTML)
        self.initial_sha = patch_engine.calculate_sha256(BASE_HTML)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    # 1. Testes de Backup
    def test_backup_preserves_content_and_sha(self):
        backup_path = create_timestamped_backup(self.target_file)
        self.assertIsNotNone(backup_path)
        with open(self.target_file, "rb") as f_orig, open(backup_path, "rb") as f_bak:
            self.assertEqual(f_orig.read(), f_bak.read())
        self.assertEqual(
            patch_engine.calculate_sha256(open(self.target_file).read()),
            patch_engine.calculate_sha256(open(backup_path).read())
        )

    def test_backup_filename_timestamp_format(self):
        timestamp_regex = re.compile(r"\.bak_\d{8}_\d{6}$")
        backup_path = create_timestamped_backup(self.target_file)
        self.assertTrue(timestamp_regex.search(backup_path))

    def test_backup_when_file_does_not_exist(self):
        non_existent = os.path.join(self.test_dir, "nao_existe.html")
        result = create_timestamped_backup(non_existent)
        self.assertIsNone(result)
        self.assertEqual(os.listdir(self.test_dir), ["index.html"])

    # 2. Testes de Compatibilidade de API
    def test_public_api_signatures_and_returns(self):
        sig_sha = inspect.signature(patch_engine.calculate_sha256)
        self.assertEqual(list(sig_sha.parameters.keys()), ["content"])

        sig_bounds = inspect.signature(patch_engine.find_slot_bounds)
        self.assertEqual(list(sig_bounds.parameters.keys()), ["html_content", "slot_id"])
        bounds = patch_engine.find_slot_bounds(BASE_HTML, "slot-header")
        self.assertEqual(len(bounds), 4)

        sig_patch = inspect.signature(patch_engine.apply_patch_transaction)
        self.assertEqual(list(sig_patch.parameters.keys()), ["target_filepath", "patch", "manifest", "post_smoke_check"])

    def test_exception_status_codes(self):
        self.assertEqual(patch_engine.SecurityViolationError("").status_code, 400)
        self.assertEqual(patch_engine.ContractViolationError("").status_code, 422)
        self.assertEqual(patch_engine.BaseConflictError("").status_code, 409)

    # 3. Simulação de Falhas de SO e Rollback
    def test_failure_during_mkstemp_leaves_file_intact(self):
        payload = {
            "schema_version": "1.0",
            "base_sha256": self.initial_sha,
            "mutations": [{"target_slot": "slot-header", "op": "set_text", "text": "Teste"}]
        }
        with patch("tempfile.mkstemp", side_effect=OSError("Disk full")):
            with self.assertRaises(OSError):
                patch_engine.apply_patch_transaction(self.target_file, payload, MANIFEST)

        with open(self.target_file, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertEqual(content, BASE_HTML)
        self.assertEqual(patch_engine.calculate_sha256(content), self.initial_sha)

    def test_failure_during_os_replace_cleans_temp_and_preserves_original(self):
        payload = {
            "schema_version": "1.0",
            "base_sha256": self.initial_sha,
            "mutations": [{"target_slot": "slot-header", "op": "set_text", "text": "Teste"}]
        }
        with patch("os.replace", side_effect=PermissionError("Access Denied")):
            with self.assertRaises(PermissionError):
                patch_engine.apply_patch_transaction(self.target_file, payload, MANIFEST)

        with open(self.target_file, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertEqual(content, BASE_HTML)
        self.assertEqual(patch_engine.calculate_sha256(content), self.initial_sha)
        self.assertEqual(os.listdir(self.test_dir), ["index.html"])

if __name__ == "__main__":
    unittest.main()