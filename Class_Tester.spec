# -*- mode: python -*-

block_cipher = None


a = Analysis(['Class_Tester.py'],
             pathex=['C:\\Users\\Bf4Ft\\Desktop\\Python Projects-20180219T162037Z-001\\Python Projects\\Ship Sidescroller\\Class Testing'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='Class_Tester',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )