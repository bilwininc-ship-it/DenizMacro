using System;
using System.Drawing;
using System.Runtime.InteropServices;
using System.Threading;
using System.Threading.Tasks;

namespace DenizMacroBot.Utils
{
    /// <summary>
    /// Provides stealth mouse control with curved, natural movements
    /// </summary>
    public static class MouseHelper
    {
        #region Win32 API

        [DllImport("user32.dll")]
        private static extern bool SetCursorPos(int x, int y);

        [DllImport("user32.dll")]
        private static extern void mouse_event(uint dwFlags, int dx, int dy, uint dwData, int dwExtraInfo);

        [DllImport("user32.dll")]
        private static extern bool GetCursorPos(out POINT lpPoint);

        [StructLayout(LayoutKind.Sequential)]
        private struct POINT
        {
            public int X;
            public int Y;
        }

        private const uint MOUSEEVENTF_LEFTDOWN = 0x0002;
        private const uint MOUSEEVENTF_LEFTUP = 0x0004;
        private const uint MOUSEEVENTF_RIGHTDOWN = 0x0008;
        private const uint MOUSEEVENTF_RIGHTUP = 0x0010;

        #endregion

        private static readonly Random _random = new Random();

        /// <summary>
        /// Gets the current cursor position
        /// </summary>
        public static Point GetCursorPosition()
        {
            GetCursorPos(out POINT point);
            return new Point(point.X, point.Y);
        }

        /// <summary>
        /// Moves the mouse to target position using a natural curved path
        /// </summary>
        public static async Task MoveToAsync(Point target, CancellationToken cancellationToken = default)
        {
            Point start = GetCursorPosition();
            
            // Don't move if already at target
            if (start.X == target.X && start.Y == target.Y)
                return;

            // Generate bezier curve points for natural movement
            var points = GenerateBezierCurve(start, target, 25 + _random.Next(15));

            foreach (var point in points)
            {
                if (cancellationToken.IsCancellationRequested)
                    break;

                SetCursorPos(point.X, point.Y);
                
                // Random micro-delays for human-like movement (1-3ms)
                await Task.Delay(_random.Next(1, 4), cancellationToken);
            }

            // Ensure we end exactly at target
            SetCursorPos(target.X, target.Y);
        }

        /// <summary>
        /// Performs a left click at the current position
        /// </summary>
        public static async Task ClickAsync(CancellationToken cancellationToken = default)
        {
            // Random pre-click delay (5-15ms)
            await Task.Delay(_random.Next(5, 16), cancellationToken);

            mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0);
            
            // Random click hold time (40-80ms)
            await Task.Delay(_random.Next(40, 81), cancellationToken);
            
            mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0);

            // Random post-click delay (5-15ms)
            await Task.Delay(_random.Next(5, 16), cancellationToken);
        }

        /// <summary>
        /// Moves to target and clicks with natural timing
        /// </summary>
        public static async Task MoveAndClickAsync(Point target, CancellationToken cancellationToken = default)
        {
            await MoveToAsync(target, cancellationToken);
            
            // Random pause before clicking (50-150ms) - humans don't click instantly
            await Task.Delay(_random.Next(50, 151), cancellationToken);
            
            await ClickAsync(cancellationToken);
        }

        /// <summary>
        /// Performs a right click at the current position
        /// </summary>
        public static async Task RightClickAsync(CancellationToken cancellationToken = default)
        {
            await Task.Delay(_random.Next(5, 16), cancellationToken);
            
            mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0);
            await Task.Delay(_random.Next(40, 81), cancellationToken);
            mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0);
            
            await Task.Delay(_random.Next(5, 16), cancellationToken);
        }

        /// <summary>
        /// Generates a randomized delay within the specified range
        /// </summary>
        public static async Task RandomDelayAsync(int minMs, int maxMs, CancellationToken cancellationToken = default)
        {
            int delay = _random.Next(minMs, maxMs + 1);
            await Task.Delay(delay, cancellationToken);
        }

        /// <summary>
        /// Generates bezier curve points for natural mouse movement
        /// </summary>
        private static Point[] GenerateBezierCurve(Point start, Point end, int steps)
        {
            // Generate control points for a cubic Bezier curve
            // This creates a natural, slightly curved path
            
            int dx = end.X - start.X;
            int dy = end.Y - start.Y;
            
            // Add some randomness to the curve
            int offsetX = _random.Next(-Math.Abs(dx / 4), Math.Abs(dx / 4) + 1);
            int offsetY = _random.Next(-Math.Abs(dy / 4), Math.Abs(dy / 4) + 1);
            
            Point control1 = new Point(
                start.X + dx / 3 + offsetX,
                start.Y + dy / 3 - offsetY
            );
            
            Point control2 = new Point(
                start.X + 2 * dx / 3 - offsetX,
                start.Y + 2 * dy / 3 + offsetY
            );

            Point[] points = new Point[steps];
            
            for (int i = 0; i < steps; i++)
            {
                double t = i / (double)(steps - 1);
                points[i] = CalculateBezierPoint(t, start, control1, control2, end);
            }
            
            return points;
        }

        /// <summary>
        /// Calculates a point on a cubic Bezier curve
        /// </summary>
        private static Point CalculateBezierPoint(double t, Point p0, Point p1, Point p2, Point p3)
        {
            double u = 1 - t;
            double tt = t * t;
            double uu = u * u;
            double uuu = uu * u;
            double ttt = tt * t;

            int x = (int)(uuu * p0.X + 3 * uu * t * p1.X + 3 * u * tt * p2.X + ttt * p3.X);
            int y = (int)(uuu * p0.Y + 3 * uu * t * p1.Y + 3 * u * tt * p2.Y + ttt * p3.Y);

            return new Point(x, y);
        }

        /// <summary>
        /// Adds a small random jitter to a point (useful for click positions)
        /// </summary>
        public static Point AddJitter(Point point, int maxJitter = 3)
        {
            return new Point(
                point.X + _random.Next(-maxJitter, maxJitter + 1),
                point.Y + _random.Next(-maxJitter, maxJitter + 1)
            );
        }
    }
}