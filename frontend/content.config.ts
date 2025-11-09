import { defineCollection, defineContentConfig, z } from "@nuxt/content"

const commonArticleSchema = z.object({
  // Define custom schema for docs collection
  title: z.string(),
  description: z.string(),
  author: z.string(),
  publishedAt: z.string(),
  categories: z.array(z.string()),
})

const commonCoreSchema = z.object({
  // Define custom schema for docs collection
  title: z.string(),
  description: z.string(),
  navigation: z.boolean(),
})

export default defineContentConfig({
  collections: {
    blog: defineCollection({
      source: "blog/*.md",
      type: "page",
      schema: commonArticleSchema,
    }),
    content: defineCollection({
      source: {
        include: "**/*.md",
        exclude: ["blog/**/*.md"],
        prefix: "/",
      },
      type: "page",
      schema: commonCoreSchema,
    }),
  },
})
