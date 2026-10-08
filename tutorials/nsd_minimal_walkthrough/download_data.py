"""Download a fixed teaching subset; no AWS account or third-party packages needed."""
import argparse
import csv
import hashlib
import json
import os
import pickle
import re
import shutil
import subprocess
import time
from pathlib import Path
import urllib.parse
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = 'https://natural-scenes-dataset.s3.us-east-2.amazonaws.com/'
DEFAULT_DATA_DIR = Path('/workspace/datasets/nsd_teaching_b') if os.name != 'nt' else HERE / 'data'
DATA_DIR = Path(os.environ.get('NSD_TEACHING_DATA_DIR', str(DEFAULT_DATA_DIR))).expanduser()
MANIFEST = DATA_DIR / 'data_manifest.json'
CAPTIONS = ROOT / 'src/nsd_visuo_semantics/get_embeddings/ms_coco_nsd_captions_test.pkl'


def digest(path, algorithm='sha256'):
    h = hashlib.new(algorithm)
    with path.open('rb') as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def request(url, headers=None, method=None):
    for attempt in range(5):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=headers or {}, method=method), timeout=30)
        except urllib.error.HTTPError as error:
            if error.code not in (408, 429, 500, 502, 503, 504) or attempt == 4:
                raise
            print(f'HTTP retry {attempt + 1}/4: {error.code} {url}', flush=True)
        except (urllib.error.URLError, TimeoutError, ConnectionError) as error:
            if attempt == 4:
                raise
            print(f'Network retry {attempt + 1}/4: {type(error).__name__} {url}', flush=True)
        time.sleep(min(2 ** attempt, 16))


def metadata(key):
    with request(BASE + key, method='HEAD') as r:
        item = {'key': key, 'size': int(r.headers['Content-Length']),
                'etag': r.headers['ETag'].strip('"')}
    if re.fullmatch(r'[0-9a-f]{32}-\d+', item['etag']):
        parts = int(item['etag'].split('-')[1])
        sizes = []
        for part in range(1, parts + 1):
            with request(BASE + key + f'?partNumber={part}', method='HEAD') as r:
                sizes.append(int(r.headers['Content-Length']))
        if sum(sizes) != item['size']:
            raise RuntimeError('Server did not expose valid multipart sizes: ' + key)
        item['part_sizes'] = sizes
    return item


def listing(prefix):
    token = None
    items = []
    ns = {'s': 'http://s3.amazonaws.com/doc/2006-03-01/'}
    while True:
        params = {'list-type': '2', 'prefix': prefix}
        if token:
            params['continuation-token'] = token
        with request(BASE + '?' + urllib.parse.urlencode(params)) as r:
            tree = ET.fromstring(r.read())
        for item in tree.findall('s:Contents', ns):
            items.append({'key': item.findtext('s:Key', namespaces=ns),
                          'size': int(item.findtext('s:Size', namespaces=ns)),
                          'etag': item.findtext('s:ETag', namespaces=ns).strip('"')})
        token = tree.findtext('s:NextContinuationToken', namespaces=ns)
        if not token:
            return items


def verify(path, item):
    if not path.exists() or path.stat().st_size != item['size']:
        return False
    if item.get('sha256'):
        return digest(path) == item['sha256']
    # Only single-part ETags are MD5; never interpret multipart ETags as MD5.
    if re.fullmatch(r'[0-9a-f]{32}', item['etag']):
        return digest(path, 'md5') == item['etag']
    if item.get('part_sizes') and sum(item['part_sizes']) == item['size']:
        # Reconstruct multipart ETag from the actual server-reported part boundaries.
        hashes = []
        with path.open('rb') as f:
            for size in item['part_sizes']:
                remaining = size
                h = hashlib.md5()
                while remaining:
                    block = f.read(min(4 * 1024 * 1024, remaining))
                    if not block:
                        return False
                    h.update(block)
                    remaining -= len(block)
                hashes.append(h.digest())
        calculated = hashlib.md5(b''.join(hashes)).hexdigest() + '-' + str(len(hashes))
        return calculated == item['etag']
    return False


