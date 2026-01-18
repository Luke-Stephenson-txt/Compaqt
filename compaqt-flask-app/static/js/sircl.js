/**
 * Semantic Identifier & Repetition Compaction Layer (SIRCL)
 * 
 * Experimental compaction layer that goes beyond formatting to compress
 * semantic-heavy tokens using high-density Unicode symbols and deterministic
 * symbol tables. Fully reversible with safety checks.
 * 
 * Key principles:
 * - Only encode when net token savings are positive
 * - Preserve control flow and critical semantics
 * - Use Unicode symbols selectively (high-frequency, long identifiers)
 * - Maintain deterministic, reversible encoding
 * - Fail safely on partial corruption
 */

// Utility functions (copied from compaction.js for SIRCL independence)

const State = {
  NORMAL: 0,
  LINE_COMMENT: 1,
  BLOCK_COMMENT: 2,
  STRING: 3,
  CHAR: 4,
  PREPROCESSOR: 5
};

const OPERATORS = [
  ">>=", "<<=", "++", "--", "->", "==", "!=", "<=", ">=",
  "&&", "||", "+=", "-=", "*=", "/=", "%=", "&=", "|=", "^=",
  "<<", ">>",
  "+", "-", "*", "/", "%", "=",
  "<", ">", "!", "~",
  "&", "|", "^",
  "?", ":", ",", ";",
  "(", ")", "[", "]", "{", "}"
].sort((a, b) => b.length - a.length);

function isIdentChar(c) {
  return /[a-zA-Z0-9_]/.test(c);
}

function minifyC(code) {
  const out = [];
  let i = 0;
  const n = code.length;
  let state = State.NORMAL;
  let atLineStart = true;

  while (i < n) {
    const c = code[i];

    if (state === State.NORMAL) {
      if (atLineStart && c === "#") {
        state = State.PREPROCESSOR;
        out.push(c);
        i += 1;
        atLineStart = false;
        continue;
      }

      if (c === "/" && i + 1 < n) {
        if (code[i + 1] === "/") {
          state = State.LINE_COMMENT;
          i += 2;
          continue;
        } else if (code[i + 1] === "*") {
          state = State.BLOCK_COMMENT;
          i += 2;
          continue;
        }
      }

      if (c === '"') {
        state = State.STRING;
        out.push(c);
        i += 1;
        continue;
      }

      if (c === "'") {
        state = State.CHAR;
        out.push(c);
        i += 1;
        continue;
      }

      if (/\s/.test(c)) {
        if (out.length > 0) {
          const prev = out[out.length - 1];
          const nextc = i + 1 < n ? code[i + 1] : "";

          if (isIdentChar(prev) && isIdentChar(nextc)) {
            out.push(" ");
          }
        }

        if (c === "\n") {
          atLineStart = true;
        }
        i += 1;
        continue;
      }

      let matched = false;
      for (const op of OPERATORS) {
        if (code.substring(i, i + op.length) === op) {
          out.push(op);
          i += op.length;
          matched = true;
          break;
        }
      }

      if (matched) {
        atLineStart = false;
        continue;
      }

      out.push(c);
      atLineStart = false;
      i += 1;
    } else if (state === State.LINE_COMMENT) {
      if (c === "\n") {
        state = State.NORMAL;
        atLineStart = true;
      }
      i += 1;
    } else if (state === State.BLOCK_COMMENT) {
      if (c === "*" && i + 1 < n && code[i + 1] === "/") {
        state = State.NORMAL;
        i += 2;
      } else {
        i += 1;
      }
    } else if (state === State.STRING) {
      out.push(c);
      if (c === "\\" && i + 1 < n) {
        out.push(code[i + 1]);
        i += 2;
      } else if (c === '"') {
        state = State.NORMAL;
        i += 1;
      } else {
        i += 1;
      }
    } else if (state === State.CHAR) {
      out.push(c);
      if (c === "\\" && i + 1 < n) {
        out.push(code[i + 1]);
        i += 2;
      } else if (c === "'") {
        state = State.NORMAL;
        i += 1;
      } else {
        i += 1;
      }
    } else if (state === State.PREPROCESSOR) {
      out.push(c);
      if (c === "\n") {
        state = State.NORMAL;
        atLineStart = true;
      }
      i += 1;
    }
  }

  return out.join("");
}

