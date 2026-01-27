using System.Drawing;
using Newtonsoft.Json;

namespace DenizMacroBot.Models
{
    /// <summary>
    /// Configuration model for the macro bot
    /// </summary>
    public class BotConfig
    {
        [JsonProperty("greenCodeRegion")]
        public RegionConfig GreenCodeRegion { get; set; } = new RegionConfig();

        [JsonProperty("button1Region")]
        public RegionConfig Button1Region { get; set; } = new RegionConfig();

        [JsonProperty("button2Region")]
        public RegionConfig Button2Region { get; set; } = new RegionConfig();

        [JsonProperty("button3Region")]
        public RegionConfig Button3Region { get; set; } = new RegionConfig();

        [JsonProperty("button4Region")]
        public RegionConfig Button4Region { get; set; } = new RegionConfig();

        [JsonProperty("delayMin")]
        public int DelayMin { get; set; } = 4000; // 4 seconds

        [JsonProperty("delayMax")]
        public int DelayMax { get; set; } = 14000; // 14 seconds

        [JsonProperty("checkIntervalMs")]
        public int CheckIntervalMs { get; set; } = 500; // Check every 0.5 seconds - FAST!

        [JsonProperty("tesseractDataPath")]
        public string TesseractDataPath { get; set; } = @".\Resources\tessdata";

        [JsonProperty("verificationCodePattern")]
        public string VerificationCodePattern { get; set; } = @"\d{4,7}"; // 4-7 digit code pattern - flexible!

        public bool AllRegionsConfigured =>
            GreenCodeRegion.IsValid &&
            Button1Region.IsValid &&
            Button2Region.IsValid &&
            Button3Region.IsValid &&
            Button4Region.IsValid;

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