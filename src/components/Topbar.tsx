import { ImageIcon } from "lucide-react";

export default function Topbar() {
  return (
    <nav className="w-full border-b border-white/5 bg-brand-bg/80 backdrop-blur-md sticky top-0 z-50">
      <div className="mx-auto max-w-[1200px] px-6 h-16 flex items-center">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-brand-accent to-brand-cyan flex items-center justify-center">
            <ImageIcon className="w-4.5 h-4.5 text-white" strokeWidth={1.8} />
          </div>
          <span className="text-lg font-semibold text-white tracking-tight">
            图小策
          </span>
        </div>
      </div>
    </nav>
  );
}
