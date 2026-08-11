#!/usr/bin/env swift

import AppKit
import Foundation

let resourceRoot = "/System/Library/CoreServices/CoreGlyphs.bundle/Contents/Resources"
let orderURL = URL(fileURLWithPath: resourceRoot).appendingPathComponent("symbol_order.plist")
let searchURL = URL(fileURLWithPath: resourceRoot).appendingPathComponent("symbol_search.plist")

func loadPlist<T>(_ url: URL, as type: T.Type) throws -> T {
    let data = try Data(contentsOf: url)
    let value = try PropertyListSerialization.propertyList(from: data, options: [], format: nil)
    guard let typed = value as? T else {
        throw NSError(domain: "sf-symbols", code: 1, userInfo: [NSLocalizedDescriptionKey: "Unexpected plist format: \(url.path)"])
    }
    return typed
}

func catalog() throws -> [String] {
    try loadPlist(orderURL, as: [String].self)
}

func searchIndex() throws -> [String: [String]] {
    try loadPlist(searchURL, as: [String: [String]].self)
}

func isLocalizedVariant(_ name: String) -> Bool {
    let suffixes = [".ar", ".he", ".hi", ".ja", ".ko", ".th", ".zh", ".rtl"]
    return suffixes.contains { name.hasSuffix($0) }
}

func search(_ terms: [String], limit: Int) throws -> [String] {
    let names = try catalog()
    let index = try searchIndex()
    let needles = terms.map { $0.lowercased() }.filter { !$0.isEmpty }

    let scored: [(String, Int, Int)] = names.enumerated().compactMap { position, name in
        guard !isLocalizedVariant(name) else { return nil }
        let lowerName = name.lowercased()
        let keywords = (index[name] ?? []).map { $0.lowercased() }
        var score = 0
        for needle in needles {
            if lowerName == needle { score += 100 }
            if lowerName.hasPrefix(needle + ".") { score += 40 }
            if lowerName.contains(needle) { score += 25 }
            if keywords.contains(needle) { score += 30 }
            if keywords.contains(where: { $0.contains(needle) || needle.contains($0) }) { score += 12 }
        }
        if name.hasSuffix(".fill") { score += 2 }
        return score > 0 ? (name, score, position) : nil
    }

    return scored
        .sorted { lhs, rhs in lhs.1 == rhs.1 ? lhs.2 < rhs.2 : lhs.1 > rhs.1 }
        .prefix(limit)
        .map(\.0)
}

func render(symbol name: String, to outputURL: URL) throws {
    guard let base = NSImage(systemSymbolName: name, accessibilityDescription: name) else {
        throw NSError(domain: "sf-symbols", code: 2, userInfo: [NSLocalizedDescriptionKey: "Unavailable SF Symbol: \(name)"])
    }

    var configuration = NSImage.SymbolConfiguration(pointSize: 34, weight: .semibold)
    configuration = configuration.applying(.init(paletteColors: [.systemBlue]))
    guard let symbol = base.withSymbolConfiguration(configuration) else {
        throw NSError(domain: "sf-symbols", code: 3, userInfo: [NSLocalizedDescriptionKey: "Could not configure SF Symbol: \(name)"])
    }

    let size = NSSize(width: 64, height: 64)
    let canvas = NSImage(size: size)
    canvas.lockFocus()
    NSColor.clear.setFill()
    NSRect(origin: .zero, size: size).fill()

    let symbolSize = symbol.size
    let scale = min(44 / symbolSize.width, 44 / symbolSize.height)
    let drawSize = NSSize(width: symbolSize.width * scale, height: symbolSize.height * scale)
    let drawRect = NSRect(
        x: (size.width - drawSize.width) / 2,
        y: (size.height - drawSize.height) / 2,
        width: drawSize.width,
        height: drawSize.height
    )
    symbol.draw(in: drawRect)
    canvas.unlockFocus()

    guard
        let tiff = canvas.tiffRepresentation,
        let bitmap = NSBitmapImageRep(data: tiff),
        let png = bitmap.representation(using: .png, properties: [:])
    else {
        throw NSError(domain: "sf-symbols", code: 4, userInfo: [NSLocalizedDescriptionKey: "Could not encode SF Symbol: \(name)"])
    }

    try FileManager.default.createDirectory(at: outputURL.deletingLastPathComponent(), withIntermediateDirectories: true)
    try png.write(to: outputURL)
}

func usage() -> Never {
    fputs("Usage:\n  sf_symbols.swift list\n  sf_symbols.swift search [--limit N] TERM...\n  sf_symbols.swift render OUTPUT_DIR SYMBOL...\n", stderr)
    exit(2)
}

let arguments = Array(CommandLine.arguments.dropFirst())
guard let command = arguments.first else { usage() }

do {
    switch command {
    case "list":
        for name in try catalog() where !isLocalizedVariant(name) {
            print(name)
        }
    case "search":
        var rest = Array(arguments.dropFirst())
        var limit = 50
        if rest.count >= 2, rest[0] == "--limit", let parsed = Int(rest[1]) {
            limit = parsed
            rest.removeFirst(2)
        }
        guard !rest.isEmpty else { usage() }
        for name in try search(rest, limit: limit) {
            print(name)
        }
    case "render":
        guard arguments.count >= 3 else { usage() }
        let outputDirectory = URL(fileURLWithPath: arguments[1], isDirectory: true)
        for name in arguments.dropFirst(2) {
            let output = outputDirectory.appendingPathComponent("\(name).png")
            try render(symbol: name, to: output)
            print(output.path)
        }
    default:
        usage()
    }
} catch {
    fputs("sf_symbols: \(error.localizedDescription)\n", stderr)
    exit(1)
}
