using System;
using System.Collections.Generic;
using System.IO;
using System.Text;




namespace lab2
{
    public class Printer : IDisposable
    {
        private static Dictionary<char, string[]> _font = new Dictionary<char, string[]>();
        private static bool _isFontLoaded = false;
        
        // ANSI escape codes
        private const string Escape = "\u001b[";
        private const string Reset = "\u001b[0m";
        
        
        private readonly Color _defaultColor;
        private readonly (int x, int y) _defaultPosition;
        private readonly string _defaultSymbol;
        private readonly StringBuilder _ansiBuilder = new StringBuilder();

        public Printer(Color color, (int x, int y) position, string symbol = "*")
        {
            _defaultColor = color;
            _defaultPosition = position;
            _defaultSymbol = symbol;
            
            if (!_isFontLoaded)
            {
                throw new InvalidOperationException("Font not loaded. Call LoadFont first.");
            }
        }

        public static void LoadFont(string fontFilePath)
        {
            _font.Clear();
            
            if (!File.Exists(fontFilePath))
            {
                throw new FileNotFoundException($"Font file not found: {fontFilePath}");
            }

            var lines = File.ReadAllLines(fontFilePath);
            var currentChar = ' ';
            var charLines = new List<string>();
            var charHeight = 0;

            foreach (var line in lines)
            {
                if (line.StartsWith("CHAR:"))
                {
                    if (currentChar != ' ' && charLines.Count > 0)
                    {
                        _font[currentChar] = charLines.ToArray();
                    }
                    
                    currentChar = line[5];
                    charLines.Clear();
                    charHeight = 0;
                }
                else if (line.StartsWith("HEIGHT:"))
                {
                    charHeight = int.Parse(line.Substring(7));
                }
                else if (!string.IsNullOrWhiteSpace(line) && currentChar != ' ')
                {
                    charLines.Add(line);
                }
            }

            if (currentChar != ' ' && charLines.Count > 0)
            {
                _font[currentChar] = charLines.ToArray();
            }

            _isFontLoaded = true;
        }

        private static string GetColorCode(Color color)
        {
            return $"{Escape}{(int)color}m";
        }

        private static void SetCursorPosition(int x, int y)
        {
            Console.SetCursorPosition(x, y);
        }

        public void Print(string text)
        {
            Print(text, _defaultColor, _defaultPosition, _defaultSymbol);
        }

        public static void Print(string text, Color color, (int x, int y) position, string symbol = "*")
        {
            if (!_isFontLoaded)
            {
                throw new InvalidOperationException("Font not loaded. Call LoadFont first.");
            }

            var colorCode = GetColorCode(color);
            var currentX = position.x;
            var currentY = position.y;

            foreach (char c in text.ToUpper())
            {
                if (_font.ContainsKey(c))
                {
                    var charPattern = _font[c];
                    for (int i = 0; i < charPattern.Length; i++)
                    {
                        SetCursorPosition(currentX, currentY + i);
                        var line = charPattern[i].Replace("*", symbol);
                        Console.Write($"{colorCode}{line}{Reset}");
                    }
                    currentX += GetCharWidth(charPattern) + 1;
                }
                else if (c == ' ')
                {
                    currentX += 4;
                }
            }
        }

        private static int GetCharWidth(string[] charPattern)
        {
            int maxWidth = 1;
            foreach (var line in charPattern)
            {
                if (line.Length > maxWidth)
                {
                    maxWidth = line.Length;
                }
            }
            return maxWidth;
        }

        public void Dispose()
        {
            Console.ResetColor();
            Console.SetCursorPosition(0, Console.WindowHeight -1);
        }
    }
}