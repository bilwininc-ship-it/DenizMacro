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
        /// Preprocesses image for better OCR results - ENHANCED VERSION
        /// </summary>
        public Bitmap PreprocessForOCR(Bitmap source)
        {
            // Scale up the image 3x for better OCR accuracy
            int scaleFactor = 3;
            Bitmap scaled = new Bitmap(source.Width * scaleFactor, source.Height * scaleFactor, PixelFormat.Format24bppRgb);
            
            using (Graphics g = Graphics.FromImage(scaled))
            {
                g.InterpolationMode = System.Drawing.Drawing2D.InterpolationMode.HighQualityBicubic;
                g.SmoothingMode = System.Drawing.Drawing2D.SmoothingMode.HighQuality;
                g.PixelOffsetMode = System.Drawing.Drawing2D.PixelOffsetMode.HighQuality;
                g.DrawImage(source, 0, 0, scaled.Width, scaled.Height);
            }

            // Convert to grayscale and apply adaptive thresholding
            for (int y = 0; y < scaled.Height; y++)
            {
                for (int x = 0; x < scaled.Width; x++)
                {
                    Color pixel = scaled.GetPixel(x, y);
                    
                    // Grayscale conversion
                    int gray = (int)(pixel.R * 0.3 + pixel.G * 0.59 + pixel.B * 0.11);
                    
                    // More aggressive thresholding for better contrast
                    gray = gray > 100 ? 255 : 0;
                    
                    Color newColor = Color.FromArgb(gray, gray, gray);
                    scaled.SetPixel(x, y, newColor);
                }
            }

            return scaled;
        }

        public void Dispose()
        {
            _graphics?.Dispose();
            _bitmap?.Dispose();
        }
    }
}