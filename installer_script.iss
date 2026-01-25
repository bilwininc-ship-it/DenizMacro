[Setup]
AppName=denizv1 Bot
AppVersion=2.0
AppPublisher=denizv1 Team
DefaultDirName={autopf}\denizv1_bot
DefaultGroupName=denizv1 Bot
OutputBaseFilename=denizv1_bot_setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
SetupIconFile=icon.ico

[Languages]
Name: "turkish"; MessagesFile: "compiler:Languages\Turkish.isl"

[Tasks]
Name: "desktopicon"; Description: "Masaüstüne kısayol oluştur"; GroupDescription: "Ek simgeler:"

[Files]
Source: "dist\denizv1_bot.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "NASIL_KULLANILIR.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\denizv1 Bot"; Filename: "{app}\denizv1_bot.exe"
Name: "{group}\Nasıl Kullanılır"; Filename: "{app}\NASIL_KULLANILIR.txt"
Name: "{autodesktop}\denizv1 Bot"; Filename: "{app}\denizv1_bot.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\denizv1_bot.exe"; Description: "denizv1 Bot'u Başlat"; Flags: nowait postinstall skipifsilent

[Code]
function InitializeSetup(): Boolean;
var
  TesseractPath: String;
  ResultCode: Integer;
begin
  Result := True;
  
  // Tesseract kontrol et
  TesseractPath := 'C:\Program Files\Tesseract-OCR\tesseract.exe';
  
  if not FileExists(TesseractPath) then
  begin
    if MsgBox('Tesseract OCR bulunamadı. denizv1 Bot çalışması için gereklidir.' + #13#10#13#10 + 
              'Tesseract indirme sayfasını açmak ister misiniz?', 
              mbConfirmation, MB_YESNO) = IDYES then
    begin
      ShellExec('open', 'https://github.com/UB-Mannheim/tesseract/wiki', '', '', SW_SHOW, ewNoWait, ResultCode);
    end;
  end;
end;