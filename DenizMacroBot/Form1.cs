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
        private TemplateMatchingService? _templateMatchingService;
        private ScreenCaptureService? _captureService;
        private CancellationTokenSource? _cancellationTokenSource;
        private bool _isRunning;

        // UI Controls
        private Button _btnSelectMainWindow = null!;
        private Button _btnStart = null!;
        private Button _btnStop = null!;
        private Button _btnSaveDebugImages = null!;
        private TextBox _txtLog = null!;
        private Label _lblStatus = null!;
        private Panel _statusPanel = null!;
        private GroupBox _configGroup = null!;
        private Label _lblMainWindowRegion = null!;
        private NumericUpDown _numDelayMin = null!;
        private NumericUpDown _numDelayMax = null!;
        private NumericUpDown _numThreshold = null!;
        private Label _lblDelayMin = null!;
        private Label _lblDelayMax = null!;
        private Label _lblThreshold = null!;
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
            Text = "DenizMacroBot - Template Matching (Dynamic Cropping)";
            Size = new Size(900, 800);
            BackColor = Color.FromArgb(30, 30, 30);
            ForeColor = Color.White;
            Font = new Font("Segoe UI", 9.5f);
            StartPosition = FormStartPosition.CenterScreen;
            MinimumSize = new Size(700, 650);

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
                Text = "⚙ Konfigürasyon - Template Matching Modu",
                ForeColor = Color.LightGray,
                Location = new Point(20, 80),
                Size = new Size(840, 320),
                Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right,
                Font = new Font("Segoe UI", 10, FontStyle.Bold)
            };
            Controls.Add(_configGroup);

            // Info label
            Label infoLabel = new Label
            {
                Text = "📌 Template Matching ile Dinamik Bölge Kırpma:\n" +
                       "• Ana pencereyi bir kez seçin (yeşil kod + 4 buton dahil)\n" +
                       "• Bot otomatik olarak %20-40 (yeşil kod) ve %40-90 (butonlar) kırpar\n" +
                       "• OpenCV ile görüntü eşleştirmesi yapar (OCR yok!)",
                Location = new Point(20, 30),
                Size = new Size(800, 75),
                ForeColor = Color.LightBlue,
                Font = new Font("Segoe UI", 9f)
            };
            _configGroup.Controls.Add(infoLabel);

            // Selection progress label
            _lblSelectionProgress = new Label
            {
                Text = "Ana pencereyi seçmek için butona tıklayın",
                Location = new Point(20, 115),
                Size = new Size(800, 25),
                ForeColor = Color.Orange,
                Font = new Font("Segoe UI", 10, FontStyle.Bold)
            };
            _configGroup.Controls.Add(_lblSelectionProgress);

            // Region status label
            _lblMainWindowRegion = new Label
            {
                Text = "❌ Ana Pencere: Seçilmedi",
                Location = new Point(20, 145),
                Size = new Size(800, 22),
                ForeColor = Color.OrangeRed,
                Font = new Font("Segoe UI", 9.5f)
            };
            _configGroup.Controls.Add(_lblMainWindowRegion);

            // Select Main Window button
            _btnSelectMainWindow = new Button
            {
                Text = "🎯 ANA PENCEREYİ SEÇ (Doğrulama Dialogu)",
                Location = new Point(20, 180),
                Size = new Size(800, 50),
                BackColor = Color.FromArgb(0, 120, 215),
                ForeColor = Color.White,
                FlatStyle = FlatStyle.Flat,
                Font = new Font("Segoe UI", 11, FontStyle.Bold),
                Cursor = Cursors.Hand
            };
            _btnSelectMainWindow.FlatAppearance.BorderSize = 0;
            _btnSelectMainWindow.Click += BtnSelectMainWindow_Click;
            _configGroup.Controls.Add(_btnSelectMainWindow);

            // Save Debug Images button
            _btnSaveDebugImages = new Button
            {
                Text = "💾 Debug Resimleri Kaydet",
                Location = new Point(20, 245),
                Size = new Size(390, 40),
                BackColor = Color.FromArgb(60, 60, 60),
                ForeColor = Color.White,
                FlatStyle = FlatStyle.Flat,
                Font = new Font("Segoe UI", 9, FontStyle.Bold),
                Cursor = Cursors.Hand,
                Enabled = false
            };
            _btnSaveDebugImages.FlatAppearance.BorderSize = 0;
            _btnSaveDebugImages.Click += BtnSaveDebugImages_Click;
            _configGroup.Controls.Add(_btnSaveDebugImages);

            // Settings group
            var settingsGroup = new GroupBox
            {
                Text = "⚙ Bot Ayarları",
                ForeColor = Color.LightGray,
                Location = new Point(20, 420),
                Size = new Size(840, 90),
                Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right,
                Font = new Font("Segoe UI", 10, FontStyle.Bold)
            };
            Controls.Add(settingsGroup);

            _lblThreshold = new Label
            {
                Text = "Eşleşme Eşiği:",
                Location = new Point(20, 35),
                Size = new Size(120, 20),
                ForeColor = Color.LightGray,
                Font = new Font("Segoe UI", 9.5f)
            };
            settingsGroup.Controls.Add(_lblThreshold);

            _numThreshold = new NumericUpDown
            {
                Location = new Point(140, 32),
                Size = new Size(80, 25),
                Minimum = 50,
                Maximum = 100,
                Value = 85,
                Increment = 1,
                DecimalPlaces = 0,
                BackColor = Color.FromArgb(45, 45, 45),
                ForeColor = Color.White
            };
            _numThreshold.ValueChanged += (s, e) => _config.MatchingThreshold = (double)_numThreshold.Value / 100.0;
            settingsGroup.Controls.Add(_numThreshold);

            Label lblThresholdPercent = new Label
            {
                Text = "% (0.85 = %85)",
                Location = new Point(225, 35),
                Size = new Size(120, 20),
                ForeColor = Color.Gray,
                Font = new Font("Segoe UI", 8.5f)
            };
            settingsGroup.Controls.Add(lblThresholdPercent);

            _lblDelayMin = new Label
            {
                Text = "Min Gecikme (sn):",
                Location = new Point(380, 35),
                Size = new Size(130, 20),
                ForeColor = Color.LightGray,
                Font = new Font("Segoe UI", 9.5f)
            };
            settingsGroup.Controls.Add(_lblDelayMin);

            _numDelayMin = new NumericUpDown
            {
                Location = new Point(510, 32),
                Size = new Size(70, 25),
                Minimum = 1,
                Maximum = 60,
                Value = 4,
                BackColor = Color.FromArgb(45, 45, 45),
                ForeColor = Color.White
            };
            _numDelayMin.ValueChanged += (s, e) => _config.DelayMin = (int)_numDelayMin.Value * 1000;
            settingsGroup.Controls.Add(_numDelayMin);

            _lblDelayMax = new Label
            {
                Text = "Max Gecikme (sn):",
                Location = new Point(600, 35),
                Size = new Size(135, 20),
                ForeColor = Color.LightGray,
                Font = new Font("Segoe UI", 9.5f)
            };
            settingsGroup.Controls.Add(_lblDelayMax);

            _numDelayMax = new NumericUpDown
            {
                Location = new Point(735, 32),
                Size = new Size(70, 25),
                Minimum = 1,
                Maximum = 60,
                Value = 14,
                BackColor = Color.FromArgb(45, 45, 45),
                ForeColor = Color.White
            };
            _numDelayMax.ValueChanged += (s, e) => _config.DelayMax = (int)_numDelayMax.Value * 1000;
            settingsGroup.Controls.Add(_numDelayMax);

            // Control buttons
            _btnStart = new Button
            {
                Text = "▶ BOT'U BAŞLAT",
                Location = new Point(20, 530),
                Size = new Size(350, 55),
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
                Location = new Point(390, 530),
                Size = new Size(350, 55),
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
                Location = new Point(20, 605),
                Size = new Size(150, 20),
                ForeColor = Color.LightGray,
                Font = new Font("Segoe UI", 10, FontStyle.Bold)
            };
            Controls.Add(lblLog);

            _txtLog = new TextBox
            {
                Location = new Point(20, 630),
                Size = new Size(840, 120),
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
            _numThreshold.Value = (decimal)(_config.MatchingThreshold * 100);

            UpdateRegionLabel();
            CheckIfRegionConfigured();
        }

        private void InitializeServices()
        {
            try
            {
                _captureService = new ScreenCaptureService();
                _templateMatchingService = new TemplateMatchingService();
                
                Log("✓ Template Matching servisi başlatıldı");
                Log("✓ OpenCvSharp4 hazır");
            }
            catch (Exception ex)
            {
                Log($"✗ Servisler başlatılamadı: {ex.Message}");
                MessageBox.Show(
                    $"Template Matching servisi başlatılamadı.\n\nHata: {ex.Message}",
                    "Başlatma Hatası",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Error
                );
            }
        }

        private void BtnSelectMainWindow_Click(object? sender, EventArgs e)
        {
            _btnSelectMainWindow.Enabled = false;
            _lblSelectionProgress.Text = "🎯 ANA PENCEREYİ SEÇİN (tüm doğrulama dialogunu çizin)...";
            _lblSelectionProgress.ForeColor = Color.Yellow;

            Task.Delay(1000).ContinueWith(_ =>
            {
                Invoke(new Action(() =>
                {
                    var region = RegionSelector.SelectRegion();
                    if (region.HasValue)
                    {
                        _config.MainWindowRegion.SetFromRectangle(region.Value);
                        _config.SaveToFile(ConfigPath);
                        
                        UpdateRegionLabel();
                        
                        _lblSelectionProgress.Text = "✅ Ana pencere başarıyla seçildi! Bot kullanıma hazır.";
                        _lblSelectionProgress.ForeColor = Color.LightGreen;
                        _btnStart.Enabled = true;
                        _btnSaveDebugImages.Enabled = true;
                        
                        Log("========================================");
                        Log("✅ ANA PENCERE SEÇİLDİ!");
                        Log($"   Boyut: {region.Value.Width}×{region.Value.Height}");
                        Log($"   Konum: ({region.Value.X}, {region.Value.Y})");
                        Log("   Dinamik kırpma oranları:");
                        Log($"   • Yeşil Kod: %{_config.TargetCodeTopPercent * 100}-{_config.TargetCodeBottomPercent * 100}");
                        Log($"   • Butonlar: %{_config.ButtonsAreaTopPercent * 100}-{_config.ButtonsAreaBottomPercent * 100}");
                        Log("========================================");
                    }
                    else
                    {
                        _lblSelectionProgress.Text = "❌ Seçim iptal edildi. Tekrar denemek için butona tıklayın.";
                        _lblSelectionProgress.ForeColor = Color.Red;
                        Log("⚠ Ana pencere seçimi iptal edildi");
                    }
                    
                    _btnSelectMainWindow.Enabled = true;
                }));
            });
        }

        private void UpdateRegionLabel()
        {
            if (_config.MainWindowRegion.IsValid)
            {
                var rect = _config.MainWindowRegion.Rectangle;
                _lblMainWindowRegion.Text = $"✅ Ana Pencere: {rect.Width}×{rect.Height} @ ({rect.X}, {rect.Y})";
                _lblMainWindowRegion.ForeColor = Color.LightGreen;
            }
        }

        private void CheckIfRegionConfigured()
        {
            if (_config.AllRegionsConfigured)
            {
                _lblSelectionProgress.Text = "✅ Yapılandırma tamamlandı! Bot başlatmaya hazır.";
                _lblSelectionProgress.ForeColor = Color.LightGreen;
                _btnStart.Enabled = true;
                _btnSaveDebugImages.Enabled = true;
            }
        }

        private async void BtnStart_Click(object? sender, EventArgs e)
        {
            if (_isRunning) return;

            _isRunning = true;
            _btnStart.Enabled = false;
            _btnStop.Enabled = true;
            _btnSelectMainWindow.Enabled = false;
            _lblStatus.Text = "● ÇALIŞIYOR";
            _lblStatus.ForeColor = Color.Lime;

            _cancellationTokenSource = new CancellationTokenSource();
            
            Log("========================================");
            Log("🤖 Bot başlatıldı - Template Matching Modu");
            Log($"⚙ Eşleşme Eşiği: {_config.MatchingThreshold:P0}");
            Log($"⏱ Gecikme: {_config.DelayMin / 1000}-{_config.DelayMax / 1000} saniye");
            Log($"🔍 Kontrol Aralığı: {_config.CheckIntervalMs / 1000} saniye");
            Log("🎯 Dinamik kırpma aktif");
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
            _btnSelectMainWindow.Enabled = true;
            _lblStatus.Text = "● HAZIR";
            _lblStatus.ForeColor = Color.Gray;
        }

        private async Task RunBotAsync(CancellationToken cancellationToken)
        {
            if (_captureService == null || _templateMatchingService == null)
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
                    // Capture main window
                    Bitmap? mainWindowCapture = null;
                    Bitmap? targetCodeBitmap = null;
                    Bitmap? buttonsAreaBitmap = null;
                    Bitmap[]? buttonBitmaps = null;

                    try
                    {
                        // Step 1: Capture the main window
                        mainWindowCapture = _captureService.CaptureRegion(_config.MainWindowRegion.Rectangle);

                        // Step 2: Dynamically crop Target Code (20-40%)
                        targetCodeBitmap = _templateMatchingService.CropRegion(
                            mainWindowCapture,
                            _config.TargetCodeTopPercent,
                            _config.TargetCodeBottomPercent
                        );

                        // Step 3: Dynamically crop Buttons Area (40-90%)
                        buttonsAreaBitmap = _templateMatchingService.CropRegion(
                            mainWindowCapture,
                            _config.ButtonsAreaTopPercent,
                            _config.ButtonsAreaBottomPercent
                        );

                        // Step 4: Split Buttons Area into 4 equal parts
                        buttonBitmaps = _templateMatchingService.SplitButtonsArea(buttonsAreaBitmap);

                        // Step 5: Perform Template Matching
                        var (buttonIndex, similarity, usedCanny) = _templateMatchingService.FindBestMatch(
                            targetCodeBitmap,
                            buttonBitmaps,
                            _config.MatchingThreshold
                        );

                        Log($"");
                        Log($"🔍 [Döngü {cycleCount}] Template Matching Tamamlandı");
                        Log($"   Preprocessing: {(usedCanny ? "Canny Edge Detection" : "Binary Threshold")}");
                        Log($"   En İyi Eşleşme: Buton {buttonIndex + 1}");
                        Log($"   Benzerlik Skoru: {similarity:P2} ({similarity:F3})");

                        // Check if similarity meets threshold
                        if (similarity >= _config.MatchingThreshold)
                        {
                            Log($"✅ EŞLEŞME BULUNDU! Buton {buttonIndex + 1} - Skor: {similarity:P2}");
                            Log($"🖱 Tıklama yapılıyor...");

                            // Calculate click position
                            // Button position = MainWindow.Y + ButtonsAreaTop + (buttonIndex * buttonHeight) + (buttonHeight / 2)
                            int buttonsAreaStartY = (int)(_config.MainWindowRegion.Rectangle.Height * _config.ButtonsAreaTopPercent);
                            int buttonsAreaHeight = (int)(_config.MainWindowRegion.Rectangle.Height * (_config.ButtonsAreaBottomPercent - _config.ButtonsAreaTopPercent));
                            int buttonHeight = buttonsAreaHeight / 4;
                            
                            int clickX = _config.MainWindowRegion.Rectangle.X + _config.MainWindowRegion.Rectangle.Width / 2;
                            int clickY = _config.MainWindowRegion.Rectangle.Y + buttonsAreaStartY + (buttonIndex * buttonHeight) + (buttonHeight / 2);
                            
                            Point clickPoint = MouseHelper.AddJitter(new Point(clickX, clickY), 5);

                            // Perform click with randomized delay
                            int preClickDelay = random.Next(_config.DelayMin, _config.DelayMax);
                            Log($"⏳ {preClickDelay / 1000} saniye gecikme uygulanıyor...");
                            await Task.Delay(preClickDelay, cancellationToken);

                            await MouseHelper.MoveAndClickAsync(clickPoint, cancellationToken);
                            
                            Log($"✅ TIKLANDI! Pozisyon: ({clickPoint.X}, {clickPoint.Y})");
                            Log($"⏳ Bot doğrulaması tamamlandı. {_config.CheckIntervalMs / 1000} saniye sonra tekrar kontrol edilecek.");
                            
                            // Wait before next check
                            await Task.Delay(_config.CheckIntervalMs, cancellationToken);
                        }
                        else
                        {
                            Log($"⚠ Eşleşme eşiği karşılanmadı (Skor: {similarity:P2} < Eşik: {_config.MatchingThreshold:P0})");
                            Log($"   En yakın: Buton {buttonIndex + 1} - {similarity:P2}");
                            Log($"   Yanlış tıklamayı önlemek için bekleyip tekrar taranacak.");
                            
                            // Continue monitoring
                            await Task.Delay(_config.CheckIntervalMs, cancellationToken);
                        }
                    }
                    finally
                    {
                        // Dispose bitmaps
                        mainWindowCapture?.Dispose();
                        targetCodeBitmap?.Dispose();
                        buttonsAreaBitmap?.Dispose();
                        
                        if (buttonBitmaps != null)
                        {
                            foreach (var bitmap in buttonBitmaps)
                            {
                                bitmap?.Dispose();
                            }
                        }
                    }
                }
                catch (Exception ex)
                {
                    Log($"⚠ Döngü hatası: {ex.Message}");
                    await Task.Delay(1000, cancellationToken);
                }
            }
        }

        private void BtnSaveDebugImages_Click(object? sender, EventArgs e)
        {
            if (_captureService == null || _templateMatchingService == null)
            {
                MessageBox.Show("Servisler başlatılmamış!", "Hata", MessageBoxButtons.OK, MessageBoxIcon.Error);
                return;
            }

            if (!_config.MainWindowRegion.IsValid)
            {
                MessageBox.Show("Önce ana pencereyi seçmelisiniz!", "Uyarı", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            try
            {
                // Capture and process
                using (Bitmap mainWindow = _captureService.CaptureRegion(_config.MainWindowRegion.Rectangle))
                using (Bitmap targetCode = _templateMatchingService.CropRegion(
                    mainWindow, 
                    _config.TargetCodeTopPercent, 
                    _config.TargetCodeBottomPercent))
                using (Bitmap buttonsArea = _templateMatchingService.CropRegion(
                    mainWindow,
                    _config.ButtonsAreaTopPercent,
                    _config.ButtonsAreaBottomPercent))
                {
                    Bitmap[] buttons = _templateMatchingService.SplitButtonsArea(buttonsArea);

                    string outputFolder = Path.Combine(
                        Environment.GetFolderPath(Environment.SpecialFolder.Desktop),
                        "DenizBot_Debug_" + DateTime.Now.ToString("yyyyMMdd_HHmmss")
                    );

                    _templateMatchingService.SaveDebugImages(targetCode, buttons, outputFolder);

                    // Dispose buttons
                    foreach (var btn in buttons)
                    {
                        btn?.Dispose();
                    }

                    Log($"✅ Debug resimleri kaydedildi: {outputFolder}");
                    MessageBox.Show(
                        $"Debug resimleri başarıyla kaydedildi!\n\nKonum: {outputFolder}",
                        "Başarılı",
                        MessageBoxButtons.OK,
                        MessageBoxIcon.Information
                    );
                }
            }
            catch (Exception ex)
            {
                Log($"✗ Debug resimleri kaydedilemedi: {ex.Message}");
                MessageBox.Show($"Hata: {ex.Message}", "Hata", MessageBoxButtons.OK, MessageBoxIcon.Error);
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
            _templateMatchingService?.Dispose();
            _captureService?.Dispose();
            base.OnFormClosing(e);
        }
    }
}
