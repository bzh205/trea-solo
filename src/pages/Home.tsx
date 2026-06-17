import Topbar from "@/components/Topbar";
import HeroSection from "@/components/HeroSection";
import FeatureGrid from "@/components/FeatureGrid";

export default function Home() {
  return (
    <div className="min-h-screen bg-brand-bg">
      <Topbar />
      <main>
        <HeroSection />
        <FeatureGrid />
      </main>
    </div>
  );
}
