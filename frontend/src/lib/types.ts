export interface SourceRef {
  field: string;
  url?: string | null;
  note?: string | null;
}

export interface ScoredSupplier {
  name: string;
  category: string;
  description?: string | null;
  city?: string | null;
  region?: string | null;
  delivery_regions: string[];
  website?: string | null;
  email?: string | null;
  phone?: string | null;
  source_url?: string | null;
  min_order?: string | null;
  price_note?: string | null;
  certificates: string[];
  delivery_terms?: string | null;
  notes?: string | null;
  sources: SourceRef[];
  confidence: number;
  score: number;
  score_breakdown: Record<string, number>;
  reason?: string | null;
}

export interface SearchResponse {
  query_id: string;
  category: string;
  region?: string | null;
  source: "live" | "cache" | "seed";
  summary?: string | null;
  suppliers: ScoredSupplier[];
  warnings: string[];
}

export interface SearchRequest {
  category: string;
  region?: string;
  filters: {
    region?: string;
    needs_certificates: boolean;
    keyword?: string;
  };
  lang: "ru" | "en";
  limit: number;
}
