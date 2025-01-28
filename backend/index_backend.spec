# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['index_rear.py','admin_rear.py','change_pwd_controller.py','data_view_rear.py','health_evaluate_rear.py','login_rear.py','model_control_controller.py','model_train_controller.py','results_view_rear.py','/e/Health/health_mamage_demo/data/load_data.py','/e/Health/health_mamage_demo/front/admin.py','/e/Health/health_mamage_demo/front/change_pwd_UI.py','/e/Health/health_mamage_demo/front/component.py','/e/Health/health_mamage_demo/front/data_view.py','/e/Health/health_mamage_demo/front/health_evaluate.py','/e/Health/health_mamage_demo/front/index.py','/e/Health/health_mamage_demo/front/login.py','/e/Health/health_mamage_demo/front/model_control_UI.py','/e/Health/health_mamage_demo/front/model_train_UI.py','/e/Health/health_mamage_demo/front/param_control_UI.py','/e/Health/health_mamage_demo/front/results_view.py','/e/Health/health_mamage_demo/model/classifer_3.py','/e/Health/health_mamage_demo/model/classifer_8.py','/e/Health/health_mamage_demo/model/CNN.py','/e/Health/health_mamage_demo/model/dataProcess.py','/e/Health/health_mamage_demo/model/kfold.py','/e/Health/health_mamage_demo/model/parse_data.py','/e/Health/health_mamage_demo/state/operate_user.py'],
    pathex=['/e/Health/health_mamage_demo'],
    binaries=[],
    datas=[('/e/Health/health_mamage_demo/data','data'),('/e/Health/health_mamage_demo/img','img'),('/e/Health/health_mamage_demo/front','front'),('/e/Health/health_mamage_demo/model','model'),('/e/Health/health_mamage_demo/rear','rear'),('/e/Health/health_mamage_demo/result/model','model'),('/e/Health/health_mamage_demo/result/status','status'),('/e/Health/health_mamage_demo/result/val_img','val_img'),('/e/Health/health_mamage_demo/state','state'),('/e/Health/health_mamage_demo/trainData','trainData')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='index_rear',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='index_rear',
)
