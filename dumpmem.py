import sys, os, re, struct

pid = sys.argv[1]
NEEDLES = [
    b'cunga-bunga-ved-in',
    b'crypto_utils',
    b'NONCE_LEN',
]
MAX_DUMP_PER_HIT = 16  # limiter le nombre de dumps

def read_regions(pid):
    regions = []
    with open(f'/proc/{pid}/maps') as f:
        for line in f:
            m = re.match(r'([0-9a-f]+)-([0-9a-f]+) (....) \S+ \S+ \S+\s*(.*)', line.strip())
            if not m:
                continue
            start, end, perms, path = m.groups()
            if perms[0] == 'r' and (path == '' or '[heap]' in path or '[stack' in path or 'anonymous' in path):
                regions.append((int(start, 16), int(end, 16), path.strip()))
    return regions

def main():
    regions = read_regions(pid)
    mem = open(f'/proc/{pid}/mem', 'rb', 0)
    hits = {n: 0 for n in NEEDLES}
    dumped = 0
    for start, end, path in regions:
        if end - start > 512 * 1024 * 1024:
            continue
        try:
            mem.seek(start)
            data = mem.read(end - start)
        except (OSError, OverflowError):
            continue
        for needle in NEEDLES:
            if hits[needle] >= 3:
                continue
            idx = 0
            while dumped < MAX_DUMP_PER_HIT * len(NEEDLES):
                idx = data.find(needle, idx)
                if idx < 0:
                    break
                lo = max(0, idx - 8192)
                hi = min(len(data), idx + len(needle) + 8192)
                chunk = data[lo:hi]
                fname = f'memdump_{needle[:12].decode("ascii", "replace").replace("-", "_")}_{hits[needle]}_{start + idx:#x}.bin'
                with open(fname, 'wb') as out:
                    out.write(chunk)
                print(f'{fname}: {len(chunk)} octets autour de {start+idx:#x}')
                hits[needle] += 1
                dumped += 1
                idx += len(needle)
    print('hits:', {k.decode(): v for k, v in hits.items()})

main()