def download(item):
    target = (DATA_DIR / item['key']).resolve()
    if not target.is_relative_to(DATA_DIR.resolve()):
        raise RuntimeError('Unsafe file key outside data directory: ' + item['key'])
    target.parent.mkdir(parents=True, exist_ok=True)
    if verify(target, item):
        print('verified:', item['key'], flush=True)
        return target
    if target.exists():
        raise RuntimeError(f'Existing file failed verification: {target}; keep it and investigate, not overwrite.')
    part = target.with_name(target.name + '.part')
    for attempt in range(5):
        try:
            offset = part.stat().st_size if part.exists() else 0
            if offset > item['size']:
                raise RuntimeError(f'Oversized partial file: {part}')
            if offset < item['size']:
                headers = {'If-Match': '"' + item['etag'] + '"'}
                if offset:
                    headers['Range'] = f'bytes={offset}-'
                with request(BASE + item['key'], headers) as r:
                    append = offset > 0 and r.status == 206
                    if append and not r.headers.get('Content-Range', '').startswith(f'bytes {offset}-'):
                        raise RuntimeError('Incorrect resume response')
                    with part.open('ab' if append else 'wb') as f:
                        last_progress = time.monotonic()
                        while True:
                            chunk = r.read(256 * 1024)
                            if not chunk:
                                break
                            f.write(chunk)
                            if time.monotonic() - last_progress >= 10:
                                print(f"progress: {item['key']} {f.tell():,}/{item['size']:,} bytes", flush=True)
                                last_progress = time.monotonic()
            if not verify(part, item):
                raise RuntimeError(f'Checksum failed: {part}; retained for diagnosis')
            part.replace(target)
            print('downloaded:', item['key'], item['size'], flush=True)
            return target
        except Exception:
            if attempt == 4:
                raise
            time.sleep(min(2 ** attempt, 16))


def initialize(sessions, max_images, workers=4):
    if MANIFEST.exists():
        raise RuntimeError('Manifest exists. Use --download/--verify; do not silently change the sample.')
    behavior = metadata('nsddata/ppdata/subj01/behav/responses.tsv')
    path = download(behavior)
    behavior['sha256'] = digest(path)
    with path.open(encoding='utf-8-sig', newline='') as f:
        rows = list(csv.DictReader(f, delimiter='\t'))
    counts = Counter(int(float(r['73KID'])) for r in rows
                     if 1 <= int(float(r['SESSION'])) <= sessions)
    images = listing('nsddata/stimuli/nsd/shared1000/')
    candidates = [(int(re.search(r'_nsd(\d+)\.png$', x['key']).group(1)), x)
                  for x in images if re.search(r'_nsd(\d+)\.png$', x['key'])]
    # Prefer repeated images, then numeric ID. Selection is written once, never random.
    chosen = sorted((p for p in candidates if p[0] in counts),
                    key=lambda p: (-counts[p[0]], p[0]))[:max_images]
    chosen.sort(key=lambda p: p[0])
    if not chosen:
        raise RuntimeError('No matching image IDs: verify official filename indexing before proceeding.')
    # This repository-owned trusted pickle is read, not an arbitrary downloaded pickle.
    with CAPTIONS.open('rb') as f:
        captions = pickle.load(f)
    if len(captions) != 73000:
        raise RuntimeError('Unexpected repository caption table length')
    selected = [{'nsd_id': i, 'caption_index': i - 1, 'trial_count': counts[i],
                 'image_key': obj['key'], 'captions': captions[i - 1]} for i, obj in chosen]
    beta_keys = [f'nsddata_betas/ppdata/subj01/fsaverage/betas_fithrf_GLMdenoise_RR/{h}.betas_session{s:02d}.mgh'
                 for s in range(1, sessions + 1) for h in ('lh', 'rh')]
    print('Resolving beta file metadata...', flush=True)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        betas = list(pool.map(metadata, beta_keys))
    manifest = {'schema': 1, 'subject': 'subj01', 'sessions': list(range(1, sessions + 1)),
                'selection': 'shared1000 intersect observed trials; highest repeat count then ID; sorted by ID',
                'max_images': max_images, 'caption_source': str(CAPTIONS.relative_to(ROOT)).replace('\\', '/'),
                'caption_source_sha256': digest(CAPTIONS), 'selected': selected,
                'files': [behavior] + [obj for _, obj in chosen] + betas}
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return manifest


