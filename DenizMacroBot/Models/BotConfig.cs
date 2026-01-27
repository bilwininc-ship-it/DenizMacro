using System.Drawing;
using Newtonsoft.Json;

namespace DenizMacroBot.Models
{
    /// <summary>
    /// Configuration model for the macro bot
    /// </summary>
    public class BotConfig
    {
        [JsonProperty("searchRegion")]
        public RegionConfig SearchRegion { get; set; } = new RegionConfig();

        [JsonProperty("delayMin")]
        public int DelayMin { get; set; } = 12000; // 12 seconds

        [JsonProperty("delayMax")]
        public int DelayMax { get; set; } = 18000; // 18 seconds

        [JsonProperty("tesseractDataPath")]
        public string TesseractDataPath { get; set; } = @".\Resources\tessdata";

        [JsonProperty("verificationCodePattern")]
        public string VerificationCodePattern { get; set; } = @"\d{4,8}"; // Multi-digit code pattern

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