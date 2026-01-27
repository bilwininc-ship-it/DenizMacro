using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.Runtime.InteropServices;

namespace DenizMacroBot.Services
{
    /// <summary>
    /// High-performance screen capture service
    /// </summary>
    public class ScreenCaptureService : IDisposable
    {
        [DllImport("user32.dll")]
        private static extern IntPtr GetDC(IntPtr hwnd);

        [DllImport("user32.dll")]
        private static extern int ReleaseDC(IntPtr hwnd, IntPtr hdc);

        [DllImport("gdi32.dll")]
        private static extern bool BitBlt(IntPtr hdcDest, int xDest, int yDest, int wDest, int hDest,
            IntPtr hdcSource, int xSrc, int ySrc, CopyPixelOperation rop);

        private Graphics? _graphics;
        private Bitmap? _bitmap;
        private Rectangle _lastRegion;

        /// <summary>
        /// Captures a region of the screen
        /// </summary>
        public Bitmap CaptureRegion(Rectangle region)
        {
            // Reuse bitmap if same size
            if (_bitmap == null || _lastRegion != region)
            {
                _bitmap?.Dispose();
                _bitmap = new Bitmap(region.Width, region.Height, PixelFormat.Format24bppRgb);
                _graphics?.Dispose();
                _graphics = Graphics.FromImage(_bitmap);
                _lastRegion = region;
            }

            // Capture from screen
            IntPtr hdcScreen = GetDC(IntPtr.Zero);
            IntPtr hdcDest = _graphics!.GetHdc();

            try
            {
                BitBlt(hdcDest, 0, 0, region.Width, region.Height,
                    hdcScreen, region.X, region.Y, CopyPixelOperation.SourceCopy);
            }
            finally
            {
                _graphics.ReleaseHdc(hdcDest);
                ReleaseDC(IntPtr.Zero, hdcScreen);
            }

            return _bitmap;
        }

        /// <summary>
        /// Captures a region and returns a copy (for processing)
        /// </summary>
        public Bitmap CaptureRegionCopy(Rectangle region)
        {
            var captured = CaptureRegion(region);
            return new Bitmap(captured);
        }

        /// <summary>
        /// Preprocesses image for better OCR results
        /// </summary>
        public Bitmap PreprocessForOCR(Bitmap source)
        {
            // Create a copy to work with
            Bitmap processed = new Bitmap(source.Width, source.Height, PixelFormat.Format24bppRgb);

            using (Graphics g = Graphics.FromImage(processed))
            {
                // High quality rendering
                g.InterpolationMode = System.Drawing.Drawing2D.InterpolationMode.HighQualityBicubic;
                g.SmoothingMode = System.Drawing.Drawing2D.SmoothingMode.HighQuality;
                g.PixelOffsetMode = System.Drawing.Drawing2D.PixelOffsetMode.HighQuality;

                // Draw the source image
                g.DrawImage(source, 0, 0, source.Width, source.Height);
            }

            // Convert to grayscale and increase contrast
            for (int y = 0; y < processed.Height; y++)
            {
                for (int x = 0; x < processed.Width; x++)
                {
                    Color pixel = processed.GetPixel(x, y);
                    
                    // Grayscale conversion
                    int gray = (int)(pixel.R * 0.3 + pixel.G * 0.59 + pixel.B * 0.11);
                    
                    // Increase contrast - threshold to pure black or white
                    gray = gray > 128 ? 255 : 0;
                    
                    Color newColor = Color.FromArgb(gray, gray, gray);
                    processed.SetPixel(x, y, newColor);
                }
            }

            return processed;
        }

        public void Dispose()
        {
            _graphics?.Dispose();
            _bitmap?.Dispose();
        }
    }
}