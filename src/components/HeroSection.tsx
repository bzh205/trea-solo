import { ArrowRight, Sparkles, MessageSquare, Wand2 } from "lucide-react";

const floatingTags = [
  { icon: Sparkles, label: "AI 理解", color: "from-brand-accent/20 to-brand-accent/5" },
  { icon: MessageSquare, label: "聊天规划", color: "from-brand-cyan/20 to-brand-cyan/5" },
  { icon: Wand2, label: "批量出图", color: "from-purple-500/20 to-purple-500/5" },
];

export default function HeroSection() {
  return (
    <section className="relative overflow-hidden py-16 md:py-24 lg:py-32">
      {/* 背景渐变光晕 */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[600px] h-[400px] bg-brand-accent/10 rounded-full blur-[120px]" />
        <div className="absolute top-1/3 right-1/4 w-[300px] h-[300px] bg-brand-cyan/8 rounded-full blur-[100px]" />
      </div>

      <div className="relative mx-auto max-w-[1200px] px-6 flex flex-col lg:flex-row items-center gap-12 lg:gap-16">
        {/* 左侧文案 */}
        <div className="flex-1 text-center lg:text-left">
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-white leading-tight tracking-tight">
            用聊天的方式
            <br />
            <span className="bg-gradient-to-r from-brand-accent to-brand-cyan bg-clip-text text-transparent">
              让 AI 精准生图
            </span>
          </h1>
          <p className="mt-6 text-lg md:text-xl text-brand-muted max-w-lg mx-auto lg:mx-0 leading-relaxed">
            上传图片、AI 理解需求、聊天式规划、一键批量出图。
            <br />
            覆盖电商、生活照、创意生图等场景。
          </p>
          <div className="mt-8 flex flex-col sm:flex-row items-center gap-4 justify-center lg:justify-start">
            <button className="w-full sm:w-auto px-8 py-3.5 rounded-full bg-gradient-to-r from-brand-accent to-brand-cyan text-white font-medium text-base hover:opacity-90 transition-opacity flex items-center justify-center gap-2">
              登录后进入工作台
              <ArrowRight className="w-4 h-4" />
            </button>
            <button className="w-full sm:w-auto px-8 py-3.5 rounded-full border border-brand-accent/40 text-brand-accent font-medium text-base hover:bg-brand-accent/10 transition-colors">
              注册新账号
            </button>
          </div>
        </div>

        {/* 右侧浮动标签 */}
        <div className="flex-shrink-0 relative w-full max-w-sm lg:max-w-md">
          <div className="relative aspect-square flex items-center justify-center">
            {/* 中心光圈 */}
            <div className="absolute inset-8 rounded-3xl bg-gradient-to-br from-brand-accent/10 via-brand-surface/50 to-brand-cyan/10 border border-white/5 backdrop-blur-sm" />

            {/* 浮动标签 */}
            {floatingTags.map((tag, i) => {
              const positions = [
                "top-4 right-4",
                "bottom-12 left-0",
                "bottom-4 right-8",
              ];
              return (
                <div
                  key={tag.label}
                  className={`absolute ${positions[i]} px-4 py-2.5 rounded-2xl bg-gradient-to-br ${tag.color} border border-white/10 backdrop-blur-md flex items-center gap-2 shadow-lg`}
                >
                  <tag.icon className="w-4 h-4 text-white/80" strokeWidth={1.8} />
                  <span className="text-sm font-medium text-white/90">{tag.label}</span>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}
