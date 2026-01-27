using System;
using System.Drawing;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Forms;
using DenizMacroBot.Models;
using DenizMacroBot.Services;
using DenizMacroBot.Utils;

namespace DenizMacroBot
{
    public partial class Form1 : Form
    {
        private const string ConfigPath = "config.json";
        
        private BotConfig _config = null!;
        private OCRService? _ocrService;
        private ScreenCaptureService? _captureService;
        private CancellationTokenSource? _cancellationTokenSource;
        private bool _isRunning;
 

        // UI Controls
        private Button _btnSelectAllRegions = null!;
        private Button _btnStart = null!;
        private Button _btnStop = null!;
        private TextBox _txtLog = null!;
        private Label _lblStatus = null!;
        private Panel _statusPanel = null!;
        private GroupBox _configGroup = null!;
        private Label _lblGreenCodeRegion = null!;
        private Label _lblButton1Region = null!;
        private Label _lblButton2Region = null!;
        private Label _lblButton3Region = null!;
        private Label _lblButton4Region = null!;
        private NumericUpDown _numDelayMin = null!;
        private NumericUpDown _numDelayMax = null!;
        private Label _lblDelayMin = null!;
        private Label _lblDelayMax = null!;
        private Label _lblSelectionProgress = null!;

        public Form1()
        {
            InitializeComponent();
            InitializeCustomUI();
            LoadConfiguration();
            InitializeServices();
        }

