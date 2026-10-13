#!/usr/bin/env python3
"""批量生成离线朗读录音（mp3）。
用法：  pip install edge-tts
        python make_audio.py shizi_20261013_v3.html
会在当前目录生成 audio/ 文件夹（文件名=文本哈希.mp3，与页面里的算法一致）。
把 audio/ 文件夹和 HTML 放在同一目录上传 GitHub 即可。已存在的文件会跳过，可重复运行。"""
import re, json, sys, os, asyncio
import edge_tts
VOICE, RATE = 'zh-CN-XiaoyiNeural', '-15%'   # 活泼女声，语速稍慢；可换 zh-CN-XiaoxiaoNeural
def h(t):
    x = 5381
    for c in t: x = ((x * 33) & 0xffffffff) ^ ord(c)
    n, s = x, ''
    while n: s = '0123456789abcdefghijklmnopqrstuvwxyz'[n % 36] + s; n //= 36
    return s or '0'
src = open(sys.argv[1], encoding='utf8').read()
def arr(name): return json.loads(re.search(r'const ' + name + r'=(\[.*?\]);\n', src, re.S).group(1))
texts = set()
for _, s in arr('L'):
    for t in s.split(' '): texts.add(t[0])
for s in arr('SS'): texts.add(s.replace('/', ''))
for _, line in arr('R'): texts.add(''.join(t[0] for t in line.split(' ')))
for f in arr('FB'): texts.update([f[0].replace('_', '，'), f[0].replace('_', f[1])])
for r in arr('RC'): texts.add(r[0])
texts.update(arr('PROMPTS')); texts.update('一二三四五六七八九十')
os.makedirs('audio', exist_ok=True)
async def one(t, sem):
    f = f'audio/{h(t)}.mp3'
    if os.path.exists(f): return
    async with sem:
        for _ in range(3):
            try: await edge_tts.Communicate(t, VOICE, rate=RATE).save(f); return
            except Exception: await asyncio.sleep(1)
        print('失败：', t)
async def main():
    sem = asyncio.Semaphore(5)
    await asyncio.gather(*(one(t, sem) for t in sorted(texts)))
    print('完成，共', len(texts), '条')
asyncio.run(main())
