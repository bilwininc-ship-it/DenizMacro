using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.Runtime.InteropServices;

namespace DenizMacroBot.Services
{
    /// <summary>
    /// High-performance, thread-safe screen capture service
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

        // Thread-safe: Use lock for screen capture operations
        private readonly object _captureLock = new object();

        /// <summary>
        /// Captures a region of the screen - THREAD-SAFE VERSION
        /// Creates a new bitmap for each capture to avoid shared state issues
        /// </summary>
        public Bitmap CaptureRegion(Rectangle region)
        {
            lock (_captureLock)
            {
                // Always create new bitmap - no shared state!
                Bitmap bitmap = new Bitmap(region.Width, region.Height, PixelFormat.Format24bppRgb);
                
                using (Graphics graphics = Graphics.FromImage(bitmap))
                {
                    IntPtr hdcScreen = GetDC(IntPtr.Zero);
                    IntPtr hdcDest = graphics.GetHdc();

                    try
                    {
                        BitBlt(hdcDest, 0, 0, region.Width, region.Height,
                            hdcScreen, region.X, region.Y, CopyPixelOperation.SourceCopy);
                    }
                    finally
                    {
                        graphics.ReleaseHdc(hdcDest);
                        ReleaseDC(IntPtr.Zero, hdcScreen);
                    }
                }

                return bitmap;
            }
        }

        /// <summary>
        /// Captures a region and returns a copy (for processing)
        /// </summary>
        public Bitmap CaptureRegionCopy(Rectangle region)
        {
            // CaptureRegion now already creates a new bitmap, so just return it
            return CaptureRegion(region);
        }

        /// <summary>
        /// Preprocesses image for better OCR results - OPTIMIZED & THREAD-SAFE VERSION
        /// Uses LockBits for 10x faster pixel processing
        /// </summary>
        public Bitmap PreprocessForOCR(Bitmap source)
        {
            // Scale up the image 3x for better OCR accuracy
            int scaleFactor = 3;
            int newWidth = source.Width * scaleFactor;
            int newHeight = source.Height * scaleFactor;
            
            Bitmap scaled = new Bitmap(newWidth, newHeight, PixelFormat.Format24bppRgb);
            
            // High-quality scaling
            using (Graphics g = Graphics.FromImage(scaled))
            {
                g.InterpolationMode = System.Drawing.Drawing2D.InterpolationMode.HighQualityBicubic;
                g.SmoothingMode = System.Drawing.Drawing2D.SmoothingMode.HighQuality;
                g.PixelOffsetMode = System.Drawing.Drawing2D.PixelOffsetMode.HighQuality;
                g.CompositingQuality = System.Drawing.Drawing2D.CompositingQuality.HighQuality;
                g.DrawImage(source, 0, 0, newWidth, newHeight);
            }

            // Fast pixel processing using LockBits (10x faster than GetPixel/SetPixel!)
            BitmapData bmpData = scaled.LockBits(
                new Rectangle(0, 0, newWidth, newHeight),
                ImageLockMode.ReadWrite,
                PixelFormat.Format24bppRgb);

            try
            {
                unsafe
                {
                    byte* ptr = (byte*)bmpData.Scan0;
                    int bytes = Math.Abs(bmpData.Stride) * newHeight;
                    int stride = bmpData.Stride;

                    // Process pixels in parallel for even more speed
                    System.Threading.Tasks.Parallel.For(0, newHeight, y =>
                    {
                        byte* row = ptr + (y * stride);
                        
                        for (int x = 0; x < newWidth; x++)
                        {
                            int offset = x * 3; // 24bpp = 3 bytes per pixel
                            
                            // Get RGB values
                            byte b = row[offset];
                            byte g = row[offset + 1];
                            byte r = row[offset + 2];
                            
                            // Grayscale conversion (weighted for human eye perception)
                            int gray = (int)(r * 0.3 + g * 0.59 + b * 0.11);
                            
                            // Adaptive thresholding for better contrast
                            byte value = (byte)(gray > 100 ? 255 : 0);
                            
                            // Set all channels to same value (grayscale)
                            row[offset] = value;     // B
                            row[offset + 1] = value; // G
                            row[offset + 2] = value; // R
                        }
                    });
                }
            }
            finally
            {
                scaled.UnlockBits(bmpData);
            }

            return scaled;
        }

        public void Dispose()
        {
            // No shared resources to dispose anymore
            GC.SuppressFinalize(this);
        }
    }
}