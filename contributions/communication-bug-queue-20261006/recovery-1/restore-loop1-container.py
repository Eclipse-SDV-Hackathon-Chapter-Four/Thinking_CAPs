import pathlib,subprocess,uuid
image=pathlib.Path('/media/jefferson/Lexar/.s-core-build/build-volume-v1.ext4')
if image.stat().st_size!=1099511627776:raise SystemExit('Image size differs')
with image.open('rb') as f:
 f.seek(1080)
 if f.read(2)!=b'\x53\xef':raise SystemExit('Image signature differs')
 f.seek(1128)
 if str(uuid.UUID(bytes=f.read(16)))!='11c42dee-73a3-4c2b-ab42-a0440011d9e0':raise SystemExit('Image UUID differs')
backing=pathlib.Path('/sys/block/loop1/loop/backing_file').read_text().strip()
if backing not in ('/.s-core-build/build-volume-v1.ext4',str(image)):raise SystemExit('Loop backing differs')
subprocess.run(['losetup','--detach','/dev/loop1'],check=True)
subprocess.run(['losetup','/dev/loop1',str(image)],check=True)
print('Existing registered image reattached to loop1')