        private void InitializeCustomUI()
        {
            // Form settings
            Text = "DenizMacroBot - Bot Doğrulama Otomasyonu";
            Size = new Size(850, 750);
            BackColor = Color.FromArgb(30, 30, 30);
            ForeColor = Color.White;
            Font = new Font("Segoe UI", 9.5f);
            StartPosition = FormStartPosition.CenterScreen;
            MinimumSize = new Size(700, 600);

            // Status panel at top
            _statusPanel = new Panel
            {
                Location = new Point(0, 0),
                Size = new Size(ClientSize.Width, 60),
                BackColor = Color.FromArgb(20, 20, 20),
                Dock = DockStyle.Top
            };
            Controls.Add(_statusPanel);

            _lblStatus = new Label
            {
                Text = "● HAZIR",
                ForeColor = Color.Gray,
                Font = new Font("Segoe UI", 14, FontStyle.Bold),
                Location = new Point(20, 18),
                AutoSize = true
            };
            _statusPanel.Controls.Add(_lblStatus);

            // Configuration group
            _configGroup = new GroupBox
            {
                Text = "⚙ Bölge Konfigürasyonu",
                ForeColor = Color.LightGray,
                Location = new Point(20, 80),
                Size = new Size(790, 280),
                Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right,
                Font = new Font("Segoe UI", 10, FontStyle.Bold)
            };
            Controls.Add(_configGroup);

            // Selection progress label
            _lblSelectionProgress = new Label
            {
                Text = "Bölgeleri seçmek için butona tıklayın",
                Location = new Point(20, 30),
                Size = new Size(750, 25),
                ForeColor = Color.Orange,
                Font = new Font("Segoe UI", 10, FontStyle.Bold)
            };
            _configGroup.Controls.Add(_lblSelectionProgress);

            // Region status labels
            _lblGreenCodeRegion = new Label
            {
                Text = "❌ Yeşil Kod Bölgesi: Seçilmedi",
                Location = new Point(20, 65),
                Size = new Size(750, 22),
                ForeColor = Color.OrangeRed,
                Font = new Font("Segoe UI", 9.5f)
            };
            _configGroup.Controls.Add(_lblGreenCodeRegion);

            _lblButton1Region = new Label
            {
                Text = "❌ 1. Buton Bölgesi: Seçilmedi",
                Location = new Point(20, 92),
                Size = new Size(750, 22),
                ForeColor = Color.OrangeRed,
                Font = new Font("Segoe UI", 9.5f)
            };
            _configGroup.Controls.Add(_lblButton1Region);

            _lblButton2Region = new Label
            {
                Text = "❌ 2. Buton Bölgesi: Seçilmedi",
                Location = new Point(20, 119),
                Size = new Size(750, 22),
                ForeColor = Color.OrangeRed,
                Font = new Font("Segoe UI", 9.5f)
            };
            _configGroup.Controls.Add(_lblButton2Region);

            _lblButton3Region = new Label
            {
                Text = "❌ 3. Buton Bölgesi: Seçilmedi",
                Location = new Point(20, 146),
                Size = new Size(750, 22),
                ForeColor = Color.OrangeRed,
                Font = new Font("Segoe UI", 9.5f)
            };
            _configGroup.Controls.Add(_lblButton3Region);

            _lblButton4Region = new Label
            {
                Text = "❌ 4. Buton Bölgesi: Seçilmedi",
                Location = new Point(20, 173),
                Size = new Size(750, 22),
                ForeColor = Color.OrangeRed,
                Font = new Font("Segoe UI", 9.5f)
            };
            _configGroup.Controls.Add(_lblButton4Region);

            // Select All Regions button
            _btnSelectAllRegions = new Button
            {
                Text = "📐 TÜM BÖLGELERİ HIZLICA SEÇ (1-5)",
                Location = new Point(20, 210),
                Size = new Size(750, 50),
                BackColor = Color.FromArgb(0, 120, 215),
                ForeColor = Color.White,
                FlatStyle = FlatStyle.Flat,
                Font = new Font("Segoe UI", 11, FontStyle.Bold),
                Cursor = Cursors.Hand
            };
            _btnSelectAllRegions.FlatAppearance.BorderSize = 0;
            _btnSelectAllRegions.Click += BtnSelectAllRegions_Click;
            _configGroup.Controls.Add(_btnSelectAllRegions);

            // Delay configuration group
            var delayGroup = new GroupBox
            {
                Text = "⏱ Zamanlama Ayarları",
                ForeColor = Color.LightGray,
                Location = new Point(20, 380),
                Size = new Size(790, 80),
                Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right,
                Font = new Font("Segoe UI", 10, FontStyle.Bold)
            };
            Controls.Add(delayGroup);

            _lblDelayMin = new Label
            {
                Text = "Min Gecikme (sn):",
                Location = new Point(20, 35),
                Size = new Size(140, 20),
                ForeColor = Color.LightGray,
                Font = new Font("Segoe UI", 9.5f)
            };
            delayGroup.Controls.Add(_lblDelayMin);

            _numDelayMin = new NumericUpDown
            {
                Location = new Point(160, 32),
                Size = new Size(80, 25),
                Minimum = 1,
                Maximum = 60,
                Value = 4,
                BackColor = Color.FromArgb(45, 45, 45),
                ForeColor = Color.White
            };
            _numDelayMin.ValueChanged += (s, e) => _config.DelayMin = (int)_numDelayMin.Value * 1000;
            delayGroup.Controls.Add(_numDelayMin);

            _lblDelayMax = new Label
            {
                Text = "Max Gecikme (sn):",
                Location = new Point(280, 35),
                Size = new Size(140, 20),
                ForeColor = Color.LightGray,
                Font = new Font("Segoe UI", 9.5f)
            };
            delayGroup.Controls.Add(_lblDelayMax);

            _numDelayMax = new NumericUpDown
            {
                Location = new Point(420, 32),
                Size = new Size(80, 25),
                Minimum = 1,
                Maximum = 60,
                Value = 14,
                BackColor = Color.FromArgb(45, 45, 45),
                ForeColor = Color.White
            };
            _numDelayMax.ValueChanged += (s, e) => _config.DelayMax = (int)_numDelayMax.Value * 1000;
            delayGroup.Controls.Add(_numDelayMax);

            // Control buttons
            _btnStart = new Button
            {
                Text = "▶ BOT'U BAŞLAT",
                Location = new Point(20, 480),
                Size = new Size(300, 55),
                BackColor = Color.FromArgb(16, 124, 16),
                ForeColor = Color.White,
                FlatStyle = FlatStyle.Flat,
                Font = new Font("Segoe UI", 13, FontStyle.Bold),
                Cursor = Cursors.Hand,
                Enabled = false
            };
            _btnStart.FlatAppearance.BorderSize = 0;
            _btnStart.Click += BtnStart_Click;
            Controls.Add(_btnStart);

            _btnStop = new Button
            {
                Text = "■ BOT'U DURDUR",
                Location = new Point(340, 480),
                Size = new Size(300, 55),
                BackColor = Color.FromArgb(180, 0, 0),
                ForeColor = Color.White,
                FlatStyle = FlatStyle.Flat,
                Font = new Font("Segoe UI", 13, FontStyle.Bold),
                Cursor = Cursors.Hand,
                Enabled = false
            };
            _btnStop.FlatAppearance.BorderSize = 0;
            _btnStop.Click += BtnStop_Click;
            Controls.Add(_btnStop);

            // Activity log
            Label lblLog = new Label
            {
                Text = "📋 Aktivite Günlüğü",
                Location = new Point(20, 555),
                Size = new Size(150, 20),
                ForeColor = Color.LightGray,
                Font = new Font("Segoe UI", 10, FontStyle.Bold)
            };
            Controls.Add(lblLog);

            _txtLog = new TextBox
            {
                Location = new Point(20, 580),
                Size = new Size(790, 130),
                Multiline = true,
                ReadOnly = true,
                BackColor = Color.FromArgb(20, 20, 20),
                ForeColor = Color.LightGreen,
                Font = new Font("Consolas", 9),
                ScrollBars = ScrollBars.Vertical,
                Anchor = AnchorStyles.Top | AnchorStyles.Bottom | AnchorStyles.Left | AnchorStyles.Right
            };
            Controls.Add(_txtLog);
        }

