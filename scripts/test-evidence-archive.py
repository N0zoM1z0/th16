#!/usr/bin/env python3
"""Check evidence restoration, corruption rejection and overwrite protection."""
import gzip
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest

_spec = importlib.util.spec_from_file_location('evidence_archive', Path(__file__).with_name('evidence-archive.py'))
module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(module)


class EvidenceArchiveControls(unittest.TestCase):
    def fixture(self, analysis):
        raw = b'Preserved historical evidence.\n'
        archive = analysis / 'report.json.gz'
        with gzip.open(archive, 'wb') as stream:
            stream.write(raw)
        return raw, dict(kind='file', path='report.json', archive=archive.name,
                         archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),
                         sha256=hashlib.sha256(raw).hexdigest(), mode=0o644, mtime_ns=1000000000)

    def test_exact_bytes_restore_and_existing_evidence_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as temporary:
            analysis = Path(temporary)
            raw, row = self.fixture(analysis)
            target = module.restore(analysis, row)
            self.assertEqual(target.read_bytes(), raw)
            with self.assertRaisesRegex(ValueError, 'already exists'):
                module.restore(analysis, row)
            self.assertEqual(target.read_bytes(), raw)

    def test_corrupt_archive_and_decompressed_checksum_are_rejected(self):
        for key in ('archive_sha256', 'sha256'):
            with tempfile.TemporaryDirectory() as temporary:
                analysis = Path(temporary)
                _, row = self.fixture(analysis)
                row[key] = '0' * 64
                with self.assertRaisesRegex(ValueError, 'checksum'):
                    module.restore(analysis, row)
                self.assertFalse((analysis / 'report.json').exists())

    def test_escaping_paths_are_rejected(self):
        for name in ('../outside', '/absolute', 'valid/../../outside'):
            with self.subTest(name=name), self.assertRaises(ValueError):
                module.safe_path(name)


if __name__ == '__main__':
    unittest.main()
