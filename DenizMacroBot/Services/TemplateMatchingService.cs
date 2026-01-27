using System;
using System.Drawing;
using System.Drawing.Imaging;
using OpenCvSharp;
using OpenCvSharp.Extensions;

namespace DenizMacroBot.Services
{
    /// <summary>
    /// Template Matching Service using OpenCvSharp4
    /// Handles dynamic cropping, preprocessing, and template matching
    /// </summary>
    public class TemplateMatchingService : IDisposable
    {
        private readonly object _matchLock = new object();

        /// <summary>
        /// Crops a region from the main window based on relative coordinates (percentage)
        /// </summary>
        public Bitmap CropRegion(Bitmap mainWindow, double topPercent, double bottomPercent)
        {
            int startY = (int)(mainWindow.Height * topPercent);
            int endY = (int)(mainWindow.Height * bottomPercent);
            int height = endY - startY;

            if (height <= 0 || startY < 0 || endY > mainWindow.Height)
            {
                throw new ArgumentException($"Invalid crop percentages: {topPercent}-{bottomPercent}");
            }

            Rectangle cropRect = new Rectangle(0, startY, mainWindow.Width, height);
            
            Bitmap croppedBitmap = new Bitmap(cropRect.Width, cropRect.Height, PixelFormat.Format24bppRgb);
            using (Graphics g = Graphics.FromImage(croppedBitmap))
            {
                g.DrawImage(mainWindow, 
                    new Rectangle(0, 0, cropRect.Width, cropRect.Height),
                    cropRect,
                    GraphicsUnit.Pixel);
            }

            return croppedBitmap;
        }

        /// <summary>
        /// Divides the buttons area into 4 equal vertical parts
        /// </summary>
        public Bitmap[] SplitButtonsArea(Bitmap buttonsArea)
        {
            int buttonHeight = buttonsArea.Height / 4;
            Bitmap[] buttons = new Bitmap[4];

            for (int i = 0; i < 4; i++)
            {
                int startY = i * buttonHeight;
                Rectangle buttonRect = new Rectangle(0, startY, buttonsArea.Width, buttonHeight);
                
                buttons[i] = new Bitmap(buttonRect.Width, buttonRect.Height, PixelFormat.Format24bppRgb);
                using (Graphics g = Graphics.FromImage(buttons[i]))
                {
                    g.DrawImage(buttonsArea,
                        new Rectangle(0, 0, buttonRect.Width, buttonRect.Height),
                        buttonRect,
                        GraphicsUnit.Pixel);
                }
            }

            return buttons;
        }

        /// <summary>
        /// Converts image to grayscale using OpenCV
        /// </summary>
        public Mat ConvertToGrayscale(Bitmap bitmap)
        {
            using (Mat colorMat = BitmapConverter.ToMat(bitmap))
            {
                Mat grayMat = new Mat();
                Cv2.CvtColor(colorMat, grayMat, ColorConversionCodes.BGR2GRAY);
                return grayMat;
            }
        }

        /// <summary>
        /// Applies Adaptive Threshold for better handling of lighting variations
        /// </summary>
        public Mat ApplyAdaptiveThreshold(Mat grayMat)
        {
            Mat thresholdMat = new Mat();
            Cv2.AdaptiveThreshold(grayMat, thresholdMat, 255, 
                AdaptiveThresholdTypes.GaussianC, ThresholdTypes.Binary, 11, 2);
            return thresholdMat;
        }
        /// <summary>
        /// Applies Binary Threshold to focus on number shapes (ignores colors)
        /// </summary>
        public Mat ApplyBinaryThreshold(Mat grayMat, double thresholdValue = 128)
        {
            Mat thresholdMat = new Mat();
            Cv2.Threshold(grayMat, thresholdMat, thresholdValue, 255, ThresholdTypes.Binary);
            return thresholdMat;
        }
        
        /// <summary>
        /// Applies OTSU threshold for automatic threshold calculation
        /// </summary>
        public Mat ApplyOtsuThreshold(Mat grayMat)
        {
            Mat thresholdMat = new Mat();
            Cv2.Threshold(grayMat, thresholdMat, 0, 255, ThresholdTypes.Binary | ThresholdTypes.Otsu);
            return thresholdMat;
        }

        /// <summary>
        /// Applies Canny Edge Detection as fallback preprocessing
        /// </summary>
        public Mat ApplyCannyEdgeDetection(Mat grayMat, double threshold1 = 50, double threshold2 = 150)
        {
            Mat cannyMat = new Mat();
            Cv2.Canny(grayMat, cannyMat, threshold1, threshold2);
            return cannyMat;
        }

        /// <summary>
        /// Preprocesses image: Grayscale + Multiple Threshold Attempts
        /// </summary>
        public Mat PreprocessImage(Bitmap bitmap, int method = 0)
        {
            using (Mat grayMat = ConvertToGrayscale(bitmap))
            {
                switch (method)
                {
                    case 0: // Adaptive Threshold (Best for varying lighting)
                        return ApplyAdaptiveThreshold(grayMat);
                    case 1: // OTSU (Automatic threshold)
                        return ApplyOtsuThreshold(grayMat);
                    case 2: // Binary Threshold
                        return ApplyBinaryThreshold(grayMat);
                    case 3: // Canny Edge Detection
                        return ApplyCannyEdgeDetection(grayMat);
                    default:
                        return ApplyAdaptiveThreshold(grayMat);
                }
            }
        }

