#!/usr/bin/env node

import { readdir, readFile } from "node:fs/promises";
import { basename, dirname, extname, join, resolve } from "node:path";
import { createInterface } from "node:readline";
import { fileURLToPath, pathToFileURL } from "node:url";

const SERVER_NAME = "subject-level-expertise";
const SERVER_VERSION = "1.0.0";
const CURRENT_PROTOCOL_VERSION = "2025-11-25";
const SUPPORTED_PROTOCOL_VERSIONS = new Set([
  CURRENT_PROTOCOL_VERSION,
  "2025-06-18",
  "2025-03-26",
  "2024-11-05"
]);
const PLUGIN_ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const KNOWLEDGE_ROOT = resolve(PLUGIN_ROOT, "skills", "industry-research", "references");

const TOOL_DEFINITIONS = [
  {
    name: "list_industries",
    title: "List industry expertise modules",
    description: "List the available sectors and industry expertise modules. Use this to resolve the repository's supported industry taxonomy before retrieving a module.",
    inputSchema: {
      type: "object",
      properties: {
        sector: {
          type: "string",
          description: "Optional sector name or partial sector name used to filter the catalog."
        }
      },
      additionalProperties: false
    },
    annotations: {
      readOnlyHint: true,
      idempotentHint: true,
      openWorldHint: false
    }
  },
  {
    name: "get_industry_expertise",
    title: "Get industry expertise",
    description: "Retrieve an industry module or one of its major sections. Results support character offsets so long modules can be read in bounded chunks.",
    inputSchema: {
      type: "object",
      properties: {
        industry: {
          type: "string",
          minLength: 1,
          description: "Industry name, filename, slug, or a unique partial match, such as 'Semiconductors' or 'oil-and-gas'."
        },
        sector: {
          type: "string",
          description: "Optional sector name used to disambiguate the industry."
        },
        section: {
          type: "string",
          description: "Optional level-two section title or unique partial title, such as 'Economics and Valuation'."
        },
        start_character: {
          type: "integer",
          minimum: 0,
          default: 0,
          description: "Zero-based character offset within the selected document or section."
        },
        max_characters: {
          type: "integer",
          minimum: 1000,
          maximum: 100000,
          default: 50000,
          description: "Maximum characters to return. Use start_character to retrieve the next chunk."
        }
      },
      required: ["industry"],
      additionalProperties: false
    },
    annotations: {
      readOnlyHint: true,
      idempotentHint: true,
      openWorldHint: false
    }
  },
  {
    name: "search_industry_expertise",
    title: "Search industry expertise",
    description: "Search across all industry modules, or within a selected sector or industry, and return ranked excerpts with resource identifiers.",
    inputSchema: {
      type: "object",
      properties: {
        query: {
          type: "string",
          minLength: 2,
          description: "Concept, metric, company role, regulation, technology, geography, or other text to search for."
        },
        sector: {
          type: "string",
          description: "Optional sector filter."
        },
        industry: {
          type: "string",
          description: "Optional industry filter."
        },
        max_results: {
          type: "integer",
          minimum: 1,
          maximum: 20,
          default: 8,
          description: "Maximum number of matching industry excerpts."
        },
        context_characters: {
          type: "integer",
          minimum: 200,
          maximum: 4000,
          default: 900,
          description: "Approximate number of characters surrounding each match."
        }
      },
      required: ["query"],
      additionalProperties: false
    },
    annotations: {
      readOnlyHint: true,
      idempotentHint: true,
      openWorldHint: false
    }
  }
];

function normalize(value) {
  return String(value ?? "")
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/&/g, " and ")
    .replace(/[^a-z0-9]+/g, " ")
    .trim()
    .replace(/\s+/g, " ");
}

function slugify(value) {
  return normalize(value).replace(/\s+/g, "-");
}

