using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.IO;
using System.Text.RegularExpressions;
using Tesseract;

namespace DenizMacroBot.Services
{
    /// <summary>
    /// OCR service using Tesseract for text recognition
    /// </summary>
    public class OCRService : IDisposable
    {
        private TesseractEngine? _engine;
        private readonly string _tessdataPath;
        private bool _initialized;

        public OCRService(string tessdataPath)
        {
            _tessdataPath = tessdataPath;
        }

        /// <summary>
        /// Initializes the Tesseract engine
        /// </summary>
        public bool Initialize()
        {
            try
            {
                // Check if tessdata exists
                string dataPath = Path.GetFullPath(_tessdataPath);
                if (!Directory.Exists(dataPath))
                {
                    throw new DirectoryNotFoundException($"Tessdata directory not found: {dataPath}");
                }

                string engFile = Path.Combine(dataPath, "eng.traineddata");
                if (!File.Exists(engFile))
                {
                    throw new FileNotFoundException($"eng.traineddata not found: {engFile}");
                }

                // Initialize engine with optimal settings for digit recognition
                _engine = new TesseractEngine(dataPath, "eng", EngineMode.Default);
                
                // Set variables for better digit recognition
                _engine.SetVariable("tessedit_char_whitelist", "0123456789");
                _engine.SetVariable("classify_bln_numeric_mode", "1");
                
                _initialized = true;
                return true;
            }
            catch (Exception ex)
            {
                _initialized = false;
                throw new InvalidOperationException($"Failed to initialize OCR engine: {ex.Message}", ex);
            }
        }

        /// <summary>
        /// Performs OCR on an image and extracts text
        /// </summary>
        public string RecognizeText(Bitmap image)
        {
            if (!_initialized || _engine == null)
            {
                throw new InvalidOperationException("OCR engine not initialized. Call Initialize() first.");
            }

            try
            {
                // Convert Bitmap to Pix using manual conversion
                using (var pix = ConvertBitmapToPix(image))
                using (var page = _engine.Process(pix))
                {
                    return page.GetText();
                }
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException($"OCR processing failed: {ex.Message}", ex);
            }
        }

        /// <summary>
        /// Converts a Bitmap to Pix format for Tesseract
        /// </summary>
        private Pix ConvertBitmapToPix(Bitmap bitmap)
        {
            // Save bitmap to memory stream
            using (var ms = new MemoryStream())
            {
                bitmap.Save(ms, System.Drawing.Imaging.ImageFormat.Png);
                ms.Position = 0;
                
                // Load from stream using Tesseract
                return Pix.LoadFromMemory(ms.ToArray());
            }
        }

        /// <summary>
        /// Extracts verification code from text using pattern matching
        /// </summary>
        public string? ExtractVerificationCode(string text, string pattern)
        {
            if (string.IsNullOrWhiteSpace(text))
                return null;

            try
            {
                // Clean the text
                text = text.Replace(" ", "").Replace("\n", "").Replace("\r", "");

                // Try to match the pattern
                var regex = new Regex(pattern);
                var match = regex.Match(text);

                if (match.Success)
                {
                    return match.Value;
                }

                return null;
            }
            catch
            {
                return null;
            }
        }

        /// <summary>
        /// Performs OCR and attempts to extract verification code in one step
        /// </summary>
        public string? RecognizeAndExtractCode(Bitmap image, string pattern)
        {
            string text = RecognizeText(image);
            return ExtractVerificationCode(text, pattern);
        }

        /// <summary>
        /// Gets confidence score for the last OCR operation
        /// </summary>
        public float GetConfidence(Bitmap image)
        {
            if (!_initialized || _engine == null)
                return 0f;

            try
            {
                using (var pix = ConvertBitmapToPix(image))
                using (var page = _engine.Process(pix))
                {
                    return page.GetMeanConfidence();
                }
            }
            catch
            {
                return 0f;
            }
        }

        public void Dispose()
        {
            _engine?.Dispose();
            _engine = null;
            _initialized = false;
        }
    }
}