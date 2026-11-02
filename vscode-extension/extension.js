'use strict';

const vscode = require('vscode');
const path = require('path');
const fs = require('fs');

function activate(context) {
  let terminal;

  const run = vscode.commands.registerCommand('seol.runFile', async () => {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
      vscode.window.showErrorMessage('실행할 설이코드 파일을 먼저 여세요.');
      return;
    }

    const document = editor.document;
    if (document.languageId !== 'seol' && !document.fileName.endsWith('.seol')) {
      vscode.window.showErrorMessage('확장자가 .seol인 설이코드 파일에서 실행해 주세요.');
      return;
    }

    if (document.isUntitled) {
      const saved = await document.save();
      if (!saved) return;
    } else if (document.isDirty) {
      const saved = await document.save();
      if (!saved) return;
    }

    const workspace = vscode.workspace.getWorkspaceFolder(document.uri);
    const config = vscode.workspace.getConfiguration('seol', document.uri);
    const configuredRunner = config.get('runnerPath', '').trim();
    const runner = configuredRunner
      ? path.resolve(configuredRunner)
      : (workspace ? path.join(workspace.uri.fsPath, 'seol.py') : '');

    if (!runner || !fs.existsSync(runner)) {
      const choice = await vscode.window.showErrorMessage(
        'seol.py 실행기를 찾지 못했습니다. SEOL-CODE 저장소 폴더를 VS Code로 열거나 seol.runnerPath를 설정하세요.',
        '설치 안내'
      );
      if (choice) {
        vscode.env.openExternal(vscode.Uri.parse('https://github.com/calbalam123/SEOL-CODE'));
      }
      return;
    }

    const python = config.get('pythonPath', 'python').trim() || 'python';
    const quote = value => '"' + value.replace(/"/g, '\\"') + '"';
    if (!terminal) {
      terminal = vscode.window.createTerminal({ name: '설이코드 실행' });
    }
    terminal.show(true);
    terminal.sendText(python + ' ' + quote(runner) + ' ' + quote(document.fileName), true);
  });

  const output = vscode.commands.registerCommand('seol.openOutput', () => {
    if (terminal) terminal.show();
    else vscode.window.showInformationMessage('아직 실행 터미널이 없습니다. F5를 눌러 코드를 실행하세요.');
  });

  context.subscriptions.push(run, output);
}

function deactivate() {
}

module.exports = { activate, deactivate };