# -*- mode: python -*-

block_cipher = None


a = Analysis(['pygame_main.py'],
             pathex=['Z:\\home\\lars\\Dev\\Ants'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.zipfiles,
          a.datas,
          a.binaries,
          # exclude_binaries=True,
          name='ants',
          debug=False,
          strip=False,
          upx=True,
          console=True )
'''
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='pygame_main')
'''
