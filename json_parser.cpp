#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <stdexcept>
#include <cctype>

// Minimal JSON value type
struct JsonValue {
    enum Type { Null, Bool, Number, String, Array, Object };
    Type type = Null;

    bool boolean = false;
    double number = 0;
    std::string string;
    std::vector<JsonValue> array;
    std::vector<std::pair<std::string, JsonValue>> object;
};

// ---------- Parser ----------

static void skipWhitespace(const std::string& s, size_t& pos) {
    while (pos < s.size() && std::isspace((unsigned char)s[pos])) pos++;
}

static std::string parseString(const std::string& s, size_t& pos) {
    pos++; // skip opening "
    std::string result;
    while (pos < s.size() && s[pos] != '"') {
        if (s[pos] == '\\') {
            pos++;
            switch (s[pos]) {
                case '"':  result += '"';  break;
                case '\\': result += '\\'; break;
                case '/':  result += '/';  break;
                case 'n':  result += '\n'; break;
                case 't':  result += '\t'; break;
                case 'r':  result += '\r'; break;
                default:   result += s[pos];
            }
        } else {
            result += s[pos];
        }
        pos++;
    }
    pos++; // skip closing "
    return result;
}

static JsonValue parseValue(const std::string& s, size_t& pos);

static JsonValue parseArray(const std::string& s, size_t& pos) {
    JsonValue val;
    val.type = JsonValue::Array;
    pos++; // skip '['
    skipWhitespace(s, pos);
    if (s[pos] == ']') { pos++; return val; }
    while (true) {
        skipWhitespace(s, pos);
        val.array.push_back(parseValue(s, pos));
        skipWhitespace(s, pos);
        if (s[pos] == ']') { pos++; break; }
        if (s[pos] == ',') pos++;
    }
    return val;
}

static JsonValue parseObject(const std::string& s, size_t& pos) {
    JsonValue val;
    val.type = JsonValue::Object;
    pos++; // skip '{'
    skipWhitespace(s, pos);
    if (s[pos] == '}') { pos++; return val; }
    while (true) {
        skipWhitespace(s, pos);
        std::string key = parseString(s, pos);
        skipWhitespace(s, pos);
        pos++; // skip ':'
        skipWhitespace(s, pos);
        val.object.emplace_back(key, parseValue(s, pos));
        skipWhitespace(s, pos);
        if (s[pos] == '}') { pos++; break; }
        if (s[pos] == ',') pos++;
    }
    return val;
}

static JsonValue parseValue(const std::string& s, size_t& pos) {
    skipWhitespace(s, pos);
    JsonValue val;

    if (s[pos] == '"') {
        val.type = JsonValue::String;
        val.string = parseString(s, pos);
    } else if (s[pos] == '[') {
        val = parseArray(s, pos);
    } else if (s[pos] == '{') {
        val = parseObject(s, pos);
    } else if (s.substr(pos, 4) == "true") {
        val.type = JsonValue::Bool; val.boolean = true; pos += 4;
    } else if (s.substr(pos, 5) == "false") {
        val.type = JsonValue::Bool; val.boolean = false; pos += 5;
    } else if (s.substr(pos, 4) == "null") {
        val.type = JsonValue::Null; pos += 4;
    } else {
        val.type = JsonValue::Number;
        size_t start = pos;
        if (s[pos] == '-') pos++;
        while (pos < s.size() && (std::isdigit((unsigned char)s[pos]) || s[pos] == '.' || s[pos] == 'e' || s[pos] == 'E' || s[pos] == '+' || s[pos] == '-'))
            pos++;
        val.number = std::stod(s.substr(start, pos - start));
    }
    return val;
}

static JsonValue parse(const std::string& s) {
    size_t pos = 0;
    return parseValue(s, pos);
}

// ---------- Modes ----------

static std::string valueToString(const JsonValue& v) {
    switch (v.type) {
        case JsonValue::Null:   return "null";
        case JsonValue::Bool:   return v.boolean ? "true" : "false";
        case JsonValue::Number: {
            std::ostringstream ss;
            ss << v.number;
            return ss.str();
        }
        case JsonValue::String: return "\"" + v.string + "\"";
        default: return "";
    }
}

static void flatten(const JsonValue& val, const std::string& prefix) {
    switch (val.type) {
        case JsonValue::Array:
            for (size_t i = 0; i < val.array.size(); i++)
                flatten(val.array[i], prefix + "[" + std::to_string(i) + "]");
            break;
        case JsonValue::Object:
            for (const auto& kv : val.object)
                flatten(kv.second, prefix.empty() ? kv.first : prefix + "." + kv.first);
            break;
        default:
            std::cout << prefix << " = " << valueToString(val) << "\n";
    }
}

static void printStructure(const JsonValue& val, int indent) {
    std::string pad(indent * 2, ' ');
    switch (val.type) {
        case JsonValue::Array:
            std::cout << pad << "Array (" << val.array.size() << " items)\n";
            for (size_t i = 0; i < val.array.size(); i++) {
                std::cout << pad << "  [" << i << "]:\n";
                printStructure(val.array[i], indent + 2);
            }
            break;
        case JsonValue::Object:
            std::cout << pad << "Object (" << val.object.size() << " keys)\n";
            for (const auto& kv : val.object) {
                std::cout << pad << "  " << kv.first << ":\n";
                printStructure(kv.second, indent + 2);
            }
            break;
        default:
            std::cout << pad << valueToString(val) << "\n";
    }
}

static void pretty(const JsonValue& val, int indent) {
    std::string pad(indent * 2, ' ');
    std::string innerPad((indent + 1) * 2, ' ');
    switch (val.type) {
        case JsonValue::Array:
            if (val.array.empty()) { std::cout << "[]"; return; }
            std::cout << "[\n";
            for (size_t i = 0; i < val.array.size(); i++) {
                std::cout << innerPad;
                pretty(val.array[i], indent + 1);
                if (i + 1 < val.array.size()) std::cout << ",";
                std::cout << "\n";
            }
            std::cout << pad << "]";
            break;
        case JsonValue::Object:
            if (val.object.empty()) { std::cout << "{}"; return; }
            std::cout << "{\n";
            for (size_t i = 0; i < val.object.size(); i++) {
                std::cout << innerPad << "\"" << val.object[i].first << "\": ";
                pretty(val.object[i].second, indent + 1);
                if (i + 1 < val.object.size()) std::cout << ",";
                std::cout << "\n";
            }
            std::cout << pad << "}";
            break;
        default:
            std::cout << valueToString(val);
    }
}

// ---------- Main ----------

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cout << "Usage: json_parser <file.json> [flatten|structure|pretty]\n";
        std::cout << "  flatten   - print all values with their key paths (default)\n";
        std::cout << "  structure - print nested structure overview\n";
        std::cout << "  pretty    - pretty-print the JSON\n";
        return 1;
    }

    std::ifstream file(argv[1]);
    if (!file) { std::cerr << "Error: cannot open file '" << argv[1] << "'\n"; return 1; }

    std::ostringstream ss;
    ss << file.rdbuf();
    std::string jsonText = ss.str();

    JsonValue root = parse(jsonText);

    std::string mode = argc > 2 ? argv[2] : "flatten";

    if (mode == "flatten")
        flatten(root, "");
    else if (mode == "structure")
        printStructure(root, 0);
    else if (mode == "pretty") {
        pretty(root, 0);
        std::cout << "\n";
    } else {
        std::cerr << "Unknown mode: " << mode << "\n";
        return 1;
    }

    return 0;
}
