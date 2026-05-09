using System;
using System.Collections.Generic;
using System.IO;
using System.Text.Json;

class JsonParser
{
    static void Main(string[] args)
    {
        if (args.Length < 1)
        {
            Console.WriteLine("Usage: JsonParser <file.json> [flatten|structure|pretty]");
            Console.WriteLine("  flatten   - print all values with their key paths (default)");
            Console.WriteLine("  structure - print nested structure overview");
            Console.WriteLine("  pretty    - pretty-print the JSON");
            return;
        }

        string filepath = args[0];
        string mode = args.Length > 1 ? args[1] : "flatten";

        string jsonText = File.ReadAllText(filepath);
        using JsonDocument doc = JsonDocument.Parse(jsonText);
        JsonElement root = doc.RootElement;

        switch (mode)
        {
            case "flatten":
                foreach (var (path, value) in Flatten(root, ""))
                    Console.WriteLine($"{path} = {value}");
                break;

            case "structure":
                PrintStructure(root, 0);
                break;

            case "pretty":
                var options = new JsonSerializerOptions { WriteIndented = true };
                Console.WriteLine(JsonSerializer.Serialize(JsonSerializer.Deserialize<object>(jsonText), options));
                break;

            default:
                Console.WriteLine($"Unknown mode: {mode}");
                break;
        }
    }

    static IEnumerable<(string Path, string Value)> Flatten(JsonElement element, string prefix)
    {
        switch (element.ValueKind)
        {
            case JsonValueKind.Array:
                int i = 0;
                foreach (var item in element.EnumerateArray())
                    foreach (var entry in Flatten(item, $"{prefix}[{i++}]"))
                        yield return entry;
                break;

            case JsonValueKind.Object:
                foreach (var prop in element.EnumerateObject())
                {
                    string newKey = string.IsNullOrEmpty(prefix) ? prop.Name : $"{prefix}.{prop.Name}";
                    foreach (var entry in Flatten(prop.Value, newKey))
                        yield return entry;
                }
                break;

            default:
                yield return (prefix, element.ToString());
                break;
        }
    }

    static void PrintStructure(JsonElement element, int indent)
    {
        string pad = new string(' ', indent * 2);

        switch (element.ValueKind)
        {
            case JsonValueKind.Array:
                int count = 0;
                foreach (var _ in element.EnumerateArray()) count++;
                Console.WriteLine($"{pad}Array ({count} items)");
                int i = 0;
                foreach (var item in element.EnumerateArray())
                {
                    Console.WriteLine($"{pad}  [{i++}]:");
                    PrintStructure(item, indent + 2);
                }
                break;

            case JsonValueKind.Object:
                int keyCount = 0;
                foreach (var _ in element.EnumerateObject()) keyCount++;
                Console.WriteLine($"{pad}Object ({keyCount} keys)");
                foreach (var prop in element.EnumerateObject())
                {
                    Console.WriteLine($"{pad}  {prop.Name}:");
                    PrintStructure(prop.Value, indent + 2);
                }
                break;

            default:
                Console.WriteLine($"{pad}{element}");
                break;
        }
    }
}
