#!/usr/bin/env python3
"""Check evidence restoration, corruption rejection and overwrite protection."""
import gzip
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tarfile
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

    def directory_fixture(self, analysis, member_name='work/native/result.txt'):
        raw = b'Historical fixture result.\n'
        archive = analysis / 'native.tar.gz'
        with tarfile.open(archive, 'w:gz') as stream:
            member = tarfile.TarInfo(member_name)
            member.size = len(raw)
            stream.addfile(member, io.BytesIO(raw))
        return raw, dict(kind='directory', path='work/native', archive=archive.name,
                         archive_sha256=module.file_digest(archive),
                         members=[dict(path=member_name, sha256=module.digest(raw),
                                       mode=0o640, mtime_ns=2000000000)],
                         directories=[dict(path='work/native', mode=0o750, mtime_ns=3000000000),
                                      dict(path='work/native/empty', mode=0o700, mtime_ns=4000000000)])

    def test_nested_archive_restores_with_directory_metadata(self):
        with tempfile.TemporaryDirectory() as temporary:
            analysis = Path(temporary)
            raw, row = self.directory_fixture(analysis)
            (analysis / 'work').mkdir()
            (analysis / 'work/retained.txt').write_text('Keep this evidence.')
            payloads = list(module.payloads(analysis, row))
            self.assertEqual(payloads[0][1], raw)
            target = module.restore(analysis, row)
            self.assertEqual((target / 'result.txt').read_bytes(), raw)
            self.assertEqual(target.stat().st_mode & 0o777, 0o750)
            self.assertEqual(target.stat().st_mtime_ns, 3000000000)
            self.assertTrue((target / 'empty').is_dir())
            self.assertEqual((analysis / 'work/retained.txt').read_text(), 'Keep this evidence.')

    def test_sibling_prefix_and_directory_metadata_cannot_escape_root(self):
        with tempfile.TemporaryDirectory() as temporary:
            analysis = Path(temporary)
            _, row = self.directory_fixture(analysis, 'work/native-other/result.txt')
            with self.assertRaisesRegex(ValueError, 'unsupported'):
                module.restore(analysis, row)
            _, row = self.directory_fixture(analysis)
            row['directories'][0]['path'] = 'work/other'
            with self.assertRaisesRegex(ValueError, 'escapes'):
                module.restore(analysis, row)
            self.assertFalse((analysis / 'work').exists())

    def test_symlink_ancestors_are_rejected_for_archive_and_destination(self):
        for field in ('archive', 'path'):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as temporary:
                analysis = Path(temporary)
                _, row = self.fixture(analysis)
                (analysis / 'linked').symlink_to(analysis, target_is_directory=True)
                row[field] = 'linked/' + row[field]
                with self.assertRaisesRegex(ValueError, 'symlink'):
                    module.restore(analysis, row)
                self.assertFalse((analysis / 'report.json').exists())

    def test_legacy_and_new_indexes_merge_and_duplicates_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            analysis = Path(temporary)
            for date, name in [('20261112', 'legacy'), ('20261113', 'nested/native')]:
                path = analysis / f'cleanup-handoff-{date}.json'
                path.write_text(json.dumps(dict(status='complete', records=[dict(path=name)])))
            self.assertEqual([r['path'] for r in module.records(analysis)], ['legacy', 'nested/native'])
            path.write_text(json.dumps(dict(status='complete', records=[dict(path='legacy')])))
            with self.assertRaisesRegex(ValueError, 'Duplicate'):
                module.records(analysis)
            path.write_text(json.dumps(dict(status='pending', records=[])))
            with self.assertRaisesRegex(ValueError, 'not complete'):
                module.records(analysis)


if __name__ == '__main__':
    unittest.main()
