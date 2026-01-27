using System;
using System.Drawing;
using System.Windows.Forms;

namespace DenizMacroBot.Utils
{
    /// <summary>
    /// Transparent overlay form for selecting a screen region
    /// </summary>
    public class RegionSelector : Form
    {
        private Point _startPoint;
        private Point _endPoint;
        private bool _isSelecting;
        private Rectangle _selectedRegion;
        private readonly Label _instructionLabel;
        private readonly Label _coordinatesLabel;

        public Rectangle SelectedRegion => _selectedRegion;
        public bool RegionSelected { get; private set; }

        public RegionSelector()
        {
            // Form setup
            FormBorderStyle = FormBorderStyle.None;
            WindowState = FormWindowState.Maximized;
            BackColor = Color.Black;
            Opacity = 0.3;
            TopMost = true;
            Cursor = Cursors.Cross;
            DoubleBuffered = true;

            // Instruction label
            _instructionLabel = new Label
            {
                Text = "Click and drag to select the monitoring region. Press ESC to cancel.",
                ForeColor = Color.White,
                BackColor = Color.FromArgb(180, 0, 0, 0),
                AutoSize = false,
                Size = new Size(600, 60),
                TextAlign = ContentAlignment.MiddleCenter,
                Font = new Font("Segoe UI", 12, FontStyle.Bold),
                Padding = new Padding(10)
            };
            _instructionLabel.Location = new Point(
                ((Screen.PrimaryScreen?.Bounds.Width ?? 1920) - _instructionLabel.Width) / 2,
                50
            );
            Controls.Add(_instructionLabel);

            // Coordinates label
            _coordinatesLabel = new Label
            {
                Text = "",
                ForeColor = Color.Lime,
                BackColor = Color.FromArgb(200, 0, 0, 0),
                AutoSize = false,
                Size = new Size(300, 30),
                TextAlign = ContentAlignment.MiddleCenter,
                Font = new Font("Consolas", 10, FontStyle.Bold),
                Visible = false
            };
            Controls.Add(_coordinatesLabel);

            // Event handlers
            MouseDown += RegionSelector_MouseDown;
            MouseMove += RegionSelector_MouseMove;
            MouseUp += RegionSelector_MouseUp;
            KeyDown += RegionSelector_KeyDown;
            Paint += RegionSelector_Paint;
        }

        private void RegionSelector_MouseDown(object? sender, MouseEventArgs e)
        {
            if (e.Button == MouseButtons.Left)
            {
                _startPoint = e.Location;
                _isSelecting = true;
                _coordinatesLabel.Visible = true;
            }
        }

        private void RegionSelector_MouseMove(object? sender, MouseEventArgs e)
        {
            if (_isSelecting)
            {
                _endPoint = e.Location;
                
                // Update coordinates label
                int width = Math.Abs(_endPoint.X - _startPoint.X);
                int height = Math.Abs(_endPoint.Y - _startPoint.Y);
                _coordinatesLabel.Text = $"Region: {width} × {height}";
                _coordinatesLabel.Location = new Point(
                    e.X + 15,
                    e.Y + 15
                );
                
                Invalidate(); // Trigger repaint
            }
        }

        private void RegionSelector_MouseUp(object? sender, MouseEventArgs e)
        {
            if (e.Button == MouseButtons.Left && _isSelecting)
            {
                _isSelecting = false;
                _endPoint = e.Location;

                // Calculate the selected rectangle
                int x = Math.Min(_startPoint.X, _endPoint.X);
                int y = Math.Min(_startPoint.Y, _endPoint.Y);
                int width = Math.Abs(_endPoint.X - _startPoint.X);
                int height = Math.Abs(_endPoint.Y - _startPoint.Y);

                _selectedRegion = new Rectangle(x, y, width, height);

                // Only accept if region has reasonable size
                if (width > 10 && height > 10)
                {
                    RegionSelected = true;
                    DialogResult = DialogResult.OK;
                    Close();
                }
                else
                {
                    MessageBox.Show(
                        "Selected region is too small. Please select a larger area.",
                        "Invalid Region",
                        MessageBoxButtons.OK,
                        MessageBoxIcon.Warning
                    );
                    _coordinatesLabel.Visible = false;
                    Invalidate();
                }
            }
        }

        private void RegionSelector_KeyDown(object? sender, KeyEventArgs e)
        {
            if (e.KeyCode == Keys.Escape)
            {
                RegionSelected = false;
                DialogResult = DialogResult.Cancel;
                Close();
            }
        }

        private void RegionSelector_Paint(object? sender, PaintEventArgs e)
        {
            if (_isSelecting)
            {
                // Draw the selection rectangle
                int x = Math.Min(_startPoint.X, _endPoint.X);
                int y = Math.Min(_startPoint.Y, _endPoint.Y);
                int width = Math.Abs(_endPoint.X - _startPoint.X);
                int height = Math.Abs(_endPoint.Y - _startPoint.Y);

                Rectangle rect = new Rectangle(x, y, width, height);

                // Fill with semi-transparent color
                using (Brush brush = new SolidBrush(Color.FromArgb(100, 0, 120, 215)))
                {
                    e.Graphics.FillRectangle(brush, rect);
                }

                // Draw border
                using (Pen pen = new Pen(Color.FromArgb(255, 0, 120, 215), 2))
                {
                    e.Graphics.DrawRectangle(pen, rect);
                }

                // Draw corner handles
                int handleSize = 8;
                using (Brush handleBrush = new SolidBrush(Color.White))
                {
                    // Top-left
                    e.Graphics.FillRectangle(handleBrush, x - handleSize / 2, y - handleSize / 2, handleSize, handleSize);
                    // Top-right
                    e.Graphics.FillRectangle(handleBrush, x + width - handleSize / 2, y - handleSize / 2, handleSize, handleSize);
                    // Bottom-left
                    e.Graphics.FillRectangle(handleBrush, x - handleSize / 2, y + height - handleSize / 2, handleSize, handleSize);
                    // Bottom-right
                    e.Graphics.FillRectangle(handleBrush, x + width - handleSize / 2, y + height - handleSize / 2, handleSize, handleSize);
                }

                // Draw dimension text
                string dimensions = $"{width} × {height}";
                using (Font font = new Font("Segoe UI", 11, FontStyle.Bold))
                using (Brush textBrush = new SolidBrush(Color.White))
                using (Brush bgBrush = new SolidBrush(Color.FromArgb(200, 0, 0, 0)))
                {
                    SizeF textSize = e.Graphics.MeasureString(dimensions, font);
                    PointF textPos = new PointF(
                        x + (width - textSize.Width) / 2,
                        y + (height - textSize.Height) / 2
                    );
                    
                    RectangleF textRect = new RectangleF(
                        textPos.X - 5,
                        textPos.Y - 5,
                        textSize.Width + 10,
                        textSize.Height + 10
                    );
                    
                    e.Graphics.FillRectangle(bgBrush, textRect);
                    e.Graphics.DrawString(dimensions, font, textBrush, textPos);
                }
            }
        }

        public static Rectangle? SelectRegion()
        {
            using (var selector = new RegionSelector())
            {
                if (selector.ShowDialog() == DialogResult.OK && selector.RegionSelected)
                {
                    return selector.SelectedRegion;
                }
            }
            return null;
        }
    }
}