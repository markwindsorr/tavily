// ArXiv category types
export type ArxivCategory = "cs" | "econ" | "math" | "physics" | "bio" | "finance" | "stat";

// Category chip definitions
export interface Category {
  id: ArxivCategory;
  label: string;
}

export const CATEGORIES: Category[] = [
  { id: "cs", label: "CS" },
  { id: "econ", label: "Econ" },
  { id: "math", label: "Math" },
  { id: "physics", label: "Physics" },
  { id: "bio", label: "Biology" },
  { id: "finance", label: "Finance" },
  { id: "stat", label: "Statistics" },
];

// Chat storage key
export const CHAT_STORAGE_KEY = "chat_messages";