        private void LoadConfiguration()
        {
            _config = BotConfig.LoadFromFile(ConfigPath);
            
            _numDelayMin.Value = _config.DelayMin / 1000;
            _numDelayMax.Value = _config.DelayMax / 1000;

            UpdateRegionLabels();
            CheckIfAllRegionsConfigured();
        }

        private void InitializeServices()
        {
            try
            {
                _captureService = new ScreenCaptureService();
                _ocrService = new OCRService(_config.TesseractDataPath);
                
                if (_ocrService.Initialize())
                {
                    Log("✓ OCR motoru başarıyla başlatıldı");
                }
            }
            catch (Exception ex)
            {
                Log($"✗ Servisler başlatılamadı: {ex.Message}");
                MessageBox.Show(
                    $"OCR motoru başlatılamadı.\n\nHata: {ex.Message}\n\nLütfen tessdata klasörünün doğru konumda olduğundan emin olun: {_config.TesseractDataPath}",
                    "Başlatma Hatası",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Error
                );
            }
        }

        private async void BtnSelectAllRegions_Click(object? sender, EventArgs e)
        {
            _btnSelectAllRegions.Enabled = false;
            _lblSelectionProgress.Text = "🎯 HAZIR! İlk bölgeyi (Yeşil Kod) seçmek için ekranda alanı çizin...";
            _lblSelectionProgress.ForeColor = Color.Yellow;

            await Task.Delay(1500); // Kullanıcıya okuma zamanı ver

            // Region 1: Green Code
            _lblSelectionProgress.Text = "🟢 1/5: YEŞİL KOD bölgesini seçin...";
            var region1 = RegionSelector.SelectRegion();
            if (region1.HasValue)
            {
                _config.GreenCodeRegion.SetFromRectangle(region1.Value);
                UpdateRegionLabel(_lblGreenCodeRegion, "Yeşil Kod Bölgesi", region1.Value);
                Log($"✓ Yeşil kod bölgesi seçildi: {region1.Value.Width}×{region1.Value.Height}");
            }
            else
            {
                ResetRegionSelection();
                return;
            }

            await Task.Delay(500);

            // Region 2: Button 1
            _lblSelectionProgress.Text = "⬜ 2/5: 1. BUTON bölgesini seçin...";
            var region2 = RegionSelector.SelectRegion();
            if (region2.HasValue)
            {
                _config.Button1Region.SetFromRectangle(region2.Value);
                UpdateRegionLabel(_lblButton1Region, "1. Buton Bölgesi", region2.Value);
                Log($"✓ 1. buton bölgesi seçildi: {region2.Value.Width}×{region2.Value.Height}");
            }
            else
            {
                ResetRegionSelection();
                return;
            }

            await Task.Delay(500);

            // Region 3: Button 2
            _lblSelectionProgress.Text = "⬜ 3/5: 2. BUTON bölgesini seçin...";
            var region3 = RegionSelector.SelectRegion();
            if (region3.HasValue)
            {
                _config.Button2Region.SetFromRectangle(region3.Value);
                UpdateRegionLabel(_lblButton2Region, "2. Buton Bölgesi", region3.Value);
                Log($"✓ 2. buton bölgesi seçildi: {region3.Value.Width}×{region3.Value.Height}");
            }
            else
            {
                ResetRegionSelection();
                return;
            }

            await Task.Delay(500);

            // Region 4: Button 3
            _lblSelectionProgress.Text = "⬜ 4/5: 3. BUTON bölgesini seçin...";
            var region4 = RegionSelector.SelectRegion();
            if (region4.HasValue)
            {
                _config.Button3Region.SetFromRectangle(region4.Value);
                UpdateRegionLabel(_lblButton3Region, "3. Buton Bölgesi", region4.Value);
                Log($"✓ 3. buton bölgesi seçildi: {region4.Value.Width}×{region4.Value.Height}");
            }
            else
            {
                ResetRegionSelection();
                return;
            }

            await Task.Delay(500);

            // Region 5: Button 4
            _lblSelectionProgress.Text = "⬜ 5/5: 4. BUTON bölgesini seçin...";
            var region5 = RegionSelector.SelectRegion();
            if (region5.HasValue)
            {
                _config.Button4Region.SetFromRectangle(region5.Value);
                UpdateRegionLabel(_lblButton4Region, "4. Buton Bölgesi", region5.Value);
                Log($"✓ 4. buton bölgesi seçildi: {region5.Value.Width}×{region5.Value.Height}");
            }
            else
            {
                ResetRegionSelection();
                return;
            }

            // All regions selected successfully
            _config.SaveToFile(ConfigPath);
            _lblSelectionProgress.Text = "✅ TÜM BÖLGELER BAŞARIYLA SEÇİLDİ! Bot artık kullanıma hazır.";
            _lblSelectionProgress.ForeColor = Color.LightGreen;
            _btnSelectAllRegions.Enabled = true;
            _btnStart.Enabled = true;
            
            Log("========================================");
            Log("✅ KURULUM TAMAMLANDI!");
            Log("Şimdi oyunu kapatıp botu başlatabilirsiniz.");
            Log("========================================");
        }

