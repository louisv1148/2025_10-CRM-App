/**
 * Notion Block Parser
 * Converts Notion API block JSON into readable text and extracts images
 */

interface NotionRichText {
  type: string;
  text?: {
    content: string;
  };
  plain_text?: string;
}

interface NotionBlock {
  object: string;
  type: string;
  local_image_path?: string;
  paragraph?: {
    rich_text: NotionRichText[];
  };
  bulleted_list_item?: {
    rich_text: NotionRichText[];
  };
  numbered_list_item?: {
    rich_text: NotionRichText[];
  };
  heading_1?: {
    rich_text: NotionRichText[];
  };
  heading_2?: {
    rich_text: NotionRichText[];
  };
  heading_3?: {
    rich_text: NotionRichText[];
  };
  quote?: {
    rich_text: NotionRichText[];
  };
  code?: {
    rich_text: NotionRichText[];
  };
  image?: {
    caption?: any[];
    type?: string;
    file?: {
      url?: string;
    };
  };
}

export interface ParsedNotionContent {
  text: string;
  imagePaths: string[];
}

/**
 * Extract text content from Notion rich_text array
 */
function extractTextFromRichText(richText: NotionRichText[]): string {
  if (!richText || !Array.isArray(richText)) return "";

  return richText
    .map((item) => {
      if (item.plain_text) return item.plain_text;
      if (item.text?.content) return item.text.content;
      return "";
    })
    .join("");
}

/**
 * Parse a single Notion block into readable text
 */
function parseNotionBlock(block: NotionBlock): string {
  if (!block || typeof block !== "object") return "";

  const type = block.type;

  switch (type) {
    case "paragraph":
      return extractTextFromRichText(block.paragraph?.rich_text || []);

    case "bulleted_list_item":
      const bulletText = extractTextFromRichText(block.bulleted_list_item?.rich_text || []);
      return bulletText ? `• ${bulletText}` : "";

    case "numbered_list_item":
      const numberedText = extractTextFromRichText(block.numbered_list_item?.rich_text || []);
      return numberedText;

    case "heading_1":
      const h1Text = extractTextFromRichText(block.heading_1?.rich_text || []);
      return h1Text ? `# ${h1Text}` : "";

    case "heading_2":
      const h2Text = extractTextFromRichText(block.heading_2?.rich_text || []);
      return h2Text ? `## ${h2Text}` : "";

    case "heading_3":
      const h3Text = extractTextFromRichText(block.heading_3?.rich_text || []);
      return h3Text ? `### ${h3Text}` : "";

    case "quote":
      const quoteText = extractTextFromRichText(block.quote?.rich_text || []);
      return quoteText ? `> ${quoteText}` : "";

    case "code":
      const codeText = extractTextFromRichText(block.code?.rich_text || []);
      return codeText ? `\`\`\`\n${codeText}\n\`\`\`` : "";

    default:
      return "";
  }
}

/**
 * Parse Notion blocks JSON string into readable text
 * Handles both array of blocks and single block
 */
export function parseNotionContent(rawContent: string | undefined | null): string {
  if (!rawContent) return "";

  try {
    // Try to parse as JSON
    const parsed = JSON.parse(rawContent);

    // Handle array of blocks
    if (Array.isArray(parsed)) {
      return parsed
        .map((block) => parseNotionBlock(block))
        .filter((text) => text.trim().length > 0)
        .join("\n\n");
    }

    // Handle single block
    if (typeof parsed === "object") {
      return parseNotionBlock(parsed);
    }

    // If not JSON, return as-is
    return rawContent;
  } catch (error) {
    // If JSON parsing fails, return the original content
    // It might already be plain text
    return rawContent;
  }
}

/**
 * Parse Notion blocks JSON and extract both text and images
 * Returns an object with text content and array of image paths
 */
export function parseNotionContentWithImages(rawContent: string | undefined | null): ParsedNotionContent {
  const result: ParsedNotionContent = {
    text: "",
    imagePaths: []
  };

  if (!rawContent) return result;

  try {
    // Try to parse as JSON
    const parsed = JSON.parse(rawContent);

    // Handle array of blocks
    if (Array.isArray(parsed)) {
      const textBlocks: string[] = [];

      for (const block of parsed) {
        // Extract text from non-image blocks
        if (block.type !== "image") {
          const text = parseNotionBlock(block);
          if (text.trim().length > 0) {
            textBlocks.push(text);
          }
        }
        // Extract image paths
        else if (block.type === "image" && block.local_image_path) {
          result.imagePaths.push(block.local_image_path);
        }
      }

      result.text = textBlocks.join("\n\n");
    }
    // Handle single block
    else if (typeof parsed === "object") {
      if (parsed.type === "image" && parsed.local_image_path) {
        result.imagePaths.push(parsed.local_image_path);
      } else {
        result.text = parseNotionBlock(parsed);
      }
    }

    return result;
  } catch (error) {
    // If JSON parsing fails, return the original content as text
    result.text = rawContent;
    return result;
  }
}
