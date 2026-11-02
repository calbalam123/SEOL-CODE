'use strict';

const vscode = require('vscode');
const path = require('path');
const fs = require('fs');

function activate(context) {
  let terminal;

  function getRunner(context) {
    if (process.platform !== 'win32') {
      vscode.window.showErrorMessage('현재 독립 실행기는 Windows x64용입니다.');
      return null;
    }
    const runner = path.join(context.extensionPath, 'bin', 'win32-x64', 'seol.exe');
    if (!fs.existsSync(runner)) {
      vscode.window.showErrorMessage('설이코드 독립 실행기가 확장 프로그램에 포함되어 있지 않습니다. 최신 Windows용 VSIX를 다시 설치해 주세요.');
      return null;
    }
    return runner;
  }

  function getTerminal() {
    if (!terminal) terminal = vscode.window.createTerminal({ name: '설이코드 실행' });
    terminal.show(true);
    return terminal;
  }

  const run = vscode.commands.registerCommand('seol.runFile', async () => {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
      vscode.window.showErrorMessage('실행할 설이코드 파일을 먼저 여세요.');
      return;
    }
    const document = editor.document;
    if (!document.fileName.toLowerCase().endsWith('.seol')) {
      vscode.window.showErrorMessage('확장자가 .seol인 설이코드 파일에서 실행해 주세요.');
      return;
    }
    if (document.isDirty && !(await document.save())) return;
    const runner = getRunner(context);
    if (!runner) return;
    const quote = value => '"' + value.replace(/"/g, '\\"') + '"';
    getTerminal().sendText('& ' + quote(runner) + ' ' + quote(document.fileName), true);
  });

  const compileBot = vscode.commands.registerCommand('seol.compileBot', async () => {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
      vscode.window.showErrorMessage('변환할 설이코드 카카오봇 파일을 먼저 여세요.');
      return;
    }
    const document = editor.document;
    if (!document.fileName.toLowerCase().endsWith('.seol')) {
      vscode.window.showErrorMessage('.seol 파일에서 카카오봇 변환을 실행해 주세요.');
      return;
    }
    if (document.isDirty && !(await document.save())) return;
    const runner = getRunner(context);
    if (!runner) return;
    const output = document.fileName.replace(/\.seol$/i, '.js');
    const quote = value => '"' + value.replace(/"/g, '\\"') + '"';
    getTerminal().sendText(
      '& ' + quote(runner) + ' --messengerbot ' + quote(document.fileName) + ' ' + quote(output),
      true
    );
    vscode.window.showInformationMessage('설이코드 카카오봇 변환 명령을 실행했습니다. 완료 메시지를 실행 터미널에서 확인하세요.');
  });

  const output = vscode.commands.registerCommand('seol.openOutput', () => {
    if (terminal) terminal.show();
    else vscode.window.showInformationMessage('아직 실행 터미널이 없습니다. F5를 눌러 코드를 실행하세요.');
  });

  context.subscriptions.push(run, compileBot, output);
}

function deactivate() {
}

module.exports = { activate, deactivate };
