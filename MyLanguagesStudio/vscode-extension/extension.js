const vscode=require("vscode");
const cp=require("child_process");
const path=require("path");
function activate(context){
 const output=vscode.window.createOutputChannel("MyLanguages Studio");
 function run(script,args,label){
  const editor=vscode.window.activeTextEditor;
  if(!editor){vscode.window.showErrorMessage("실행할 파일을 먼저 여세요.");return;}
  const file=editor.document.uri.fsPath;
  if(editor.document.isDirty) editor.document.save();
  const root=vscode.workspace.workspaceFolders?.[0]?.uri.fsPath||path.dirname(file);
  const py=vscode.workspace.getConfiguration("mylanguages").get("pythonPath","python");
  output.show(true);output.appendLine("["+label+"] "+file);
  const p=cp.spawn(py,[path.join(context.extensionPath,script),...args(file,root)],{cwd:root});
  p.stdout.on("data",d=>output.append(d.toString()));p.stderr.on("data",d=>output.append(d.toString()));
  p.on("error",e=>output.appendLine("실행기 오류: "+e.message+" (Python 3 설치와 PATH를 확인하세요.)"));
  p.on("close",c=>output.appendLine("종료 코드: "+c));
 }
 context.subscriptions.push(
  vscode.commands.registerCommand("mylanguages.runKorin",()=>run("runtime/korin.py",f=>["실행",f],"Korin")),
  vscode.commands.registerCommand("mylanguages.runNexaDB",()=>run("runtime/nexadb_cli.py",f=>[f],"NexaDB")),
  vscode.commands.registerCommand("mylanguages.buildWeb",()=>{const root=vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;if(!root){vscode.window.showErrorMessage("프로젝트 폴더를 먼저 여세요.");return;}const py=vscode.workspace.getConfiguration("mylanguages").get("pythonPath","python");const p=cp.spawn(py,[path.join(context.extensionPath,"runtime/korin.py"),"웹빌드",root],{cwd:root});output.show(true);p.stdout.on("data",d=>output.append(d.toString()));p.stderr.on("data",d=>output.append(d.toString()));}),output);
}
function deactivate(){}
module.exports={activate,deactivate};