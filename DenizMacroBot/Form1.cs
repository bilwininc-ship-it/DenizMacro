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
        
        private BotConfig _config;
        private OCRService? _ocrService;
        private ScreenCaptureService? _captureService;
        private CancellationTokenSource? _cancellationTokenSource;
        private bool _isRunning;

        // UI Controls
        private Button _btnSelectRegion;
        private Button _btnStart;
        private Button _btnStop;
        private TextBox _txtLog;
        private Label _lblStatus;
        private Panel _statusPanel;
        private GroupBox _configGroup;
        private Label _lblRegion;
        private NumericUpDown _numDelayMin;
        private NumericUpDown _numDelayMax;
        private Label _lblDelayMin;
        private Label _lblDelayMax;

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
            Text = "DenizMacroBot - Screen Automation";
            Size = new Size(800, 650);
            BackColor = Color.FromArgb(30, 30, 30);
            ForeColor = Color.White;
            Font = new Font("Segoe UI", 9.5f);
            StartPosition = FormStartPosition.CenterScreen;
            MinimumSize = new Size(600, 500);

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
                Text = "● IDLE",
                ForeColor = Color.Gray,
                Font = new Font("Segoe UI", 14, FontStyle.Bold),
                Location = new Point(20, 18),
                AutoSize = true
            };
            _statusPanel.Controls.Add(_lblStatus);

            // Configuration group
            _configGroup = new GroupBox
            {
                Text = "Configuration",
                ForeColor = Color.LightGray,
                Location = new Point(20, 80),
                Size = new Size(740, 160),
                Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right
            };
            Controls.Add(_configGroup);

            // Region info label
            _lblRegion = new Label
            {
                Text = "No region selected",
                Location = new Point(20, 30),
                Size = new Size(700, 20),
                ForeColor = Color.Orange
            };
            _configGroup.Controls.Add(_lblRegion);

            // Select Region button
            _btnSelectRegion = new Button
            {
                Text = "📐 Select Region",
                Location = new Point(20, 60),
                Size = new Size(200, 40),
                BackColor = Color.FromArgb(0, 120, 215),
                ForeColor = Color.White,
                FlatStyle = FlatStyle.Flat,
                Font = new Font("Segoe UI", 10, FontStyle.Bold),
                Cursor = Cursors.Hand
            };
            _btnSelectRegion.FlatAppearance.BorderSize = 0;
            _btnSelectRegion.Click += BtnSelectRegion_Click;
            _configGroup.Controls.Add(_btnSelectRegion);

            // Delay configuration
            _lblDelayMin = new Label
            {
                Text = "Min Delay (sec):",
                Location = new Point(20, 115),
                Size = new Size(120, 20),
                ForeColor = Color.LightGray
            };
            _configGroup.Controls.Add(_lblDelayMin);

            _numDelayMin = new NumericUpDown
            {
                Location = new Point(140, 112),
                Size = new Size(80, 25),
                Minimum = 1,
                Maximum = 60,
                Value = 12,
                BackColor = Color.FromArgb(45, 45, 45),
                ForeColor = Color.White
            };
            _numDelayMin.ValueChanged += (s, e) => _config.DelayMin = (int)_numDelayMin.Value * 1000;
            _configGroup.Controls.Add(_numDelayMin);

            _lblDelayMax = new Label
            {
                Text = "Max Delay (sec):",
                Location = new Point(250, 115),
                Size = new Size(120, 20),
                ForeColor = Color.LightGray
            };
            _configGroup.Controls.Add(_lblDelayMax);

            _numDelayMax = new NumericUpDown
            {
                Location = new Point(370, 112),
                Size = new Size(80, 25),
                Minimum = 1,
                Maximum = 60,
                Value = 18,
                BackColor = Color.FromArgb(45, 45, 45),
                ForeColor = Color.White
            };
            _numDelayMax.ValueChanged += (s, e) => _config.DelayMax = (int)_numDelayMax.Value * 1000;
            _configGroup.Controls.Add(_numDelayMax);

            // Control buttons
            _btnStart = new Button
            {
                Text = "▶ START",
                Location = new Point(20, 260),
                Size = new Size(200, 50),
                BackColor = Color.FromArgb(16, 124, 16),
                ForeColor = Color.White,
                FlatStyle = FlatStyle.Flat,
                Font = new Font("Segoe UI", 12, FontStyle.Bold),
                Cursor = Cursors.Hand,
                Enabled = false
            };
            _btnStart.FlatAppearance.BorderSize = 0;
            _btnStart.Click += BtnStart_Click;
            Controls.Add(_btnStart);

            _btnStop = new Button
            {
                Text = "■ STOP",
                Location = new Point(240, 260),
                Size = new Size(200, 50),
                BackColor = Color.FromArgb(180, 0, 0),
                ForeColor = Color.White,
                FlatStyle = FlatStyle.Flat,
                Font = new Font("Segoe UI", 12, FontStyle.Bold),
                Cursor = Cursors.Hand,
                Enabled = false
            };
            _btnStop.FlatAppearance.BorderSize = 0;
            _btnStop.Click += BtnStop_Click;
            Controls.Add(_btnStop);

            // Activity log
            Label lblLog = new Label
            {
                Text = "Activity Log",
                Location = new Point(20, 330),
                Size = new Size(100, 20),
                ForeColor = Color.LightGray
            };
            Controls.Add(lblLog);

            _txtLog = new TextBox
            {
                Location = new Point(20, 355),
                Size = new Size(740, 230),
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

            if (_config.SearchRegion.IsValid)
            {
                UpdateRegionLabel();
                _btnStart.Enabled = true;
            }
        }

        private void InitializeServices()
        {
            try
            {
                _captureService = new ScreenCaptureService();
                _ocrService = new OCRService(_config.TesseractDataPath);
                
                if (_ocrService.Initialize())
                {
                    Log("✓ OCR engine initialized successfully");
                }
            }
            catch (Exception ex)
            {
                Log($"✗ Failed to initialize services: {ex.Message}");
                MessageBox.Show(
                    $"Failed to initialize OCR engine.\n\nError: {ex.Message}\n\nPlease ensure tessdata is in: {_config.TesseractDataPath}",
                    "Initialization Error",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Error
                );
            }
        }

        private void BtnSelectRegion_Click(object? sender, EventArgs e)
        {
            var region = RegionSelector.SelectRegion();
            if (region.HasValue)
            {
                _config.SearchRegion.SetFromRectangle(region.Value);
                _config.SaveToFile(ConfigPath);
                UpdateRegionLabel();
                _btnStart.Enabled = true;
                Log($"✓ Region selected: {region.Value.Width}×{region.Value.Height} at ({region.Value.X}, {region.Value.Y})");
            }
        }

        private void UpdateRegionLabel()
        {
            var r = _config.SearchRegion;
            _lblRegion.Text = $"Region: {r.Width}×{r.Height} at position ({r.X}, {r.Y})";
            _lblRegion.ForeColor = Color.LightGreen;
        }

        private async void BtnStart_Click(object? sender, EventArgs e)
        {
            if (_isRunning) return;

            _isRunning = true;
            _btnStart.Enabled = false;
            _btnStop.Enabled = true;
            _btnSelectRegion.Enabled = false;
            _lblStatus.Text = "● RUNNING";
            _lblStatus.ForeColor = Color.Lime;

            _cancellationTokenSource = new CancellationTokenSource();
            
            Log("========================================");
            Log("Bot started - Monitoring region...");
            Log("========================================");

            try
            {
                await RunBotAsync(_cancellationTokenSource.Token);
            }
            catch (OperationCanceledException)
            {
                Log("Bot stopped by user");
            }
            catch (Exception ex)
            {
                Log($"✗ Error: {ex.Message}");
                MessageBox.Show($"An error occurred:\n\n{ex.Message}", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
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
            _btnSelectRegion.Enabled = true;
            _lblStatus.Text = "● IDLE";
            _lblStatus.ForeColor = Color.Gray;
        }

        private async Task RunBotAsync(CancellationToken cancellationToken)
        {
            if (_captureService == null || _ocrService == null)
            {
                throw new InvalidOperationException("Services not initialized");
            }

            int cycleCount = 0;

            while (!cancellationToken.IsCancellationRequested)
            {
                cycleCount++;
                Log($"[Cycle {cycleCount}] Capturing screen region...");

                // Capture the screen region
                var screenshot = _captureService.CaptureRegionCopy(_config.SearchRegion.Rectangle);
                
                // Preprocess for OCR
                var processed = _captureService.PreprocessForOCR(screenshot);

                // Perform OCR
                string? code = _ocrService.RecognizeAndExtractCode(processed, _config.VerificationCodePattern);

                if (!string.IsNullOrEmpty(code))
                {
                    Log($"✓ Detected verification code: {code}");
                    
                    // Simulate clicking on detected buttons
                    // In a real implementation, you would detect button positions
                    // For demonstration, we'll just log the action
                    Log($"Processing verification code: {code}");
                    
                    // Example: Click at a position within the region
                    int clickX = _config.SearchRegion.X + _config.SearchRegion.Width / 2;
                    int clickY = _config.SearchRegion.Y + _config.SearchRegion.Height / 2;
                    Point clickPoint = MouseHelper.AddJitter(new Point(clickX, clickY));
                    
                    Log($"Moving to target position...");
                    await MouseHelper.MoveAndClickAsync(clickPoint, cancellationToken);
                    Log($"✓ Click executed at ({clickPoint.X}, {clickPoint.Y})");
                }
                else
                {
                    Log("No verification code detected");
                }

                screenshot.Dispose();
                processed.Dispose();

                // Random delay between checks
                int delay = new Random().Next(_config.DelayMin, _config.DelayMax);
                Log($"Waiting {delay / 1000.0:F1}s before next check...");
                await Task.Delay(delay, cancellationToken);
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