function estimateTokens(text) {
  if (!text) return 0;
  
  text = text.trim();
  if (!text) return 0;
  
  if (text.length <= 3) {
    return 1;
  }
  
  const segments = text.split(/[^a-zA-Z0-9]+/).filter(s => s.length > 0);
  
  if (segments.length === 0) {
    return Math.max(1, Math.ceil(text.length / 2));
  }
  
  let tokens = 0;
  
  for (const segment of segments) {
    if (segment.length <= 3) {
      tokens += 1;
    } else if (segment.length <= 6) {
      tokens += Math.ceil(segment.length / 4);
    } else {
      const camelCaseSplits = segment.match(/[a-z][A-Z]/g) || [];
      const effectiveLength = segment.length - (camelCaseSplits.length * 0.5);
      tokens += Math.ceil(effectiveLength / 3.5);
    }
  }
  
  const specialChars = (text.match(/[^\w\s]/g) || []).length;
  tokens += Math.ceil(specialChars / 3);
  
  return Math.max(1, tokens);
}

function calculateTokenSavings(original, symbol, frequency, existingLegendLength = 0) {
  const originalTokensPerOccurrence = estimateTokens(original);
  const totalOriginalTokens = originalTokensPerOccurrence * frequency;
  
  const symbolTokensPerOccurrence = estimateTokens(symbol);
  const totalSymbolTokens = symbolTokensPerOccurrence * frequency;
  
  const legendEntryText = existingLegendLength === 0 
    ? `// IDENTIFIERS: ${symbol}=${original}, `
    : `${symbol}=${original}, `;
  const legendEntryTokens = estimateTokens(legendEntryText);
  
  const tokenSavingsFromReplacement = totalOriginalTokens - totalSymbolTokens;
  const netSavings = tokenSavingsFromReplacement - legendEntryTokens;
  
  return {
    savings: netSavings,
    shouldReplace: netSavings > 0,
    originalTokens: totalOriginalTokens,
    symbolTokens: totalSymbolTokens,
    legendTokens: legendEntryTokens,
    replacementSavings: tokenSavingsFromReplacement
  };
}

// Chinese character symbol pool (CJK Unified Ideographs)
// Using common characters that are visually distinct
const CJK_SYMBOLS = [
  '甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸', // 10
  '子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', // 20
  '戌', '亥', '金', '木', '水', '火', '土', '日', '月', '星'  // 30
];

// ASCII macro symbols (for repeated patterns)
const ASCII_MACRO_PREFIX = '§';

// Control flow keywords that MUST remain readable
const CONTROL_FLOW_KEYWORDS = new Set([
  'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'break', 'continue',
  'return', 'goto', 'try', 'catch', 'throw'
]);

// Semantic-rich identifiers that should be preserved or encoded carefully
const SEMANTIC_PRESERVE_PATTERNS = [
  /^(main|init|setup|cleanup|destroy)$/i,
  /^(get|set|is|has|can|should|will)$/i, // Verbs
  /^(error|err|fail|success|ok|result)$/i, // Status
  /^(create|destroy|alloc|free|malloc|calloc|realloc)$/i // Memory ops
];

/**
 * Semantic Identifier Encoder (Stage A)
 * 
 * Encodes high-frequency, semantically rich identifiers using:
 * - Chinese characters for long identifiers (≥6 chars) with high frequency
 * - Short ASCII symbols (v0, f0, T0) for medium identifiers
 * - Preserves control flow, verbs, and critical semantics
 */
export class SemanticIdentifierEncoder {
  constructor(config = {}) {
    this.config = {
      // Minimum identifier length to consider for Chinese encoding
      minLengthForUnicode: config.minLengthForUnicode || 6,
      // Minimum frequency to consider encoding
      minFrequency: config.minFrequency || 3,
      // Minimum net token savings required
      minNetSavings: config.minNetSavings || 10,
      // Preserve control flow keywords
      preserveControlFlow: config.preserveControlFlow !== false,
      // Preserve semantic verbs
      preserveVerbs: config.preserveVerbs !== false,
      // Use hybrid encoding (keep verbs readable)
      hybridEncoding: config.hybridEncoding !== false,
      // Cross-file stability
      crossFileStable: config.crossFileStable !== false,
      ...config
    };
    
    // Symbol allocation
    this.cjkCounter = 0;
    this.asciiCounter = { variable: 0, function: 0, type: 0 };
    
    // Mappings
    this.globalMapping = new Map(); // original -> symbol
    this.globalReverseMapping = new Map(); // symbol -> original
    this.symbolMetadata = new Map(); // symbol -> { original, type, semanticHint }
  }
  