        private void ResetRegionSelection()
        {
            _lblSelectionProgress.Text = "❌ Bölge seçimi iptal edildi. Tekrar denemek için butona tıklayın.";
            _lblSelectionProgress.ForeColor = Color.Red;
            _btnSelectAllRegions.Enabled = true;
            Log("⚠ Bölge seçimi iptal edildi");
        }

        private void UpdateRegionLabel(Label label, string name, Rectangle region)
        {
            label.Text = $"✅ {name}: {region.Width}×{region.Height} @ ({region.X}, {region.Y})";
            label.ForeColor = Color.LightGreen;
        }

        private void UpdateRegionLabels()
        {
            if (_config.GreenCodeRegion.IsValid)
                UpdateRegionLabel(_lblGreenCodeRegion, "Yeşil Kod Bölgesi", _config.GreenCodeRegion.Rectangle);
            
            if (_config.Button1Region.IsValid)
                UpdateRegionLabel(_lblButton1Region, "1. Buton Bölgesi", _config.Button1Region.Rectangle);
            
            if (_config.Button2Region.IsValid)
                UpdateRegionLabel(_lblButton2Region, "2. Buton Bölgesi", _config.Button2Region.Rectangle);
            
            if (_config.Button3Region.IsValid)
                UpdateRegionLabel(_lblButton3Region, "3. Buton Bölgesi", _config.Button3Region.Rectangle);
            
            if (_config.Button4Region.IsValid)
                UpdateRegionLabel(_lblButton4Region, "4. Buton Bölgesi", _config.Button4Region.Rectangle);
        }