def main():
    global DATA_DIR, MANIFEST
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data-dir', type=Path, default=DATA_DIR, help='Data root; Docker default: /workspace/datasets/nsd_teaching_b')
    p.add_argument('--manifest', type=Path, help='Optional pinned manifest; default: DATA_DIR/data_manifest.json')
    p.add_argument('--init', action='store_true', help='Create fixed manifest; downloads behavior metadata first')
    p.add_argument('--sessions', type=int, default=6, choices=range(1, 7))
    p.add_argument('--max-images', type=int, default=200)
    p.add_argument('--workers', type=int, default=4, choices=range(1, 9), help='Concurrent file transfers/metadata queries, 1-8; does not change selected data')
    p.add_argument('--download', action='store_true')
    p.add_argument('--verify', action='store_true')
    p.add_argument('--agreement-confirmed', action='store_true', help='Use only after personally completing NSD access agreement')
    args = p.parse_args()
    DATA_DIR = args.data_dir.expanduser().resolve()
    MANIFEST = args.manifest.expanduser().resolve() if args.manifest else DATA_DIR / 'data_manifest.json'
    if (args.init or args.download) and not args.agreement_confirmed:
        p.error('Complete NSD Data Access Agreement first; then supply --agreement-confirmed.')
    if args.max_images < 1:
        p.error('--max-images must be positive')
    if not args.init and not MANIFEST.exists():
        p.error('No data_manifest.json yet. After agreeing on download location and completing the NSD agreement, initialize once with --init. This command did not download anything.')
    if args.init or args.download:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    print('Data directory:', DATA_DIR, flush=True)
    print('Manifest:', MANIFEST, flush=True)
    m = initialize(args.sessions, args.max_images, args.workers) if args.init else json.loads(MANIFEST.read_text(encoding='utf-8'))
    if digest(CAPTIONS) != m['caption_source_sha256']:
        raise RuntimeError('Caption source differs from pinned manifest')
    total = sum(x['size'] for x in m['files'])
    print(f"{len(m['selected'])} images; {total:,} bytes = {total / 1e9:.3f} GB = {total / 2**30:.3f} GiB", flush=True)
    if args.download:
        needed = 0
        for item in m['files']:
            target = DATA_DIR / item['key']
            part = target.with_name(target.name + '.part')
            if not target.exists():
                needed += max(0, item['size'] - (part.stat().st_size if part.exists() else 0))
        free = shutil.disk_usage(DATA_DIR).free
        if free < needed + 1024 ** 3:
            raise RuntimeError(f'Not enough free space: {free:,} bytes free; need {needed:,} bytes plus 1 GiB reserve.')
        # Worker threads transfer separate files; only this thread edits the manifest.
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            for item, path in zip(m['files'], pool.map(download, m['files'])):
                if not item.get('sha256'):
                    item['sha256'] = digest(path)
                    MANIFEST.write_text(json.dumps(m, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if args.verify:
        failed = [x['key'] for x in m['files'] if not verify(DATA_DIR / x['key'], x)]
        if failed:
            raise RuntimeError('Missing or damaged files: ' + repr(failed))
        print('All pinned files verified.')
        if args.download:
            summary = {'manifest_sha256': digest(MANIFEST), 'data_dir': str(DATA_DIR),
                       'images': len(m['selected']), 'total_bytes': total,
                       'all_files_verified': True}
            try:
                summary['git_commit'] = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
            except (OSError, subprocess.CalledProcessError):
                summary['git_commit'] = 'unavailable'
            report_path = DATA_DIR / 'download_report.json'
            report_path.write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
            print('Download report:', report_path)


if __name__ == '__main__':
    main()
