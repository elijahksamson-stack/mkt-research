import assert from "node:assert/strict";
import test from "node:test";

import {
  createRequestHandler,
  loadCatalog,
  resolveIndustry,
  searchCatalog
} from "./index.js";

const catalog = await loadCatalog();

test("catalog discovers every industry module", () => {
  assert.equal(catalog.length, 39);
  assert.equal(new Set(catalog.map((module) => module.sector)).size, 11);
});

test("industry resolution accepts names and slugs", () => {
  assert.equal(resolveIndustry(catalog, "Semiconductors").module.industry, "Semiconductors");
  assert.equal(resolveIndustry(catalog, "oil-and-gas").module.industry, "Oil & Gas");
});

test("search ranks the relevant industry", () => {
  const searched = searchCatalog(catalog, { query: "deposit beta", max_results: 3 });
  assert.equal(searched.results[0].industry, "Banks");
  assert.match(searched.results[0].excerpt.toLowerCase(), /deposit beta/);
});

test("request handler exposes tools, resources, and bounded module chunks", async () => {
  const handleRequest = createRequestHandler(catalog);
  const tools = await handleRequest({ method: "tools/list" });
  const resources = await handleRequest({ method: "resources/list" });
  const retrieved = await handleRequest({
    method: "tools/call",
    params: {
      name: "get_industry_expertise",
      arguments: {
        industry: "Semiconductors",
        section: "Economics and Valuation",
        max_characters: 1000
      }
    }
  });

  assert.deepEqual(
    tools.tools.map((tool) => tool.name),
    ["list_industries", "get_industry_expertise", "search_industry_expertise"]
  );
  assert.equal(resources.resources.length, 39);
  assert.equal(retrieved.structuredContent.industry, "Semiconductors");
  assert.equal(retrieved.structuredContent.section, "5. Economics and Valuation");
  assert.equal(retrieved.structuredContent.endCharacter, 1000);
});