        private void CheckIfAllRegionsConfigured()
        {
            if (_config.AllRegionsConfigured)
            {
                _lblSelectionProgress.Text = "✅ Tüm bölgeler yapılandırıldı! Bot başlatmaya hazır.";
                _lblSelectionProgress.ForeColor = Color.LightGreen;
                _btnStart.Enabled = true;
            }
        }

        private async void BtnStart_Click(object? sender, EventArgs e)
        {
            if (_isRunning) return;

            _isRunning = true;
            _btnStart.Enabled = false;
            _btnStop.Enabled = true;
            _btnSelectAllRegions.Enabled = false;
            _lblStatus.Text = "● ÇALIŞIYOR";
            _lblStatus.ForeColor = Color.Lime;

            _cancellationTokenSource = new CancellationTokenSource();
            
            Log("========================================");
            Log("🤖 Bot başlatıldı - Ekran izleniyor...");
            Log("⚡ HIZLI MOD: Her 0.5 saniyede kontrol edilecek");
            Log("🔍 OCR: 3x büyütülmüş görüntü, gelişmiş tanıma");
            Log("Bot doğrulaması tespit edildiğinde ANINDA işlem yapılacak.");
            Log("========================================");

            try
            {
                await RunBotAsync(_cancellationTokenSource.Token);
            }
            catch (OperationCanceledException)
            {
                Log("Bot kullanıcı tarafından durduruldu");
            }
            catch (Exception ex)
            {
                Log($"✗ Hata: {ex.Message}");
                MessageBox.Show($"Bir hata oluştu:\n\n{ex.Message}", "Hata", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
            finally
            {
                StopBot();
            }
        }

        private void BtnStop_Click(object? sender, EventArgs e)
        {
            StopBot();
        }

        private void StopBot()
        {
            _cancellationTokenSource?.Cancel();
            _isRunning = false;
            _btnStart.Enabled = true;
            _btnStop.Enabled = false;
            _btnSelectAllRegions.Enabled = true;
            _lblStatus.Text = "● HAZIR";
            _lblStatus.ForeColor = Color.Gray;
        }

        private async Task RunBotAsync(CancellationToken cancellationToken)
        {
            if (_captureService == null || _ocrService == null)
            {
                throw new InvalidOperationException("Servisler başlatılmamış");
            }

            int cycleCount = 0;
            Random random = new Random();

            while (!cancellationToken.IsCancellationRequested)
            {
                cycleCount++;
                
                try
                {
                    // Capture green code region with proper disposal
                    Bitmap? greenCodeScreenshot = null;
                    Bitmap? processedGreen = null;
                    string? greenCode = null;

                    try
                    {
                        greenCodeScreenshot = _captureService.CaptureRegionCopy(_config.GreenCodeRegion.Rectangle);
                        processedGreen = _captureService.PreprocessForOCR(greenCodeScreenshot);
                        greenCode = _ocrService.RecognizeAndExtractCode(processedGreen, _config.VerificationCodePattern);
                    }
                    finally
                    {
                        greenCodeScreenshot?.Dispose();
                        processedGreen?.Dispose();
                    }

                    if (!string.IsNullOrEmpty(greenCode))
                    {
                        Log($"");
                        Log($"🎯 [Döngü {cycleCount}] BOT DOĞRULAMASI TESPİT EDİLDİ!");
                        Log($"🟢 Yeşil Kod: {greenCode}");

                        // Read all 4 buttons QUICKLY
                        string?[] buttonCodes = new string?[4];
                        RegionConfig[] buttonRegions = {
                            _config.Button1Region,
                            _config.Button2Region,
                            _config.Button3Region,
                            _config.Button4Region
                        };

                        // Read all buttons in parallel for SPEED with proper disposal
                        var buttonTasks = new Task<string?>[4];
                        for (int i = 0; i < 4; i++)
                        {
                            int index = i; // Capture for closure
                            buttonTasks[i] = Task.Run(() => {
                                Bitmap? buttonScreenshot = null;
                                Bitmap? processedButton = null;
                                try
                                {
                                    buttonScreenshot = _captureService.CaptureRegionCopy(buttonRegions[index].Rectangle);
                                    processedButton = _captureService.PreprocessForOCR(buttonScreenshot);
                                    return _ocrService.RecognizeAndExtractCode(processedButton, _config.VerificationCodePattern);
                                }
                                catch (Exception ex)
                                {
                                    Log($"⚠ Buton {index + 1} okuma hatası: {ex.Message}");
                                    return null;
                                }
                                finally
                                {
                                    buttonScreenshot?.Dispose();
                                    processedButton?.Dispose();
                                }
                            });
                        }

                        await Task.WhenAll(buttonTasks);
                        
                        for (int i = 0; i < 4; i++)
                        {
                            buttonCodes[i] = buttonTasks[i].Result;
                            Log($"   Buton {i + 1}: {buttonCodes[i] ?? "Okunamadı"}");
                        }

                        // Find matching button
                        int matchingButton = -1;
                        for (int i = 0; i < 4; i++)
                        {
                            if (buttonCodes[i] == greenCode)
                            {
                                matchingButton = i;
                                break;
                            }
                        }

                        if (matchingButton != -1)
                        {
                            Log($"✅ EŞLEŞME BULUNDU! Buton {matchingButton + 1} - Kod: {greenCode}");
                            Log($"🖱 HEMEN TIKLANIYOR...");

                            // Calculate click position (center of button region)
                            Rectangle buttonRect = buttonRegions[matchingButton].Rectangle;
                            int clickX = buttonRect.X + buttonRect.Width / 2;
                            int clickY = buttonRect.Y + buttonRect.Height / 2;
                            Point clickPoint = MouseHelper.AddJitter(new Point(clickX, clickY), 5);

                            // Perform click IMMEDIATELY - NO DELAY!
                            await MouseHelper.MoveAndClickAsync(clickPoint, cancellationToken);
                            
                            Log($"✅ TIKLANDI! Pozisyon: ({clickPoint.X}, {clickPoint.Y})");
                            Log($"⏳ Bot doğrulaması tamamlandı. Sonraki kontrol için bekleniyor...");

                            // Wait longer after successful verification
                            int delay = random.Next(_config.DelayMin, _config.DelayMax);
                            await Task.Delay(delay, cancellationToken);
                        }
                        else
                        {
                            Log($"⚠ Eşleşme bulunamadı! Yeşil kod: {greenCode}");
                            Log($"   Okunan buton kodları: {string.Join(", ", buttonCodes.Select(c => c ?? "null"))}");
                            Log($"   HEMEN TEKRAR DENENİYOR!");
                            
                            // IMMEDIATE retry - no delay!
                            await Task.Delay(300, cancellationToken);
                        }
                    }
                    else
                    {
                        // No verification detected, check again FAST
                        await Task.Delay(_config.CheckIntervalMs, cancellationToken);
                    }
                }
                catch (Exception ex)
                {
                    Log($"⚠ Döngü hatası: {ex.Message}");
                    Log($"   Detay: {ex.GetType().Name}");
                    await Task.Delay(1000, cancellationToken);
                }
            }
        }

        private void Log(string message)
        {
            if (InvokeRequired)
            {
                Invoke(new Action(() => Log(message)));
                return;
            }

            string timestamp = DateTime.Now.ToString("HH:mm:ss");
            _txtLog.AppendText($"[{timestamp}] {message}\r\n");
            _txtLog.SelectionStart = _txtLog.Text.Length;
            _txtLog.ScrollToCaret();
        }

        protected override void OnFormClosing(FormClosingEventArgs e)
        {
            StopBot();
            _ocrService?.Dispose();
            _captureService?.Dispose();
            base.OnFormClosing(e);
        }
    }
}
