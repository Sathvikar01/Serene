import { SurfaceLoading } from "@/components/layout/SurfaceLoading";

// Test builds only: inspect the actual transition component without adding
// a slow network request or artificial delay to the product.
export default function LoadingFixturePage() {
  return <><h1 className="visually-hidden">Loading preview</h1><SurfaceLoading /></>;
}
