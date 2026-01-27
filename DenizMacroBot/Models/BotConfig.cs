using System.Drawing;
using Newtonsoft.Json;

namespace DenizMacroBot.Models
{
    /// <summary>
    /// Configuration model for the macro bot - Template Matching version
    /// </summary>
    public class BotConfig
    {
        // Single main window region (entire verification dialog)
        [JsonProperty("mainWindowRegion")]
        public RegionConfig MainWindowRegion { get; set; } = new RegionConfig();

        // Template matching threshold (0.0 to 1.0, default 0.70)
        [JsonProperty("matchingThreshold")]
        public double MatchingThreshold { get; set; } = 0.70;

        // Click delay range (randomized between min and max)
        [JsonProperty("delayMin")]
        public int DelayMin { get; set; } = 4000; // 4 seconds

        [JsonProperty("delayMax")]
        public int DelayMax { get; set; } = 14000; // 14 seconds

        // How often to check for verification dialog (milliseconds)
        [JsonProperty("checkIntervalMs")]
        public int CheckIntervalMs { get; set; } = 5000; // Check every 5 seconds

        // Dynamic cropping percentages
        [JsonProperty("targetCodeTopPercent")]
        public double TargetCodeTopPercent { get; set; } = 0.20; // 20%

        [JsonProperty("targetCodeBottomPercent")]
        public double TargetCodeBottomPercent { get; set; } = 0.40; // 40%

        [JsonProperty("buttonsAreaTopPercent")]
        public double ButtonsAreaTopPercent { get; set; } = 0.40; // 40%

        [JsonProperty("buttonsAreaBottomPercent")]
        public double ButtonsAreaBottomPercent { get; set; } = 0.90; // 90%

        public bool AllRegionsConfigured => MainWindowRegion.IsValid;

        public static BotConfig LoadFromFile(string path)
        {
            if (!File.Exists(path))
                return new BotConfig();

            try
            {
                var json = File.ReadAllText(path);
                return JsonConvert.DeserializeObject<BotConfig>(json) ?? new BotConfig();
            }
            catch
            {
                return new BotConfig();
            }
        }

        public void SaveToFile(string path)
        {
            var json = JsonConvert.SerializeObject(this, Formatting.Indented);
            File.WriteAllText(path, json);
        }
    }

    public class RegionConfig
    {
        [JsonProperty("x")]
        public int X { get; set; }

        [JsonProperty("y")]
        public int Y { get; set; }

        [JsonProperty("width")]
        public int Width { get; set; }

        [JsonProperty("height")]
        public int Height { get; set; }

        [JsonIgnore]
        public Rectangle Rectangle => new Rectangle(X, Y, Width, Height);

        [JsonIgnore]
        public bool IsValid => Width > 0 && Height > 0;

        public void SetFromRectangle(Rectangle rect)
        {
            X = rect.X;
            Y = rect.Y;
            Width = rect.Width;
            Height = rect.Height;
        }
    }
}