        /// <summary>
        /// Performs template matching between target and template
        /// Returns similarity score (0.0 to 1.0)
        /// </summary>
        public double MatchTemplate(Mat target, Mat template)
        {
            lock (_matchLock)
            {
                // Ensure both images are the same size for direct comparison
                if (target.Width != template.Width || target.Height != template.Height)
                {
                    // Resize template to match target size
                    using (Mat resizedTemplate = new Mat())
                    {
                        Cv2.Resize(template, resizedTemplate, new OpenCvSharp.Size(target.Width, target.Height));
                        return PerformMatching(target, resizedTemplate);
                    }
                }
                else
                {
                    return PerformMatching(target, template);
                }
            }
        }

        /// <summary>
        /// Internal method to perform actual template matching
        /// </summary>
        private double PerformMatching(Mat target, Mat template)
        {
            try
            {
                using (Mat result = new Mat())
                {
                    Cv2.MatchTemplate(target, template, result, TemplateMatchModes.CCoeffNormed);
                    
                    // Get min and max values
                    Cv2.MinMaxLoc(result, out double minVal, out double maxVal, out _, out _);
                    
                    // CCoeffNormed returns values between -1 and 1, where 1 is perfect match
                    // We return the max value (best match score)
                    return maxVal;
                }
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException($"Template matching failed: {ex.Message}", ex);
            }
        }

        /// <summary>
        /// Compares target code against all 4 buttons and finds the best match
        /// Uses multi-method preprocessing for better accuracy
        /// Returns: (buttonIndex, similarityScore, methodUsed)
        /// </summary>
        public (int buttonIndex, double similarity, string methodUsed) FindBestMatch(
            Bitmap targetCodeBitmap, 
            Bitmap[] buttonBitmaps, 
            double minimumThreshold)
        {
            // Method names for logging
            string[] methodNames = { "Adaptive Threshold", "OTSU", "Binary Threshold", "Canny Edge" };
            
            // Try all 4 preprocessing methods
            for (int method = 0; method < 4; method++)
            {
                Mat targetProcessed = null;
                Mat[] buttonsProcessed = new Mat[4];

                try
                {
                    // Preprocess target code with current method
                    targetProcessed = PreprocessImage(targetCodeBitmap, method);
                    
                    // Preprocess all buttons and calculate scores
                    double[] scores = new double[4];
                    for (int i = 0; i < 4; i++)
                    {
                        buttonsProcessed[i] = PreprocessImage(buttonBitmaps[i], method);
                        scores[i] = MatchTemplate(targetProcessed, buttonsProcessed[i]);
                    }

                    // Find best match
                    int bestIndex = Array.IndexOf(scores, scores.Max());
                    double bestScore = scores[bestIndex];

                    // If threshold met, return immediately
                    if (bestScore >= minimumThreshold)
                    {
                        return (bestIndex, bestScore, methodNames[method]);
                    }
                    
                    // If this is the last method, return best found
                    if (method == 3)
                    {
                        return (bestIndex, bestScore, methodNames[method]);
                    }
                }
                finally
                {
                    // Dispose all Mats
                    targetProcessed?.Dispose();
                    foreach (var mat in buttonsProcessed)
                    {
                        mat?.Dispose();
                    }
                }
            }

            // Fallback (should never reach here)
            return (0, 0.0, "None");
        }

        /// <summary>
        /// Debug method: Saves preprocessed images to disk for inspection
        /// </summary>
        public void SaveDebugImages(Bitmap targetCode, Bitmap[] buttons, string outputFolder)
        {
            if (!System.IO.Directory.Exists(outputFolder))
            {
                System.IO.Directory.CreateDirectory(outputFolder);
            }

            string[] methodNames = { "adaptive", "otsu", "binary", "canny" };

            // Save original images
            targetCode.Save(System.IO.Path.Combine(outputFolder, "0_target_original.png"));
            for (int i = 0; i < buttons.Length; i++)
            {
                buttons[i].Save(System.IO.Path.Combine(outputFolder, $"{i + 1}_button{i + 1}_original.png"));
            }

            // Save preprocessed images for all methods
            for (int method = 0; method < 4; method++)
            {
                using (Mat targetProcessed = PreprocessImage(targetCode, method))
                {
                    targetProcessed.SaveImage(System.IO.Path.Combine(outputFolder, $"0_target_{methodNames[method]}.png"));
                }

                for (int i = 0; i < buttons.Length; i++)
                {
                    using (Mat buttonProcessed = PreprocessImage(buttons[i], method))
                    {
                        buttonProcessed.SaveImage(System.IO.Path.Combine(outputFolder, $"{i + 1}_button{i + 1}_{methodNames[method]}.png"));
                    }
                }
            }
        }

        public void Dispose()
        {
            GC.SuppressFinalize(this);
        }
    }
}
