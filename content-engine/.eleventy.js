import { feedPlugin } from "@11ty/eleventy-plugin-rss";
import markdownItAnchor from "markdown-it-anchor";

export default function (eleventyConfig) {
  // ===========================================================================
  // Collections — group articles by cluster for navigation/related-links
  // ===========================================================================
  const clusters = [
    "cost", "industries", "platforms", "redesign", "conversion",
    "performance", "seo", "brand", "operations", "ai-search", "process",
  ];

  clusters.forEach((cluster) => {
    eleventyConfig.addCollection(cluster, (api) =>
      api.getAll().filter((item) => item.data.cluster === cluster)
    );
  });

  // Pillars only (across all clusters)
  eleventyConfig.addCollection("pillars", (api) =>
    api.getAll().filter((item) => item.data.pillar === true)
  );

  // All articles (excluding home, sitemap)
  eleventyConfig.addCollection("articles", (api) =>
    api
      .getAll()
      .filter((item) => item.data.cluster)
      .sort((a, b) => (a.data.write_order || 999) - (b.data.write_order || 999))
  );

  // ===========================================================================
  // Filters
  // ===========================================================================
  eleventyConfig.addFilter("isoDate", (d) =>
    new Date(d).toISOString()
  );
  eleventyConfig.addFilter("readableDate", (d) =>
    new Date(d).toLocaleDateString("en-US", {
      year: "numeric", month: "long", day: "numeric",
    })
  );
  eleventyConfig.addFilter("readingTime", (text) => {
    const words = (text || "").split(/\s+/).length;
    return Math.max(1, Math.ceil(words / 220));
  });

  // ===========================================================================
  // Markdown — anchor links on H2/H3 for deep-linking from AI engines
  // ===========================================================================
  eleventyConfig.amendLibrary("md", (md) =>
    md.use(markdownItAnchor, {
      level: [2, 3],
      permalink: markdownItAnchor.permalink.headerLink(),
    })
  );

  // ===========================================================================
  // RSS feed — for SEO discovery and AI crawler signals
  // ===========================================================================
  eleventyConfig.addPlugin(feedPlugin, {
    type: "atom",
    outputPath: "/feed.xml",
    collection: { name: "articles", limit: 50 },
    metadata: {
      language: "en",
      title: "DesigXner — Web Design Insights for Small Businesses",
      subtitle: "Practical web design and development advice for SMBs.",
      base: "https://designxner.com/",
      author: { name: "DesigXner" },
    },
  });

  // ===========================================================================
  // Passthrough copy (CSS, images, downloadable assets)
  // ===========================================================================
  eleventyConfig.addPassthroughCopy("src/css");
  eleventyConfig.addPassthroughCopy("src/images");
  eleventyConfig.addPassthroughCopy("src/downloads");
  eleventyConfig.addPassthroughCopy("src/tools");

  return {
    dir: { input: "src", output: "_site", includes: "_includes" },
    markdownTemplateEngine: "njk",
    htmlTemplateEngine: "njk",
    templateFormats: ["md", "njk", "html"],
  };
}