  /**
   * Check if identifier should be preserved (not encoded)
   */
  shouldPreserve(identifier, code, position) {
    // Preserve very short identifiers (won't save tokens)
    if (identifier.length <= 3) return true;
    
    // Preserve control flow if configured
    if (this.config.preserveControlFlow && CONTROL_FLOW_KEYWORDS.has(identifier)) {
      return true;
    }
    
    // Preserve semantic patterns (verbs, status, memory ops)
    if (this.config.preserveVerbs) {
      for (const pattern of SEMANTIC_PRESERVE_PATTERNS) {
        if (pattern.test(identifier)) return true;
      }
    }
    
    // CRITICAL: Preserve struct type names in typedef/struct declarations
    // Check if this identifier appears in a typedef struct or struct declaration context
    if (code && position !== undefined) {
      const before = code.substring(Math.max(0, position - 50), position);
      const after = code.substring(position + identifier.length, Math.min(code.length, position + identifier.length + 10));
      
      // Preserve if it's in typedef declaration: "typedef struct/enum/union { ... } identifier;"
      // Check if identifier appears right after closing brace and before semicolon
      if (after.trim().startsWith(';')) {
        const beforeTrimmed = before.trim();
        if (beforeTrimmed.endsWith('}')) {
          // Check if there's a typedef keyword before the opening brace
          const extendedBefore = code.substring(Math.max(0, position - 200), position);
          if (extendedBefore.match(/typedef\s*(struct|enum|union)\s*\{/)) {
            return true; // Preserve type name in typedef
          }
        }
      }
      
      // Preserve if it's in "struct identifier {" pattern (struct definition)
      if (before.match(/struct\s+$/) && after.trim().startsWith('{')) {
        return true;
      }
      
      // Preserve if it's in "enum identifier {" pattern (enum definition)
      if (before.match(/enum\s+$/) && after.trim().startsWith('{')) {
        return true;
      }
      
      // Preserve if it's in "union identifier {" pattern (union definition)
      if (before.match(/union\s+$/) && after.trim().startsWith('{')) {
        return true;
      }
      
      // Preserve if it's in forward declaration: "struct identifier;" or "enum identifier;"
      if ((before.match(/struct\s+$/) || before.match(/enum\s+$/) || before.match(/union\s+$/)) && after.trim().startsWith(';')) {
        return true;
      }
    }
    
    return false;
  }
  
  /**
   * Generate semantic hint for identifier
   */
  generateSemanticHint(original, type) {
    // Extract key semantic parts
    const parts = original.split(/[_-]/);
    const lastPart = parts[parts.length - 1];
    
    // For compound names, use the most meaningful part
    if (parts.length > 1) {
      // Prefer nouns over common prefixes
      const meaningfulParts = parts.filter(p => 
        !['get', 'set', 'is', 'has', 'the', 'a', 'an'].includes(p.toLowerCase())
      );
      return meaningfulParts[meaningfulParts.length - 1] || lastPart;
    }
    
    return lastPart;
  }
  
  /**
   * Allocate symbol for identifier
   * Returns: { symbol, shouldUseUnicode, semanticHint }
   */
  allocateSymbol(identifier, type, frequency, originalTokens) {
    // Check if we should use Unicode (Chinese) encoding
    const shouldUseUnicode = 
      identifier.length >= this.config.minLengthForUnicode &&
      originalTokens >= 2 && // Original must be 2+ tokens
      frequency >= this.config.minFrequency;
    
    let symbol;
    let semanticHint = this.generateSemanticHint(identifier, type);
    
    if (shouldUseUnicode && this.cjkCounter < CJK_SYMBOLS.length) {
      // Use Chinese character
      symbol = CJK_SYMBOLS[this.cjkCounter];
      this.cjkCounter++;
    } else {
      // Use short ASCII (v0, f0, T0)
      const prefix = type === 'function' ? 'f' : type === 'type' ? 'T' : 'v';
      const counterKey = type === 'function' ? 'function' : type === 'type' ? 'type' : 'variable';
      symbol = `${prefix}${this.asciiCounter[counterKey]}`;
      this.asciiCounter[counterKey]++;
    }
    
    return { symbol, shouldUseUnicode, semanticHint };
  }
  
  /**
   * Encode identifiers in code
   */
  encode(code, identifiers) {
    const mapping = new Map();
    const reverseMapping = new Map();
    
    // Count frequency
    const frequencyMap = new Map();
    for (const ident of identifiers) {
      frequencyMap.set(ident.name, (frequencyMap.get(ident.name) || 0) + 1);
    }
    
    // Build candidate list
    const candidates = [];
    let currentLegendLength = 0;
    
    for (const ident of identifiers) {
      // Check if should preserve (pass code and position for context-aware checks)
      if (this.shouldPreserve(ident.name, code, ident.position)) continue;
      
      const frequency = frequencyMap.get(ident.name);
      if (frequency < 2) continue; // Need at least 2 occurrences
      
      // Check if already mapped (cross-file stability)
      let symbol;
      let shouldUseUnicode = false;
      let semanticHint = null;
      
      if (this.config.crossFileStable && this.globalMapping.has(ident.name)) {
        symbol = this.globalMapping.get(ident.name);
        const metadata = this.symbolMetadata.get(symbol);
        semanticHint = metadata?.semanticHint;
        shouldUseUnicode = metadata?.shouldUseUnicode || false;
      } else {
        const originalTokens = estimateTokens(ident.name);
        const allocation = this.allocateSymbol(ident.name, ident.type, frequency, originalTokens);
        symbol = allocation.symbol;
        shouldUseUnicode = allocation.shouldUseUnicode;
        semanticHint = allocation.semanticHint;
        
        // Store in global mapping
        this.globalMapping.set(ident.name, symbol);
        this.globalReverseMapping.set(symbol, ident.name);
        this.symbolMetadata.set(symbol, {
          original: ident.name,
          type: ident.type,
          semanticHint: semanticHint,
          shouldUseUnicode: shouldUseUnicode
        });
      }
      
      // Calculate token savings
      const savings = calculateTokenSavings(ident.name, symbol, frequency, currentLegendLength);
      
      // For Unicode symbols, add semantic hint cost
      let legendEntryText;
      if (shouldUseUnicode && semanticHint) {
        // Format: "symbol=original (hint)"
        legendEntryText = currentLegendLength === 0
          ? `// IDENTIFIERS: ${symbol}=${ident.name} (${semanticHint}), `
          : `${symbol}=${ident.name} (${semanticHint}), `;
      } else {
        legendEntryText = currentLegendLength === 0
          ? `// IDENTIFIERS: ${symbol}=${ident.name}, `
          : `${symbol}=${ident.name}, `;
      }
      
      const legendEntryTokens = estimateTokens(legendEntryText);
      const netSavings = savings.replacementSavings - legendEntryTokens;
      
      // Only include if net savings meet threshold
      if (netSavings >= this.config.minNetSavings) {
        candidates.push({
          original: ident.name,
          symbol: symbol,
          type: ident.type,
          frequency: frequency,
          netSavings: netSavings,
          shouldUseUnicode: shouldUseUnicode,
          semanticHint: semanticHint,
          legendTokens: legendEntryTokens
        });
        currentLegendLength += legendEntryTokens;
      }
    }
    
    // Sort by net savings (highest first)
    candidates.sort((a, b) => b.netSavings - a.netSavings);
    
    // Build final mapping
    for (const candidate of candidates) {
      mapping.set(candidate.original, candidate.symbol);
      reverseMapping.set(candidate.symbol, candidate.original);
    }
    
    // Apply replacements (longest first) with context-aware replacement
    const sortedNames = Array.from(mapping.keys()).sort((a, b) => b.length - a.length);
    let result = code;
    
    for (const original of sortedNames) {
      const symbol = mapping.get(original);
      
      // Use a more sophisticated replacement that preserves struct/typedef contexts
      // Replace with word boundaries, but skip if in typedef struct context
      const escapedOriginal = original.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      const regex = new RegExp('\\b' + escapedOriginal + '\\b', 'g');
      
      // Find all matches in current result with their positions
      const matches = [];
      let match;
      // Reset regex lastIndex
      regex.lastIndex = 0;
      while ((match = regex.exec(result)) !== null) {
        matches.push({
          index: match.index,
          length: match[0].length,
          text: match[0]
        });
      }
      
      // Replace in reverse order to preserve indices
      for (let i = matches.length - 1; i >= 0; i--) {
        const m = matches[i];
        const offset = m.index;
        
        // Check context at this position in current result
        const before = result.substring(Math.max(0, offset - 100), offset);
        const after = result.substring(offset + m.length, Math.min(result.length, offset + m.length + 10));
        
        // Don't replace if in typedef declaration: "typedef struct/enum/union { ... } identifier;"
        // Check if identifier appears right after closing brace and before semicolon
        // This pattern works for both spaced and minified code
        if (after.trim().startsWith(';')) {
          // Look backwards to find if we're in a typedef context
          // Pattern: "} identifier;" where before contains "typedef"
          const beforeTrimmed = before.trim();
          if (beforeTrimmed.endsWith('}')) {
            // Check if there's a typedef keyword before the opening brace
            // Look for "typedef" followed by optional whitespace and struct/enum/union
            const extendedBefore = result.substring(Math.max(0, offset - 200), offset);
            if (extendedBefore.match(/typedef\s*(struct|enum|union)\s*\{/)) {
              continue; // Skip this occurrence - preserve type name in typedef
            }
          }
        }
        
        // Don't replace if in struct definition: "struct identifier {"
        if (before.match(/struct\s+$/) && after.trim().startsWith('{')) {
          continue; // Skip this occurrence - preserve struct name in definition
        }
        
        // Don't replace if in enum definition: "enum identifier {"
        if (before.match(/enum\s+$/) && after.trim().startsWith('{')) {
          continue; // Skip this occurrence - preserve enum name in definition
        }
        
        // Don't replace if in union definition: "union identifier {"
        if (before.match(/union\s+$/) && after.trim().startsWith('{')) {
          continue; // Skip this occurrence - preserve union name in definition
        }
        
        // Don't replace if in forward declaration: "struct identifier;" or "enum identifier;"
        if ((before.match(/struct\s+$/) || before.match(/enum\s+$/) || before.match(/union\s+$/)) && after.trim().startsWith(';')) {
          continue; // Skip this occurrence - preserve type name in forward declaration
        }
        
        // Replace with symbol
        result = result.substring(0, offset) + symbol + result.substring(offset + m.length);
      }
    }
    
    return {
      code: result,
      mapping: Object.fromEntries(mapping),
      reverseMapping: Object.fromEntries(reverseMapping),
      globalMapping: Object.fromEntries(this.globalMapping),
      globalReverseMapping: Object.fromEntries(this.globalReverseMapping),
      symbolMetadata: Object.fromEntries(this.symbolMetadata),
      candidates: candidates
    };
  }
}

/**
 * Enhanced Repetition Compressor (Stage B)
 * 
 * Detects and compresses repeated code fragments using macro symbols.
 * Enhanced to detect more patterns and calculate token savings accurately.
 */
export class EnhancedRepetitionCompressor {
  constructor(config = {}) {
    this.config = {
      minOccurrences: config.minOccurrences || 2,
      macroPrefix: config.macroPrefix || ASCII_MACRO_PREFIX,
      maxMacros: config.maxMacros || 26,
      minPatternLength: config.minPatternLength || 10, // Minimum pattern length
      ...config
    };
    this.macroCounter = 0;
    this.macros = new Map();
    this.reverseMacros = new Map();
  }
  
  /**
   * Normalize pattern for comparison
   */
  normalizePattern(code) {
    return code
      .replace(/\b[a-zA-Z_][a-zA-Z0-9_]*\b/g, 'VAR') // Replace identifiers
      .replace(/\d+\.?\d*/g, 'NUM') // Replace numbers
      .replace(/"[^"]*"/g, 'STR') // Replace strings
      .replace(/'[^']*'/g, 'CHAR') // Replace chars
      .replace(/\s+/g, ' ') // Normalize whitespace
      .trim();
  }
  
  /**
   * Detect repeated patterns in code
   */
  detectPatterns(code) {
    const patterns = [];
    const patternMap = new Map(); // normalized -> occurrences
    
    // Split code into potential patterns (statements, blocks)
    // Look for repeated sequences of statements
    
    // Pattern 1: Repeated function call patterns
    const callPattern = /[a-zA-Z_][a-zA-Z0-9_]*\s*\([^)]*\)\s*;/g;
    const calls = [...code.matchAll(callPattern)];
    const callGroups = new Map();
    for (const call of calls) {
      const normalized = this.normalizePattern(call[0]);
      if (!callGroups.has(normalized)) {
        callGroups.set(normalized, []);
      }
      callGroups.get(normalized).push(call);
    }
    
    for (const [normalized, occurrences] of callGroups.entries()) {
      if (occurrences.length >= this.config.minOccurrences) {
        const template = occurrences[0][0];
        if (template.length >= this.config.minPatternLength) {
          patterns.push({
            type: 'function_call',
            normalized: normalized,
            template: template,
            occurrences: occurrences,
            pattern: new RegExp(template.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g')
          });
        }
      }
    }
    
    // Pattern 2: Repeated assignment patterns
    const assignPattern = /[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*[^;]+;/g;
    const assigns = [...code.matchAll(assignPattern)];
    const assignGroups = new Map();
    for (const assign of assigns) {
      const normalized = this.normalizePattern(assign[0]);
      if (!assignGroups.has(normalized)) {
        assignGroups.set(normalized, []);
      }
      assignGroups.get(normalized).push(assign);
    }
    
    for (const [normalized, occurrences] of assignGroups.entries()) {
      if (occurrences.length >= this.config.minOccurrences) {
        const template = occurrences[0][0];
        if (template.length >= this.config.minPatternLength) {
          patterns.push({
            type: 'assignment',
            normalized: normalized,
            template: template,
            occurrences: occurrences,
            pattern: new RegExp(template.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g')
          });
        }
      }
    }
    
    // Pattern 3: Repeated struct initialization patterns
    const structPattern = /\{[^}]*\}/g;
    const structs = [...code.matchAll(structPattern)];
    const structGroups = new Map();
    for (const struct of structs) {
      const normalized = this.normalizePattern(struct[0]);
      if (normalized.length >= this.config.minPatternLength) {
        if (!structGroups.has(normalized)) {
          structGroups.set(normalized, []);
        }
        structGroups.get(normalized).push(struct);
      }
    }
    
    for (const [normalized, occurrences] of structGroups.entries()) {
      if (occurrences.length >= this.config.minOccurrences) {
        const template = occurrences[0][0];
        patterns.push({
          type: 'struct_init',
          normalized: normalized,
          template: template,
          occurrences: occurrences,
          pattern: new RegExp(template.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g')
        });
      }
    }
    
    return patterns;
  }
  
  /**
   * Compress repeated patterns
   */
  compress(code, patterns) {
    let result = code;
    const macroLegend = [];
    const macroMap = new Map();
    
    // Sort patterns by frequency and length (most profitable first)
    const sortedPatterns = patterns.sort((a, b) => {
      const aSavings = (a.template.length - 2) * a.occurrences.length; // Rough estimate
      const bSavings = (b.template.length - 2) * b.occurrences.length;
      return bSavings - aSavings;
    });
    
    for (const pattern of sortedPatterns) {
      if (this.macroCounter >= this.config.maxMacros) break;
      if (pattern.occurrences.length < this.config.minOccurrences) continue;
      
      const template = pattern.template;
      const occurrences = pattern.occurrences.length;
      
      // Calculate token savings
      const templateTokens = estimateTokens(template);
      const totalOriginalTokens = templateTokens * occurrences;
      
      const macroSymbol = `${this.config.macroPrefix}${String.fromCharCode(65 + this.macroCounter)}`;
      const symbolTokens = estimateTokens(macroSymbol);
      const totalSymbolTokens = symbolTokens * occurrences;
      
      // Legend cost
      const legendText = `// ${macroSymbol} = ${template.substring(0, 60)}${template.length > 60 ? '...' : ''}`;
      const legendTokens = estimateTokens(legendText);
      
      // Net savings
      const netSavings = totalOriginalTokens - totalSymbolTokens - legendTokens;
      
      // Only create macro if it saves tokens
      if (netSavings <= 0) continue;
      
      this.macroCounter++;
      
      this.macros.set(macroSymbol, template);
      this.reverseMacros.set(pattern.normalized, macroSymbol);
      
      // Replace all occurrences (in reverse order to preserve positions)
      const sortedOccurrences = [...pattern.occurrences].sort((a, b) => b.index - a.index);
      for (const match of sortedOccurrences) {
        const before = result.substring(0, match.index);
        const after = result.substring(match.index + match[0].length);
        result = before + macroSymbol + after;
        macroMap.set(match[0], macroSymbol);
      }
      
      macroLegend.push({
        symbol: macroSymbol,
        template: template,
        normalized: pattern.normalized,
        occurrences: occurrences,
        tokenSavings: netSavings
      });
    }
    
    return {
      code: result,
      macros: Object.fromEntries(this.macros),
      macroLegend: macroLegend,
      macroMap: Object.fromEntries(macroMap)
    };
  }
}

/**
 * SIRCL Encoder
 * 
 * Main encoder that orchestrates semantic identifier encoding and
 * repetition compression.
 */
export class SIRCLEncoder {
  constructor(config = {}) {
    this.config = {
      enableSemanticEncoding: config.enableSemanticEncoding !== false,
      enableRepetitionCompression: config.enableRepetitionCompression !== false,
      preserveControlFlow: config.preserveControlFlow !== false,
      preserveVerbs: config.preserveVerbs !== false,
      hybridEncoding: config.hybridEncoding !== false,
      crossFileStable: config.crossFileStable !== false,
      minLengthForUnicode: config.minLengthForUnicode || 6,
      minFrequency: config.minFrequency || 3,
      minNetSavings: config.minNetSavings || 10,
      macroMinOccurrences: config.macroMinOccurrences || 2,
      maxMacros: config.maxMacros || 26,
      ...config
    };
    
    this.semanticEncoder = new SemanticIdentifierEncoder({
      minLengthForUnicode: this.config.minLengthForUnicode,
      minFrequency: this.config.minFrequency,
      minNetSavings: this.config.minNetSavings,
      preserveControlFlow: this.config.preserveControlFlow,
      preserveVerbs: this.config.preserveVerbs,
      hybridEncoding: this.config.hybridEncoding,
      crossFileStable: this.config.crossFileStable
    });
    
    this.repetitionCompressor = new EnhancedRepetitionCompressor({
      minOccurrences: this.config.macroMinOccurrences,
      maxMacros: this.config.maxMacros
    });
  }
  
  /**
   * Encode a single file
   */
  encodeFile(code, filePath = '') {
    // Step 0: Minify C code first
    const minifiedCode = minifyC(code);
    
    // Simple parser for identifier extraction
    const parser = this.createParser(minifiedCode);
    let result = minifiedCode;
    const metadata = {
      filePath,
      originalLength: code.length,
      minifiedLength: minifiedCode.length,
      identifierMapping: {},
      macroLegend: [],
      symbolMetadata: {}
    };
    
    // Step 1: Semantic identifier encoding
    if (this.config.enableSemanticEncoding) {
      const identifiers = parser.extractIdentifiers();
      const encodeResult = this.semanticEncoder.encode(result, identifiers);
      result = encodeResult.code;
      metadata.identifierMapping = encodeResult.mapping;
      metadata.globalMapping = encodeResult.globalMapping;
      metadata.symbolMetadata = encodeResult.symbolMetadata;
    }
    
    // Step 2: Repetition compression
    if (this.config.enableRepetitionCompression) {
      const patterns = this.repetitionCompressor.detectPatterns(result);
      const compressResult = this.repetitionCompressor.compress(result, patterns);
      result = compressResult.code;
      metadata.macroLegend = compressResult.macroLegend;
      metadata.macros = compressResult.macros;
    }
    
    // Build final output with legend
    let output = '';
    let hasLegend = false;
    
    // Identifier legend
    if (Object.keys(metadata.identifierMapping).length > 0) {
      const legendEntries = [];
      for (const [orig, sym] of Object.entries(metadata.identifierMapping)) {
        const meta = metadata.symbolMetadata[sym];
        if (meta && meta.semanticHint && meta.shouldUseUnicode) {
          legendEntries.push(`${sym}=${orig} (${meta.semanticHint})`);
        } else {
          legendEntries.push(`${sym}=${orig}`);
        }
      }
      output += `// IDENTIFIERS: ${legendEntries.join(', ')}\n`;
      hasLegend = true;
    }
    
    // Macro legend
    if (metadata.macroLegend.length > 0) {
      output += `// MACROS:\n`;
      for (const macro of metadata.macroLegend) {
        const template = macro.template.length > 60 
          ? macro.template.substring(0, 57) + '...' 
          : macro.template;
        output += `// ${macro.symbol} = ${template.replace(/\n/g, ' ')}\n`;
      }
      hasLegend = true;
    }
    
    if (hasLegend) {
      output += '\n';
    }
    
    output += result;
    
    metadata.compressedLength = output.length;
    metadata.compressedCode = output;
    
    return {
      code: output,
      metadata
    };
  }
  
  /**
   * Encode multiple files (for cross-file stability)
   */
  encodeFiles(files) {
    const results = [];
    
    for (const file of files) {
      const result = this.encodeFile(file.content, file.path);
      results.push({
        ...file,
        content: result.code,
        size: result.code.length,
        originalSize: file.size,
        sirclMetadata: result.metadata
      });
    }
    
    return results;
  }
  
  /**
   * Create a simple parser for identifier extraction
   */
  createParser(code) {
    // Reuse SimpleCParser logic from compaction.js
    // For now, use a simplified version
    return {
      extractIdentifiers: () => {
        const identifiers = [];
        const pattern = /\b[a-zA-Z_][a-zA-Z0-9_]*\b/g;
        const keywords = new Set([
          'auto', 'break', 'case', 'char', 'const', 'continue', 'default', 'do',
          'double', 'else', 'enum', 'extern', 'float', 'for', 'goto', 'if',
          'inline', 'int', 'long', 'register', 'restrict', 'return', 'short',
          'signed', 'sizeof', 'static', 'struct', 'switch', 'typedef', 'union',
          'unsigned', 'void', 'volatile', 'while', '_Bool', 'Complex', '_Imaginary',
          'true', 'false', 'NULL'
        ]);
        
        let match;
        while ((match = pattern.exec(code)) !== null) {
          const ident = match[0];
          if (keywords.has(ident)) continue;
          
          const pos = match.index;
          const after = code.substring(pos + ident.length, Math.min(code.length, pos + ident.length + 10)).trim();
          
          let type = 'variable';
          if (after.startsWith('(')) {
            type = 'function';
          } else if (code.substring(Math.max(0, pos - 30), pos).match(/\b(struct|enum|typedef|union|class)\s+$/)) {
            type = 'type';
          }
          
          identifiers.push({
            name: ident,
            type: type,
            position: pos,
            length: ident.length
          });
        }
        
        return identifiers;
      }
    };
  }
}

/**
 * SIRCL Decoder with Safety Checks
 * 
 * Handles LLM output that may have been modified, with robust
 * error handling and fallback mechanisms.
 */
export class SIRCLDecoder {
  constructor() {
    this.identifierMapping = new Map();
    this.macroMapping = new Map();
    this.symbolMetadata = new Map();
  }
  
  /**
   * Parse legend from compressed code
   */
  parseLegend(code) {
    const lines = code.split('\n');
    const identifierMapping = {};
    const macroMapping = {};
    const symbolMetadata = {};
    let inMacros = false;
    
    for (const line of lines) {
      if (line.startsWith('// IDENTIFIERS:')) {
        const legendStr = line.substring('// IDENTIFIERS:'.length).trim();
        const entries = legendStr.split(',');
        for (const entry of entries) {
          const trimmed = entry.trim();
          // Handle format: "symbol=original" or "symbol=original (hint)"
          const match = trimmed.match(/^([^=]+)=(.+?)(?:\s*\(([^)]+)\))?$/);
          if (match) {
            const sym = match[1].trim();
            const orig = match[2].trim();
            const hint = match[3] ? match[3].trim() : null;
            identifierMapping[sym] = orig;
            if (hint) {
              symbolMetadata[sym] = { semanticHint: hint };
            }
          }
        }
      } else if (line.startsWith('// MACROS:')) {
        inMacros = true;
      } else if (inMacros && line.startsWith('// ') && line.includes('=')) {
        const match = line.match(/\/\/\s*([§A-Z])\s*=\s*(.+)/);
        if (match) {
          macroMapping[match[1]] = match[2].trim();
        }
      } else if (line.trim() && !line.startsWith('//')) {
        break;
      }
    }
    
    return { identifierMapping, macroMapping, symbolMetadata };
  }
  
  /**
   * Decode compressed code with safety checks
   */
  decode(code, options = {}) {
    const {
      strict = false, // If true, fail on unknown symbols
      preserveNewSymbols = true, // Preserve symbols not in mapping
      fallbackToOriginal = true // Fallback to uncompressed if decode fails
    } = options;
    
    try {
      // Parse legend
      const { identifierMapping, macroMapping, symbolMetadata } = this.parseLegend(code);
      
      // Remove legend from code
      let result = code;
      const legendEnd = result.indexOf('\n\n');
      if (legendEnd > 0 && result.substring(0, legendEnd).includes('//')) {
        result = result.substring(legendEnd + 2);
      }
      
      // Track unknown symbols
      const unknownSymbols = new Set();
      
      // Replace macros first (before identifier replacement)
      for (const [macro, template] of Object.entries(macroMapping)) {
        const regex = new RegExp(`\\b${macro.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'g');
        if (result.includes(macro)) {
          result = result.replace(regex, template);
        }
      }
      
      // Replace identifiers (longest symbols first)
      const sortedSymbols = Object.keys(identifierMapping).sort((a, b) => b.length - a.length);
      for (const symbol of sortedSymbols) {
        const original = identifierMapping[symbol];
        const regex = new RegExp(`\\b${symbol.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'g');
        result = result.replace(regex, original);
      }
      
      // Detect unknown symbols (potential LLM inventions)
      const symbolPattern = new RegExp(`\\b([${CJK_SYMBOLS.join('')}]|[vft]\\d+|§[A-Z])\\b`, 'g');
      let match;
      while ((match = symbolPattern.exec(result)) !== null) {
        const sym = match[1];
        if (!identifierMapping[sym] && !macroMapping[sym]) {
          unknownSymbols.add(sym);
        }
      }
      
      // Handle unknown symbols
      if (unknownSymbols.size > 0) {
        if (strict) {
          throw new Error(`Unknown symbols detected: ${Array.from(unknownSymbols).join(', ')}`);
        }
        // In non-strict mode, preserve unknown symbols (LLM may have introduced them)
        // Log for debugging
        console.warn(`SIRCL Decoder: Preserving unknown symbols: ${Array.from(unknownSymbols).join(', ')}`);
      }
      
      return {
        code: result,
        identifierMapping,
        macroMapping,
        symbolMetadata,
        unknownSymbols: Array.from(unknownSymbols),
        decoded: true,
        warnings: unknownSymbols.size > 0 ? [`Preserved ${unknownSymbols.size} unknown symbols`] : []
      };
    } catch (error) {
      if (fallbackToOriginal) {
        // Remove legend and return code as-is
        let result = code;
        const legendEnd = result.indexOf('\n\n');
        if (legendEnd > 0 && result.substring(0, legendEnd).includes('//')) {
          result = result.substring(legendEnd + 2);
        }
        return {
          code: result,
          decoded: false,
          error: error.message,
          warnings: ['Decode failed, returning code with legend removed']
        };
      } else {
        throw error;
      }
    }
  }
}

/**
 * Convenience functions
 */
export function encodeWithSIRCL(code, config = {}) {
  const encoder = new SIRCLEncoder(config);
  return encoder.encodeFile(code);
}

export function decodeSIRCL(code, options = {}) {
  const decoder = new SIRCLDecoder();
  return decoder.decode(code, options);
}
