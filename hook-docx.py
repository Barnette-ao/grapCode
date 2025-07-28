from PyInstaller.utils.hooks import collect_all

datas, binaries, hiddenimports = collect_all('docx')

hiddenimports.extend([
    'saveToWord',
    'docx.shared',
    'docx.enum.text',
    'docx.oxml',
    'docx.opc',
    'docx.parts'
])