function titleFromMarkdown(content, filename) {
  const match = content.match(/^#\s+(.+)$/m);
  return match?.[1]?.trim() || basename(filename, extname(filename));
}

function extractSections(content) {
  const matches = [...content.matchAll(/^##\s+(.+)$/gm)];
  return matches.map((match, index) => ({
    title: match[1].trim(),
    start: match.index,
    end: matches[index + 1]?.index ?? content.length
  }));
}

export async function loadCatalog(root = KNOWLEDGE_ROOT) {
  const rootEntries = await readdir(root, { withFileTypes: true });
  const modules = [];

  for (const entry of rootEntries) {
    if (!entry.isDirectory() || entry.name.startsWith(".")) continue;

    const sectorPath = join(root, entry.name);
    const sectorFiles = (await readdir(sectorPath, { withFileTypes: true }))
      .filter((file) => file.isFile() && extname(file.name).toLowerCase() === ".md")
      .sort((left, right) => left.name.localeCompare(right.name));

    for (const file of sectorFiles) {
      const path = join(sectorPath, file.name);
      const content = await readFile(path, "utf8");
      const industry = titleFromMarkdown(content, file.name);
      const sector = entry.name;
      const industrySlug = slugify(industry);
      const sectorSlug = slugify(sector);

      modules.push({
        sector,
        sectorSlug,
        industry,
        industrySlug,
        filename: file.name,
        path,
        uri: `industry-expertise://${sectorSlug}/${industrySlug}`,
        content,
        sections: extractSections(content),
        aliases: new Set([
          normalize(industry),
          normalize(basename(file.name, extname(file.name))),
          normalize(industrySlug),
          normalize(`${sector} ${industry}`)
        ])
      });
    }
  }

  return modules.sort((left, right) =>
    left.sector.localeCompare(right.sector) || left.industry.localeCompare(right.industry)
  );
}

function filterBySector(catalog, sector) {
  if (!sector) return catalog;
  const query = normalize(sector);
  return catalog.filter((module) => {
    const candidate = normalize(module.sector);
    return candidate === query || candidate.includes(query) || query.includes(candidate);
  });
}

export function resolveIndustry(catalog, industry, sector) {
  const query = normalize(industry);
  if (!query) {
    return { error: "The industry argument must not be empty." };
  }

  const sectorMatches = filterBySector(catalog, sector);
  if (sector && sectorMatches.length === 0) {
    return { error: `No sector matches "${sector}".` };
  }

  const exact = sectorMatches.filter((module) => module.aliases.has(query));
  if (exact.length === 1) return { module: exact[0] };

  const partial = sectorMatches.filter((module) =>
    [...module.aliases].some((alias) => alias.includes(query) || query.includes(alias))
  );
  const candidates = exact.length > 1 ? exact : partial;

  if (candidates.length === 1) return { module: candidates[0] };
  if (candidates.length === 0) {
    return { error: `No industry module matches "${industry}"${sector ? ` in ${sector}` : ""}.` };
  }

  return {
    error: `"${industry}" is ambiguous. Choose one of: ${candidates
      .map((module) => `${module.sector} / ${module.industry}`)
      .join(", ")}.`
  };
}

function resolveSection(module, requestedSection) {
  if (!requestedSection) {
    return { title: null, content: module.content };
  }

  const query = normalize(requestedSection);
  const exact = module.sections.filter((section) => normalize(section.title) === query);
  const partial = module.sections.filter((section) => normalize(section.title).includes(query));
  const candidates = exact.length > 0 ? exact : partial;

  if (candidates.length === 1) {
    const section = candidates[0];
    return {
      title: section.title,
      content: module.content.slice(section.start, section.end).trimEnd()
    };
  }

  if (candidates.length > 1) {
    return {
      error: `Section "${requestedSection}" is ambiguous. Choose one of: ${candidates
        .map((section) => section.title)
        .join(", ")}.`
    };
  }

  return {
    error: `No section matches "${requestedSection}". Available sections: ${module.sections
      .map((section) => section.title)
      .join(", ")}.`
  };
}

function clampInteger(value, fallback, minimum, maximum) {
  if (!Number.isInteger(value)) return fallback;
  return Math.min(maximum, Math.max(minimum, value));
}

function toolText(text, structuredContent) {
  const result = { content: [{ type: "text", text }] };
  if (structuredContent !== undefined) result.structuredContent = structuredContent;
  return result;
}

function toolError(message) {
  return {
    isError: true,
    content: [{ type: "text", text: message }]
  };
}

function listIndustries(catalog, args) {
  const matches = filterBySector(catalog, args.sector);
  if (args.sector && matches.length === 0) {
    return toolError(`No sector matches "${args.sector}".`);
  }

  const sectors = new Map();
  for (const module of matches) {
    if (!sectors.has(module.sector)) sectors.set(module.sector, []);
    sectors.get(module.sector).push({
      industry: module.industry,
      uri: module.uri,
      sections: module.sections.map((section) => section.title)
    });
  }

  const data = [...sectors].map(([sector, industries]) => ({ sector, industries }));
  const lines = data.flatMap(({ sector, industries }) => [
    `## ${sector}`,
    ...industries.map(({ industry, uri }) => `- ${industry} — ${uri}`),
    ""
  ]);

  return toolText(
    `${matches.length} industry modules across ${data.length} sectors.\n\n${lines.join("\n").trim()}`,
    { count: matches.length, sectors: data }
  );
}

function getIndustryExpertise(catalog, args) {
  const resolved = resolveIndustry(catalog, args.industry, args.sector);
  if (resolved.error) return toolError(resolved.error);

  const module = resolved.module;
  const selected = resolveSection(module, args.section);
  if (selected.error) return toolError(selected.error);

  const start = clampInteger(args.start_character, 0, 0, selected.content.length);
  const limit = clampInteger(args.max_characters, 50000, 1000, 100000);
  const end = Math.min(selected.content.length, start + limit);
  const chunk = selected.content.slice(start, end);
  const truncated = end < selected.content.length;
  const header = [
    `Sector: ${module.sector}`,
    `Industry: ${module.industry}`,
    `Resource: ${module.uri}`,
    `Section: ${selected.title ?? "Full module"}`,
    `Characters: ${start}-${end} of ${selected.content.length}`
  ].join("\n");
  const continuation = truncated
    ? `\n\n[Truncated. Call get_industry_expertise again with start_character: ${end}.]`
    : "";

  return toolText(`${header}\n\n${chunk}${continuation}`, {
    sector: module.sector,
    industry: module.industry,
    uri: module.uri,
    section: selected.title,
    startCharacter: start,
    endCharacter: end,
    totalCharacters: selected.content.length,
    truncated,
    nextStartCharacter: truncated ? end : null
  });
}

function countOccurrences(text, term) {
  let count = 0;
  let position = 0;
  while ((position = text.indexOf(term, position)) !== -1) {
    count += 1;
    position += Math.max(term.length, 1);
  }
  return count;
}

function makeExcerpt(content, position, contextCharacters) {
  const half = Math.floor(contextCharacters / 2);
  let start = Math.max(0, position - half);
  let end = Math.min(content.length, position + half);

  if (start > 0) {
    const nextBoundary = content.indexOf("\n", start);
    if (nextBoundary !== -1 && nextBoundary < position) start = nextBoundary + 1;
  }
  if (end < content.length) {
    const previousBoundary = content.lastIndexOf("\n", end);
    if (previousBoundary > position) end = previousBoundary;
  }

  return `${start > 0 ? "…" : ""}${content.slice(start, end).trim()}${end < content.length ? "…" : ""}`;
}

export function searchCatalog(catalog, args) {
  const query = String(args.query ?? "").trim();
  if (query.length < 2) return { error: "The search query must contain at least two characters." };

  let candidates = filterBySector(catalog, args.sector);
  if (args.sector && candidates.length === 0) {
    return { error: `No sector matches "${args.sector}".` };
  }

  if (args.industry) {
    const resolved = resolveIndustry(candidates, args.industry, args.sector);
    if (resolved.error) return resolved;
    candidates = [resolved.module];
  }

  const normalizedQuery = normalize(query);
  const terms = normalizedQuery.split(" ").filter((term) => term.length > 1);
  const contextCharacters = clampInteger(args.context_characters, 900, 200, 4000);
  const maxResults = clampInteger(args.max_results, 8, 1, 20);
  const results = [];

  for (const module of candidates) {
    const lowerContent = module.content.toLowerCase();
    const exactPosition = lowerContent.indexOf(query.toLowerCase());
    const termPositions = terms
      .map((term) => lowerContent.indexOf(term))
      .filter((position) => position >= 0);
    if (exactPosition < 0 && termPositions.length === 0) continue;

    const exactCount = countOccurrences(lowerContent, query.toLowerCase());
    const termCount = terms.reduce((total, term) => total + countOccurrences(lowerContent, term), 0);
    const matchedTerms = terms.filter((term) => lowerContent.includes(term)).length;
    const score = exactCount * 20 + matchedTerms * 4 + Math.min(termCount, 20);
    const position = exactPosition >= 0 ? exactPosition : Math.min(...termPositions);

    results.push({
      sector: module.sector,
      industry: module.industry,
      uri: module.uri,
      score,
      excerpt: makeExcerpt(module.content, position, contextCharacters)
    });
  }

  return {
    results: results
      .sort((left, right) => right.score - left.score || left.industry.localeCompare(right.industry))
      .slice(0, maxResults)
  };
}

function searchIndustryExpertise(catalog, args) {
  const searched = searchCatalog(catalog, args);
  if (searched.error) return toolError(searched.error);
  if (searched.results.length === 0) {
    return toolText(`No industry expertise matches "${args.query}".`, { query: args.query, results: [] });
  }

  const text = searched.results
    .map(
      (result, index) =>
        `## ${index + 1}. ${result.sector} / ${result.industry}\nResource: ${result.uri}\n\n${result.excerpt}`
    )
    .join("\n\n");

  return toolText(text, { query: args.query, results: searched.results });
}

function resourceList(catalog) {
  return catalog.map((module) => ({
    uri: module.uri,
    name: `${module.sector} / ${module.industry}`,
    title: module.industry,
    description: `End-to-end investment research orientation for ${module.industry} in ${module.sector}.`,
    mimeType: "text/markdown",
    annotations: {
      audience: ["assistant"],
      priority: 0.8
    }
  }));
}

function promptList() {
  return [
    {
      name: "investigate-industry",
      title: "Investigate an industry",
      description: "Ground a company, security, or research question in the relevant industry module.",
      arguments: [
        {
          name: "industry",
          description: "Industry to investigate.",
          required: true
        },
        {
          name: "focus",
          description: "Optional company, security, theme, or question to analyze.",
          required: false
        }
      ]
    }
  ];
}

function promptGet(params) {
  if (params.name !== "investigate-industry") {
    throw rpcError(-32602, `Unknown prompt: ${params.name}`);
  }
  const industry = String(params.arguments?.industry ?? "").trim();
  if (!industry) throw rpcError(-32602, "The industry prompt argument is required.");
  const focus = String(params.arguments?.focus ?? "").trim();
  const focusInstruction = focus
    ? ` Apply that context specifically to: ${focus}.`
    : " Identify the key implications for security-level investment research.";

  return {
    description: `Investigate ${industry} using the subject-level expertise catalog.`,
    messages: [
      {
        role: "user",
        content: {
          type: "text",
          text: `Use the industry-expertise MCP tools to retrieve the ${industry} module. Analyze the industry's structure, economics, value chain, operating mechanics, competitive dynamics, regulation, geographic dependencies, risks, and disruption.${focusInstruction} Verify time-sensitive claims against current primary sources.`
        }
      }
    ]
  };
}

function rpcError(code, message, data) {
  const error = new Error(message);
  error.rpcCode = code;
  if (data !== undefined) error.rpcData = data;
  return error;
}

export function createRequestHandler(catalog) {
  const resourcesByUri = new Map(catalog.map((module) => [module.uri, module]));

  return async function handleRequest(request) {
    const params = request.params ?? {};

    switch (request.method) {
      case "initialize": {
        const requestedVersion = params.protocolVersion;
        const protocolVersion = SUPPORTED_PROTOCOL_VERSIONS.has(requestedVersion)
          ? requestedVersion
          : CURRENT_PROTOCOL_VERSION;
        return {
          protocolVersion,
          capabilities: {
            tools: { listChanged: false },
            resources: { listChanged: false, subscribe: false },
            prompts: { listChanged: false }
          },
          serverInfo: {
            name: SERVER_NAME,
            title: "Subject-Level Industry Expertise",
            version: SERVER_VERSION,
            description: "Sector- and industry-level orientation for investment research."
          },
          instructions: "Use list_industries to resolve the supported taxonomy, get_industry_expertise to retrieve a module or section, and search_industry_expertise for cross-industry or concept-specific retrieval. Verify time-sensitive facts against current primary sources."
        };
      }
      case "ping":
        return {};
      case "tools/list":
        return { tools: TOOL_DEFINITIONS };
      case "tools/call": {
        const args = params.arguments ?? {};
        switch (params.name) {
          case "list_industries":
            return listIndustries(catalog, args);
          case "get_industry_expertise":
            return getIndustryExpertise(catalog, args);
          case "search_industry_expertise":
            return searchIndustryExpertise(catalog, args);
          default:
            throw rpcError(-32602, `Unknown tool: ${params.name}`);
        }
      }
      case "resources/list":
        return { resources: resourceList(catalog) };
      case "resources/read": {
        const module = resourcesByUri.get(params.uri);
        if (!module) throw rpcError(-32002, `Resource not found: ${params.uri}`);
        return {
          contents: [
            {
              uri: module.uri,
              name: `${module.sector} / ${module.industry}`,
              title: module.industry,
              mimeType: "text/markdown",
              text: module.content
            }
          ]
        };
      }
      case "resources/templates/list":
        return { resourceTemplates: [] };
      case "prompts/list":
        return { prompts: promptList() };
      case "prompts/get":
        return promptGet(params);
      default:
        throw rpcError(-32601, `Method not found: ${request.method}`);
    }
  };
}

function writeMessage(message) {
  process.stdout.write(`${JSON.stringify(message)}\n`);
}

async function runServer() {
  const catalog = await loadCatalog();
  if (catalog.length === 0) {
    throw new Error(`No industry modules were found under ${KNOWLEDGE_ROOT}.`);
  }
  const handleRequest = createRequestHandler(catalog);
  const input = createInterface({ input: process.stdin, crlfDelay: Infinity });

  for await (const line of input) {
    if (!line.trim()) continue;

    let request;
    try {
      request = JSON.parse(line);
    } catch (error) {
      writeMessage({
        jsonrpc: "2.0",
        id: null,
        error: { code: -32700, message: "Parse error", data: error.message }
      });
      continue;
    }

    if (request.jsonrpc !== "2.0" || typeof request.method !== "string") {
      if (request.id !== undefined) {
        writeMessage({
          jsonrpc: "2.0",
          id: request.id ?? null,
          error: { code: -32600, message: "Invalid Request" }
        });
      }
      continue;
    }

    if (request.id === undefined) continue;

    try {
      const result = await handleRequest(request);
      writeMessage({ jsonrpc: "2.0", id: request.id, result });
    } catch (error) {
      writeMessage({
        jsonrpc: "2.0",
        id: request.id,
        error: {
          code: error.rpcCode ?? -32603,
          message: error.message || "Internal error",
          ...(error.rpcData === undefined ? {} : { data: error.rpcData })
        }
      });
    }
  }
}

const isMain = process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href;
if (isMain) {
  runServer().catch((error) => {
    process.stderr.write(`${SERVER_NAME}: ${error.stack || error.message}\n`);
    process.exitCode = 1;
  });
}
