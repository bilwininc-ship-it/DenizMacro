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
        /// Applies Binary Threshold to focus on number shapes (ignores colors)
        /// </summary>
        public Mat ApplyBinaryThreshold(Mat grayMat, double thresholdValue = 128)
        {
            Mat thresholdMat = new Mat();
            Cv2.Threshold(grayMat, thresholdMat, thresholdValue, 255, ThresholdTypes.Binary);
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
        /// Preprocesses image: Grayscale + Binary Threshold
        /// </summary>
        public Mat PreprocessImage(Bitmap bitmap, bool useCanny = false)
        {
            using (Mat grayMat = ConvertToGrayscale(bitmap))
            {
                if (useCanny)
                {
                    return ApplyCannyEdgeDetection(grayMat);
                }
                else
                {
                    return ApplyBinaryThreshold(grayMat);
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
        /// Returns: (buttonIndex, similarityScore, usedCanny)
        /// </summary>
        public (int buttonIndex, double similarity, bool usedCanny) FindBestMatch(
            Bitmap targetCodeBitmap, 
            Bitmap[] buttonBitmaps, 
            double minimumThreshold)
        {
            Mat targetProcessed = null;
            Mat targetCannyProcessed = null;
            Mat[] buttonsProcessed = new Mat[4];
            Mat[] buttonsCannyProcessed = new Mat[4];

            try
            {
                // First try: Binary Threshold preprocessing
                targetProcessed = PreprocessImage(targetCodeBitmap, useCanny: false);
                
                double[] scores = new double[4];
                for (int i = 0; i < 4; i++)
                {
                    buttonsProcessed[i] = PreprocessImage(buttonBitmaps[i], useCanny: false);
                    scores[i] = MatchTemplate(targetProcessed, buttonsProcessed[i]);
                }

                // Find best match
                int bestIndex = Array.IndexOf(scores, scores.Max());
                double bestScore = scores[bestIndex];

                // If threshold met, return result
                if (bestScore >= minimumThreshold)
                {
                    return (bestIndex, bestScore, usedCanny: false);
                }

                // Second try: Canny Edge Detection (fallback)
                targetCannyProcessed = PreprocessImage(targetCodeBitmap, useCanny: true);
                
                double[] cannyScores = new double[4];
                for (int i = 0; i < 4; i++)
                {
                    buttonsCannyProcessed[i] = PreprocessImage(buttonBitmaps[i], useCanny: true);
                    cannyScores[i] = MatchTemplate(targetCannyProcessed, buttonsCannyProcessed[i]);
                }

                // Find best match with Canny
                int bestCannyIndex = Array.IndexOf(cannyScores, cannyScores.Max());
                double bestCannyScore = cannyScores[bestCannyIndex];

                return (bestCannyIndex, bestCannyScore, usedCanny: true);
            }
            finally
            {
                // Dispose all OpenCV Mats
                targetProcessed?.Dispose();
                targetCannyProcessed?.Dispose();
                
                foreach (var mat in buttonsProcessed)
                {
                    mat?.Dispose();
                }
                
                foreach (var mat in buttonsCannyProcessed)
                {
                    mat?.Dispose();
                }
            }
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

            // Save original images
            targetCode.Save(System.IO.Path.Combine(outputFolder, "0_target_original.png"));
            for (int i = 0; i < buttons.Length; i++)
            {
                buttons[i].Save(System.IO.Path.Combine(outputFolder, $"{i + 1}_button{i + 1}_original.png"));
            }

            // Save preprocessed (threshold) images
            using (Mat targetThreshold = PreprocessImage(targetCode, useCanny: false))
            {
                targetThreshold.SaveImage(System.IO.Path.Combine(outputFolder, "0_target_threshold.png"));
            }

            for (int i = 0; i < buttons.Length; i++)
            {
                using (Mat buttonThreshold = PreprocessImage(buttons[i], useCanny: false))
                {
                    buttonThreshold.SaveImage(System.IO.Path.Combine(outputFolder, $"{i + 1}_button{i + 1}_threshold.png"));
                }
            }

            // Save preprocessed (canny) images
            using (Mat targetCanny = PreprocessImage(targetCode, useCanny: true))
            {
                targetCanny.SaveImage(System.IO.Path.Combine(outputFolder, "0_target_canny.png"));
            }

            for (int i = 0; i < buttons.Length; i++)
            {
                using (Mat buttonCanny = PreprocessImage(buttons[i], useCanny: true))
                {
                    buttonCanny.SaveImage(System.IO.Path.Combine(outputFolder, $"{i + 1}_button{i + 1}_canny.png"));
                }
            }
        }

        public void Dispose()
        {
            GC.SuppressFinalize(this);
        }
    }
}
